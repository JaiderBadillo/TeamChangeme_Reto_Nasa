"""Independent quality checks and per-channel metrics for the expanded dataset."""
from pathlib import Path
import json,hashlib,importlib.metadata
import duckdb,pandas as pd
import pandera.pandas as pa

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/expanded_processed'

def main():
 c=duckdb.connect(str(OUT/'nasa_expanded.duckdb'),read_only=True)
 n=c.execute('SELECT count(*) FROM sensor_timeseries').fetchone()[0]
 assert n==225300
 assert c.execute('SELECT count(DISTINCT record_id) FROM sensor_timeseries').fetchone()[0]==n
 assert c.execute('SELECT count(*) FROM sensors_with_experiment WHERE experiment_id IS NULL').fetchone()[0]==0
 assert c.execute('SELECT count(*) FROM sensors_with_experiment').fetchone()[0]==n
 assert c.execute('SELECT count(*) FROM sensor_timeseries WHERE elapsed_time_s IS NULL OR elapsed_time_s < 0').fetchone()[0]==0
 assert c.execute('SELECT count(*) FROM (SELECT source_file_id,elapsed_time_s,count(*) n FROM sensor_timeseries GROUP BY ALL HAVING n>1)').fetchone()[0]==0
 assert c.execute('SELECT count(*) FROM (SELECT source_file_id,epoch_time,count(*) n FROM sensor_timeseries GROUP BY ALL HAVING n>1)').fetchone()[0]==0
 steps=c.execute('''SELECT investigation_id,source_test_id,min(dt) AS min_dt,max(dt) AS max_dt,median(dt) AS median_dt
 FROM (SELECT *,elapsed_time_s-lag(elapsed_time_s) OVER(PARTITION BY source_file_id ORDER BY source_row) AS dt FROM sensor_timeseries)
 WHERE dt IS NOT NULL GROUP BY ALL ORDER BY ALL''').fetchdf()
 assert (steps.min_dt>0).all()
 steps.to_csv(OUT/'sampling_intervals.csv',index=False)
 fields=c.execute('DESCRIBE sensor_timeseries').fetchdf()
 metrics=[]
 for f in fields.itertuples():
  if f.column_type not in ('DOUBLE','BIGINT','FLOAT','INTEGER'):continue
  col='"'+f.column_name.replace('"','""')+'"'
  r=c.execute(f'SELECT count({col}), min({col}),max({col}),count(*) FILTER(WHERE {col}=0) FROM sensor_timeseries').fetchone()
  metrics.append({'column':f.column_name,'non_null':r[0],'null_count':n-r[0],'min':r[1],'max':r[2],'zero_count':r[3]})
 pd.DataFrame(metrics).to_csv(OUT/'channel_quality.csv',index=False)
 sample=c.execute('SELECT record_id,investigation_id,elapsed_time_s,source_row FROM sensor_timeseries').fetchdf()
 pa.DataFrameSchema({'record_id':pa.Column(str,unique=True),'investigation_id':pa.Column(str,pa.Check.isin(['PSI-98','PSI-99','PSI-100'])),
  'elapsed_time_s':pa.Column(float,pa.Check.ge(0)),'source_row':pa.Column(int,pa.Check.ge(3))},strict=True).validate(sample,lazy=True)
 manifest=json.loads((ROOT/'data/expanded_raw/manifest.json').read_text(encoding='utf-8'))
 verified=0
 for f in manifest:
  if f['download_status']=='error':continue
  p=ROOT/f['local_file']
  assert p.stat().st_size==f['bytes']
  assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
  verified+=1
 report={'sensor_time_records':n,'sensor_columns_including_provenance':len(fields),'unique_record_ids':True,
  'unique_times_per_source':True,'strictly_increasing_elapsed_times':True,'sample_metadata_join_complete':True,
  'source_files_verified':verified,'download_errors':[{'file_name':f['file_name'],'error':f['error']} for f in manifest if f['download_status']=='error'],
  'total_verified_source_bytes':sum(f['bytes'] for f in manifest if f['download_status']!='error'),
  'important_limitation':'Sensor calibration and physical interpretation are reported by source, not independently revalidated; source timeseries are correlated.',
  'libraries':{p:importlib.metadata.version(p) for p in ['pandas','pandera','pint','duckdb','pyarrow','python-calamine','openpyxl']}}
 (OUT/'validation_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 c.close();print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
