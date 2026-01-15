import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline_node_agents.core.pipeline import Pipeline
from examples.trip_planner.nodes import TripPlannerNodes
from src.pipeline_node_agents.core.logger_bootstrap import init_pipeline_logger
from src.pipeline_node_agents.core.logging_config import get_logger

init_pipeline_logger(pipeline_name="trip_planner_pipeline")
logger = get_logger(__name__)


def main():
    # Full pipeline
    main_pipeline = Pipeline(nodes=[
        TripPlannerNodes.research_cities_node,
        TripPlannerNodes.city_selection_node,
        TripPlannerNodes.extract_chosen_city_node,
        TripPlannerNodes.local_expert_node,
        TripPlannerNodes.travel_concierge_node
    ])


    list_of_cities = input("Enter a list of cities (comma-separated): ").split(",")
    start_date = input("Enter start date (DD Month YYYY): ")
    end_date = input("Enter end date (DD Month YYYY): ")

    print("\n🛫 Planning your trip...\n")

    # Full context
    context = {"list_of_cities": list_of_cities, "dates": (start_date, end_date), "location": "Vienna", "interests": "art, history, and food"}
    logger.info(f"Context: {context}\n")
    
    start_time = time.perf_counter()
    result = main_pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    time.sleep(0.1)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print("Chosen city:", result.get("chosen_city"))
    print("Trip itinerary:", result.get("trip_itinerary"))
    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")

    logger.info(f"✅ Final Pipeline Output:\n chosen_city: {result.get('chosen_city')}\n trip_itinerary: {result.get('trip_itinerary')}")
    logger.info(f"⏱️  Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()