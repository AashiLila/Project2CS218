"""Run with: python -m streamlit run app.py"""
from pathlib import Path
import os
import streamlit as st
from recommender import CRITERIA, LIMITATIONS, load_data, rank_cities, build_evidence, local_explanation

st.set_page_config(page_title='City fit advisor', page_icon='🏙️', layout='centered')

def setting(name, default=''):
    value = os.environ.get(name)
    if value is not None:
        return value
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default

@st.cache_data
def data():
    return load_data(Path(__file__).parent / 'data' / 'cities.csv')

st.title('Find a city that fits your priorities')
st.write('Explore the sample data, compare cities, and request an evidence-based explanation.')
st.caption('Course prototype • fictional employee profiles • descriptive data, not relocation advice')
try:
    df = data()
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()
with st.expander('Understand this sample dataset', expanded=False):
    st.write(LIMITATIONS)
    st.write('Demonstration assumptions: higher Income and Composite education scores are preferred. '
             'Bachelors+ is zero by default to avoid double-weighting education. '
             'Sleep has zero weight until its definition and preferred direction are verified. '
             'These are editable preferences, not claims about what makes a city better.')
    st.dataframe(df, hide_index=True)

with st.form('preferences'):
    profile = st.text_area('Fictional employee context (optional)', max_chars=1200,
                          placeholder='Example: I want to compare the available measures before deciding what else to research.')
    st.caption('This text helps explain the results; only the weights and state filter determine the ranking. '
               'Do not enter personal or sensitive information.')
    states = st.multiselect('States to consider (leave empty for all)', sorted(df.State.unique()))
    weights, directions = {}, {}
    for col, label in CRITERIA.items():
        left, right = st.columns([2,1])
        weights[col] = left.slider(f'Priority: {label}', 0, 10, 5 if col in ('Income', 'Composite') else 0, key=f'w_{col}')
        directions[col] = right.selectbox(f'Prefer {label}', ['higher','lower'], key=f'd_{col}')
    number = st.slider('Number of cities to show', 1, 5, 3)
    submitted = st.form_submit_button('Compare cities', type='primary')

if submitted:
    # Drop old explanations immediately so a revised profile cannot show a stale answer.
    st.session_state.pop('result', None)
    st.session_state.pop('explanation', None)
    try:
        ranked, excluded = rank_cities(df, weights, directions, states or None)
        if ranked.empty:
            st.warning('No cities have complete data for these preferences. Try other states or criteria.')
        else:
            top = ranked.head(number)
            st.session_state.result = {
                'top': top, 'excluded': excluded,
                'evidence': build_evidence(top, weights, directions, states or None, profile),
            }
    except ValueError as exc:
        st.warning(str(exc))

if 'result' in st.session_state:
    result = st.session_state.result
    top = result['top']
    st.subheader('Your comparison')
    st.caption(f"{result['excluded']} cities excluded for missing actively weighted values. "
               'Fit is relative to the full sample. Exact ties use alphabetical order.')
    st.dataframe(top[['City','State','County','Fit score',*CRITERIA]], hide_index=True)
    chart = top.assign(City=top.City + ', ' + top.State).set_index('City')[['Fit score']]
    st.bar_chart(chart)
    with st.expander('View evidence used and scoring contributions'):
        st.json(result['evidence'])
        st.write('Each contribution = normalized value × share of active weights × 100. '
                 'Sum the contributions to reproduce the fit score. A constant column contributes a neutral value.')
    st.download_button('Download comparison CSV', top.to_csv(index=False), 'city-comparison.csv', 'text/csv')
    enabled = str(setting('ENABLE_AI', 'false')).lower() == 'true'
    key, model = setting('OPENAI_API_KEY'), setting('OPENAI_MODEL')
    live = enabled and bool(key) and bool(model)
    st.caption('AI explanations are enabled.' if live else 'Local mode: no API key needed and no API requests made.')
    if live:
        expected = str(setting('DEMO_ACCESS_CODE'))
        entered = st.text_input('Course demo access code', type='password') if expected else ''
        if not expected:
            st.warning('For a public demo, the instructor should configure DEMO_ACCESS_CODE before enabling paid calls.')
        allowed = bool(expected) and entered == expected
    else:
        allowed = True
    if st.button('Explain these results' if live else 'Show local summary', disabled=not allowed):
        st.session_state.pop('explanation', None)
        if live:
            # Session cap is a classroom convenience, not a global spending limit.
            calls = st.session_state.get('api_calls', 0)
            if calls >= 5:
                st.warning('This session has reached its five-request demo limit.')
            else:
                st.session_state.api_calls = calls + 1
                try:
                    from ai import explain
                    with st.spinner('Writing an explanation from the supplied evidence…'):
                        st.session_state.explanation = explain(result['evidence'], key, model)
                except Exception:
                    st.error('The AI request did not complete. Ask the instructor to check the model, '
                             'API billing, and connection; or disable AI to use local mode.')
        else:
            st.session_state.explanation = local_explanation(top)
    if 'explanation' in st.session_state:
        st.subheader('Explanation')
        st.markdown(st.session_state.explanation)
else:
    st.info('Choose your priorities and select Compare cities to begin. No API key is required.')
