from time import perf_counter

def list_diff(l1: list, l2: list) -> list:
    return (list(list(set(l1)-set(l2)) + list(set(l2)-set(l1))))

def threaded(func, param, workers: int = 4):
    from concurrent.futures import ThreadPoolExecutor as PoolExecutor
    with PoolExecutor(max_workers=workers) as executor:
        for _ in executor.map(func, param):
            pass

def var_to_dict(**kwargs) -> dict:
    return locals()['kwargs']

def get_timestamp(tz: str = 'UTC', fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    from datetime import datetime
    from pytz import timezone
    return datetime.now(timezone(tz)).strftime(fmt)

def seconds_formatter(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int((seconds % 3600) % 60)
    hours = '' if hrs == 0 else f"{hrs} hour{'' if hrs == 1 else 's'}"
    minutes = '' if mins == 0 else f"{'' if hrs == 0 else ', '}{mins} minute{'' if mins == 1 else 's'}"
    if secs == 0 and mins == 0 and hrs == 0:
        second = f"{secs} seconds"
    else:
        second = '' if secs == 0 else f"{'' if mins == 0 and hrs == 0 else ', '}{secs} second{'' if secs == 1 else 's'}"
    return f"{hours}{minutes}{second}".lstrip().rstrip()

def command_types(cmd: str) -> tuple:
    commands = {
        'git': ['clone', 'checkout'],
        'dbt': ['debug', 'compile', 'run', 'test', 'deps', 'snapshot', 'clean', 'seed', 'docs', 'source']
    }
    for key in commands.keys():
        for item in commands[key]:
            if not cmd.lower().find(item) == -1:
                return key, item
    return 'unk', 'invalid'

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        self._start_time = perf_counter()

    def stop(self):
        elapsed_time = perf_counter() - self._start_time
        self._start_time = None
        return elapsed_time

class Increment:
    def __init__(self, incrementor=0):
        self.value = incrementor

    def add(self):
        self.value += 1

    @property
    def incrementor(self):
        return self._value

    @incrementor.setter
    def incrementor(self, value):
        self._value = value