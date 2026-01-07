import sys
import time

from src.adapters.python_fn_adapter import PythonFnAdapter
from src.adapters.crewai_adapter import CrewAIAdapter
from src.core.node import FunctionNode, AgentNode
from src.core.pipeline import Pipeline
from src.tools.scraper import Scraper
from src.tools.websearch import WebSearcher
from examples.trip_planner.agents import TripPlannerAgents
from src.core.logging_config import get_logger

logger = get_logger(__name__)

class TripPlannerFunctions:
    @staticmethod
    def format_dict_as_sections(data: dict[str, str]) -> str:
        """Format a dictionary into sections with headers."""
        lines = []
        for key, value in data.items():
            lines.append(f"### {key}")
            lines.append("")
            lines.append(str(value))
            lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def research_cities(list_of_cities: list[str], dates: tuple[str, str], location: str) -> dict:
        """Choose a city out of the list with the best weather on provided dates."""
        weather_summaries = {}
        tickets_summaries = {}
        
        for city in list_of_cities:
            search_weather_node = FunctionNode(
                name="SearchWeatherNode",
                adapter=PythonFnAdapter(WebSearcher.duckduckgo_search),
                inputs=["query_weather", "max_results"],
                outputs=["weather_search_results"]
            )

            search_tickets_node = FunctionNode(
                name="SearchTicketsNode",
                adapter=PythonFnAdapter(WebSearcher.duckduckgo_search),
                inputs=["query_tickets", "max_results"],
                outputs=["tickets_search_results"]
            )

            # scrape_node = FunctionNode(
            #     name="ScrapeNode",
            #     adapter=PythonFnAdapter(Scraper.scrape),
            #     inputs=["weather_search_results"],
            #     outputs=["page_content"]
            # )

            weather_summary_node = AgentNode(
                name="WeatherSummaryNode",
                adapter=CrewAIAdapter(
                    TripPlannerAgents.summary_agent,
                    task_description=f"Analyze the provided search results and summarize information about weather in {city} around dates {dates[0]} and {dates[1]}.",
                    expected_output="Short summary of the weather information.",
                    outputs="weather_summary"
                ),
                inputs=["weather_search_results"]
            )

            tickets_summary_node = AgentNode(
                name="TicketsSummaryNode",
                adapter=CrewAIAdapter(
                    TripPlannerAgents.summary_agent,
                    task_description=f"Analyze the provided search results and summarize information about prices of flight tickets from {location} to {city} around dates {dates[0]} and {dates[1]}.",
                    expected_output="Short summary of the flight ticket prices.",
                    outputs="tickets_summary"
                ),
                inputs=["tickets_search_results"]
            )

            city_pipeline = Pipeline(nodes=[search_weather_node, search_tickets_node, weather_summary_node, tickets_summary_node])
            city_context = {
                "query_weather": f"weather forecast {city} from {dates[0]} to {dates[1]}", 
                "query_tickets": f"flight tickets from {location} to {city}", 
                "max_results": 5}
            result = city_pipeline.run(city_context)

            time.sleep(0.1)
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            print(f"\n✅ Pipeline Output of {city}:")
            print(result.get("weather_summary"))
            print(result.get("tickets_summary"))

            logger.info(f"✅Pipeline Output of {city}:\n{result.get('weather_summary')}\n{result.get('tickets_summary')}")

            weather_summaries[city] = result.get("weather_summary")
            tickets_summaries[city] = result.get("tickets_summary")

        return {"weather_summaries": TripPlannerFunctions.format_dict_as_sections(weather_summaries),
                "tickets_summaries": TripPlannerFunctions.format_dict_as_sections(tickets_summaries)}

    @staticmethod
    def extract_chosen_city(chosen_city_summary: str) -> dict:
        """Extract the chosen city from the agent's summary."""
        first_line = chosen_city_summary.splitlines()[0]
        chosen_city = first_line.strip()
        return {"chosen_city": chosen_city}