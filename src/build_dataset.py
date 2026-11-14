"""Conservative, traceable ETL for five NASA PSI experimental tables.

Offline: reads original CSVs; never rewrites raw data or imputes observations.
"""
from pathlib import Path
from datetime import datetime
from collections import Counter
import csv, io, json, re, hashlib, math, importlib.metadata
import pandas as pd
import pandera.pandas as pa
from pydantic import BaseModel, ConfigDict, model_validator
from pint import UnitRegistry
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
UREG = UnitRegistry()
NAMES = {'PSI-98':'SAFFIRE-I','PSI-99':'SAFFIRE-II','PSI-100':'SAFFIRE-III',
         'PSI-26':'BASS','PSI-25':'BASS-II'}
NUM = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
UNITS = {'mm':'millimeter','cm':'centimeter','micron':'micrometer','microns':'micrometer',
         'in':'inch','cm/s':'centimeter/second','mm/s':'millimeter/second',
         's':'second','W':'watt','ppm':'ppm','%':'percent'}

def clean(s): return re.sub(r'\s+', ' ', str(s)).strip()

class ParsedValue(BaseModel):
    model_config = ConfigDict(strict=True)
    status: str
    value: float | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None
    unit: str | None = None
    qualifier: str | None = None

    @model_validator(mode='after')
    def consistent(self):
        if self.status == 'interval':
            assert self.value is None and self.lower_bound is not None and self.upper_bound is not None
            assert self.lower_bound <= self.upper_bound
        if self.status in ('missing','not_applicable','overrange','qualitative','ambiguous'):
            assert self.value is None
        for x in (self.value,self.lower_bound,self.upper_bound):
            assert x is None or math.isfinite(x)
        return self

def parse_value(raw, default_unit=None):
    """Only parse a full recognized expression; preserve everything else as text."""
    s = clean(raw)
    out = {'status':'qualitative','unit':default_unit}
    if not s or s.lower() in ('none','na','nan','--','---','----'):
        return ParsedValue(status='missing',unit=default_unit).model_dump()
    if re.fullmatch(r'n/?a(?:\s*\(.*\))?', s, re.I):
        return ParsedValue(status='not_applicable',unit=default_unit).model_dump()
    if s.lower() in ('or','+or','over'):
        return ParsedValue(status='overrange',unit=default_unit).model_dump()
    if re.search(r'(?<![\d.])0\d{2,}(?![\d.])',s):
        return ParsedValue(status='ambiguous',unit=default_unit).model_dump()
    suffix = r'(?:\s*(cm/s|mm/s|mm|cm|microns?|s|W|ppm|%))?'
    m=re.fullmatch(rf'([<>]=?)\s*({NUM})'+suffix,s)
    if m:
        op,n,u=m.groups(); out={'status':'bound','qualifier':op,'unit':u or default_unit}
        out['lower_bound' if op.startswith('>') else 'upper_bound']=float(n)
    else:
        m=re.fullmatch(rf'(~|≈)?\s*({NUM})\s*(to|[-–])\s*({NUM})'+suffix,s)
        if m:
            approx,a,sep,b,u=m.groups()
            out={'status':'interval','lower_bound':min(float(a),float(b)),
                 'upper_bound':max(float(a),float(b)),'unit':u or default_unit,
                 'qualifier':'ordered_change' if sep=='to' else ('approximate' if approx else 'range')}
        else:
            m=re.fullmatch(rf'(~|≈)?\s*({NUM})'+suffix,s)
            if m:
                approx,n,u=m.groups()
                out={'status':'approximate' if approx else 'numeric','value':float(n),
                     'unit':u or default_unit,'qualifier':'approximate' if approx else None}
    return ParsedValue(**out).model_dump()

def convert(parsed, target):
    result=parsed.copy()
    source=result['unit']
    if source==target: return result
    if not source or not target: return result
    for k in ('value','lower_bound','upper_bound'):
        if result[k] is not None:
            result[k]=float(UREG.Quantity(result[k],UNITS.get(source,source)).to(UNITS.get(target,target)).magnitude)
    result['unit']=target
    return result

