import requests
from config import TRELLO_API_KEY, TRELLO_API_TOKEN

params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_API_TOKEN
}

def get_actions_by_board(board_id):
    actions_api = f"https://api.trello.com/1/boards/{board_id}/actions"
    actions = requests.get(actions_api, params=params, timeout=60).json()

    return  actions

def get_lists_by_board(board_id):
    boards_api = f"https://api.trello.com/1/boards/{board_id}/lists"
    lists = requests.get(boards_api, params=params, timeout=60).json()

    return lists

def get_cards_by_list(list_id):
    lists_api = f"https://api.trello.com/1/lists/{list_id}/cards"
    cards = requests.get(lists_api, params=params, timeout=60).json()

    return cards

def get_card_by_id(card_id):
    cards_api = f"https://api.trello.com/1/cards/{card_id}"
    card = requests.get(cards_api, params=params, timeout=60).json()

    return card

def get_checklist_by_id(checklist_id):
    checklists_api = f"https://api.trello.com/1/checklists/{checklist_id}"
    checklist = requests.get(checklists_api, params=params, timeout=60).json()

    return checklist

def delete_comment_by_action(action):
    action_id = action['id']
    card_id = action['data']['card']['id']
    url = f"https://api.trello.com/1/cards/{card_id}/actions/{action_id}/comments"
    result = requests.delete(url, params=params, timeout=60)

    return