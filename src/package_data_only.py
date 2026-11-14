"""Package only data and provenance. No PDFs, documents, source books or photo metadata."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/integrated'
OUT=ROOT/'outputs'

def write(name,paths):
 dest=OUT/name
 with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=2) as z:
  for p in sorted(set(paths)):
   assert p.suffix.lower() in ('.parquet','.csv','.json','.gz')
   z.write(p,p.relative_to(ROOT))
 print(name,dest.stat().st_size,'bytes',flush=True)
 with ZipFile(dest) as z:
  assert z.testzip() is None
  assert not any(n.lower().endswith(('.pdf','.docx','.pptx','.xlsx','.txt')) for n in z.namelist())
 digest=hashlib.sha256()
 with dest.open('rb') as stream:
  while block:=stream.read(8*1024*1024):digest.update(block)
 return {'file':str(dest.relative_to(ROOT)),'bytes':dest.stat().st_size,'sha256':digest.hexdigest()}

def main():
 small=list(DATA.glob('*.csv'))+list(DATA.glob('*.json'))
 main=[DATA/n for n in ['dataset_integrado.parquet','dataset_analisis.parquet',
  'sensores_calibrados_completos.parquet','matrix_fields.parquet','matrix_records.parquet',
  'calibration_records.parquet','eventos_sin_reloj.parquet']]
 work=write('NASA_DATOS_INTEGRADOS_v0.3.zip',small+main)
 detail=write('NASA_DATOS_DETALLADOS_v0.3.zip',small+list(DATA.glob('*.parquet')))
 (OUT/'packages_v0.3.json').write_text(json.dumps([work,detail],indent=2),encoding='utf-8')

if __name__=='__main__':main()