# Source-name mappings are explicit; numerical-looking identifiers stay textual.
MAPPING = {
 'Sample Number':('source_test_id',None), 'Test #':('source_test_id',None),
 'Sample #':('source_sample_id',None), 'As Run Test #':('as_run_test_id',None),
 'Material':('material_description',None),'Fuel Sample Material':('material_description',None),
 'Date':('test_date_raw',None),'GMT':('gmt_raw',None),'PI':('principal_investigator',None),
 'Sample Thickness (cm)':('thickness','cm'),'Samle Thickness':('thickness',None),
 'Sample Thickness':('thickness',None),'Sample Length (cm)':('length','cm'),
 'Sample Length':('length',None),'Sample Width (cm)':('width','cm'),'Sample Width':('width',None),
 'Air Flow (cm/s)':('air_velocity','cm/s'),'Air Flow':('air_velocity',None),
 'Percent O2':('oxygen_ambient','%'),'Percent O2 (Note 1)':('oxygen_ambient','%'),
 'Ignition Power (W)':('ignition_power','W'),'Ignition Time (s)':('igniter_on_time','s'),
 'Burn Time (s)':('burn_duration','s'),'Flow Direction':('flow_direction',None),
 'Direction':('flow_direction',None),'Camera 1':('camera_1',None),'Camera 2':('camera_2',None),
 '?-g Burn Length':('reduced_g_burn_length_unverified',None),
 '?-g Spread Length':('reduced_g_spread_unverified',None),
 '1-g Burn Length':('normal_g_burn_length',None),'1-g Spread Rate':('normal_g_spread_rate',None),
 'Flow restrictor':('flow_restrictor_code',None),'Fan display':('fan_display_raw',None),
 'Air display':('air_display_raw',None),'Radiometer gain (1000 250 50 10)':('radiometer_gain_raw',None),
 'Total Frames Shot':('frames_raw',None),
 'Calibrated initial O2 % by vol':('oxygen_initial','%'),
 'Calibrated final O2 % by vol':('oxygen_final','%'),
 'Initial CO2 % by vol':('carbon_dioxide_initial','%'),'Final CO2 % by vol':('carbon_dioxide_final','%'),
 'Initial CO (ppm)':('carbon_monoxide_initial','ppm'),'Final CO (ppm)':('carbon_monoxide_final','ppm')}
NUMERIC_FIELDS={'thickness','length','width','air_velocity','oxygen_ambient','ignition_power',
 'igniter_on_time','burn_duration','reduced_g_burn_length_unverified','reduced_g_spread_unverified',
 'normal_g_burn_length','normal_g_spread_rate','oxygen_initial','oxygen_final',
 'carbon_dioxide_initial','carbon_dioxide_final','carbon_monoxide_initial','carbon_monoxide_final'}
TARGET={'thickness':'mm','length':'mm','width':'mm','air_velocity':'cm/s',
 'normal_g_burn_length':'mm','normal_g_spread_rate':'mm/s'}

def material_name(s):
    t=s.casefold()
    if 'pmma' in t and 'nomex' in t: return 'PMMA + Nomex'
    if 'sibal' in t: return 'SIBAL'
    if 'pmma' in t: return 'PMMA'
    if 'silicone' in t: return 'Silicone'
    if 'nomex' in t: return 'Nomex'  # grade kept separately in description, never merged experimentally
    if 'ultem' in t: return 'Ultem'
    if 'japan' in t and 'wax' in t: return 'Japan wax'
    if 'paraffin' in t or 'parrafin' in t: return 'Paraffin wax'
    return None

def classify(row, accession):
    vals=[clean(v) for v in row.values()]
    if not any(vals): return 'empty'
    if vals[0].startswith('Note '): return 'note'
    if any('Pre-test flow' in v for v in vals): return 'auxiliary'
    if any('SOOT Cleaning' in v for v in vals): return 'maintenance'
    return 'experiment'

