"""Retrieve public sensor/telemetry tables, excluding all audiovisual files."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from datetime import datetime, timezone
import json, hashlib, time

ROOT=Path(__file__).resolve().parents[1]
SELECTION={
 'PSI-98':['PSI-98_Raw Data_Saffire-I Telemetry Data Good Process Version.xlsx',
           'PSI-98_Raw Data_Saffire-I Sample 1 Sensor Data Complete TM graphs.xlsx',
           'PSI-98_Raw Data_Saffire-I Sample 2 Sensor Data Complete TM graphs.xlsx'],
 'PSI-100':['PSI-100_Raw Data_Saffire_Data_Table2017.161.00.42.03-EU.csv',
            'PSI-100_Raw Data_Raw telemetry file.csv',
            'PSI-100_Raw Data_Saffire-III 1 Hz Telemetry Data.xlsx']}

def main():
 dest=ROOT/'data/telemetry_raw';dest.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for acc,names in SELECTION.items():
  meta=json.loads((ROOT/f'data/raw/{acc}_metadata.json').read_text(encoding='utf-8'))
  inventory={f['file_name']:f for f in meta['added'] if 'file_name' in f}
  for i,name in enumerate(names):
   f=inventory[name]
   if f.get('restricted'):raise ValueError('Restricted file')
   path=dest/f'{acc}_{i+1:02d}{Path(name).suffix}'
   start=time.monotonic()
   print('START',name,int(f['file_size']),'bytes',flush=True)
   endpoint=f'https://psi.nasa.gov/geode-py/ws/studies/{acc}/download?'+urlencode({'file':name,'version':f['version'],'redirect':'false'})
   if not path.exists():
    with urlopen(endpoint,timeout=45) as r: signed=r.read().decode().strip().strip('"')
    if not signed.startswith('https://'):raise ValueError('Invalid download URL')
    tmp=path.with_suffix(path.suffix+'.part')
    with urlopen(signed,timeout=60) as response,tmp.open('wb') as out:
     while chunk:=response.read(1024*1024):out.write(chunk)
    tmp.rename(path)
   content=path.read_bytes()
   if len(content)!=int(f['file_size']):raise ValueError('Byte count mismatch '+name)
   manifest.append({'investigation_id':acc,'file_name':name,'file_version':f['version'],
       'repository_version':meta['version'],'doi':meta['doi'],'source_url':f'https://psi.nasa.gov/physci/repo/data/investigations/{acc}',
       'download_endpoint':endpoint,'local_file':str(path.relative_to(ROOT)),'bytes':len(content),
       'sha256':hashlib.sha256(content).hexdigest(),'retrieved_at':datetime.now(timezone.utc).isoformat()})
   (dest/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
   print('DONE',len(content),'bytes',round(time.monotonic()-start,1),'seconds',flush=True)

if __name__=='__main__':main()
