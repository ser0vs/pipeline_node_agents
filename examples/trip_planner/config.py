import os

os.environ["OLLAMA_HOST"] = "http://localhost:11434"

from crewai import LLM


class TripPlannerConfig:
    ollama_llm = LLM(
        model="ollama/qwen3:8b",
        base_url="http://localhost:11434",
        extra_body={"options": {"think": False}}
    )
