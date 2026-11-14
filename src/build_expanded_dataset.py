"""Extract all nonvisual tables; consolidate calibrated sensor rows without resampling."""
from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib,io,csv
import pandas as pd
import duckdb
from lxml import etree
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/expanded_processed'

def slug(s):
 s=str(s).strip().lower().replace('₂','2').replace('+','_plus_')
 s=re.sub(r'-(?=\d)', '_minus_', s)
 s=re.sub(r'[^a-z0-9]+','_',s).strip('_')
 return s or 'unnamed'

def text(x):
 if x is None or (not isinstance(x,str) and pd.isna(x)):return ''
 return str(x)

def prepare_sensor_frame(df,f,sheet):
 """The inspected Calibrated Data sheet uses row 1 labels and row 2 units."""
 headers=[text(x) for x in df.iloc[0]];units=[text(x) for x in df.iloc[1]]
 names=[];seen={};dictionary=[]
 for i,h in enumerate(headers):
  base=slug(h);seen[base]=seen.get(base,0)+1
  name=base if seen[base]==1 else f'{base}_{seen[base]}'
  names.append(name)
  dictionary.append({'investigation_id':f['investigation_id'],'file_name':f['file_name'],
   'sheet':sheet,'source_column_number':i+1,'source_header':h,'source_unit':units[i],
   'normalized_column':name,'definition_status':'source_label_preserved'})
 d=df.iloc[2:].copy();d.columns=names
 d.insert(0,'source_row',range(3,len(d)+3))
 # A primary data row must contain a numeric elapsed time; extra note rows remain in source extracts.
 elapsed=pd.to_numeric(d['elapsed_time_s'],errors='coerce')
 d=d.loc[elapsed.notna()].copy();d['elapsed_time_s']=elapsed.loc[d.index].astype('float64')
 for c in names:
  if c=='timestamp_ms':d[c]=d[c].map(text).astype('string');continue
  d[c]=pd.to_numeric(d[c],errors='coerce')
 # Unlabelled spreadsheet columns are preserved in source extracts, not asserted to be sensors.
 d=d.drop(columns=[c for c,h in zip(names,headers) if not h])
 n=int(re.search(r'Sample (\d+)',f['file_name'],re.I).group(1))
 acc=f['investigation_id'];test=f'2-{n}' if acc=='PSI-99' else f'S{n}'
 d.insert(0,'source_test_id',test);d.insert(0,'investigation_id',acc)
 d.insert(0,'source_file_id',f['file_id'])
 d.insert(0,'source_file_name',f['file_name'])
 d.insert(0,'source_sheet',sheet)
 d.insert(0,'record_id',[f"{acc}:{f['file_id']}:{sheet}:r{r}" for r in d.source_row])
 d['source_doi']=f['doi']
 d['quality_status']='source_calibrated_not_independently_validated'
 d['unit_policy']='source_units_preserved_see_sensor_dictionary'
 return d,dictionary

