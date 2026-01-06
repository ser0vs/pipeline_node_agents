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

    # start_date = (datetime.now() + timedelta(days=3)).strftime("%d %B %Y")
    # end_date = (datetime.now() + timedelta(days=10)).strftime("%d %B %Y")

    # Full context
    context = {"list_of_cities": ["Madrid", "Dubai"], "dates": (start_date, end_date)}
    print(f"Context: {context}\n")

    # Debug: simpler context
    # context = {"dates": (start_date, end_date), "chosen_city": "Dubai"}
    
    start_time = time.perf_counter()
    result = main_pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    time.sleep(0.1)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print("chosen_city:", result.get("chosen_city"))
    print("trip_itinerary:", result.get("trip_itinerary"))
    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()