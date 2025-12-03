from src.adapters.base_adapter import BaseAdapter
from crewai import Agent, Task, Crew

class CrewAIAdapter(BaseAdapter):
    def __init__(self, agent_or_crew):
        self.entity = agent_or_crew

    def invoke(self, messages_template: list[dict] | None = None, **kwargs) -> dict:
        if hasattr(self.entity, "run"):
            # Single agent
            input_text = " ".join(f"{k}: {v}" for k, v in kwargs.items())
            output = self.entity.run(input=input_text)

        elif hasattr(self.entity, "kickoff"):
            if messages_template:
                messages = [
                    {msg["role"]: msg.get("role", "user"),
                     "content": msg["content"].format(**kwargs) if "{"+list(kwargs.keys())[0]+"}" in msg["content"] else msg["content"]}
                    for msg in messages_template
                ]
            else:
                # default messages
                input_text = ", ".join(f"{k}: {v}" for k, v in kwargs.items())
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Process the following input: {input_text}"}
                ]
            output = self.entity.kickoff(messages)
        else:
            raise ValueError("Entity must be a CrewAI Agent or Crew.")
        
        return {"summary": str(output)}
