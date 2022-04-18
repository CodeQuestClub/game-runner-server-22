from datetime import datetime


def log(msg):
    print(msg)
    current_time = datetime.now().strftime("%b %d - %H:%M:%S")
    with open('logs.txt', 'a') as f:
        f.write(f'{current_time} | {msg}\n')
