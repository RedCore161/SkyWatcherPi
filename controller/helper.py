from threading import Thread


def start_as_thread(func):
    """
    wrapper-decorator to start a thread
    :param func: function that will be started as a thread
    :return: /
    """
    def decorator(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator
