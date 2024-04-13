import sys
if sys.version_info < (3, 9):
	print("[FATAL] Python 3.9 or newer is required!")
	sys.exit(1)
# # # # # # # # # #

import time
import traceback
import json
import requests
# # # # # # # # # #

from config import telegram_api_token, actions_api, chat_id, set_logging, delay
# # # # # # # # # #

def say(message, chat_id): # Надо будет нахуй переделать, чтобы работало через pytelegrambotapi
	message = message.replace("	","")
	print(message)
	result = requests.post(f"https://api.telegram.org/bot{telegram_api_token}/sendMessage",
		data={
		"chat_id": chat_id,
		"text": message,
		"parse_mode": "HTML",
		"disable_web_page_preview": "true",
		}, timeout=30).text
	return result
# # # # # # # # # #

result_old = requests.get(actions_api, timeout=60).json() # Первый запрос, чтобы впоследствие было с чем сравнивать
if "old" not in result_old[0]["data"]:
	result_old[0]["data"]["old"] = {} # if not exists
# # # # # # # # # #

print("[#] Trello bot started..")
print("Delay: " + str(delay) + " sec")
while True:
	# # # # # # # # # #
	while True:
		try:
			result_new = requests.get(actions_api, timeout=60).json()
			break
		except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
			print("=== Exception caught!")
			print(traceback.format_exc())
			time.sleep(5)
	# # # # # # # # # #

	if "old" not in result_new[0]["data"]:
		result_new[0]["data"]["old"] = {} # if not exists
	# # # # # # # # # #

	if result_old[0] != result_new[0]:
		event_data = result_new[0]["data"]
		# # # # # # # # # #

		if "card" not in event_data:
			pass

		# MOVING CARD #
		elif "listBefore" in event_data and "listAfter" in event_data:
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			lest_after = event_data['listAfter']['name']
			msg = f"""Задача <a href='https://trello.com/c/{link}'><b>{card_name}</b></a> перемещена в <b>{lest_after}</b>"""

			say(msg, chat_id)

		# RENAMING CARD #
		elif "name" in event_data["old"]:
			old_name = event_data['old']['name']
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			msg = f'''Задача <i>{old_name}</i> переименована в <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>'''

			say(msg, chat_id)

		# CREATING CARD #
		elif result_new[0]["type"] == "createCard":
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			msg = f"""🔥 Добавлена новая задача - <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>"""

			say(msg, chat_id)

		# ADDING MEMBER/LEAVING FROM CARD #
		elif "idMember" in event_data:
			member = event_data['member']['name']
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			msg = f'''🔥 <b>{member}</b> {'взял(а)' if not 'deactivated' in event_data else 'бросил(а)'} задачу <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>'''

			say(msg, chat_id)

		# ARCHIVING CARD #
		elif "closed" in event_data['card']:
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			msg = f'''🗑️ Задача <a href='https://trello.com/c/{link}'><i>{card_name}</i></a> <b>архивирована</b>'''

			say(msg, chat_id)

		# ANOTHER EVENT #
		# else:
		# 	msg = '<i>Неизвестное событие</i>'
		# 	say(msg, chat_id)
		# # # # # # # # # #

	result_old = result_new
	time.sleep(delay)
