from datetime import datetime
from pathlib import Path
from src.core.logging_config import configure_logging


def init_pipeline_logger(pipeline_name: str, log_path: str = "logs", level: str = "INFO"):
    timestamp = datetime.now().strftime("%d_%m_%y__%H_%M_%S")
    log_file = (
        Path(log_path)
        / pipeline_name
        / f"{pipeline_name}_run_{timestamp}.log"
    )

    configure_logging(log_file=log_file, level=level)

    return log_file
