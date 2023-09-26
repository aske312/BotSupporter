# -*- coding: utf-8 -*-


def log_errors(func):
    def surrogate(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            bad_log = open('../lib/logs/logs.log', 'a')
            bad_log.write('Funcs: ' + str(func.__name__)
                          + ' Calls: ' + str(Exception.__call__(*args, *kwargs))
                          + ' Types: ' + str(type(exc).__name__)
                          + ' Value: ' + str(exc) + '\n')
            bad_log.close()
            exit(f'FATAL ERROR: Cancel launch check by logs.log called: "{str(type(exc).__name__)}".')
    return surrogate


class UnknownSource(Exception):
    def __init__(self, text):
        self.txt = text


class ResponseNotOk(Exception):
    def __init__(self, text):
        self.txt = text


# class TheNewsExists(Exception):
#     def __init__(self, text):
#         self.txt = text
