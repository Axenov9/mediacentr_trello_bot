from functions import *
class handler():
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

# COMMANDS
    def handle(self):

        @self.bot.message_handler(commands=['start'])
        def handle(message):
            print(message.from_user.username + ": " + message.text)
            text = '''Это бот бла бла бла, он ничего не умеет'''
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_to_message_id=message.message_id)

        # CALLS
        # Пример работы с call
        # @self.bot.callback_query_handler(func=lambda call: 'marks' in call.data)
        # def handle(call):
        #     print(call.from_user.username + ": " + call.data)
        #     some_func(self.bot, call)

