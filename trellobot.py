#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 * Copyright (C) 2023 Nikita Beloglazov <nnikita.beloglazov@gmail.com>
 *
 * This file is part of Nebobot/Trello-Telegram-Bot.
 *
 * Nebobot/Trello-Telegram-Bot is free software; you can redistribute it and/or
 * modify it under the terms of the Mozilla Public License 2.0
 * published by the Mozilla Foundation.
 *
 * Nebobot/Trello-Telegram-Bot is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY.
 *
 * You should have received a copy of the Mozilla Public License 2.0
 * along with Nebobot/Trello-Telegram-Bot.
 * If not, see https://mozilla.org/en-US/MPL/2.0.
 *
 * Description: Main program. Regularly checks trello and reports events.
 * Version: 1.1
"""

import sys
if sys.version_info < (3, 9):
	print("[FATAL] Python 3.9 or newer is required!")
	sys.exit(1)
# # # #
import time
import traceback
import json
import requests

# # # #
from config import telegram_api_token, actions_api, chat_id, set_logging, delay

print(1)
def say(message, chat_id):
	""" A imprortant feature for sending messages to telegram by a bot """
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

# # # #

result_old = requests.get(actions_api, timeout=60).json()
if "old" not in result_old[0]["data"]:
	result_old[0]["data"]["old"] = {} # if not exists
# # # # # # # # # # # #

print("[#] Trello bot started..")
print("Delay: " + str(delay) + " sec")
while True:
	# # # # # # # # # #
	while True: # make error catching, retry request if error occurs
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


	# # # # # # # # # # # #
	if result_old[0] != result_new[0]:
		event_data = result_new[0]["data"]
		# # # # # # # # # # # # # # # # # # # # # # # # # # #
		if "card" not in event_data:
			pass

		# MOVING CARD #
		elif "listBefore" in event_data and "listAfter" in event_data:
			temp1 = event_data['card']['name'].replace("<", "&lt;").replace(">", "&gt;") # capitalize first letter
			temp1 = temp1[0].upper() + temp1[1:] # capitalize first letter

			say(f"""🗄️ <b>{temp1}</b>

				<code>{event_data['listBefore']['name']}</code> <b>-></b> <code>{event_data['listAfter']['name']}</code>""", chat_id)

		# RENAMING CARD #
		elif "name" in event_data["old"]:
			Old_name = event_data['old']['name']
			Name = event_data['card']['name']
			link = event_data['card']['shortLink']

			msg = f"""🗄️ Переименование карточки с состоянием {event_data['list']['name']}!

<i>{Old_name}</i>

<code>-= 🔽 🔽 🔽 =-</code>
				
<a href='https://trello.com/c/{link}'><b>{Name}</b></a>"""

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


		# ARCHIVING CARD #
		elif "closed" in event_data['card']:
			card_name = event_data['card']['name']
			link = event_data['card']['shortLink']
			msg = f'''🗑️ Задача <a href='https://trello.com/c/{link}'><i>{card_name}</i></a> <b>архивирована</b>'''
			say(msg, chat_id)


		# else:
		# 	say("❗ Новое событие на Trello.\nНо мне не удалось отобразить изменения.\n\n📃 Дополнительная инфомация была записана в unknown_events.log", chat_id)
		# 	with open("unknown_events.log", "w", encoding="utf-8") as f:
		# 		f.write("\n\n" + str(result_new[0]))
		# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	result_old = result_new
	time.sleep(delay)
