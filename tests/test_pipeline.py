import unittest, json, csv, io, math
from pathlib import Path
import pandas as pd
import duckdb
from hypothesis import given, strategies as st, settings
from src.build_dataset import parse_value, convert, ROOT

class ParsingTests(unittest.TestCase):
    def test_missing_and_zero_differ(self):
        self.assertEqual(parse_value('')['status'],'missing')
        self.assertEqual(parse_value('n/a')['status'],'not_applicable')
        self.assertEqual(parse_value('0')['value'],0.0)

    def test_bound_is_not_exact_measurement(self):
        x=parse_value('>500','ppm')
        self.assertIsNone(x['value'])
        self.assertEqual(x['lower_bound'],500.)
        self.assertEqual(x['qualifier'],'>')

    def test_uncertain_and_composite_text(self):
        self.assertEqual(parse_value('037 mm')['status'],'ambiguous')
        self.assertEqual(parse_value('0.85 and 0.37 mm')['status'],'qualitative')
        self.assertEqual(parse_value('Insignificant','s')['status'],'qualitative')
        self.assertEqual(parse_value('OR','ppm')['status'],'overrange')

    def test_ordered_oxygen_change(self):
        x=parse_value('22.1 to 22.0','%')
        self.assertEqual(x['qualifier'],'ordered_change')
        self.assertIsNone(x['value'])
        self.assertEqual((x['lower_bound'],x['upper_bound']),(22.,22.1))

    @settings(max_examples=100)
    @given(st.floats(min_value=0.001,max_value=1000,allow_nan=False,allow_infinity=False))
    def test_unit_conversion_preserves_magnitude(self,x):
        p=parse_value(f'{x:.8f} cm')
        mm=convert(p,'mm')
        self.assertAlmostEqual(mm['value'],float(f'{x:.8f}')*10,places=8)

    @settings(max_examples=100)
    @given(st.text(max_size=100))
    def test_arbitrary_input_is_preserved_as_a_status(self,s):
        p=parse_value(s)
        for k in ('value','lower_bound','upper_bound'):
            self.assertTrue(p[k] is None or math.isfinite(p[k]))

class DatasetTests(unittest.TestCase):
    def test_raw_cells_preserved(self):
        sources=pd.read_parquet(ROOT/'data/processed/source_records.parquet')
        for acc in sources.investigation_id.unique():
            original=list(csv.reader(io.StringIO((ROOT/f'data/raw/{acc}.csv').read_text(encoding='utf-8-sig'),newline='')))
            subset=sources[sources.investigation_id==acc]
            self.assertEqual(len(subset),len(original)-1)
            for r in subset.itertuples():
                self.assertEqual(json.loads(r.original_values_json),original[r.csv_record_number-1])
                self.assertEqual(json.loads(r.original_headers_json),original[0])

    def test_suspect_values_remain_but_are_not_analytical(self):
        obs=pd.read_parquet(ROOT/'data/processed/observations.parquet')
        for tid,value in [('B2',1.6),('P22b',39.1),('T28b',40.4)]:
            r=obs[(obs.experiment_id.str.contains(f'PSI-25:{tid}:')) & (obs.field=='oxygen_final')].iloc[0]
            self.assertEqual(r.value,value)
            self.assertFalse(r.usable_for_analysis)

    def test_database_relations_and_no_silent_row_loss(self):
        con=duckdb.connect(str(ROOT/'data/processed/nasa_unified.duckdb'),read_only=True)
        count=con.execute('SELECT count(*) FROM experiments').fetchone()[0]
        self.assertEqual(count,263)
        for table in ('observations','resources','note_links','condition_protocols','quality_issues'):
            missing=con.execute(f'SELECT count(*) FROM {table} x LEFT JOIN experiments e USING(experiment_id) WHERE e.experiment_id IS NULL').fetchone()[0]
            self.assertEqual(missing,0)
        self.assertEqual(con.execute('SELECT count(*) FROM source_records').fetchone()[0],272)
        con.close()

if __name__=='__main__': unittest.main()
