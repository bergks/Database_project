import logging

def configure_logging(level=logging.DEBUG):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(module)s:%(lineno)d %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logging.root.setLevel(level)
    logging.root.addHandler(handler)