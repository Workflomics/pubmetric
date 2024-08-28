""" Logging methods"""
from datetime import datetime

def log_with_timestamp(message: str):
    """
    Logs a message with a timestamp.

    :param message: The message to be logged.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")


def step_timer(start_time: datetime, step_name: str):
    """
    Logs the elapsed time for a specific step.

    :param start_time: The start time of the process or step to be measured.
    :param step_name: A descriptive name for the step, used in the log message.
    """
    elapsed_time = datetime.now() - start_time
    log_with_timestamp(f"{step_name} took {elapsed_time}")
