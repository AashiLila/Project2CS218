# Validation

11 automated checks passed on the supplied sample dataset:

- Composite-only ranking and income-only ranking produce the expected opposite orders.
- Active versus inactive missing values are handled differently.
- Lower-is-better and state filtering preserve the full-sample baseline.
- Constant columns produce neutral contributions and deterministic ties.
- Empty selections, all-missing criteria and invalid weights are handled.
- Weighted contributions reproduce scores and evidence serializes missing values as null.
- CSV extraction matches the original workbook for all four numeric criteria.
- Mocked Responses API call contains the supplied evidence and configured model.
- Incomplete API output is rejected.
- Streamlit local-mode form, explanation reset and zero-weight validation work.
- Streamlit live-mode access-code gating and button behavior work with a mocked AI call.

Tested with Python 3.12, Streamlit 1.66.1, OpenAI Python 2.54.0,
pandas 2.2.3 and NumPy 2.3.5. Dependency bounds permit compatible updates.

No paid API request was made. Live model access/billing, actual GitHub publication,
Community Cloud deployment and the published Google Sites embed must be checked
in the instructor's accounts after connection and configuration.
