import logging


async def actor_logging_hook():
    logging.basicConfig()
    logging.getLogger('magda').setLevel(logging.INFO)
    logging.getLogger('magda').setLevel(logging.DEBUG)
