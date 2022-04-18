from datetime import datetime
from pytz import timezone


def log(msg):
    print(msg)
    current_time = datetime.now(timezone('Australia/Melbourne')).strftime("%b %d - %H:%M:%S")
    with open('logs.txt', 'a') as f:
        f.write(f'{current_time} | {msg}\n')
