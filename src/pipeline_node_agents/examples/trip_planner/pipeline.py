import sys
import time
import logging

from pipeline_node_agents.core.pipeline import Pipeline
from pipeline_node_agents.examples.trip_planner.nodes import TripPlannerNodes
from pipeline_node_agents.core.logger_bootstrap import init_pipeline_logger
from pipeline_node_agents.core.logging_config import get_logger


class TripPlannerPipeline:
    """
    A pipeline that plans a trip by researching cities, selecting the best one,
    and creating a detailed itinerary.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def run(self) -> dict:
        self.logger.info("Starting TripPlannerPipeline")

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
        context = {
            "list_of_cities": list_of_cities,
            "dates": (start_date, end_date),
            "location": "Vienna",
            "interests": "art, history, and food"
        }
        self.logger.info("Context: %s", context)

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

        self.logger.info("✅ Final Pipeline Output:\n chosen_city: %s\n trip_itinerary: %s",
                         result.get('chosen_city'), result.get('trip_itinerary'))
        self.logger.info("⏱️  Execution time: %.2f seconds", elapsed_time)

        return result


def main():
    init_pipeline_logger(pipeline_name="trip_planner_pipeline")
    logger = get_logger(__name__)

    pipeline = TripPlannerPipeline(logger=logger)
    pipeline.run()


if __name__ == "__main__":
    main()