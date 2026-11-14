"""Add the non-temporal experiments and calibration to the data-only master export."""
from pathlib import Path
import json
import pandas as pd
import duckdb
from src.build_dataset import parse_value
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/integrated'

def main():
 c=duckdb.connect(str(OUT/'nasa_integrado.duckdb'))
 c.execute("SET memory_limit='1GB'");c.execute('SET threads=2')
 c.execute('''CREATE OR REPLACE TABLE matrix_canonical AS SELECT
 sha256(to_json(struct_pack(i:=investigation_id,r:=record_type,v:=values_json))) AS record_id,
 investigation_id,record_type,source_test_id,values_json,count(*) AS source_occurrences
 FROM matrix_records GROUP BY ALL''')
 cells=[]
 for r in c.execute('SELECT * FROM matrix_canonical').fetchdf().itertuples():
  for field,raw in json.loads(r.values_json).items():
   cells.append({'record_id':r.record_id,'field':field,'raw_value':raw,**parse_value(raw)})
 df=pd.DataFrame(cells);c.register('_fields',df)
 c.execute('CREATE OR REPLACE TABLE matrix_fields AS SELECT * FROM _fields');c.unregister('_fields')
 df.to_parquet(OUT/'matrix_fields.parquet',index=False)
 c.execute('''CREATE OR REPLACE VIEW dataset_temporal AS SELECT * FROM events LEFT JOIN event_values_wide USING(event_id)''')
 c.execute('''CREATE OR REPLACE VIEW dataset_integrado AS
 SELECT event_id AS record_id,'temporal_event' AS record_type,* EXCLUDE(event_id) FROM dataset_temporal
 UNION ALL BY NAME
 SELECT record_id,record_type,investigation_id,source_test_id,values_json AS conditions_json,
 source_occurrences FROM matrix_canonical
 UNION ALL BY NAME
 SELECT sha256(source_table_id||':'||source_row||':'||block) AS record_id,'calibration_point' AS record_type,
 investigation_id,values_json AS calibration_values_json,headers_json AS calibration_headers_json,
 date_header_json AS calibration_date_header_json,gmt_header_json AS calibration_gmt_header_json
 FROM calibration_records''')
 c.execute('COPY dataset_integrado TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/'dataset_integrado.parquet')])
 c.execute('COPY dataset_integrado TO ? (HEADER,COMPRESSION GZIP)',[str(OUT/'dataset_integrado.csv.gz')])
 c.execute('COPY calibrated_timeseries TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/'sensores_calibrados_completos.parquet')])
 counts=c.execute('SELECT investigation_id,record_type,count(*) AS records FROM dataset_integrado GROUP BY ALL ORDER BY ALL').fetchdf()
 counts.to_csv(OUT/'counts_by_record_type.csv',index=False)
 report=json.loads((OUT/'report.json').read_text())
 report['master_rows']=c.execute('SELECT count(*) FROM dataset_integrado').fetchone()[0]
 report['master_columns']=len(c.execute('DESCRIBE dataset_integrado').fetchall())
 report['matrix_canonical']=c.execute('SELECT count(*) FROM matrix_canonical').fetchone()[0]
 report['counts_by_record_type']=counts.to_dict(orient='records')
 c.execute("CREATE OR REPLACE VIEW dataset_analisis AS SELECT * FROM dataset_integrado WHERE record_type<>'temporal_event' OR NOT missing_clock")
 c.execute('COPY dataset_analisis TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/'dataset_analisis.parquet')])
 c.execute('COPY dataset_analisis TO ? (HEADER,COMPRESSION GZIP)',[str(OUT/'dataset_analisis.csv.gz')])
 c.execute('COPY (SELECT * FROM events WHERE missing_clock) TO ? (FORMAT PARQUET,COMPRESSION ZSTD)',[str(OUT/'eventos_sin_reloj.parquet')])
 report['analysis_rows']=c.execute('SELECT count(*) FROM dataset_analisis').fetchone()[0]
 report['events_with_value_conflicts']=c.execute('SELECT count(*) FROM events WHERE has_conflicting_values').fetchone()[0]
 # All recovered temporal source values remain represented through one or more lineage records.
 assert c.execute('SELECT sum(source_occurrences) FROM measurement_versions').fetchone()[0]==report['measurement_lineage']
 assert c.execute('SELECT count(*) FROM dataset_integrado').fetchone()[0]==c.execute('SELECT count(DISTINCT record_id) FROM dataset_integrado').fetchone()[0]
 assert c.execute('SELECT count(*) FROM calibrated_timeseries').fetchone()[0]==225300
 assert c.execute('SELECT count(*) FROM observations o LEFT JOIN events e USING(event_id) WHERE e.event_id IS NULL').fetchone()[0]==0
 # Conflicts are never silently averaged in the flat export.
 assert c.execute('SELECT count(*) FROM event_channel_values WHERE value IS NOT NULL AND (event_id,variable) IN (SELECT event_id,domain||\'__\'||channel||CASE WHEN unit=\'\' THEN \'__unit_unspecified\' ELSE \'__\'||regexp_replace(unit,\'[^a-zA-Z0-9]\',\'_\',\'g\') END FROM observations WHERE has_conflicting_values)').fetchone()[0]==0
 report['checks']={'lineage_reconciled':True,'master_unique_record_ids':True,'all_calibrated_rows_retained':True,
                    'no_orphan_observations':True,'conflicts_not_averaged':True}
 (OUT/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 (OUT/'excluded_tables.json').write_text((OUT/'excluded_tables.json').read_text(),encoding='utf-8')
 c.execute('CHECKPOINT');c.close()
 print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
