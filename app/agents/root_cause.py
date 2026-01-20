from pydantic_ai import Agent
from app.services.llm import MODEL
from app.utils.retry import llm_retry
import re

agent = Agent(
    model=f"openrouter:{MODEL}"
)

@llm_retry
async def analyze_root_cause(error_log: str, language: str) -> str:
    prompt = f"""
Explain the root cause in simple language.

Return ONLY valid JSON (no markdown, no code blocks).

JSON format:
{{
  "summary": "short explanation",
  "detailed_explanation": "clear beginner-friendly explanation"
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
