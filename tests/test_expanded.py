import unittest,json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import duckdb
from src.build_dataset import ROOT

class ExpandedTests(unittest.TestCase):
 def test_sensor_rows_reconcile_to_original_excel_xml(self):
  manifest=json.loads((ROOT/'data/expanded_raw/manifest.json').read_text(encoding='utf-8'))
  con=duckdb.connect(str(ROOT/'data/expanded_processed/nasa_expanded.duckdb'),read_only=True)
  files=con.execute('SELECT DISTINCT source_file_id,source_file_name FROM sensor_timeseries').fetchall()
  total=0
  for fid,name in files:
   source=next(f for f in manifest if f['file_id']==fid)
   count=0;first_o2=None
   with ZipFile(ROOT/source['local_file']) as z:
    wb=etree.fromstring(z.read('xl/workbook.xml'))
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheet=next(s for s in wb.find('s:sheets',ns) if s.get('name')=='Calibrated Data')
    rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    relationships=etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target=next(r.get('Target') for r in relationships if r.get('Id')==rid)
    xml_path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    with z.open(xml_path) as stream:
     for event,row in etree.iterparse(stream,events=('end',),tag='{*}row'):
      r=int(row.get('r'))
      if r>=3:
       cell=next((c for c in row if c.get('r')==f'A{r}'),None)
       if cell is not None and cell.get('t') not in ('s','str','inlineStr'):
        v=cell.find('s:v',ns)
        if v is not None:
         try:float(v.text)
         except (ValueError,TypeError):pass
         else:
          count+=1
          if first_o2 is None:
           o=next(c for c in row if c.get('r')==f'G{r}')
           first_o2=float(o.find('s:v',ns).text)
      row.clear()
   expected=con.execute('SELECT count(*) FROM sensor_timeseries WHERE source_file_id=?',[fid]).fetchone()[0]
   self.assertEqual(count,expected,name)
   exported=con.execute('SELECT o2 FROM sensor_timeseries WHERE source_file_id=? ORDER BY source_row LIMIT 1',[fid]).fetchone()[0]
   self.assertAlmostEqual(first_o2,exported,places=10)
   total+=count
  self.assertEqual(total,225300)
  con.close()

 def test_voltage_polarities_remain_distinct(self):
  con=duckdb.connect(str(ROOT/'data/expanded_processed/nasa_expanded.duckdb'),read_only=True)
  fields={r[0] for r in con.execute('DESCRIBE sensor_timeseries').fetchall()}
  self.assertIn('pc104_minus_12v',fields)
  self.assertIn('pc104_plus_12v',fields)
  con.close()

if __name__=='__main__':unittest.main()
