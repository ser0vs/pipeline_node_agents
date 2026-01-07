import os
import sys
import time
from datetime import datetime, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.pipeline import Pipeline
from examples.trip_planner.nodes import TripPlannerNodes
from src.core.logger_bootstrap import init_pipeline_logger
from src.core.logging_config import get_logger

init_pipeline_logger(pipeline_name="trip_planner_pipeline")
logger = get_logger(__name__)


def main():
    # Full pipeline
    main_pipeline = Pipeline(nodes=[
        TripPlannerNodes.research_cities_node,
        TripPlannerNodes.city_selection_node,
        TripPlannerNodes.extract_chosen_city_node,
        # TripPlannerNodes.local_expert_node,
        # TripPlannerNodes.travel_concierge_node
    ])


    ### Debug user input (TODO: uncomment for real use case)
    # list_of_cities = input("Enter a list of cities (comma-separated): ").split(",")
    # start_date = input("Enter start date (DD Month YYYY): ")
    # end_date = input("Enter end date (DD Month YYYY): ")
    # location = input("Enter your current location: ")
    # interests = input("Enter your interests: ")

    print("\n🛫 Planning your trip...\n")

    # Debug values (TODO: remove for real use case)
    list_of_cities = ["Madrid", "Dubai"]
    start_date = (datetime.now() + timedelta(days=3)).strftime("%d %B %Y")
    end_date = (datetime.now() + timedelta(days=10)).strftime("%d %B %Y")
    location = "Vienna"
    interests = "art, history, food"

    # Full context
    context = {"list_of_cities": list_of_cities, "dates": (start_date, end_date), "location": location, "interests": interests}

    logger.info(f"Context: {context}\n")

    # Debug: simpler context
    # context = {"dates": (start_date, end_date), "chosen_city": "Dubai"}
    
    start_time = time.perf_counter()
    result = main_pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    time.sleep(0.1)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print("Chosen city:", result.get("chosen_city"))
    print("Trip itinerary:", result.get("chosen_city_summary"))  # Debug TODO: change to itinerary when travel_concierge_node is enabled
    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")

    # Debug TODO: change to itinerary when travel_concierge_node is enabled
    logger.info(f"✅ Final Pipeline Output:\n chosen_city: {result.get('chosen_city')}\n chosen_city_summary: {result.get('chosen_city_summary')}")
    logger.info(f"⏱️  Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()