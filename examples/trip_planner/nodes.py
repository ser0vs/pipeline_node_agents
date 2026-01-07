from src.adapters.python_fn_adapter import PythonFnAdapter
from src.adapters.crewai_adapter import CrewAIAdapter
from src.core.node import FunctionNode, AgentNode
from examples.trip_planner.agents import TripPlannerAgents
from examples.trip_planner.functions import TripPlannerFunctions


class TripPlannerNodes:
    research_cities_node = FunctionNode(
        name="ResearchCitiesNode",
        adapter=PythonFnAdapter(TripPlannerFunctions.research_cities),
        inputs=["list_of_cities", "dates"],
        output="weather_summaries"
    )


    city_selection_node = AgentNode(
        name="CitySelectionNode",
        adapter=CrewAIAdapter(
            TripPlannerAgents.city_selection_agent,
            task_description="Choose one city from the provided list based on the weather summaries.",
            expected_output="First line: Chosen city name. Following lines: brief explanation of why this city was chosen."
        ),
        inputs=["weather_summaries"],
        output="chosen_city_summary"
    )

    extract_chosen_city_node = FunctionNode(
        name="ExtractChosenCityNode",
        adapter=PythonFnAdapter(TripPlannerFunctions.extract_chosen_city),
        inputs=["chosen_city_summary"],
        output="chosen_city"
    )

    local_expert_node = AgentNode(
        name="LocalExpertNode",
        adapter=CrewAIAdapter(
            TripPlannerAgents.local_expert_agent,
            task_description="Gather insights about key attractions, food places, and daily activity recommendations of the chosen city.",
            expected_output="City guide including hidden gems, cultural hotspots, and practical travel tips"
        ),
        inputs=["chosen_city", "dates"],
        output="list_of_attractions"
    )

    travel_concierge_node = AgentNode(
        name="TravelConciergeNode",
        adapter=CrewAIAdapter(
            TripPlannerAgents.travel_concierge_agent,
            task_description="Plan a 7-day trip itinerary based on the chosen city and provided information.",
            expected_output="Detailed 7-day itinerary including daily activities, dining options, and transportation tips.",
        ),
        inputs=["chosen_city", "list_of_attractions", "dates"],
        output="trip_itinerary"
    )