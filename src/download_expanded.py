"""Download all classified non-audiovisual data/documents from current inventories."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
import json,hashlib,time,re
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data/expanded_raw'

def main():
 DEST.mkdir(parents=True,exist_ok=True)
 inventory=json.loads((ROOT/'data/inventory/files.json').read_text(encoding='utf-8'))
 existing={}
 for manifest in [ROOT/'data/raw/manifest.json',ROOT/'data/telemetry_raw/manifest.json',DEST/'manifest.json']:
  if manifest.exists():
   for x in json.loads(manifest.read_text(encoding='utf-8')):
    if x.get('local_file') and (ROOT/x['local_file']).exists(): existing[x['file_name']]=x
 chosen=[];excluded=[]
 for f in inventory:
  if f['classification'] not in ('numeric_or_metadata','documentation','numeric_archive_candidate'):
   excluded.append({**f,'reason':'audiovisual_or_unclassified_archive'});continue
  if re.search(r'proofsheet|imageframesizes|image.directory.nomenclature',f['file_name'],re.I):
   excluded.append({**f,'reason':'visual_contact_sheet_or_image_index_document'});continue
  if f['restricted']:
   excluded.append({**f,'reason':'restricted'});continue
  chosen.append(f)
 (DEST/'excluded_inventory.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf-8')
 print('SELECTED',len(chosen),'files',sum(f['bytes'] for f in chosen),'bytes',flush=True)
 def download(f):
  name=f['file_name'];acc=f['investigation_id'];path=DEST/f"{acc}_{f['file_id']}{Path(name).suffix.lower()}"
  if name in existing:
   old=existing[name];return {**f,**{k:old[k] for k in ['local_file','sha256','retrieved_at']},'download_status':'reused'}
  endpoint=f'https://psi.nasa.gov/geode-py/ws/studies/{acc}/download?'+urlencode({'file':f['file_id'],'version':f['file_version'],'redirect':'false'})
  for attempt in range(2):
   try:
    if not path.exists():
     with urlopen(endpoint,timeout=45) as r:signed=r.read().decode().strip().strip('"')
     if not signed.startswith('https://'):raise ValueError('Invalid download response')
     part=path.with_suffix(path.suffix+'.part')
     with urlopen(signed,timeout=60) as r,part.open('wb') as out:
      while chunk:=r.read(1024*1024):out.write(chunk)
     if part.stat().st_size!=f['bytes']:raise ValueError('Size mismatch')
     part.replace(path)
    return {**f,'local_file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'retrieved_at':datetime.now(timezone.utc).isoformat(),'download_status':'downloaded','download_endpoint':endpoint}
   except Exception as e:
    if attempt==1:return {**f,'download_status':'error','error':str(e)}
 results=[]
 with ThreadPoolExecutor(max_workers=4) as ex:
  tasks={ex.submit(download,f):f for f in chosen}
  for task in as_completed(tasks):
   result=task.result();results.append(result)
   (DEST/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
   print(len(results),'/',len(chosen),result['download_status'],result['file_name'],flush=True)
 print('FINISHED',len(results),'errors',sum(r['download_status']=='error' for r in results),flush=True)

if __name__=='__main__':main()
