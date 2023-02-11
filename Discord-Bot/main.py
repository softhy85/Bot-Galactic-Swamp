from threading import Thread
from health_check import start_health_check, stop_health_check
from main_bot import start_bot
import time

if __name__ == "__main__":
    health_check_thread = Thread(target = start_health_check)
    bot_thread = Thread(target = start_bot)
    health_check_thread.start()
    bot_thread.start()
    while bot_thread.is_alive():
        time.sleep(10)
    stop_health_check()
