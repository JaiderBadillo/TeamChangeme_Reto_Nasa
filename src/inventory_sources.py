from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json,re
ROOT=Path(__file__).resolve().parents[1]

def classify(name):
 ext=Path(name).suffix.lower()
 if ext in ('.csv','.xlsx','.xls','.txt','.dat','.mat','.h5','.hdf5','.json'):
  return 'numeric_or_metadata'
 if ext in ('.pdf','.docx','.doc','.pptx','.ppt'):return 'documentation'
 if ext=='.zip':
  if re.search(r'_txt\.zip$|sensor|telemetry|analog|radiomet|anemom',name,re.I):return 'numeric_archive_candidate'
  if re.search(r'metadata',name,re.I):return 'metadata_archive'
  return 'archive_unclassified'
 return 'audiovisual_or_other'

def fetch_inventory(n):
 acc=f'PSI-{n}'
 meta=json.loads((ROOT/f'data/raw/{acc}_metadata.json').read_text(encoding='utf-8'))
 req=Request('https://psi.nasa.gov/geode-py/ws/files/v2',data=json.dumps({'folder':'','fileType':'study','studyId':acc,'version':meta['version']}).encode(),headers={'Content-Type':'application/json'})
 with urlopen(req,timeout=60) as r:content=r.read()
 directory=ROOT/'data/inventory';directory.mkdir(parents=True,exist_ok=True)
 (directory/f'{acc}.json').write_bytes(content)
 found={}
 def walk(x):
  if isinstance(x,dict):
   if 'id' in x and not x.get('directory',True):
    name=x['key'].rsplit('/',1)[-1]
    found[x['id']]={'investigation_id':acc,'repository_version':meta['version'],'doi':meta['doi'],
       'file_name':name,'file_id':x['id'],'file_version':x['version'],'bytes':int(x.get('bytes_size',0)),
       'subcategory':x.get('subcategory'),'restricted':x.get('restricted',False),
       'classification':classify(name),'key':x['key']}
   for k,v in x.items():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(json.loads(content))
 print(acc,len(found),'files',flush=True)
 return list(found.values())

def main():
 with ThreadPoolExecutor(max_workers=3) as ex: groups=list(ex.map(fetch_inventory,[98,99,100,26,25]))
 files=[f for g in groups for f in g]
 (ROOT/'data/inventory/files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
 for acc in ['PSI-98','PSI-99','PSI-100','PSI-26','PSI-25']:
  chosen=[f for f in files if f['investigation_id']==acc and f['classification'] in ('numeric_or_metadata','documentation','numeric_archive_candidate')]
  print(acc,len(chosen),sum(f['bytes'] for f in chosen),'bytes selected')
  for f in chosen:print(f['bytes'],f['file_name'])

if __name__=='__main__':main()
