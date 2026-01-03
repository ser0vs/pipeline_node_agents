import os, sys

os.environ["OLLAMA_HOST"] = "http://localhost:11434"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from crewai import Agent
from examples.trip_planner.config import TripPlannerConfig


class TripPlannerAgents:
    summary_agent = Agent(
        name="SummaryAgent",
        role="Expert in summarizing textual content.",
        goal="Summarize the provided text with respect to the given task.",
        backstory="You are a highly skilled expert in summarizing information.",
        llm=TripPlannerConfig.ollama_llm
    )

    city_selection_agent = Agent(
        name="CitySelectionAgent",
        role="Expert in city and place recommendations.",
        goal="Choose one city from the provided list based on weather summaries.",
        backstory="You are a highly skilled city travel expert.",
        llm=TripPlannerConfig.ollama_llm
    )

    local_expert_agent = Agent(
        name="LocalExpertAgent",
        role="Local Expert in defined city.",
        goal="Provide the best recommendation where to go in defined city based on text content.",
        backstory="You are a highly skilled local expert with deep knowledge of the city's culture, attractions, and hidden gems.",
        llm=TripPlannerConfig.ollama_llm
    )

    travel_concierge_agent = Agent(
        name="TravelConciergeAgent",
        role="Expert in planning of trips and travel itineraries.",
        goal="Plan the best trip itinerary based on the chosen city and provided information.",
        backstory="You are a highly skilled travel concierge with expertise in creating personalized travel plans.",
        llm=TripPlannerConfig.ollama_llm
    )