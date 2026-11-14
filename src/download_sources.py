"""Download only the public experimental CSVs, never raw audiovisual collections."""
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://psi.nasa.gov/geode-py/ws'
IDS = [98, 99, 100, 26, 25]

def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'NASA-hackathon-data-review/1.0'}), timeout=40) as r:
        return r.read()

def main():
    dest = ROOT / 'data' / 'raw'
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    for n in IDS:
        accession = f'PSI-{n}'
        meta_url = f'{BASE}/repo/investigations/{accession}'
        raw_meta = fetch(meta_url)
        (dest / f'{accession}_metadata.json').write_bytes(raw_meta)
        meta = json.loads(raw_meta)
        # The repository model explicitly lists the currently selected experimental table.
        candidates = []
        def walk(obj, trail=''):
            if isinstance(obj, dict):
                if str(obj.get('file_name', '')).lower().endswith('.csv') and 'experimental table' in str(obj.get('file_name', '')).lower():
                    candidates.append((trail, obj))
                for k, v in obj.items(): walk(v, trail+'/'+k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj): walk(v, trail+f'/{i}')
        walk(meta)
        # Prefer current experimentalTable to history (added/removed).
        candidates.sort(key=lambda x: (any(t in x[0].lower() for t in ['/removed', '/added', '/updated']), x[0]))
        current = [(t, o) for t, o in candidates if not any(w in t.lower() for w in ['/removed', '/added', '/updated'])]
        if not current:
            raise ValueError(f'{accession}: no current experimental CSV; keys={list(meta)} candidates={[t for t,o in candidates]}')
        trail, f = current[0]
        if f.get('restricted'): raise ValueError('Restricted source: '+accession)
        query = urlencode({'file': f['file_name'], 'version': f.get('version', 1), 'redirect': 'false'})
        endpoint = f'{BASE}/studies/{accession}/download?{query}'
        signed = fetch(endpoint).decode('utf-8').strip().strip('"')
        if not signed.startswith('https://'): raise ValueError('Unexpected download response')
        content = fetch(signed)
        if len(content)>2_000_000 or content.lstrip().startswith(b'<'): raise ValueError('Unexpected CSV content')
        path = dest / f'{accession}.csv'
        path.write_bytes(content)
        entry = {'investigation_id': accession, 'landing_url': f'https://psi.nasa.gov/physci/repo/data/investigations/{accession}',
                 'metadata_url': meta_url, 'file_name': f['file_name'], 'file_version': f.get('version'),
                 'repository_version': meta.get('version'), 'doi': meta.get('doi'),
                 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'local_file': str(path.relative_to(ROOT)),
                 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content), 'metadata_field': trail,
                 'download_endpoint': endpoint}
        manifest.append(entry)
        (dest / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        print(accession, len(content), 'bytes', trail, flush=True)

if __name__ == '__main__': main()