def export_table(name, records, folder):
    df=pd.DataFrame(records)
    for col in ('value','lower_bound','upper_bound'):
        if col in df: df[col]=pd.to_numeric(df[col]).astype('Float64')
    df.to_csv(folder/f'{name}.csv',index=False,encoding='utf-8-sig')
    df.to_parquet(folder/f'{name}.parquet',index=False)
    (folder/f'{name}.json').write_text(df.to_json(orient='records',force_ascii=False,indent=2),encoding='utf-8')
    return df

def main():
    out=DATA/'processed'; quality=DATA/'quality'; staging=DATA/'staging'
    for d in (out,quality,staging): d.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((DATA/'raw/manifest.json').read_text(encoding='utf-8'))
    experiments=[]; observations=[]; other_rows=[]; issues=[]; source_records=[]; resources=[]; sources=[]; protocols=[]
    coverage=[]
    def issue(eid,field,code,message,severity='warning'):
        issues.append({'issue_id':f'Q{len(issues)+1:05d}','experiment_id':eid,'field':field,
                       'code':code,'severity':severity,'message':message,'resolution':'pending_review'})
    for src in manifest:
        acc=src['investigation_id']; path=ROOT/src['local_file']
        b=path.read_bytes(); assert hashlib.sha256(b).hexdigest()==src['sha256']
        meta=json.loads((DATA/f'raw/{acc}_metadata.json').read_text(encoding='utf-8'))
        src['repository_version']=meta.get('version')
        sources.append({**src,'study_name':NAMES[acc],'repository_version':meta.get('version'),
                        'license':'CC0-1.0','extraction_method':'direct_original_csv'})
        matrix=list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline='')))
        original_headers=matrix[0]; headers=[clean(c) for c in original_headers]
        assert len(headers)==len(set(headers))
        unknown=set(headers)-set(MAPPING)
        if unknown: raise ValueError(f'Unmapped headers: {unknown}')
        counts=Counter()
        for rownum,values in enumerate(matrix[1:],start=2):
            assert len(values)==len(headers),(acc,rownum,len(values),len(headers))
            raw=dict(zip(headers,values)); kind=classify(raw,acc);counts[kind]+=1
            rid=f'{acc}:row:{rownum:04d}'
            source_records.append({'source_record_id':rid,'investigation_id':acc,'csv_record_number':rownum,
                'row_type':kind,'original_headers_json':json.dumps(original_headers,ensure_ascii=False),
                'original_values_json':json.dumps(values,ensure_ascii=False)})
            if kind!='experiment':
                other_rows.append({'source_record_id':rid,'investigation_id':acc,'row_type':kind,
                    'content':json.dumps(raw,ensure_ascii=False)})
                continue
            r={MAPPING[k][0]:clean(v) for k,v in raw.items()}
            tid=r.get('source_test_id',''); eid=f'{acc}:{tid}:r{rownum}'
            e={'experiment_id':eid,'investigation_id':acc,'study_name':NAMES[acc],
               'source_record_id':rid,'source_test_id':tid,'source_sample_id':r.get('source_sample_id') or None,
               'as_run_test_id':r.get('as_run_test_id') or None,'material_original':r.get('material_description',''),
               'material_normalized':material_name(r.get('material_description','')),
               'flow_direction':r.get('flow_direction') or None,'test_date':None,
               'test_date_raw':r.get('test_date_raw') or None,'gmt_raw':r.get('gmt_raw') or None,
               'source_url':src['landing_url'],'source_doi':src.get('doi'),
               'repository_version':meta.get('version'),'contains_stage_sequence':False,
               'material_grade_text':r.get('material_description','') if 'nomex' in r.get('material_description','').lower() else None}
            if not tid: issue(eid,'source_test_id','missing_identifier','No published test identifier')
            if not e['material_normalized']:
                issue(eid,'material_normalized','material_unresolved','Material missing or not explicit; no forward fill')
            if r.get('test_date_raw'):
                try:
                    date=datetime.strptime(r['test_date_raw'],'%m/%d/%Y')
                    if date.year>2026: raise ValueError('Future year')
                    e['test_date']=date.date().isoformat()
                    if r.get('gmt_raw','').isdigit() and date.timetuple().tm_yday!=int(r['gmt_raw']):
                        issue(eid,'test_date','date_day_mismatch','Published GMT/day code disagrees with calendar day; definition requires review')
                    if acc=='PSI-25' and date.year==2018:
                        issue(eid,'test_date','date_campaign_review','2018 date requires campaign verification')
                except ValueError: issue(eid,'test_date','invalid_date','Original date retained; normalized date null')
            for k,v in raw.items():
                field,unit=MAPPING[k]; numeric=field in NUMERIC_FIELDS
                parsed=parse_value(v,unit) if numeric else ParsedValue(status='text').model_dump()
                flags=[]
                if numeric:
                    if parsed['status']=='ambiguous': flags.append('ambiguous_numeric_text')
                    if 'unverified' in field: flags.append('header_semantics_unverified')
                    if acc in ('PSI-98','PSI-100') and field=='thickness': flags.append('source_thickness_review')
                    if acc=='PSI-98' and field in ('length','width'): flags.append('dimension_orientation_conflict')
                    if acc=='PSI-99' and r.get('source_test_id')=='2-7' and field in ('thickness','length'):
                        flags.append('multiple_components')
                    try: parsed=convert(parsed,TARGET.get(field,parsed['unit']))
                    except Exception: flags.append('unit_incompatible')
                    if parsed['status'] in ('numeric','approximate','interval','bound') and parsed['unit'] is None:
                        flags.append('unit_not_explicit')
                    if field in ('oxygen_initial','oxygen_final') and parsed['value'] is not None and not 10<=parsed['value']<=25:
                        flags.append('oxygen_outside_documented_campaign_range')
                    if field in ('carbon_monoxide_initial','carbon_monoxide_final') and parsed['value'] is not None and parsed['value']<0:
                        flags.append('negative_sensor_reading')
                    if acc=='PSI-99' and field.startswith('oxygen_'): method='derived_from_CO2_see_note_1'
                    elif field.startswith('oxygen_') and acc=='PSI-25': method='calibrated_endpoint_reading'
                    else: method='reported_in_source_table'
                else: method='source_metadata'
                usable=numeric and not flags and parsed['status'] in ('numeric','approximate','interval','bound')
                obs={'observation_id':f'{eid}:c{headers.index(k)+1:02d}','experiment_id':eid,
                     'source_record_id':rid,'source_column':original_headers[headers.index(k)],'field':field,
                     'raw_value':v,**parsed,'method':method,'usable_for_analysis':usable,
                     'quality_flags':json.dumps(flags),'source_url':src['landing_url']}
                observations.append(obs)
                for flag in flags: issue(eid,field,flag,'See raw_value and source_column in observations')
                if field in ('fan_display_raw','air_display_raw','radiometer_gain_raw'):
                    if len(re.findall(NUM,clean(v)))>1 or re.search(r'ext|blow|decr|incr|down|up',v,re.I):
                        e['contains_stage_sequence']=True
                if field in ('camera_1','camera_2') and clean(v).lower() not in ('','n/a','none'):
                    resources.append({'experiment_id':eid,'resource_type':'camera_reference','source_column':k,
                                      'resource_identifier':v,'downloaded':False})
                if numeric:
                    suffix={'mm':'mm','cm/s':'cm_s','mm/s':'mm_s','%':'pct','ppm':'ppm','s':'s','W':'w'}.get(parsed['unit'],'unknown_unit')
                    e[f'{field}_{suffix}']=parsed['value'] if usable and parsed['status'] in ('numeric','approximate') else None
                    e[f'{field}_status']=parsed['status']
                    e[f'{field}_qualifier']=parsed['qualifier']
            if acc=='PSI-25':
                protocols.append({'experiment_id':eid,'fan_display_raw':r.get('fan_display_raw',''),
                    'air_display_raw':r.get('air_display_raw',''),'radiometer_gain_raw':r.get('radiometer_gain_raw',''),
                    'flow_restrictor_code':r.get('flow_restrictor_code',''),
                    'has_multiple_stages_or_changes':e['contains_stage_sequence'],
                    'stage_times_available':False,'alignment_status':'not_reconstructed',
                    'source_record_id':rid})
            experiments.append(e)
        coverage.append({'investigation_id':acc,'study_name':NAMES[acc],'source_rows':len(matrix)-1,
                         'source_columns':len(headers),**counts})
    # Explicitly link table notes to all relevant experiments, without inventing missing row values.
    note_links=[]
    for n in other_rows:
        if n['row_type']!='note': continue
        for e in experiments:
            if e['investigation_id']==n['investigation_id']:
                note_links.append({'experiment_id':e['experiment_id'],'note_source_record_id':n['source_record_id'],
                                   'scope':'table_context_verify_specific_reference'})
    for e in experiments:
        e['quality_issue_count']=sum(q['experiment_id']==e['experiment_id'] for q in issues)
    ef=pd.DataFrame(experiments)
    schema=pa.DataFrameSchema({'experiment_id':pa.Column(str,unique=True),
        'investigation_id':pa.Column(str,pa.Check.isin(list(NAMES))),
        'source_record_id':pa.Column(str,unique=True),'source_test_id':pa.Column(str)},strict=False)
    schema.validate(ef,lazy=True)
    tables={
       'experiments':export_table('experiments',experiments,out),
       'observations':export_table('observations',observations,out),
       'source_records':export_table('source_records',source_records,out),
       'non_experimental_rows':export_table('non_experimental_rows',other_rows,out),
       'resources':export_table('resources',resources,out),
       'note_links':export_table('note_links',note_links,out),
       'condition_protocols':export_table('condition_protocols',protocols,out),
       'quality_issues':export_table('quality_issues',issues,quality)}
    # A versioned source manifest contains no expiring signed URLs or credentials.
    (out/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
    db=duckdb.connect(str(out/'nasa_unified.duckdb'))
    for name,df in tables.items():
        db.register('_input',df); db.execute(f'CREATE OR REPLACE TABLE {name} AS SELECT * FROM _input');db.unregister('_input')
    assert db.execute('SELECT count(*) FROM observations o LEFT JOIN experiments e USING(experiment_id) WHERE e.experiment_id IS NULL').fetchone()[0]==0
    assert len(source_records)==len(experiments)+len(other_rows)
    expected_cells=sum(c['source_columns']*c['experiment'] for c in coverage)
    assert len(observations)==expected_cells
    db.execute('CREATE OR REPLACE VIEW observations_analysis AS SELECT * FROM observations WHERE usable_for_analysis')
    db.close()
    # Flattened export for the web: one row per source experimental record.
    ef.to_csv(out/'dataset_unificado.csv',index=False,encoding='utf-8-sig')
    versions={p:importlib.metadata.version(p) for p in ('pandas','pandera','pint','pydantic','duckdb','pyarrow','hypothesis')}
    report={'schema_version':'0.1.0','coverage':coverage,'experiment_records':len(experiments),
        'all_source_rows':len(source_records),'non_experimental_rows':len(other_rows),
        'observations_including_metadata_and_missing':len(observations),
        'usable_numeric_observations':sum(o['usable_for_analysis'] for o in observations),
        'quality_issues':len(issues),'issue_counts':dict(Counter(i['code'] for i in issues)),
        'checks':{'source_row_reconciliation':True,'source_cell_reconciliation':True,'unique_ids':True,'foreign_keys':True,'raw_hashes':True},
        'libraries':versions}
    (quality/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    # Schema dictionary is generated from actually exported columns, not a hypothetical schema.
    dictionary=[{'table':name,'column':str(c),'dtype':str(df[c].dtype),
                 'non_null_count':int(df[c].notna().sum()),'row_count':len(df)} for name,df in tables.items() for c in df.columns]
    pd.DataFrame(dictionary).to_csv(out/'data_dictionary.csv',index=False,encoding='utf-8-sig')
    (ROOT/'requirements.txt').write_text('\n'.join(f'{p}=={v}' for p,v in versions.items())+'\n',encoding='utf-8')
    (staging/'column_mappings.json').write_text(json.dumps(MAPPING,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
