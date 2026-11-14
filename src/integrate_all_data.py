"""Data-only integration: all physical telemetry, calibrated sensors and BASS matrices.

No reports, image indices, photo metadata or synthetic measurements are included.
"""
from pathlib import Path
import json,re,hashlib
import pandas as pd
import duckdb
from src.build_dataset import parse_value
from src.build_expanded_dataset import slug

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/integrated'

def q(s):return '"'+str(s).replace('"','""')+'"'
def lit(s):return "'"+str(s).replace("'","''")+"'"
def num(s):return pd.to_numeric(s,errors='coerce')

def channel_name(header):
 h=str(header).strip()
 h=re.sub(r'^P@sfsHk\.', '',h)
 h=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',h)
 h=re.sub(r'(\d)([A-Za-z])',r'\1 \2',h)
 h=re.sub(r'([A-Za-z])(\d)',r'\1 \2',h)
 h=re.sub(r'\s*\([^)]*\)\s*$','',h).strip()
 h=re.sub(r'\bvalue$','',h,flags=re.I)
 h=re.sub(r'IgniterV$', 'Igniter Voltage',h)
 h=re.sub(r'IgniterI$', 'Igniter Current',h)
 h=h.replace('Smoke Wire V','Smoke Wire Voltage').replace('Smoke Wire I','Smoke Wire Current')
 return slug(h)

