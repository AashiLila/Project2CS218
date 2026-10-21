# CityRecommender_CS218

A city recommender template for the CS218 course assignment: pandas + Streamlit + OpenAI.

A classroom starter: choose preferences, rank cities in Python, inspect the evidence,
and explain the results. Runs without an API key. No separate web server or frontend.

**Default ranking uses Income and the supplied Composite education score.**
Bachelors+ and Sleep remain available with initial weights of zero.

## First run (optional; Cloud deployment needs no local installation)

Use Python 3.11 or 3.12. From this folder:

```bash
python -m venv .venv
```

Activate on Windows: `.venv\Scripts\activate`. On macOS/Linux: `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Choose preferences and click **Compare cities**, then **Show local summary**.
The local summary is deterministic text, clearly labeled; it is not an AI simulation.

## Publish and embed

Follow [SETUP.md](SETUP.md) for GitHub templates, Community Cloud, API configuration,
and Google Sites embedding. No command-line Git knowledge is needed.

## Where students work

| File | Responsibility |
| --- | --- |
| `app.py` | Form, charts, evidence panel, session state, explanation button |
| `recommender.py` | CSV loading, transparent scoring, evidence preparation |
| `ai.py` | Instructions and a single Responses API request |
| `data/cities.csv` | Seven selected columns from the workbook's merged sheet |
| `data/CitySleepCountyIncomeEducation.xlsx` | Original workbook for provenance |
| `docs/ASSIGNMENT.md` | Milestones, experiments, and evaluation |
| `docs/DATA_NOTES.md` | Meanings, missing data, assumptions, and limitations |
| `.streamlit/secrets.toml.example` | Placeholder configuration; never contains a key |

### Bring your pandas work into the app

Export your already-merged DataFrame with `df.to_csv('data/cities.csv', index=False)`.
Keep the seven required columns or update `CRITERIA`, `load_data`, the form defaults,
and the evidence instructions together. Put reusable analysis into functions in
`recommender.py`; do not execute a notebook inside each app request.
For this workbook, extraction used:

```python
import pandas as pd
merged = pd.read_excel('data/CitySleepCountyIncomeEducation.xlsx',
                       sheet_name='SleepIncomeBachelors')
merged[['City', 'State', 'County', 'Sleep', 'Income', 'Bachelors+', 'Composite']].to_csv(
    'data/cities.csv', index=False)
```

## Scoring contract

Default weights: Income 5, Composite 5, Bachelors+ 0, Sleep 0. Higher is preferred initially;
these are demonstration choices, not objective judgments. Sleep remains inactive
until its meaning is verified. Every direction and weight is editable.

For each active variable, use min-max scaling against all 500 cities. Reverse the
scaled value if lower is preferred. Weight by that criterion's share of all
positive weights and multiply by 100. Sum the contributions. Constant columns get
a neutral 0.5. State filtering does not change the baseline. Cities missing any
active variable are excluded and counted; inactive missing values do not exclude.
Exact ties are ordered alphabetically. Fit is not a confidence percentage.
The employee free-text context informs the explanation, not the ranking.

## AI behavior and classroom access

No request occurs on startup, form submission, chart interaction, or download.
Only the explanation button makes an API request, and only when explicitly enabled
with a key, model, and course access code. The request sends the top 1–5 city rows,
scoring metadata, limitations, and fictional employee context. It does not upload
the workbook. AI output can still make mistakes: students must verify claims.

The access code and five-request session cap discourage casual use; they are not
strong authentication or a global spending limit. Reloading/resetting a session can
reset that cap. Use an instructor-controlled API project, monitor usage, and disable
AI after demonstrations. A hidden key alone does not prevent paid use of a public app.
No credentials are cached globally. Responses use `store=False`; this does not imply
zero provider retention. Do not enter real employee or sensitive information.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests exercise ranking, missingness, ties, no matches, evidence serialization,
API request construction using a fake client, and UI flows with Streamlit AppTest.
They make no paid API calls. There is no live API credential bundled here.

## Reuse

Starter code may be copied and adapted for teaching. The original dataset is supplied
by the instructor; this project does not assert a license for that data. Review its
source terms before publishing or redistributing. Original sources, dates and variable
meanings need verification before substantive recommendations.
