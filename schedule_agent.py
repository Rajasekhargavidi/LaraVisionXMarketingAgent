import logging
import time

import schedule

from social_agent.agent import run_agent_once


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def job() -> None:
    logging.info("Running LaraVisionX social media agent job.")
    run_agent_once()
    logging.info("Job finished.")


def main() -> None:
    # Example: run once every day at 09:00 server time.
    schedule.every().day.at("09:00").do(job)

    logging.info("Scheduler started; waiting for next run.")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

