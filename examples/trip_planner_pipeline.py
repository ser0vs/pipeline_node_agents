import random, os, sys
import time, json, requests

os.environ["OLLAMA_HOST"] = "http://localhost:11434"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from src.adapters.python_fn_adapter import PythonFnAdapter
from src.adapters.crewai_adapter import CrewAIAdapter
from src.core.node import FunctionNode, AgentNode
from src.core.pipeline import Pipeline
from crewai import Agent, LLM
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from src.tools.scraper import Scraper
from src.tools.websearch import WebSearcher
from datetime import datetime, timedelta


# --- CrewAI Node: Summarize results ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

summary_agent = Agent(
    name="SummaryAgent",
    role="Expert in summarizing textual content.",
    goal="Summarize the provided text with respect to the given task.",
    backstory="You are a highly skilled expert in summarizing information.",
    llm=ollama_llm
)

city_selection_agent = Agent(
    name="CitySelectionAgent",
    role="Expert in city and place recommendations.",
    goal="Choose one city from the provided list based on weather summaries.",
    backstory="You are a highly skilled city travel expert.",
    llm=ollama_llm
)

local_expert_agent = Agent(
    name="LocalExpertAgent",
    role="Local Expert in defined city.",
    goal="Provide the best recommendation where to go in defined city based on text content.",
    backstory="You are a highly skilled local expert with deep knowledge of the city's culture, attractions, and hidden gems.",
    llm=ollama_llm
)

travel_concierge_agent = Agent(
    name="TravelConciergeAgent",
    role="Expert in planning of trips and travel itineraries.",
    goal="Plan the best trip itinerary based on the chosen city and provided information.",
    backstory="You are a highly skilled travel concierge with expertise in creating personalized travel plans.",
    llm=ollama_llm
)


def format_dict_as_sections(data: dict[str, str]) -> str:
    """Format a dictionary into sections with headers."""
    lines = []
    for key, value in data.items():
        lines.append(f"### {key}")
        lines.append("")
        lines.append(str(value))
        lines.append("")

    return "\n".join(lines).strip()


def research_cities(list_of_cities: list[str], dates: tuple[str, str]) -> dict:
    """Choose a city out of the list with the best weather on provided dates."""
    weather_summaries = {}
    for city in list_of_cities:
        search_node = FunctionNode(
            name="DuckDuckGoSearchNode",
            adapter=PythonFnAdapter(WebSearcher.duckduckgo_search),
            inputs=["query", "max_results"],
            outputs=["search_results"]
        )

        scrape_node = FunctionNode(
            name="ScrapeNode",
            adapter=PythonFnAdapter(Scraper.scrape),
            inputs=["search_results"],
            outputs=["page_content"]
        )

        weather_summary_node = AgentNode(
            name="WeatherSummaryNode",
            adapter=CrewAIAdapter(
                summary_agent,
                task_description=f"Analyze the provided text and summarize information about weather in {city} on dates from {dates[0]} to {dates[1]}.",
                expected_output="Short summary of the weather information."
            ),
            inputs=["page_content"],
            outputs=["summary"]
        )

        city_pipeline = Pipeline(nodes=[search_node, scrape_node, weather_summary_node])

        city_context = {"query": f"weather forecast {city} from {dates[0]} to {dates[1]}", "max_results": 5}
        result = city_pipeline.run(city_context)

        time.sleep(0.1)
        sys.stdout = sys.__stdout__ 
        sys.stderr = sys.__stderr__

        print(f"\n✅ Pipeline Output of {city}:")
        print(result.get("summary"))

        weather_summaries[city] = result.get("summary")

    return {"weather_summaries": format_dict_as_sections(weather_summaries)}

    ### debug return value
    # return {"weather_summaries": "### Vienna\n\nThe weather in Vienna from 1 January 2026 to 10 January 2026 is expected to be cold with temperatures ranging from -2°C to 4°C. There may be occasional snowfall and cloudy days.\n\n### Madrid\n\nMadrid will experience mild winter weather during this period, with temperatures between 5°C and 15°C. Sunny days are expected with low chances of rain.\n\n### Paris\n\nParis is likely to have chilly weather with temperatures ranging from 1°C to 7°C. There may be some rainy days and overcast skies throughout the week.\n\n### Dubai\n\nDubai will have warm weather with temperatures ranging from 18°C to 26°C. Mostly sunny days are expected with very low humidity."}


def extract_chosen_city(chosen_city_summary: str) -> dict:
    """Extract the chosen city from the agent's summary."""
    first_line = chosen_city_summary.splitlines()[0]
    chosen_city = first_line.strip()
    return {"chosen_city": chosen_city}

def main():
    research_cities_node = FunctionNode(
        name="ResearchCitiesNode",
        adapter=PythonFnAdapter(research_cities),
        inputs=["list_of_cities", "dates"],
        outputs=["weather_summaries"]
    )


    city_selection_node = AgentNode(
        name="CitySelectionNode",
        adapter=CrewAIAdapter(
            city_selection_agent,
            task_description="Choose one city from the provided list based on the weather summaries.",
            expected_output="First line: Chosen city name. Following lines: brief explanation of why this city was chosen.",
            outputs="chosen_city_summary"
        ),
        inputs=["weather_summaries"]
    )

    extract_chosen_city_node = FunctionNode(
        name="ExtractChosenCityNode",
        adapter=PythonFnAdapter(extract_chosen_city),
        inputs=["chosen_city_summary"],
        outputs=["chosen_city"]
    )

    local_expert_node = AgentNode(
        name="LocalExpertNodes",
        adapter=CrewAIAdapter(
            local_expert_agent,
            task_description="Gather insights about key attractions, food places, and daily activity recommendations of the chosen city.",
            expected_output="City guide including hidden gems, cultural hotspots, and practical travel tips",
            outputs="list_of_attractions"
        ),
        inputs=["chosen_city", "dates"]
    )

    travel_concierge_node = AgentNode(
        name="TravelConciergeNode",
        adapter=CrewAIAdapter(
            travel_concierge_agent,
            task_description="Plan a 7-day trip itinerary based on the chosen city and provided information.",
            expected_output="Detailed 7-day itinerary including daily activities, dining options, and transportation tips.",
            outputs="trip_itinerary"
        ),
        inputs=["chosen_city", "list_of_attractions", "dates"]
    )



    # main_pipeline = Pipeline(nodes=[research_cities_node, city_selection_node, extract_chosen_city_node, local_expert_node, travel_concierge_node])
    ### debug simpler pipeline
    main_pipeline = Pipeline(nodes=[local_expert_node, travel_concierge_node])

    start_date = (datetime.now() + timedelta(days=3)).strftime("%d %B")
    end_date = (datetime.now() + timedelta(days=10)).strftime("%d %B")

    # context = {"list_of_cities": ["Madrid", "Dubai"], "dates": (start_date, end_date)}
    ### debug simpler context
    context = {"dates": (start_date, end_date), "chosen_city": "Dubai"}
    result = main_pipeline.run(context)

    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print("chosen_city", result.get("chosen_city"))
    print("trip_itinerary", result.get("trip_itinerary"))




if __name__ == "__main__":
    main()