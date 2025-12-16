from src.adapters.base_adapter import BaseAdapter
from crewai import Agent, Task, Crew

from src.adapters.base_adapter import BaseAdapter
from crewai import Agent, Task, Crew

class CrewAIAdapter(BaseAdapter):
    def __init__(self, agent_or_crew, task_description: str = None, expected_output: str = None):
        self.entity = agent_or_crew
        self.task_description = task_description
        self.expected_output = expected_output or "A detailed analysis based on the input."

    def invoke(self, messages_template: list[dict] | None = None, **kwargs) -> dict:
        if isinstance(self.entity, Agent):
            input_text = "\n\n".join(f"### {k.upper()} ###\n{v}" for k, v in kwargs.items())
            
            max_input_length = 8000
            if len(input_text) > max_input_length:
                input_text = input_text[:max_input_length] + "\n\n[... content truncated ...]"
            
            description = self.task_description or self.entity.goal or "Process this input"
            
            full_description = f"""YOUR TASK: {description}

Based on the following content, complete the task above. Focus specifically on answering the task.

---
{input_text}
---

Remember: {description}"""

            task = Task(
                description=full_description,
                agent=self.entity,
                expected_output=self.expected_output
            )

            print(f"[CrewAIAdapter] Task description: {description}")
            print(f"[CrewAIAdapter] Expected output: {self.expected_output}")
            print(f"[CrewAIAdapter] Input length: {len(input_text)} chars")
            
            crew = Crew(agents=[self.entity], tasks=[task])
            output = crew.kickoff()
            return {"summary": str(output)}

        elif hasattr(self.entity, "kickoff"):
            output = self.entity.kickoff(inputs=kwargs)
            return {"summary": str(output)}
        
        else:
            raise ValueError("Entity must be a CrewAI Agent or Crew.")