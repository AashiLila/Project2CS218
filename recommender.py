"""Pure pandas ranking logic: edit this module for your course project."""
import json
import numpy as np
import pandas as pd

CRITERIA = {
    'Income': 'Income (reported value)',
    'Bachelors+': "Bachelor’s+ (reported value)",
    'Composite': 'Composite education score',
    'Sleep': 'Sleep (definition unverified)',
}
LIMITATIONS = (
    'Source: supplied CitySleepCountyIncomeEducation.xlsx, SleepIncomeBachelors sheet. '
    'Years, units, and the precise Sleep definition are not documented in the workbook. '
    'County-derived values attached to cities are not individual employee outcomes. '
    'Income is not a salary offer or a cost-of-living measure; Bachelors+ is not school quality. '
    'No housing, commute, safety, climate, or office availability data is included. '
    'Composite is the supplied composite education score. Its narrow sample range (about 24.975–25.025) '
    'is expanded by min-max scaling; small raw differences should not imply substantial educational advantages. '
    'Unnamed join columns are not used. Scores are relative fit indices, not probabilities.'
)

def load_data(path):
    df = pd.read_csv(path)
    required = ['City', 'State', 'County', *CRITERIA]
    if not set(required).issubset(df):
        raise ValueError('CSV must include: ' + ', '.join(required))
    df = df[required].copy()
    for col in CRITERIA:
        df[col] = pd.to_numeric(df[col], errors='coerce').replace([np.inf, -np.inf], np.nan)
    if df[['City','State','County']].isna().any().any() or df.duplicated(['City','State']).any():
        raise ValueError('City, State and County must be present, with unique City/State rows.')
    return df


def rank_cities(df, weights, directions, states=None):
    """Global min-max scaling; exclude only rows missing an actively weighted value.

    A constant criterion contributes a neutral 0.5. State filtering does not
    change the normalization baseline. A tied score uses City/State ordering.
    """
    if set(weights) != set(CRITERIA) or set(directions) != set(CRITERIA):
        raise ValueError('Supply all criteria in weights and directions.')
    if any(not np.isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError('Weights must be finite and nonnegative.')
    active = [c for c, w in weights.items() if w > 0]
    if not active:
        raise ValueError('Choose at least one positive weight.')
    if any(directions[c] not in ('higher', 'lower') for c in CRITERIA):
        raise ValueError('Directions must be higher or lower.')
    candidates = df if states is None else df[df.State.isin(states)]
    valid = candidates.dropna(subset=active).copy()
    excluded = len(candidates) - len(valid)
    valid['Fit score'] = 0.0
    for col in active:
        low, high = df[col].min(), df[col].max()
        if pd.isna(low) or pd.isna(high):
            # Every candidate was already excluded for this missing active criterion.
            scaled = pd.Series(0.5, index=valid.index)
        elif high == low:
            scaled = pd.Series(0.5, index=valid.index)
        else:
            scaled = (valid[col] - low) / (high - low)
        if directions[col] == 'lower':
            scaled = 1 - scaled
        valid[f'{col} contribution'] = scaled * (weights[col] / sum(weights.values())) * 100
        valid['Fit score'] += valid[f'{col} contribution']
    return valid.sort_values(['Fit score','City','State'], ascending=[False,True,True]).reset_index(drop=True), excluded


def build_evidence(top, weights, directions, states, profile):
    """Exactly what the AI sees. No full workbook or hidden employee records."""
    return {
        'employee_context': profile[:1200],
        'weights': weights, 'preferred_direction': directions,
        'state_filter': states, 'limitations': LIMITATIONS,
        'method': 'Weighted global min-max fit index, 0–100. Higher fit is better. '
                  'Rows missing an active criterion are excluded. Ties are alphabetical.',
        'recommended_cities': json.loads(top.to_json(orient='records', double_precision=6)),
    }


def local_explanation(top):
    """Clearly labeled no-API fallback; not simulated AI output."""
    first = top.iloc[0]
    return (f"**Local summary — no AI request made.**\n\n"
            f"{first['City']}, {first['State']} leads this selection with a relative fit "
            f"score of {first['Fit score']:.1f}/100. Compare the raw values and weighted "
            'contributions in the evidence panel. A high score reflects the chosen '
            'preferences, not overall city quality. This dataset cannot establish '
            'affordability, job offers, school quality, or individual health outcomes.')