def main():
 for p in [OUT,OUT/'tables',OUT/'sensor_parts',OUT/'documents']:p.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'data/expanded_raw/manifest.json').read_text(encoding='utf-8'))
 catalog=[];errors=[];dictionary=[];sensor_parts=[];archive_inventory=[]
 for f in manifest:
  if f['download_status']=='error':continue
  path=ROOT/f['local_file'];ext=path.suffix.lower();name=f['file_name'];fid=f['file_id']
  print('EXTRACT',name,flush=True)
  try:
   if ext in ('.xlsx','.xls'):
    with pd.ExcelFile(path,engine='calamine') as book:
     for si,sheet in enumerate(book.sheet_names):
      # Camera parameter sheets are audiovisual metadata, not physical sensor observations.
      if 'camera' in sheet.lower():
       catalog.append({'file_name':name,'sheet':sheet,'status':'excluded_camera_metadata','rows':0});continue
      dest=OUT/'tables'/f'{fid}_{si:02d}.parquet'
      df=book.parse(sheet,header=None,dtype=object,keep_default_na=False)
      # A rectangular source extract uses positional columns so duplicate/empty headers survive.
      df.columns=[f'c{i+1:03d}' for i in range(len(df.columns))]
      raw=df.map(text)
      raw.to_parquet(dest,index=False,compression='zstd')
      category='image_index' if re.search('mergeresult',name,re.I) else ('calibrated_sensors' if sheet=='Calibrated Data' else 'source_table')
      catalog.append({'investigation_id':f['investigation_id'],'file_name':name,'file_id':fid,'sheet':sheet,
                      'rows':len(df),'columns':len(df.columns),'category':category,'status':'extracted',
                      'local_table':str(dest.relative_to(ROOT))})
      if sheet=='Calibrated Data' and re.search(r'Sample \d+',name,re.I):
       d,defs=prepare_sensor_frame(df,f,sheet)
       target=OUT/'sensor_parts'/f'{fid}.parquet';d.to_parquet(target,index=False,compression='zstd')
       dictionary.extend(defs);sensor_parts.append(str(target))
   elif ext=='.csv':
    # CSV reader honors quoted fields; no line.split(',').
    with path.open(encoding='utf-8-sig',newline='') as h:rows=list(csv.reader(h))
    maxcols=max(map(len,rows)) if rows else 0
    d=pd.DataFrame([r+['']*(maxcols-len(r)) for r in rows],columns=[f'c{i+1:03d}' for i in range(maxcols)])
    dest=OUT/'tables'/f'{fid}.parquet';d.to_parquet(dest,index=False,compression='zstd')
    catalog.append({'investigation_id':f['investigation_id'],'file_name':name,'file_id':fid,'sheet':'CSV',
       'rows':len(rows),'columns':maxcols,'category':'csv_source','status':'extracted','local_table':str(dest.relative_to(ROOT))})
   elif ext=='.zip':
    with ZipFile(path) as z:
     for member in z.infolist():
      if member.is_dir():continue
      entry={'file_id':fid,'file_name':name,'member':member.filename,'bytes':member.file_size}
      if member.filename.lower().endswith(('.txt','.csv','.dat','.json','.xml')):
       content=z.read(member)
       encoding='utf-8'
       try:s=content.decode(encoding)
       except UnicodeDecodeError:encoding='cp1252';s=content.decode(encoding,errors='replace')
       target=OUT/'documents'/f'{fid}_{hashlib.sha256(member.filename.encode()).hexdigest()[:12]}.txt'
       target.write_text(s,encoding='utf-8')
       entry.update({'status':'text_extracted','encoding':encoding,'local_text':str(target.relative_to(ROOT)),
          'kind':'camera_metadata_candidate' if re.search('exif|shutter|exposure|aperture',s[:5000],re.I) else 'unclassified_text'})
      else:entry['status']='not_extracted_nontext_member'
      archive_inventory.append(entry)
   elif ext in ('.docx','.pptx'):
    with ZipFile(path) as z:
     pieces=[]
     for member in z.namelist():
      if member=='word/document.xml' or re.fullmatch(r'ppt/slides/slide\d+\.xml',member):
       root=etree.fromstring(z.read(member));pieces.append('\n'.join(root.xpath('//*[local-name()="t"]/text()')))
     (OUT/'documents'/f'{fid}.txt').write_text('\n'.join(pieces),encoding='utf-8')
   elif ext=='.pdf':
    reader=PdfReader(path)
    s='\n'.join(f'\n=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
    (OUT/'documents'/f'{fid}.txt').write_text(s,encoding='utf-8')
  except Exception as e:
   errors.append({'file_name':name,'error':str(e)});print('EXTRACT ERROR',name,str(e),flush=True)
 if sensor_parts:
  con=duckdb.connect(str(OUT/'nasa_expanded.duckdb'))
  con.execute('CREATE OR REPLACE TABLE sensor_timeseries AS SELECT * FROM read_parquet(?,union_by_name=true)',[sensor_parts])
  con.execute("COPY sensor_timeseries TO ? (FORMAT PARQUET,COMPRESSION ZSTD)",[str(OUT/'dataset_sensores_unificado.parquet')])
  con.execute("COPY sensor_timeseries TO ? (HEADER,COMPRESSION GZIP)",[str(OUT/'dataset_sensores_unificado.csv.gz')])
  counts=con.execute('SELECT investigation_id,source_test_id,count(*) AS records FROM sensor_timeseries GROUP BY ALL ORDER BY ALL').fetchdf()
  counts.to_csv(OUT/'counts_by_test.csv',index=False)
  total=con.execute('SELECT count(*) FROM sensor_timeseries').fetchone()[0]
  distinct=con.execute('SELECT count(DISTINCT record_id) FROM sensor_timeseries').fetchone()[0]
  assert total==distinct
  # Joinable experiment metadata remains a separate dimension; all samples are retained.
  con.execute('CREATE OR REPLACE TABLE experiments AS SELECT * FROM read_parquet(?)',[str(ROOT/'data/processed/experiments.parquet')])
  con.execute('CREATE OR REPLACE VIEW sensors_with_experiment AS SELECT s.*, e.experiment_id, e.material_original, e.flow_direction FROM sensor_timeseries s LEFT JOIN experiments e USING(investigation_id,source_test_id)')
  con.close()
 else:total=0
 pd.DataFrame(catalog).to_csv(OUT/'table_catalog.csv',index=False)
 pd.DataFrame(dictionary).to_csv(OUT/'sensor_dictionary.csv',index=False)
 (OUT/'archive_inventory.json').write_text(json.dumps(archive_inventory,indent=2,ensure_ascii=False),encoding='utf-8')
 report={'sensor_time_records':total,'sensor_files':len(sensor_parts),'source_tables':len(catalog),
         'source_rows_all_tables_including_overlapping_views':sum(x.get('rows',0) for x in catalog),
         'extract_errors':errors,'archive_text_files':len(archive_inventory),
         'no_resampling':True,'no_imputation':True,'audiovisual_downloaded':False}
 (OUT/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
