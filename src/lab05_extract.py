"""Lab 5 - Read the discharge note with Content Understanding."""
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.contentunderstanding import ContentUnderstandingClient

load_dotenv()
NOTE_PATH = Path(__file__).resolve().parent.parent / "data" / "discharge_note.pdf"

client = ContentUnderstandingClient(
    endpoint=os.environ["FOUNDRY_RESOURCE_ENDPOINT"],  # resource root!
    credential=DefaultAzureCredential(),
)

print(f"Analyzing {NOTE_PATH.name} (this takes ~10-30 seconds)...")
poller = client.begin_analyze_binary(
    analyzer_id="prebuilt-layout",
    binary_input=NOTE_PATH.read_bytes(),
)
result = poller.result()          # SDK polls the long-running job for you
print(result)
content = result.contents[0]      # one input -> one content item
markdown = content.markdown

out_path = NOTE_PATH.with_suffix(".md")
out_path.write_text(markdown, encoding="utf-8")
print(f"Saved extracted markdown to {out_path}")
print("\n--- first lines ---")
print("\n".join(markdown.splitlines()[:12]))
