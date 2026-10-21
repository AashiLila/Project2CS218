# Instructor setup: template → Streamlit → Google Sites

The prepared course repository is https://github.com/Pelonza/CityRecommender_CS218.
Once its Template repository setting is enabled, students can use **Use this template**
and continue at step 2 below. For deploying the instructor copy, use repository
`Pelonza/CityRecommender_CS218`, branch `main`, entrypoint `app.py`.

## 1. Create your GitHub template once

1. Unzip the starter download.
2. In GitHub, create a new repository named `city-advisor-starter`. Choose your
   account or course organization. Public is simplest for classroom copying, provided
   you have permission to publish the supplied sample data.
3. Choose **Add file → Upload files**. Upload the **contents** of the extracted
   `city-advisor-starter` folder. `app.py`, `requirements.txt`, and `data/` must be
   at the repository root, not inside another `city-advisor-starter/` folder.
4. Commit the files. Hidden folders can be omitted by file pickers: ensure
   `.streamlit/secrets.toml.example`, `.streamlit/config.toml`, and `.gitignore`
   are included. If necessary use **Add file → Create new file** with each full path.
   The app runs without the optional theme files, but keep `.gitignore`.
5. In repository **Settings → General**, enable **Template repository**.
6. Share the repository link. Students choose **Use this template → Create a new
   repository** and create their own copy. The actual template switch is a GitHub
   setting; a ZIP alone cannot enable it.

Do not upload a real API key, `.env`, or `.streamlit/secrets.toml`.
You do not need GitHub Pages; it cannot run the Python app.

## 2. Deploy a student copy on Streamlit Community Cloud

1. Visit https://share.streamlit.io/ and sign in/connect GitHub as prompted.
2. Choose **Create app**, then the option for an existing app/repository.
3. Select your repository, its default branch (usually `main`), and **`app.py`**
   as the entrypoint. Use Python 3.11 or 3.12 in the advanced settings.
4. Deploy. Community Cloud installs `requirements.txt` and runs the app.
5. Open the resulting `https://your-app.streamlit.app` URL. Test a comparison and
   local summary. No OpenAI account or secrets are required for this stage.

Updates committed to the deployed branch are picked up by Community Cloud.
If dependencies change, check the build logs and reboot if needed.

## 3. Enable AI only when ready

The instructor needs an OpenAI API project with billing/credits and a text model
available to that project. A ChatGPT subscription is separate from API billing.
Do not distribute one unrestricted instructor key to student repositories.
An instructor can configure the Cloud app secrets; collaborators who can administer
that deployment must be treated as trusted credential holders.

In Community Cloud, open your app's **Settings → Secrets** (or Advanced settings
while deploying). Paste and edit:

```toml
ENABLE_AI = true
OPENAI_API_KEY = "PASTE_YOUR_REAL_API_KEY_HERE"
OPENAI_MODEL = "YOUR_AVAILABLE_TEXT_MODEL_ID"
DEMO_ACCESS_CODE = "choose-a-course-demo-code"
```

`YOUR_AVAILABLE_TEXT_MODEL_ID` is a placeholder: replace it with an exact model ID
from your API project. Model choice is deliberately configuration, not student code.
Use a model supporting Responses API text generation. Save the settings and restart
if prompted. Enter the demo code in the app and click **Explain these results**.

For a local run, copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml` and edit that local file. The Git ignore rule excludes it.

To stop paid calls, set `ENABLE_AI = false` in Cloud Secrets. Use a restricted
project/key and monitor its usage. Session limits and the demo code are classroom
conveniences, not a hard spending cap. Do not publish sensitive data or profiles.

## 4. Embed in Google Sites

1. Confirm the Streamlit app is public; private app embedding has no official support.
2. In Google Sites, open the appropriate page and choose **Insert → Embed → By URL**.
3. Enter your own app address with the embed parameter:

```text
https://your-app.streamlit.app/?embed=true
```

4. Insert it. Make the frame wide and around 850–1100 pixels tall, adjusting for
   your page and screen. Publish the Google Site.
5. If URL embedding does not preview correctly, use **Embed code** instead:

```html
<iframe
  src="https://your-app.streamlit.app/?embed=true"
  title="City fit advisor"
  width="100%"
  height="1000"
  style="border:0;"
></iframe>
```

6. Add a Google Sites button, **Open city advisor in a new tab**, linking to the
   ordinary app URL. This helps on phones or if embedded content is restricted.
7. Test the **published** site in a private/incognito browser window. Check that
   data appears, controls work, and explanations stay associated with their results.
   Publishing Google Sites does not change the Streamlit app's access settings.

The public app URL remains accessible outside Google Sites. Restricting the Google
Site alone does not protect the separately hosted app.

## Common problems

| Symptom | Action |
| --- | --- |
| `app.py` not found | Move project contents to repository root or correct the entrypoint |
| Data not found | Preserve `data/cities.csv`, capitalization, and folder structure |
| A Python package is missing | Check `requirements.txt` and the Cloud build log |
| App remains in local mode | Check ENABLE_AI, API key and exact model ID in Cloud Secrets |
| Explain button is disabled | Configure DEMO_ACCESS_CODE and enter the matching code |
| API request fails | Instructor checks model access, billing, network and API status; use local mode meanwhile |
| No cities appear | Change state selection/weights; missing actively weighted values are excluded |
| All weights are zero | Give at least one variable a positive priority |
| Embedded app is blank | Open app URL directly, confirm public access, wake/reboot it, then try iframe code |
| App needs to wake up | Open it before class; shared hosting is not an always-on production service |
| Ranking ignores employee text | Intentional: weights/filter drive rankings; text informs explanation only |

## Official references (checked October 21, 2026)

- GitHub template repositories: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
- Community Cloud deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Streamlit embeds: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app/embed-your-app
- Google Sites embeds: https://support.google.com/sites/answer/90569?hl=en
- OpenAI Python SDK / Responses API: https://developers.openai.com/api/reference/python
