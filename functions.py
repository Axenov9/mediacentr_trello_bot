import time, datetime
import traceback
import json
import requests
import locale


from config import actions_api, chat_id, delay, BOARD_ID, exclude_lists_names
from trello_api_requests import *
def new_actions(new, old):
    actions = []
    for action in new:  # поиск всех новых действий для обработки
        if action not in old:
            actions.append(action)

    actions.reverse() # переворот массива, чтобы бот слал уведомления в прямом порядке действий
    return actions

def update_api(bot):

    result_old = get_actions_by_board(BOARD_ID)  # Первый запрос, чтобы впоследствие было с чем сравнивать
    # if "old" not in result_old[0]["data"]:
    #     result_old[0]["data"]["old"] = {}  # if not exists
    # # # # # # # # # #

    print("[#] Trello bot started..")
    print("Delay: " + str(delay) + " sec")
    while True:
        # # # # # # # # # #
        while True:
            try:
                result_new = get_actions_by_board(BOARD_ID) # запрос новых действий для сравнения со старыми
                break
            except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
                print("=== Exception caught!")
                print(traceback.format_exc())
                time.sleep(5)
        # # # # # # # # # #

        actions = new_actions(result_new, result_old)

        print(actions)

        for action in actions: # обработка каждого действия отдельно

            event = action
            event_data = action["data"]
            # # # # # # # # # # #

            # UPDATING CARD PARAMETERS #
            if event['type'] == 'updateCard':

                # RENAMING CARD #
                if "name" in event_data["old"]:
                    old_name = event_data['old']['name']
                    card_name = event_data['card']['name']
                    link = event_data['card']['shortLink']
                    msg = f'''Задача <i>{old_name}</i> переименована в <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>'''

                    bot.send_message(chat_id, msg, parse_mode='HTML')

                # MOVING CARD #
                elif "listBefore" in event_data and "listAfter" in event_data:
                    card_name = event_data['card']['name']
                    link = event_data['card']['shortLink']
                    lest_after = event_data['listAfter']['name']
                    msg = f"""Задача <a href='https://trello.com/c/{link}'><b>{card_name}</b></a> перемещена в <b>{lest_after}</b>"""

                    bot.send_message(chat_id, msg, parse_mode='HTML')

                # ARCHIVING CARD #
                elif "closed" in event_data['card']:
                    card_name = event_data['card']['name']
                    link = event_data['card']['shortLink']
                    msg = f'''🗑️ Задача <a href='https://trello.com/c/{link}'><i>{card_name}</i></a> <b>архивирована</b>'''

                    bot.send_message(chat_id, msg, parse_mode='HTML')

            # CREATING CARD #
            elif event["type"] == "createCard":
                card_name = event_data['card']['name']
                link = event_data['card']['shortLink']
                msg = f"""🔥 Добавлена новая задача - <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>"""

                bot.send_message(chat_id, msg, parse_mode='HTML')

            # ADDING MEMBER/LEAVING FROM CARD #
            elif event['type'] == 'addMemberToCard' or event['type'] == 'removeMemberFromCard':
                member = event_data['member']['name']
                card_name = event_data['card']['name']
                link = event_data['card']['shortLink']
                msg = f'''🔥 <b>{member}</b> {'взял(а)' if event['type'] == 'addMemberToCard' else 'бросил(а)'} задачу <a href='https://trello.com/c/{link}'><b>{card_name}</b></a>'''

                bot.send_message(chat_id, msg, parse_mode='HTML')

            # UPDATING CHECKLIST #
            elif event['type'] == 'updateCheckItemStateOnCard':
                checklist = get_checklist_by_id(event_data['checklist']['id'])
                card = event_data['card']

                msg = f'''Обновлен чек-лист {checklist["name"]} в <a href='trello.com/c/{card["shortLink"]}'><b>{card["name"]}</b></a>: \n\n'''
                for checkitem in checklist['checkItems']:
                    if checkitem['id'] == event_data['checkItem']['id']:
                        msg = msg + f'''{'✅' if checkitem['state'] == 'complete' else '❌'} <b>{checkitem['name']}</b> \n'''
                    else:
                        msg = msg + f'''{'✅' if checkitem['state'] == 'complete' else '❌'} {checkitem['name']} \n'''

                bot.send_message(chat_id, msg, parse_mode='HTML')

            # COMMENTING CARD #
            elif event['type'] == 'commentCard':

                if 'Готов к отправке' in event_data['text']:
                    delete_comment_by_action(event)
                    result_new.append(result_old[-1])
                    result_old.remove(result_old[-1])

                    # send_task ////




        # ANOTHER EVENT #
        # else:
        # 	msg = '<i>Неизвестное событие</i>'
        # 	bot.send_message(chat_id, msg, parse_mode='HTML')
        # # # # # # # #

        result_old = result_new
        time.sleep(delay)


def all_tasks(bot):
    locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
    msg = F'''📒 <i>Все задачи на данный момент:</i>

'''
    lists = get_lists_by_board(BOARD_ID)

    for list in lists:
        if not list["name"] in exclude_lists_names:
            msg = msg + f'''<b>{list["name"]}:</b>
'''
            cards = get_cards_by_list(list['id'])

            for card_raw in cards:
                card = get_card_by_id(card_raw['shortLink'])
                msg = msg + f'''- <a href='https://trello.com/c/{card_raw['shortLink']}'>{card["name"]}</a> - {datetime.datetime.strptime(card['start'].split('T')[0], '%Y-%m-%d').strftime('%d %b') if card["start"] else 'время не назначено'}
'''
            msg = msg + '''
'''
    return msg