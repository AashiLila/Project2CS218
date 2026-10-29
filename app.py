
"""Redwood Financial AI Relocation Advisor."""

from pathlib import Path
import os
import json
import pandas as pd
import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="Redwood Financial Relocation Advisor",
    page_icon="🏙️",
    layout="centered"
)

# Load the ranked dataset
@st.cache_data
def load_data():
    path = Path(__file__).parent / "data" / "cities.csv"
    df = pd.read_csv(path)

    df["Rank"] = pd.to_numeric(df["Rank"])
    df = df.sort_values("Rank")

    return df.head(5).copy()

top_5 = load_data()

# Convert top five cities to JSON for the AI
city_data = top_5.to_json(
    orient="records",
    indent=2
)

# System instructions
SYSTEM_PROMPT = """
You are Redwood Financial's AI Relocation Advisor.

ROLE:
You are a friendly and professional customer support
representative helping employees choose where to relocate.

BACKGROUND:
Redwood Financial is a Chicago-based financial services
company specializing in investments and retirement planning.

The company ranked 500 US cities using 15 features across
economic, environmental, health, lifestyle, and geographic
categories.

Employees can relocate ONLY to the five highest-ranked
cities provided in the dataset.

YOUR TASK:
Help employees compare the five eligible cities and
choose the location that best fits their preferences.

RULES:
1. Always use the provided dataset when answering.
2. Only recommend the five eligible cities.
3. Never invent statistics or information.
4. If information is unavailable, explain that.
5. Do not assume the highest-ranked city is best for everyone.
6. Consider each employee's personal priorities.
7. Explain advantages and disadvantages.
8. Distinguish county-level data from city-level data.
9. Do not confuse overall ranking with personal fit.
10. Do not recommend cities outside the eligible five.

COMPARISON CATEGORIES:

Affordability (12%):
- Cost of Living
- Poverty Rate

Climate and Environment (8%):
- Winter Weather
- Water Area

Health and Lifestyle (32%):
- COVID Cases and Deaths
- Lack of Leisure Physical Activity
- Mental Health
- Physical Distress

Local Economy (29%):
- Income by City
- Employment
- Education Level
- Industries

Safety and Natural Hazards (19%):
- Fatal Police Shootings
- Drought
- Earthquake

Only compare features available in the dataset.

IMPORTANT DATA LIMITATIONS:
- Some measurements are county-level rather than city-level.
- COVID values are historical cumulative totals.
- Employment and COVID totals are not population-adjusted.
- Missing values must not be treated as zero.
- Do not assume higher hazard risk scores indicate
  greater danger without verified scoring definitions.
- Fatal police shootings are not a complete measure
  of public safety.
- Water area does not guarantee recreational access.
- The overall weighted score is a relative ranking,
  not a measure of individual employee satisfaction.

RECOMMENDATIONS:
When an employee asks where to relocate:
1. Identify their priorities.
2. Compare relevant city features.
3. Explain the pros and cons.
4. Recommend the best-fitting eligible city.
5. Explain why it matches their preferences.

If the employee has not shared enough preferences,
ask a helpful follow-up question.

RESPONSE STYLE:
- Friendly, helpful, and professional.
- Keep answers clear and concise.
- Use bullet points when helpful.
- Explain statistics in simple language.
- Reference actual dataset values when possible.
- Acknowledge missing data.

If asked about unrelated topics, politely redirect
the conversation to relocation assistance.

Your goal is to help employees make informed relocation
decisions using the provided data.
"""

# Read settings from environment or Streamlit secrets
def setting(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except FileNotFoundError:
        return os.getenv(name, default)

api_key = setting("OPENAI_API_KEY")
model = setting("OPENAI_MODEL", "gpt-4.1-mini")
enable_ai = setting("ENABLE_AI", "false").lower() == "true"

# Main page
st.title("🏙️ Redwood Financial")
st.subheader("AI Relocation Advisor")

st.write(
    "Thinking about relocating? Our AI advisor helps "
    "you compare Redwood Financial's five recommended "
    "office locations based on your career goals, "
    "lifestyle, and personal priorities."
)

# Sidebar
with st.sidebar:
    st.header("🏙️ Top 5 Cities")

    for _, city in top_5.iterrows():
        st.write(
            f"**#{int(city['Rank'])} "
            f"{city['City']}, {city['State']}**"
        )
        st.caption(
            f"Weighted Score: "
            f"{city['Weighted Score (0-100)']:.2f}/100"
        )

    st.divider()

    st.header("Comparison Categories")

    st.write("💰 Affordability — 12%")
    st.write("🌎 Climate and Environment — 8%")
    st.write("❤️ Health and Lifestyle — 32%")
    st.write("💼 Local Economy — 29%")
    st.write("🛡️ Safety and Natural Hazards — 19%")

    st.divider()

    with st.expander("View City Dataset"):
        st.dataframe(top_5, hide_index=True)

    if st.button("Clear Conversation"):
        st.session_state.pop("messages", None)
        st.rerun()

# Check API configuration
if not enable_ai:
    st.info(
        "AI is currently disabled. Set ENABLE_AI "
        "to true in your Streamlit secrets."
    )
    st.stop()

if not api_key:
    st.error("OpenAI API key not configured.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm Redwood Financial's AI "
                "Relocation Advisor.\n\n"
                "I can help you compare our five "
                "recommended cities and find the best "
                "match for your lifestyle and career.\n\n"
                "What matters most to you in a new city?"
            )
        }
    ]

if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Employee chat input
prompt = st.chat_input(
    "Ask about your relocation options..."
)

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.api_calls >= 5:
            st.warning(
                "You've reached the five-request "
                "limit for this demo session."
            )
        else:
            try:
                client = OpenAI(
                    api_key=api_key,
                    timeout=45.0,
                    max_retries=0
                )

                instructions = (
                    SYSTEM_PROMPT
                    + "\n\nELIGIBLE CITY DATA:\n"
                    + city_data
                )

                # Exclude the initial assistant greeting
                history = st.session_state.messages[1:]

                with st.spinner("Comparing cities..."):
                    st.session_state.api_calls += 1

                    response = client.responses.create(
                        model=model,
                        instructions=instructions,
                        input=history,
                        max_output_tokens=1200,
                        store=False
                    )

                if (
                    response.status != "completed"
                    or not response.output_text.strip()
                ):
                    raise ValueError("Incomplete AI response")

                answer = response.output_text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception:
                st.error(
                    "Unable to get a response. "
                    "Please check your API configuration "
                    "and try again."
                )

st.caption(
    "Redwood Financial | AI Relocation Advisor | "
    "CS218 Course Project"
)
