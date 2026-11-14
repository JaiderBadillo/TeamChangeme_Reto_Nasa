import unittest,json
import duckdb
from src.build_dataset import ROOT

class IntegratedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=duckdb.connect(str(ROOT/'data/integrated/nasa_integrado.duckdb'),read_only=True)
 @classmethod
 def tearDownClass(cls):cls.c.close()
 def test_master_has_all_five_investigations(self):
  ids={r[0] for r in self.c.execute('SELECT DISTINCT investigation_id FROM dataset_integrado').fetchall()}
  self.assertEqual(ids,{'PSI-98','PSI-99','PSI-100','PSI-25','PSI-26'})
 def test_all_temporal_source_values_accounted_for(self):
  n=self.c.execute('SELECT sum(source_occurrences) FROM measurement_versions').fetchone()[0]
  self.assertEqual(n,self.c.execute('SELECT count(*) FROM measurement_lineage').fetchone()[0])
  self.assertEqual(n,13390304)
 def test_master_identity_and_granularity(self):
  n,unique=self.c.execute('SELECT count(*),count(DISTINCT record_id) FROM dataset_integrado').fetchone()
  self.assertEqual(n,unique)
  self.assertEqual(n,420421)
  self.assertEqual(self.c.execute('SELECT count(*) FROM calibrated_timeseries').fetchone()[0],225300)
 def test_missing_clock_not_in_default_analysis(self):
  self.assertEqual(self.c.execute("SELECT count(*) FROM dataset_analisis WHERE record_type='temporal_event' AND missing_clock").fetchone()[0],0)
 def test_planned_rows_separate_from_reported(self):
  self.assertEqual(self.c.execute("SELECT count(*) FROM matrix_canonical WHERE record_type='planned_conditions'").fetchone()[0],53)
 def test_matrix_excludes_nondata_prefaces(self):
  rows=self.c.execute("SELECT min(source_row) FROM matrix_records WHERE record_type='planned_conditions'").fetchone()[0]
  self.assertGreaterEqual(rows,7)
 def test_pure_data_inventory(self):
  names=[r[0] for r in self.c.execute('SELECT source_file_name FROM source_tables').fetchall()]
  self.assertTrue(all(n.lower().endswith(('.csv','.xlsx','.xls')) for n in names))
  self.assertFalse(any('mergeresult' in n.lower() for n in names))

if __name__=='__main__':unittest.main()
