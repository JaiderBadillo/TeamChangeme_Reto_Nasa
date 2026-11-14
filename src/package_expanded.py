from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'outputs'

def make_zip(name,files):
 p=OUTPUT/name
 files=sorted(set(files))
 with ZipFile(p,'w',ZIP_DEFLATED,compresslevel=3) as z:
  for f in files:z.write(f,f.relative_to(ROOT))
 print(name,len(files),'files',p.stat().st_size,'bytes',flush=True)
 with ZipFile(p) as z:
  assert z.testzip() is None
 return {'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files)}

def main():
 OUTPUT.mkdir(exist_ok=True)
 processed=ROOT/'data/expanded_processed'
 common=[ROOT/'DATASET_AMPLIADO_README.md',ROOT/'DATASET_README.md',ROOT/'requirements.txt']
 common+=list((ROOT/'src').glob('*.py'))+list((ROOT/'tests').glob('*.py'))
 common+=list(processed.glob('*.csv'))+list(processed.glob('*.json'))
 common+=[processed/'dataset_sensores_unificado.parquet',processed/'dataset_sensores_unificado.csv.gz',processed/'nasa_expanded.duckdb']
 for folder in ['data/processed','data/quality','data/staging','data/raw','data/inventory']:
  common += [p for p in (ROOT/folder).rglob('*') if p.is_file()]
 # Light version includes source provenance, original summary CSVs and the primary sensor dataset.
 light=make_zip('NASA_SAFFIRE_BASS_DATOS_v0.2.zip',common+[ROOT/'data/expanded_raw/manifest.json',ROOT/'data/expanded_raw/excluded_inventory.json'])
 manifest=json.loads((ROOT/'data/expanded_raw/manifest.json').read_text(encoding='utf-8'))
 originals=[ROOT/f['local_file'] for f in manifest if f['download_status']!='error']
 extra=[p for p in processed.rglob('*') if p.is_file()]
 extra += [ROOT/'data/expanded_raw/manifest.json',ROOT/'data/expanded_raw/excluded_inventory.json']
 full=make_zip('NASA_SAFFIRE_BASS_COMPLETO_v0.2.zip',common+originals+extra)
 (OUTPUT/'packages_v0.2.json').write_text(json.dumps([light,full],indent=2),encoding='utf-8')

if __name__=='__main__':main()
