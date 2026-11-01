"""Lab 5 - Distill the extracted note into structured JSON."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()
markdown = (
    Path(__file__).resolve().parent.parent / "data" / "discharge_note.md"
).read_text(encoding="utf-8")

PROMPT = """Extract these fields from the discharge note below and reply
with JSON only (no code fences, no commentary):
- patient_name (string)
- discharge_date (YYYY-MM-DD)
- diagnosis (string)
- medications (array of {name, dose, schedule})
- follow_up ({department, timeframe})
- warning_signs (array of strings)

--- DISCHARGE NOTE ---
"""

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project.get_openai_client()
response = openai_client.responses.create(
    model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
    input=PROMPT + markdown,
)

record = json.loads(response.output_text)
print(json.dumps(record, indent=2))
