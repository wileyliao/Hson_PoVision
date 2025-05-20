import logging

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            logging.info(f'{func.__name__} is starting...')
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f'{func.__name__}: {e}'
            logging.error(error_message)
            raise RuntimeError(error_message)
    return wrapper


def safe_extractor(extractor_func, *args, default_value=("", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]), **kwargs):
    try:
        return extractor_func(*args, **kwargs)
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f"{extractor_func.__name__} failed: {e}")
        return default_value