def unit(header):
 m=re.search(r'\(([^()]*)\)\s*$',header)
 return m.group(1) if m else None

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 con=duckdb.connect(str(OUT/'nasa_integrado.duckdb'))
 con.execute("SET memory_limit='1GB'")
 con.execute('SET threads=2')
 con.execute('CREATE OR REPLACE TABLE staging (investigation_id VARCHAR, domain VARCHAR, clock VARCHAR, time_key VARCHAR, source_test_id VARCHAR, channel VARCHAR, unit VARCHAR, value DOUBLE, origin_id VARCHAR, source_table_id VARCHAR, source_row BIGINT, source_column BIGINT)')
 catalog=pd.read_csv(ROOT/'data/expanded_processed/table_catalog.csv').fillna('')
 source_manifest=json.loads((ROOT/'data/expanded_raw/manifest.json').read_text(encoding='utf-8'))
 source_info={f['file_id']:f for f in source_manifest}
 tables=[];columns=[];excluded=[];matrix_rows=[];calibration=[];matrix_columns=[]
 def add_series(cat,d,start,time_col,clock,domain,selected_cols,test='',time_offset=0):
  """Each channel selects its own physical clock; missing clocks retain row identity."""
  t=num(d.iloc[start:,time_col]);valid=t.notna();rows=d.index[start:][valid]+1
  if not len(rows):return
  times=t[valid]
  key=times.map(lambda x:format(float(x),'.17g'))
  # Zero clocks are not observations at epoch zero and must not collapse unrelated records.
  bad=times<=0
  key=key.where(~bad, pd.Series([f'unknown:{cat.file_id}:{cat.sheet}:r{r}' for r in rows],index=key.index))
  table_id=f'{cat.file_id}:{cat.sheet}'
  for ci,h,u in selected_cols:
   values=num(d.iloc[start:,ci]).loc[valid]
   nonnull=values.notna()
   if not nonnull.any():continue
   frame=pd.DataFrame({'investigation_id':cat.investigation_id,'domain':domain,'clock':clock,
    'time_key':key.loc[nonnull].values,'source_test_id':test,'channel':h,'unit':u,
    'value':values.loc[nonnull].astype(float).values,'source_row':rows[nonnull.to_numpy()],
    'source_column':ci+1,'source_table_id':table_id})
   frame['origin_id']=[f'{table_id}:r{r}:c{ci+1}' for r in frame.source_row]
   con.register('_values',frame)
   con.execute('INSERT INTO staging BY NAME SELECT * FROM _values');con.unregister('_values')
 def add_matrix(cat,d,header_row,start,record_type):
  headers=d.iloc[header_row].tolist()
  # Camera acquisition fields do not describe physical experimental measurements.
  skip=re.compile(r'camera|shutter|iso\b|f.stop|exposure|bracket|release.mode|sd.card|frames|filter.y|date.on.video',re.I)
  keep=[i for i,h in enumerate(headers) if h.strip() and not skip.search(h)]
  names=[];seen={}
  for i in keep:
   h=headers[i];s=slug(h);seen[s]=seen.get(s,0)+1
   k=s if seen[s]==1 else f'{s}_{seen[s]}'
   names.append((i,k))
   matrix_columns.append({'table_id':f'{cat.file_id}:{cat.sheet}','column':k,'source_header':h,'source_column':i+1})
  for idx in range(start,len(d)):
   vals={h:d.iloc[idx,i] for i,h in names if d.iloc[idx,i].strip()}
   if not vals:continue
   # Exclude setup/header/footer rows; keep records with a published test-point identifier.
   ids=[v for k,v in vals.items() if k in ('test_no','test_point','test_no_')]
   if not ids or not any(re.fullmatch(r'[A-Za-z]?\d+[A-Za-z0-9-]*',v.strip()) for v in ids):continue
   matrix_rows.append({'investigation_id':cat.investigation_id,'record_type':record_type,
    'source_table_id':f'{cat.file_id}:{cat.sheet}','source_row':idx+1,
    'source_record_id':f'{cat.file_id}:{cat.sheet}:r{idx+1}',
    'source_test_id':ids[0].strip(),'values_json':json.dumps(vals,ensure_ascii=False)})

 for cat in catalog.itertuples():
  if cat.status!='extracted' or cat.category=='image_index':
   excluded.append({'file_name':cat.file_name,'sheet':cat.sheet,'reason':'image_index_or_camera_metadata'});continue
  d=pd.read_parquet(ROOT/cat.local_table).fillna('')
  headers=d.iloc[0].tolist();tid=f'{cat.file_id}:{cat.sheet}'
  tables.append({'source_table_id':tid,'investigation_id':cat.investigation_id,'source_file_name':cat.file_name,
    'source_sheet':cat.sheet,'doi':source_info[cat.file_id]['doi'],'source_file_sha256':source_info[cat.file_id].get('sha256','')})
  print('INTEGRATE',cat.investigation_id,cat.sheet,flush=True)
  if cat.category=='calibrated_sensors':
   n=int(re.search(r'Sample (\d+)',cat.file_name,re.I).group(1));test=f'2-{n}' if cat.investigation_id=='PSI-99' else f'S{n}'
   units=d.iloc[1].tolist()
   chosen=[]
   for i,h in enumerate(headers):
    if i<4 or not h.strip() or re.search(r'avg|average|camera|led|gse|pc104|avionics|control|enable|select|set point|tach /100',h,re.I):continue
    chosen.append((i,channel_name(h),units[i] or unit(h)))
    columns.append({'source_table_id':tid,'source_column':i+1,'source_header':h,'channel':channel_name(h),'unit':units[i] or unit(h),'domain':'sample_calibrated'})
   add_series(cat,d,2,1,'epoch_time_ms_source','sample_calibrated',chosen,test)
   continue
  if cat.investigation_id in ('PSI-25','PSI-26'):
   if cat.sheet=='CSV':continue # Original summaries are imported as structured observations below.
   if cat.sheet=='BASS Test Matrix':add_matrix(cat,d,4,6,'planned_conditions')
   elif cat.investigation_id=='PSI-25' and cat.sheet!='Fan Calibration data':add_matrix(cat,d,0,1,'reported_conditions')
   elif cat.sheet in ('as run matrix','2012'):add_matrix(cat,d,2,3,'reported_conditions')
   elif cat.sheet=='2013':add_matrix(cat,d,1,3,'reported_conditions')
   elif cat.sheet=='TP without Data':
    # Same columns as the as-run matrix; only data rows, not introductory text.
    template=catalog[(catalog.sheet=='as run matrix')].iloc[0]
    h=pd.read_parquet(ROOT/template.local_table).iloc[2].tolist()
    dd=d.copy();dd.iloc[0]=h;add_matrix(cat,dd,0,3,'reported_conditions_without_media')
   elif cat.sheet=='Fan Calibration data':
    # Independent calibration blocks use their own date/GMT and labels; never flatten dates away.
    starts=[i for i,v in enumerate(d.iloc[5]) if v.strip()=='Pot']
    for bi,begin in enumerate(starts):
     end=starts[bi+1] if bi+1<len(starts) else len(d.columns)
     hs=d.iloc[5,begin:end].tolist()
     for rr in range(6,len(d)):
      if num(pd.Series([d.iloc[rr,begin]])).isna().iloc[0]:continue
      vals={f'c{i+1}':d.iloc[rr,i] for i in range(begin,end) if d.iloc[rr,i].strip()}
      if len(vals)<2:continue
      calibration.append({'investigation_id':'PSI-25','source_table_id':tid,'source_row':rr+1,
       'block':bi+1,'block_start_column':begin+1,'date_header_json':json.dumps(d.iloc[2,begin:end].tolist()),
       'gmt_header_json':json.dumps(d.iloc[3,begin:end].tolist()),'headers_json':json.dumps(hs),
       'values_json':json.dumps(vals)})
   continue
  # Remaining SAFFIRE sources are general telemetry; source clocks and processing stay separate.
  if cat.sheet=='CSV' and 'telemetry' not in cat.file_name.lower() and 'Data_Table' not in cat.file_name:continue
  if cat.sheet=='CygnusSmokeDetectorData':
   for a,b in [(0,4),(5,9)]:
    hs=d.iloc[1].tolist();chosen=[(i,channel_name(hs[i]),unit(hs[i])) for i in range(a+3,min(b,len(hs))) if hs[i].strip()]
    add_series(cat,d,2,a,'cygnus_timestamp_raw','telemetry',chosen)
   continue
  if cat.sheet=='CygnusPressureData':
   # Plot-only dummy igniter values to the right are deliberately excluded.
   chosen=[(i,channel_name(h),unit(h)) for i,h in enumerate(headers[:7]) if i>=3 and h.strip()]
   add_series(cat,d,1,0,'cygnus_timestamp_raw','telemetry',chosen);continue
  if cat.sheet=='CygnusTemperatureData':
   add_series(cat,d,1,0,'cygnus_timestamp_raw','telemetry',[(3,channel_name(headers[3]),unit(headers[3]))]);continue
  if cat.sheet in ('RawData','CygnusData','SaffireData','CSV'):
   is_csv=cat.sheet=='CSV'
   for i,h in enumerate(headers):
    h=str(h).strip()
    if not h or re.search(r'timestamp|relative|delta|repeat|tach/100',h,re.I):continue
    # CSV labels and workbook labels differ; keep explicit names, don't merge uncertain aliases.
    cyg=bool(re.search(r'PCM|FIZ|body.rate|acceleration',h,re.I))
    if cat.sheet=='CygnusData':cyg=True
    ti=next((j for j,x in enumerate(headers) if x==('CygnusTimestamp' if cyg else 'SaffireTimestamp')),None)
    if ti is None:continue
    cname=channel_name(h)
    columns.append({'source_table_id':tid,'source_column':i+1,'source_header':h,'channel':cname,'unit':unit(h),'domain':'telemetry'})
    add_series(cat,d,1,ti,'cygnus_timestamp_raw' if cyg else 'saffire_timestamp_raw','telemetry',[(i,cname,unit(h))])
  else:excluded.append({'file_name':cat.file_name,'sheet':cat.sheet,'reason':'no_supported_physical_record_structure'})

 con.execute("UPDATE staging SET unit='' WHERE unit IS NULL")
 # A value version is exact and dimension/context-specific; no rounding or averaging.
 con.execute('''CREATE OR REPLACE TABLE measurement_versions AS
 SELECT sha256(to_json(struct_pack(i:=investigation_id,d:=domain,c:=clock,t:=time_key,s:=source_test_id,h:=channel,u:=unit,v:=value))) AS measurement_id,
 investigation_id,domain,clock,time_key,source_test_id,channel,unit,value,count(*) AS source_occurrences
 FROM staging GROUP BY ALL''')
 con.execute('''CREATE OR REPLACE TABLE measurement_lineage AS SELECT
 sha256(to_json(struct_pack(i:=investigation_id,d:=domain,c:=clock,t:=time_key,s:=source_test_id,h:=channel,u:=unit,v:=value))) AS measurement_id,
 origin_id,source_table_id,source_row,source_column FROM staging''')
 con.execute('''CREATE OR REPLACE TABLE observations AS SELECT *,
 sha256(to_json(struct_pack(i:=investigation_id,d:=domain,c:=clock,t:=time_key,s:=source_test_id))) AS event_id,
 count(*) OVER(PARTITION BY investigation_id,domain,clock,time_key,source_test_id,channel,unit)>1 AS has_conflicting_values,
 starts_with(time_key,'unknown:') AS missing_clock FROM measurement_versions''')
 con.execute('''CREATE OR REPLACE TABLE events AS SELECT event_id,investigation_id,domain,clock,time_key,source_test_id,
 count(*) AS measurement_versions,count(DISTINCT channel) AS channels,
 bool_or(has_conflicting_values) AS has_conflicting_values,bool_or(missing_clock) AS missing_clock
 FROM observations GROUP BY ALL''')
 for name,records in [('source_tables',tables),('channel_dictionary',columns),('matrix_records',matrix_rows),('calibration_records',calibration)]:
  frame=pd.DataFrame(records);con.register('_table',frame)
  con.execute(f'CREATE OR REPLACE TABLE {name} AS SELECT * FROM _table');con.unregister('_table')
  frame.to_csv(OUT/f'{name}.csv',index=False,encoding='utf-8-sig')
 con.execute('CREATE OR REPLACE TABLE experiments AS SELECT * FROM read_parquet(?)',[str(ROOT/'data/processed/experiments.parquet')])
 con.execute('CREATE OR REPLACE TABLE experiment_observations AS SELECT * FROM read_parquet(?)',[str(ROOT/'data/processed/observations.parquet')])
 con.execute('CREATE OR REPLACE TABLE calibrated_timeseries AS SELECT * FROM read_parquet(?)',[str(ROOT/'data/expanded_processed/dataset_sensores_unificado.parquet')])
 # Flat event-level representation; conflicting observations remain null here and accessible in observations.
 con.execute('''CREATE OR REPLACE TABLE event_channel_values AS SELECT event_id,
 domain||'__'||channel||CASE WHEN unit='' THEN '__unit_unspecified' ELSE '__'||regexp_replace(unit,'[^a-zA-Z0-9]','_','g') END AS variable,
 CASE WHEN bool_or(has_conflicting_values) THEN NULL ELSE min(value) END AS value
 FROM observations GROUP BY ALL''')
 con.execute('CREATE OR REPLACE TABLE event_values_wide AS PIVOT event_channel_values ON variable USING first(value) GROUP BY event_id')
 con.execute('CREATE OR REPLACE VIEW dataset_integrado AS SELECT * FROM events LEFT JOIN event_values_wide USING(event_id)')
 for name in ['events','observations','matrix_records','calibration_records','measurement_lineage']:
  con.execute(f'COPY {name} TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/f'{name}.parquet')])
 con.execute('COPY dataset_integrado TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/'dataset_integrado.parquet')])
 con.execute('COPY dataset_integrado TO ? (HEADER,COMPRESSION GZIP)',[str(OUT/'dataset_integrado.csv.gz')])
 con.execute('SELECT investigation_id,domain,count(*) AS events FROM events GROUP BY ALL ORDER BY ALL').fetchdf().to_csv(OUT/'counts.csv',index=False)
 report={name:con.execute(f'SELECT count(*) FROM {name}').fetchone()[0] for name in ['staging','events','observations','measurement_lineage','matrix_records','calibration_records']}
 report['exact_repeated_values_collapsed']=report['staging']-report['observations']
 report['conflicting_value_versions']=con.execute('SELECT count(*) FROM observations WHERE has_conflicting_values').fetchone()[0]
 report['unknown_clock_events']=con.execute('SELECT count(*) FROM events WHERE missing_clock').fetchone()[0]
 report['all_lineage_retained']=report['staging']==report['measurement_lineage']
 assert con.execute('SELECT count(*) FROM measurement_lineage l LEFT JOIN observations o USING(measurement_id) WHERE o.measurement_id IS NULL').fetchone()[0]==0
 assert con.execute('SELECT count(*) FROM dataset_integrado').fetchone()[0]==report['events']
 con.execute('DROP TABLE staging');con.execute('CHECKPOINT');con.close()
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 (OUT/'excluded_tables.json').write_text(json.dumps(excluded,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
