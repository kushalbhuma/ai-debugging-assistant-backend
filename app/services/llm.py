import os
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")

agent = Agent(
    model=f"openrouter:{MODEL}"
)
