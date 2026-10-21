# Sample data and provenance

The original supplied workbook is preserved in `data/`. The app reads `cities.csv`,
a seven-column extraction of its `SleepIncomeBachelors` sheet. It contains 500 distinct
City/State combinations. No new join or imputation was performed.

| Field | Handling |
| --- | --- |
| City, State, County | Geographic labels retained exactly as supplied |
| Sleep | Numeric, but definition/units/year unverified; default weight zero |
| Income | Numeric reported aggregate; 11 missing values; not employee salary or affordability |
| Bachelors+ | Numeric reported education measure; 9 missing values; not a school-quality rating |
| Composite | Composite education score, as clarified by the instructor; included with an editable weight |
| Unnamed: 3 | Omitted: apparent join identifier, not a recommendation criterion |

The workbook also includes an Education by County sheet and a Sources sheet.
The Sources sheet references https://github.com/evangambit/JsonOfCounties/blob/master/counties.json
and describes an original counties.json file with 3,143 county rows and 732 features.
That pointer does not establish the meaning, year, geography, or units of every
merged variable. Students must locate and document variable-specific metadata.

The income and education columns appear to carry county information into city rows;
validate the original merge and geographic interpretation before making claims.
Cities may span counties. Shared county values should not be interpreted as
independently measured city statistics. The app makes no claims about individual
employee education, income, sleep, health, or future outcomes.

No currency or percent symbol is added to the app's raw values without verification.
No housing, schools, commuting, safety, climate, taxes or company office availability
is modeled. The default preference for higher income/composite education is a teaching choice
that students should critique. Publish data only after checking redistribution rights.

Composite ranges from approximately 24.975 to 25.025. Global min-max scaling
stretches this narrow variation across the full 0–1 scale. It is included as requested,
but students should investigate the original formula and discuss how this scaling
can magnify tiny differences. Higher Composite is the editable default preference.
Bachelors+ defaults to zero to avoid counting overlapping education measures twice.
