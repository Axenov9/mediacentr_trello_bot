from telebot import TeleBot
from handlers import handler
from config import TG_API
import threading
from functions import update_api

class Bot:

    def __init__(self):
        self.token = TG_API
        self.bot = TeleBot(self.token)
        self.handler = handler(self.bot)

    def start_polling(self):
        self.handler.handle()
        self.bot.polling(non_stop=True)
    def start_updating_api(self):
        update_api(self.bot)
    def run(self):
        thread_polling = threading.Thread(target=self.start_polling)
        thread_updating_api = threading.Thread(target=self.start_updating_api)
        thread_polling.start()
        thread_updating_api.start()



if __name__ == '__main__':

    bot = Bot()
    bot.run()

