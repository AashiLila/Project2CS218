import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import pandas as pd
from recommender import CRITERIA, load_data, rank_cities, build_evidence

ROOT = Path(__file__).resolve().parents[1]

def prefs(**changes):
    weights = {c: 0 for c in CRITERIA}
    weights.update(changes)
    return weights, {c: 'higher' for c in CRITERIA}

class RankingTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'City':['A','B','C'], 'State':['AA','BB','BB'], 'County':['X','Y','Z'],
            'Income':[10.,20.,30.], 'Bachelors+':[10.,None,30.],
            'Sleep':[1.,1.,1.], 'Composite':[30.,20.,10.]})

    def test_composite_changes_ranking(self):
        w,d = prefs(Composite=1)
        ranked,_ = rank_cities(self.df,w,d)
        self.assertEqual(ranked.City.tolist(),['A','B','C'])
        self.assertEqual(ranked['Fit score'].tolist(),[100.,50.,0.])
        ranked,_ = rank_cities(self.df,*prefs(Income=1))
        self.assertEqual(ranked.City.tolist(),['C','B','A'])

    def test_missing_active_vs_inactive(self):
        self.assertEqual(len(rank_cities(self.df,*prefs(Income=1))[0]),3)
        ranked,n = rank_cities(self.df,*prefs(**{'Bachelors+':1}))
        self.assertEqual((len(ranked),n),(2,1))

    def test_direction_and_global_baseline(self):
        w,d = prefs(Income=1)
        d['Income']='lower'
        ranked,_ = rank_cities(self.df,w,d,states=['BB'])
        self.assertEqual(ranked.City.tolist(),['B','C'])
        self.assertEqual(ranked['Fit score'].tolist(),[50.,0.])

    def test_constant_and_tie(self):
        ranked,_ = rank_cities(self.df,*prefs(Sleep=1))
        self.assertEqual(ranked.City.tolist(),['A','B','C'])
        self.assertTrue((ranked['Fit score']==50).all())

    def test_empty_zero_negative_and_missing(self):
        w,d=prefs(Income=1)
        self.assertTrue(rank_cities(self.df,w,d,states=['ZZ'])[0].empty)
        with self.assertRaises(ValueError): rank_cities(self.df,*prefs())
        with self.assertRaises(ValueError): rank_cities(self.df,*prefs(Income=-1))
        missing=self.df.copy(); missing['Income']=None
        self.assertTrue(rank_cities(missing,w,d)[0].empty)

    def test_contributions_sum_and_json_null(self):
        w,d=prefs(Income=1,Composite=2)
        ranked,_=rank_cities(self.df,w,d)
        self.assertAlmostEqual(ranked.iloc[0]['Fit score'], 200/3)
        self.assertTrue((ranked['Fit score']-ranked[['Income contribution','Composite contribution']].sum(axis=1)).abs().lt(1e-8).all())
        payload=build_evidence(ranked,w,d,None,'Example')
        self.assertIn('null',json.dumps(payload,allow_nan=False))
        self.assertIn('Composite',json.dumps(payload))

    def test_sample_integrity(self):
        sample=load_data(ROOT/'data/cities.csv')
        original=pd.read_excel(ROOT/'data/CitySleepCountyIncomeEducation.xlsx')
        self.assertEqual(len(sample),500)
        self.assertEqual(sample.Income.isna().sum(),11)
        for col in CRITERIA:
            pd.testing.assert_series_equal(sample[col],original[col],check_exact=False)
        self.assertFalse(sample.duplicated(['City','State']).any())

class APITests(unittest.TestCase):
    @patch('ai.OpenAI')
    def test_request_uses_supplied_evidence(self, client):
        from ai import explain
        client.return_value.responses.create.return_value=SimpleNamespace(status='completed',output_text='Grounded explanation')
        self.assertEqual(explain({'Composite':25},'fake-test-key','configured-model'),'Grounded explanation')
        args=client.return_value.responses.create.call_args.kwargs
        self.assertEqual(args['model'],'configured-model')
        self.assertFalse(args['store'])
        self.assertEqual(json.loads(args['input']),{'Composite':25})
        self.assertEqual(args['max_output_tokens'],1200)

    @patch('ai.OpenAI')
    def test_incomplete_response_is_not_displayed(self, client):
        from ai import explain
        client.return_value.responses.create.return_value=SimpleNamespace(status='incomplete',output_text='Partial')
        with self.assertRaises(ValueError): explain({},'fake','model')

class UITests(unittest.TestCase):
    def test_local_flow_reset_and_validation(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict('os.environ', {'ENABLE_AI':'false'}):
            at=AppTest.from_file(str(ROOT/'app.py')).run(timeout=20)
            self.assertEqual(len(at.exception),0)
            self.assertEqual(at.slider(key='w_Composite').value,5)
            self.assertEqual(at.slider(key='w_Bachelors+').value,0)
            at.button[0].click().run()
            self.assertEqual(len(at.exception),0)
            self.assertIn('result',at.session_state)
            at.button[-1].click().run()
            self.assertIn('Local summary',at.session_state['explanation'])
            at.slider(key='w_Income').set_value(2)
            at.button[0].click().run()
            self.assertNotIn('explanation',at.session_state)
            for c in CRITERIA: at.slider(key=f'w_{c}').set_value(0)
            at.button[0].click().run()
            self.assertNotIn('result',at.session_state)
            self.assertTrue(any('positive weight' in w.value for w in at.warning))
            self.assertEqual(len(at.exception),0)

    def test_live_flow_mocked(self):
        from streamlit.testing.v1 import AppTest
        env={'ENABLE_AI':'true','OPENAI_API_KEY':'fake','OPENAI_MODEL':'test-model','DEMO_ACCESS_CODE':'class-demo'}
        with patch.dict('os.environ',env), patch('ai.explain',return_value='Mock explanation') as explain:
            at=AppTest.from_file(str(ROOT/'app.py')).run(timeout=20)
            at.button[0].click().run()
            self.assertTrue(at.button[-1].disabled)
            at.text_input[0].set_value('class-demo').run()
            self.assertFalse(at.button[-1].disabled)
            at.button[-1].click().run()
            self.assertEqual(at.session_state['explanation'],'Mock explanation')
            self.assertEqual(explain.call_count,1)
            self.assertEqual(len(at.exception),0)

if __name__ == '__main__':
    unittest.main()
