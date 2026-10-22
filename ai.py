"""One bounded, server-side Responses API request per explicit button click."""
import json
from openai import OpenAI

INSTRUCTIONS = '''You explain results for a fictional employee relocation advisor.
'''


def explain(evidence, api_key, model):
    client = OpenAI(api_key=api_key, timeout=45.0, max_retries=0)
    response = client.responses.create(
        model=model,
        instructions=INSTRUCTIONS,
        input=json.dumps(evidence, ensure_ascii=False, allow_nan=False),
        max_output_tokens=1200,
        store=False,
    )
    if response.status != 'completed' or not response.output_text.strip():
        raise ValueError('Response incomplete or empty; try again or use local mode.')
    return response.output_text
