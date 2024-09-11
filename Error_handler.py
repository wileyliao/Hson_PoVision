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
