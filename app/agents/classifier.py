from pydantic_ai import Agent
from app.services.llm import MODEL
from app.utils.retry import llm_retry
import json
import re

agent = Agent(
    model=f"openrouter:{MODEL}"
)

@llm_retry
async def classify_error(error_log: str, language: str) -> str:
    prompt = f"""
You are an expert debugging assistant.

Return ONLY valid JSON (no markdown, no code blocks).

Allowed categories:
- syntax_error
- runtime_error
- dependency_error
- configuration_error
- unknown

JSON format:
{{
  "category": "dependency_error",
  "confidence": 0.85
}}

Error logs:
{error_log}
"""
    result = await agent.run(prompt)
    # Remove markdown code blocks if present
    output = result.output.strip()
    if output.startswith("```"):
        output = re.sub(r'^```(?:json)?\n', '', output)
        output = re.sub(r'\n```$', '', output)
    return output
