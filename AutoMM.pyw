import json
import os
import random
import threading as th
from base64 import b64encode
from time import sleep

import PySimpleGUI as sg
import requests
import urllib3

config = None
rolePriority = None
queueId = 0

dropdown_number = 0
num_dropdowns = 30

gui_created = False

gui_config_update = False

protocol = 0
host = '127.0.0.1'
port = 0
username = 'riot'
headers = 0
s = 0

threadLock = th.Lock()

threads = {}
kill = False
changed = False
killed = False

role = {"sup": "UTILITY", "mid": "MIDDLE", "bot": "BOTTOM", "top": "TOP", "jungle": "JUNGLE", "fill": "FILL",
        "random": "random"}
randomRole = ["UTILITY", "MIDDLE", "BOTTOM", "TOP", "JUNGLE"]
roleName = {}
roleChanged = True

queues = {"Draft Pick": "400", "Solo/Duo": "420", "Blind Pick": "430", "Flex": "440", "Aram": "450",
          "TFT Normal": "1090", "TFT Ranked": "1100", "TFT Hyperroll": "1130"}
drafts = ["Draft Pick", "Solo/Duo", "Flex"]

champions = {"Annie": "1", "Olaf": "2", "Galio": "3", "Twisted Fate": "4", "Xin Zhao": "5", "Urgot": "6",
             "LeBlanc": "7", "Vladimir": "8", "Fiddlesticks": "9", "Kayle": "10", "Master Yi": "11", "Alistar": "12",
             "Ryze": "13", "Sion": "14", "Sivir": "15", "Soraka": "16", "Teemo": "17", "Tristana": "18",
             "Warwick": "19", "Nunu": "20", "Miss Fortune": "21", "Ashe": "22", "Tryndamere": "23", "Jax": "24",
             "Morgana": "25", "Zilean": "26", "Singed": "27", "Evelynn": "28", "Twitch": "29", "Karthus": "30",
             "ChoGath": "31", "Amumu": "32", "Rammus": "33", "Anivia": "34", "Shaco": "35", "Dr. Mundo": "36",
             "Sona": "37", "Kassadin": "38", "Irelia": "39", "Janna": "40", "Gangplank": "41", "Corki": "42",
             "Karma": "43", "Taric": "44", "Veigar": "45", "Trundle": "48", "Swain": "50", "Caitlyn": "51",
             "Blitzcrank": "53", "Malphite": "54", "Katarina": "55", "Nocturne": "56", "Maokai": "57", "Renekton": "58",
             "Jarvan IV": "59", "Elise": "60", "Orianna": "61", "Wukong": "62", "Brand": "63", "Lee Sin": "64",
             "Vayne": "67", "Rumble": "68", "Cassiopeia": "69", "Skarner": "72", "Heimerdinger": "74", "Nasus": "75",
             "Nidalee": "76", "Udyr": "77", "Poppy": "78", "Gragas": "79", "Pantheon": "80", "Ezreal": "81",
             "Mordekaiser": "82", "Yorick": "83", "Akali": "84", "Kennen": "85", "Garen": "86", "Leona": "89",
             "Malzahar": "90", "Talon": "91", "Riven": "92", "KogMaw": "96", "Shen": "98", "Lux": "99", "Xerath": "101",
             "Shyvana": "102", "Ahri": "103", "Graves": "104", "Fizz": "105", "Volibear": "106", "Rengar": "107",
             "Varus": "110", "Nautilus": "111", "Viktor": "112", "Sejuani": "113", "Fiora": "114", "Ziggs": "115",
             "Lulu": "117", "Draven": "119", "Hecarim": "120", "KhaZix": "121", "Darius": "122", "Jayce": "126",
             "Lissandra": "127", "Diana": "131", "Quinn": "133", "Syndra": "134", "Aurelion Sol": "136", "Kayn": "141",
             "Zoe": "142", "Zyra": "143", "KaiSa": "145", "Seraphine": "147", "Gnar": "150", "Zac": "154",
             "Yasuo": "157", "VelKoz": "161", "Taliyah": "163", "Camille": "164", "Akshan": "166", "Braum": "201",
             "Jhin": "202", "Kindred": "203", "Jinx": "222", "Tahm Kench": "223", "Viego": "234", "Senna": "235",
             "Lucian": "236", "Zed": "238", "Kled": "240", "Ekko": "245", "Qiyana": "246", "Vi": "254", "Aatrox": "266",
             "Nami": "267", "Azir": "268", "Yuumi": "350", "Samira": "360", "Thresh": "412", "Illaoi": "420",
             "Sylas": "517", "Neeko": "518", "Aphelios": "523", "Rell": "526", "Pyke": "555", "Vex": "711",
             "Yone": "777", "Sett": "875", "Lillia": "876", "Gwen": "887"}
championNames = []
num_champions = 0
for championName in champions.keys():
    championNames.append(championName)
    num_champions += 1
if num_champions < num_dropdowns:
    num_dropdowns = num_champions
championNames = sorted(championNames, key=str.lower)

banPriority = {}
pickPriority = {}

lastPhase = ""
phase = ""

defaultConfig = '{"roles":["top", "mid"], "dir":"C://Riot Games//League of Legends", "queue":"Solo/Duo", ' \
                '"autoPick":false, "autoBan":false, "banPrio":{"mid":["Yasuo", "Yone"],"top":[],"jungle":[],' \
                '"sup":[],"bot":[]}, "pickPrio":{"mid":[],"top":[],"jungle":[],"sup":[],"bot":[]}}'


def initialize():
    global config
    global rolePriority
    global queueId
    global threadLock
    global gui_created
    global gui_config_update
    global banPriority

    file = open('config.json', 'a+')

    if os.path.getsize('config.json') == 0:
        file.write(defaultConfig)
        file.close()
        gui_config_update = True
        with open('config.json', 'r') as f:
            config = json.load(f)
    else:
        file.close()
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            config_file = open('config.json', 'w')
            config_file.write(defaultConfig)
            config_file.close()
            gui_config_update = True
            with open('config.json', 'r') as f:
                config = json.load(f)

    for key in role:
        roleName[role[key].lower()] = key

    try:
        gui_config_update = False

        if config['roles'][0] == "fill" and config['roles'][1] != "fill":
            config['roles'][1] = "fill"
            gui_config_update = True

        if config['roles'][0] == "random" and config['roles'][1] != "random":
            config['roles'][1] = "random"
            gui_config_update = True

        keys = list(role.keys())

        if config['roles'][0] not in keys:
            if config['roles'][1] != "mid":
                config['roles'][0] = "mid"
            else:
                config['roles'][0] = "top"
            gui_config_update = True

        if config['roles'][1] not in keys:
            if config['roles'][0] != "mid":
                config['roles'][1] = "mid"
            else:
                config['roles'][1] = "top"
            gui_config_update = True

        rolePriority = [
            role[config['roles'][0]],
            role[config['roles'][1]]
        ]
    except:
        config['roles'] = []
        config['roles'][0] = "mid"
        config['roles'][1] = "top"
        gui_config_update = True
        rolePriority = [
            role[config['roles'][0]],
            role[config['roles'][1]]
        ]

    if 'queue' not in config:
        config['queue'] = "Solo/Duo"
    queueId = queues[config['queue']]

    if 'autoBan' in config:
        if config['autoBan']:
            if 'banPrio' not in config:
                config['banPrio'] = {}
                gui_config_update = True
            if 'top' not in config['banPrio']:
                config['banPrio']['top'] = []
                gui_config_update = True
            if 'mid' not in config['banPrio']:
                config['banPrio']['mid'] = []
                gui_config_update = True
            if 'bot' not in config['banPrio']:
                config['banPrio']['bot'] = []
                gui_config_update = True
            if 'sup' not in config['banPrio']:
                config['banPrio']['sup'] = []
                gui_config_update = True
            if 'jungle' not in config['banPrio']:
                config['banPrio']['jungle'] = []
                gui_config_update = True
            banPriority = config['banPrio']
    else:
        config['autoBan'] = False
        gui_config_update = True

    if gui_config_update:
        json.dump('config.json', config)
        if not gui_created:
            gui_config_update = False

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def request(method, path, query='', data=None):
    global protocol
    global host
    global port
    global headers
    global s

    if not query:
        url = '%s://%s:%s%s' % (protocol, host, port, path)
    else:
        url = '%s://%s:%s%s?%s' % (protocol, host, port, path, query)

    fn = getattr(s, method)

    if not data:
        return_value = fn(url, verify=False, headers=headers)
    else:
        return_value = fn(url, verify=False, headers=headers, json=data)

    return return_value


def get_pick_priority():
    global pickPriority
    global champions
    global config
    global gui_config_update
    global threadLock

    try:
        available_champs = request('get', '/lol-champions/v1/owned-champions-minimal').json()
    except:
        return False
    if 'pickPrio' not in config:
        config['pickPrio'] = {}
        gui_config_update = True
    if 'top' not in config['pickPrio']:
        config['pickPrio']['top'] = []
        gui_config_update = True
    if 'mid' not in config['pickPrio']:
        config['pickPrio']['mid'] = []
        gui_config_update = True
    if 'bot' not in config['pickPrio']:
        config['pickPrio']['bot'] = []
        gui_config_update = True
    if 'sup' not in config['pickPrio']:
        config['pickPrio']['sup'] = []
        gui_config_update = True
    if 'jungle' not in config['pickPrio']:
        config['pickPrio']['jungle'] = []
        gui_config_update = True
    for position in list(config['pickPrio'].keys()):
        pickPriority[position] = []
        for champion_name in config['pickPrio'][position]:
            for aChamp in available_champs:
                try:
                    if int(aChamp['id']) == int(champions[champion_name]):
                        if aChamp['rankedPlayEnabled']:
                            pickPriority[position].append(aChamp['id'])
                except:
                    return False
    threadLock.acquire()
    if gui_config_update:
        json.dump('config.json', config)
    threadLock.release()
    return True


def get_role():
    local_lobby = request('get', '/lol-lobby/v2/lobby').json()
    local_lobby = local_lobby['localMember']

    if local_lobby['firstPositionPreference'] == rolePriority[0]:
        if local_lobby['secondPositionPreference'] == rolePriority[1]:
            return 1
        else:
            return 0
    else:
        return 0


def set_role():
    request('put', '/lol-lobby/v2/lobby/members/localMember/position-preferences', '',
            {"firstPreference": rolePriority[0], "secondPreference": rolePriority[1]})


def leader():
    ps = request('get', '/lol-gameflow/v1/gameflow-metadata/player-status').json()
    return ps["currentLobbyStatus"]["isLeader"]


def exists_search_error():
    state = request('get', '/lol-lobby/v2/lobby/matchmaking/search-state').json()

    if state['errors']:
        return True

    return False


def search():
    request('post', '/lol-lobby/v2/lobby/matchmaking/search')


def get_queue_id():
    queue_id = request('get', '/lol-lobby/v2/lobby').json()
    return queue_id['gameConfig']['queueId']


def lobby():
    global drafts
    global config

    if get_role() == 0 and config['queue'] in drafts:
        set_role()
    else:
        if leader() == 1:
            if not exists_search_error():
                search()


def queue():
    global queueId

    request('post', '/lol-lobby/v2/lobby', '', {"queueId": queueId})


def ready_check():
    request('post', '/lol-matchmaking/v1/ready-check/accept')


def get_cell_id():
    session = request('get', '/lol-champ-select/v1/session').json()
    return session['localPlayerCellId']


def get_phase():
    session = request('get', '/lol-champ-select/v1/session').json()

    for actions in session['actions']:
        for action in actions:
            if action['isInProgress']:
                return action['type']

    return False


def get_position(cell_id):
    session = request('get', '/lol-champ-select/v1/session').json()

    for player in session['myTeam']:
        if player['cellId'] == cell_id:
            return player['assignedPosition']

    return False


def get_ban_action_slot(cell_id):
    session = request('get', '/lol-champ-select/v1/session').json()
    for actions in session['actions']:
        for action in actions:
            if action['actorCellId'] == cell_id:
                if action['type'] == "ban":
                    if action['isInProgress'] and not action['completed']:
                        return action['id']

    return False


def get_ban(position):
    global banPriority

    priority = []

    if position:
        priority = banPriority[roleName[position.lower()]]

    session = request('get', '/lol-champ-select/v1/session').json()

    bans = []

    for action in session['actions'][0]:
        if action['completed']:
            bans.append(action['championId'])

    for champion_id in priority:
        if champion_id not in bans:
            return champion_id

    return False


def ban(champion_id, action_slot):
    url = '/lol-champ-select/v1/session/actions/%d' % action_slot
    data = {'championId': champion_id}
    sleep(0.1)
    request('patch', url, '', data)
    sleep(0.1)
    request('post', url + '/complete', '', data)


def get_pick_action_slot(cell_id):
    session = request('get', '/lol-champ-select/v1/session').json()

    for actions in session['actions']:
        for action in actions:
            if action['actorCellId'] == cell_id:
                if action['type'] == "pick":
                    if action['isInProgress'] and not action['completed']:
                        return action['id']

    return False


def get_pick(position):
    global pickPriority

    priority = []

    if position:
        priority = pickPriority[roleName[position.lower()]]

    session = request('get', '/lol-champ-select/v1/session').json()

    not_available = []

    for actions in session['actions']:
        for action in actions:
            if action['completed']:
                not_available.append(action['championId'])

    for champion_id in priority:
        if champion_id not in not_available:
            return champion_id

    return False


def pick(pick_id, action_slot):
    url = '/lol-champ-select/v1/session/actions/%d' % action_slot
    data = {'championId': pick_id}
    sleep(0.1)
    request('patch', url, '', data)
    sleep(0.1)
    request('post', url + '/complete', '', data)


def pick_ban():
    global config
    global threadLock
    global s

    current_phase = get_phase()

    if current_phase:
        cell_id = get_cell_id()
        if cell_id != -1:
            position = get_position(cell_id)
            if current_phase == "ban" and config['autoBan']:
                action_slot = get_ban_action_slot(cell_id)
                if action_slot:
                    champion_ban_id = get_ban(position)
                    if champion_ban_id:
                        ban(champion_ban_id, action_slot)
            elif current_phase == "pick" and config['autoPick']:
                action_slot = get_pick_action_slot(cell_id)
                if action_slot:
                    champion_pick_id = get_pick(position)
                    if champion_pick_id:
                        pick(champion_pick_id, action_slot)


def routine():
    global kill
    global killed
    global threadLock
    global lastPhase
    global phase
    global rolePriority
    global randomRole
    global queueId

    while True:
        try:
            session = request('get', '/lol-login/v1/session')
        except:
            threadLock.acquire()
            killed = True
            kill = False
            threadLock.release()
            sleep(0.1)
            return

        if session.status_code != 200:
            threadLock.acquire()
            killed = True
            kill = False
            threadLock.release()
            sleep(0.1)
            return

        if session.json()['state'] == 'SUCCEEDED':
            break
        else:
            threadLock.acquire()
            killed = True
            kill = False
            threadLock.release()
            sleep(0.1)
            return

    try:
        session.json()['summonerId']
    except:
        threadLock.acquire()
        killed = True
        kill = False
        threadLock.release()
        sleep(0.1)
        return

    if 'autoPick' in config:
        if config['autoPick']:
            priority = False
            while not priority:
                priority = get_pick_priority()
    else:
        config['autoPick'] = False

    if config["roles"][0] == "random":
        pos = random.randint(0, 4)
        rolePriority[0] = randomRole[pos]
        pos2 = pos
        while pos2 == pos:
            pos2 = random.randint(0, 4)
        rolePriority[1] = randomRole[pos2]

    try:
        session = request('get', '/lol-gameflow/v1/gameflow-phase')
        if session.status_code != 200:
            raise
    except:
        threadLock.acquire()
        killed = True
        kill = False
        threadLock.release()
        sleep(0.1)
        return

    threadLock.acquire()

    while not kill:
        threadLock.release()

        try:
            session = request('get', '/lol-gameflow/v1/gameflow-phase')

            if session.status_code != 200:
                threadLock.acquire()
                continue

            phase = session.json()

            if phase == "ReadyCheck":
                ready_check()

            elif phase == 'ChampSelect':
                pick_ban()

            elif phase == "None" or phase == "EndOfGame" or (phase == 'Lobby' and int(get_queue_id()) != int(queueId)):
                queue()

            elif phase == 'Lobby':
                lobby()

            elif phase == 'InProgress':
                sleep(0.5)

            lastPhase = phase

        except:
            threadLock.acquire()
            killed = True
            kill = False
            threadLock.release()
            sleep(0.1)
            return

        sleep(0.1)
        threadLock.acquire()

    kill = False
    killed = False
    threadLock.release()
    sleep(0.1)
    return


def main():
    global kill
    global killed
    global protocol
    global username
    global port
    global headers
    global threadLock
    global s
    global threads
    global config
    global changed
    global gui_config_update

    threadLock.acquire()

    while not changed:
        threadLock.release()
        lockfile = None
        path = None
        threadLock.acquire()

        while not lockfile and not changed:
            threadLock.release()
            path = r'%s\lockfile' % config["dir"]
            threadLock.acquire()

            try:
                if os.path.isfile(path):
                    lockfile = open(r'%s\lockfile' % config["dir"], 'r')
                    break
            except:
                config["dir"] = "C://Riot Games//League of Legends"
                gui_config_update = True
                json.dump('config.json', config)
            sleep(0.1)
        threadLock.release()

        if changed:
            threadLock.acquire()
            changed = False
            threadLock.release()
            sleep(0.1)
            return

        try:
            data = lockfile.read()
            lockfile.close()
            lock = data.split(':')
            port = lock[2]
            password = lock[3]
            protocol = lock[4]
            user = b64encode(bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')
            headers = {'Authorization': 'Basic %s' % user}
            s = requests.session()
        except:
            sleep(0.1)
            threadLock.acquire()
            continue

        threads[1] = th.Thread(target=routine)
        threads[1].start()

        while True:
            threadLock.acquire()
            if killed:
                killed = False
                threadLock.release()
                sleep(0.2)
                break
            elif not os.path.isfile(path) or changed:
                kill = True
                threadLock.release()
                threads[1].join()
                break
            threadLock.release()
            sleep(0.1)
        threadLock.acquire()
        killed = False
        kill = False

    changed = False
    threadLock.release()
    sleep(0.1)
    return


def create_dropdown(number):
    return [sg.Drop(values=[], default_value='', size=(10, 5), key="dropdown" + str(number), auto_size_text=False,
                    readonly=True, enable_events=True)]


def create_dropdowns():
    global dropdown_number
    global num_dropdowns
    global num_champions
    dropdowns = []

    for i in range(num_dropdowns):
        dropdown = create_dropdown(i + (dropdown_number * num_champions))
        dropdowns.append(dropdown)

    dropdown_number += 1

    return dropdowns


def create_gui():
    global config
    global championNames
    global roleName
    global rolePriority
    global gui_created

    sg.theme("DarkAmber")
    sg.SetOptions(text_justification='right')
    threadLock.acquire()

    layout_bans = [[sg.Text('Toplane', size=(10, 1)),
                    sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                               size=(12, 6), key='_BANS_TOPLANE_', default_values=config['banPrio']['top']),
                    sg.VSeparator(),
                    sg.Text('Midlane', size=(10, 1)),
                    sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                               size=(12, 6), key='_BANS_MIDLANE_', default_values=config['banPrio']['mid'])],
                   [sg.Text('ADC', size=(10, 1)),
                    sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                               size=(12, 6), key='_BANS_ADC_', default_values=config['banPrio']['bot']),
                    sg.VSeparator(),
                    sg.Text('Support', size=(10, 1)),
                    sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                               size=(12, 6), key='_BANS_SUPPORT_', default_values=config['banPrio']['sup'])],
                   [sg.Text('Jungle', size=(10, 1)),
                    sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                               size=(12, 6), key='_BANS_JUNGLE_', default_values=config['banPrio']['jungle'])]]

    layout_order_bans = [[sg.Text('Toplane', size=(10, 1)),
                          sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110)),
                          sg.VSeparator(),
                          sg.Text('Midlane', size=(10, 1)),
                          sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))],
                         [sg.Text('ADC', size=(10, 1)),
                          sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110)),
                          sg.VSeparator(),
                          sg.Text('Support', size=(10, 1)),
                          sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))],
                         [sg.Text('Jungle', size=(10, 1)),
                          sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))]
                         ]

    layout_picks = [[sg.Text('Toplane', size=(10, 1)),
                     sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                                size=(12, 6), key='_PICKS_TOPLANE_', default_values=config['pickPrio']['top']),
                     sg.VSeparator(),
                     sg.Text('Midlane', size=(10, 1)),
                     sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                                size=(12, 6), key='_PICKS_MIDLANE_', default_values=config['pickPrio']['mid'])],
                    [sg.Text('ADC', size=(10, 1)),
                     sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                                size=(12, 6), key='_PICKS_ADC_', default_values=config['pickPrio']['bot']),
                     sg.VSeparator(),
                     sg.Text('Support', size=(10, 1)),
                     sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                                size=(12, 6), key='_PICKS_SUPPORT_', default_values=config['pickPrio']['sup'])],
                    [sg.Text('Jungle', size=(10, 1)),
                     sg.Listbox(values=championNames, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True,
                                size=(12, 6), key='_PICKS_JUNGLE_', default_values=config['pickPrio']['jungle'])]]

    layout_order_picks = [[sg.Text('Toplane', size=(10, 1)),
                           sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110)),
                           sg.VSeparator(),
                           sg.Text('Midlane', size=(10, 1)),
                           sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))],
                          [sg.Text('ADC', size=(10, 1)),
                           sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110)),
                           sg.VSeparator(),
                           sg.Text('Support', size=(10, 1)),
                           sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))],
                          [sg.Text('Jungle', size=(10, 1)),
                           sg.Col(create_dropdowns(), scrollable=True, vertical_scroll_only=True, size=(95, 110))]
                          ]

    layout = [[sg.Text('League Path'),
               sg.Input(default_text=config["dir"], key='_INPUT_', justification="left")],
              [sg.Text('Roles'),
               sg.Drop(values=list(roleName.values()),
                       default_value=roleName[rolePriority[0].lower()], size=(10, 1), key="role1", auto_size_text=False,
                       readonly=True, enable_events=True),
               sg.Drop(values=list(roleName.values()),
                       default_value=roleName[rolePriority[1].lower()], size=(10, 1), key="role2", auto_size_text=False,
                       readonly=True, enable_events=True)],
              [sg.Text('Queue'),
               sg.Drop(values=list(queues.keys()), default_value=config['queue'], size=(10, 1), key="queue",
                       auto_size_text=False, readonly=True)],
              [sg.HSeparator()],
              [sg.Text(text='Bans', font=('Helvetica', 16)),
               sg.Checkbox('', default=config['autoBan'], key="_BANS_")],
              [sg.TabGroup([[sg.Tab('Choose Bans', layout_bans, key="_TAB_BANS_"),
                             sg.Tab('Order Bans', layout_order_bans, key="_TAB_ORDER_BANS_")]], enable_events=True,
                           key="_TABGROUP_BANS_")],
              [sg.HSeparator()],
              [sg.Text(text='Picks', font=('Helvetica', 16)),
               sg.Checkbox('', default=config['autoPick'], key="_PICKS_")],
              [sg.TabGroup([[sg.Tab('Choose Picks', layout_picks, key="_TAB_PICKS_"),
                             sg.Tab('Order Picks', layout_order_picks, key="_TAB_ORDER_PICKS_")]], enable_events=True,
                           key="_TABGROUP_PICKS_")],
              [sg.Submit(), sg.Button("Start", enable_events=True, key="start"), sg.Button("Stop", enable_events=True,
                                                                                           key="stop")]]

    window = sg.Window('Auto Matchmaking - League of Legends', layout)

    gui_created = True

    threadLock.release()

    return window


def gui(window):
    global threads
    global changed
    global config
    global num_champions
    global championNames
    global gui_config_update
    roles = [roleName[rolePriority[0].lower()], roleName[rolePriority[1].lower()]]
    dropdown_data = [''] * (num_champions * 10)
    started = False

    while True:
        event, values = window_handle.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            threadLock.acquire()
            changed = True
            threadLock.release()
            window.close()
            if started:
                threads[0].join()
            return
        elif event == 'Submit':
            threadLock.acquire()
            if started:
                changed = True
                threadLock.release()
                threads[0].join()
            else:
                threadLock.release()
            config['dir'] = values['_INPUT_']
            config['roles'] = [values['role1'], values['role2']]
            config['queue'] = values['queue']

            if values['_BANS_']:
                config['autoBan'] = True
            else:
                config['autoBan'] = False

            if values['_PICKS_']:
                config['autoPick'] = True
            else:
                config['autoPick'] = False

            if values['_TABGROUP_BANS_'] == '_TAB_ORDER_BANS_':
                config['banPrio']['top'] = []
                i = 0
                for _ in values['_BANS_TOPLANE_']:
                    if i == num_dropdowns:
                        break
                    config['banPrio']['top'].append(values['dropdown' + str(i)])
                    i += 1

                config['banPrio']['mid'] = []
                i = num_champions
                for _ in values['_BANS_MIDLANE_']:
                    if i == num_dropdowns + num_champions:
                        break
                    config['banPrio']['mid'].append(values['dropdown' + str(i)])
                    i += 1

                config['banPrio']['bot'] = []
                i = num_champions * 2
                for _ in values['_BANS_ADC_']:
                    if i == num_dropdowns + (num_champions * 2):
                        break
                    config['banPrio']['bot'].append(values['dropdown' + str(i)])
                    i += 1

                config['banPrio']['sup'] = []
                i = num_champions * 3
                for _ in values['_BANS_SUPPORT_']:
                    if i == num_dropdowns + (num_champions * 3):
                        break
                    config['banPrio']['sup'].append(values['dropdown' + str(i)])
                    i += 1

                config['banPrio']['jungle'] = []
                i = num_champions * 4
                for _ in values['_BANS_JUNGLE_']:
                    if i == num_dropdowns + (num_champions * 4):
                        break
                    config['banPrio']['jungle'].append(values['dropdown' + str(i)])
                    i += 1
            else:
                ban_priority_top = config['banPrio']['top']
                config['banPrio']['top'] = []
                for champion in ban_priority_top:
                    if champion in values['_BANS_TOPLANE_']:
                        config['banPrio']['top'].append(champion)
                for champion in values['_BANS_TOPLANE_']:
                    if champion not in ban_priority_top:
                        config['banPrio']['top'].append(champion)

                ban_priority_mid = config['banPrio']['mid']
                config['banPrio']['mid'] = []
                for champion in ban_priority_mid:
                    if champion in values['_BANS_MIDLANE_']:
                        config['banPrio']['mid'].append(champion)
                for champion in values['_BANS_MIDLANE_']:
                    if champion not in ban_priority_mid:
                        config['banPrio']['mid'].append(champion)

                ban_priority_bot = config['banPrio']['bot']
                config['banPrio']['bot'] = []
                for champion in ban_priority_bot:
                    if champion in values['_BANS_ADC_']:
                        config['banPrio']['bot'].append(champion)
                for champion in values['_BANS_ADC_']:
                    if champion not in ban_priority_bot:
                        config['banPrio']['bot'].append(champion)

                ban_priority_sup = config['banPrio']['sup']
                config['banPrio']['sup'] = []
                for champion in ban_priority_sup:
                    if champion in values['_BANS_SUPPORT_']:
                        config['banPrio']['sup'].append(champion)
                for champion in values['_BANS_SUPPORT_']:
                    if champion not in ban_priority_sup:
                        config['banPrio']['sup'].append(champion)

                ban_priority_jungle = config['banPrio']['jungle']
                config['banPrio']['jungle'] = []
                for champion in ban_priority_jungle:
                    if champion in values['_BANS_JUNGLE_']:
                        config['banPrio']['jungle'].append(champion)
                for champion in values['_BANS_JUNGLE_']:
                    if champion not in ban_priority_jungle:
                        config['banPrio']['jungle'].append(champion)

            if values['_TABGROUP_BANS_'] == '_TAB_ORDER_BANS_':
                config['pickPrio']['top'] = []
                i = num_champions * 5
                for _ in values['_PICKS_TOPLANE_']:
                    if i == num_dropdowns + (num_champions * 5):
                        break
                    config['pickPrio']['top'].append(values['dropdown' + str(i)])
                    i += 1

                config['pickPrio']['mid'] = []
                i = num_champions * 6
                for _ in values['_PICKS_MIDLANE_']:
                    if i == num_dropdowns + (num_champions * 6):
                        break
                    config['pickPrio']['mid'].append(values['dropdown' + str(i)])
                    i += 1

                config['pickPrio']['bot'] = []
                i = num_champions * 7
                for _ in values['_PICKS_ADC_']:
                    if i == num_dropdowns + (num_champions * 7):
                        break
                    config['pickPrio']['bot'].append(values['dropdown' + str(i)])
                    i += 1

                config['pickPrio']['sup'] = []
                i = num_champions * 8
                for _ in values['_PICKS_SUPPORT_']:
                    if i == num_dropdowns + (num_champions * 8):
                        break
                    config['pickPrio']['sup'].append(values['dropdown' + str(i)])
                    i += 1

                config['pickPrio']['jungle'] = []
                i = num_champions * 9
                for _ in values['_PICKS_JUNGLE_']:
                    if i == num_dropdowns + (num_champions * 9):
                        break
                    config['pickPrio']['jungle'].append(values['dropdown' + str(i)])
                    i += 1
            else:
                pick_priority_top = config['pickPrio']['top']
                config['pickPrio']['top'] = []
                for champion in pick_priority_top:
                    if champion in values['_PICKS_TOPLANE_']:
                        config['pickPrio']['top'].append(champion)
                for champion in values['_PICKS_TOPLANE_']:
                    if champion not in pick_priority_top:
                        config['pickPrio']['top'].append(champion)

                pick_priority_mid = config['pickPrio']['mid']
                config['pickPrio']['mid'] = []
                for champion in pick_priority_mid:
                    if champion in values['_PICKS_MIDLANE_']:
                        config['pickPrio']['mid'].append(champion)
                for champion in values['_PICKS_MIDLANE_']:
                    if champion not in pick_priority_mid:
                        config['pickPrio']['mid'].append(champion)

                pick_priority_bot = config['pickPrio']['bot']
                config['pickPrio']['bot'] = []
                for champion in pick_priority_bot:
                    if champion in values['_PICKS_ADC_']:
                        config['pickPrio']['bot'].append(champion)
                for champion in values['_PICKS_ADC_']:
                    if champion not in pick_priority_bot:
                        config['pickPrio']['bot'].append(champion)

                pick_priority_sup = config['pickPrio']['sup']
                config['pickPrio']['sup'] = []
                for champion in pick_priority_sup:
                    if champion in values['_PICKS_SUPPORT_']:
                        config['pickPrio']['sup'].append(champion)
                for champion in values['_PICKS_SUPPORT_']:
                    if champion not in pick_priority_sup:
                        config['pickPrio']['sup'].append(champion)

                pick_priority_jungle = config['pickPrio']['jungle']
                config['pickPrio']['jungle'] = []
                for champion in pick_priority_jungle:
                    if champion in values['_PICKS_JUNGLE_']:
                        config['pickPrio']['jungle'].append(champion)
                for champion in values['_PICKS_JUNGLE_']:
                    if champion not in pick_priority_jungle:
                        config['pickPrio']['jungle'].append(champion)

            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)

            initialize()
            if gui_config_update:

                index_list = []
                for champion in config['banPrio']['top']:
                    index_list.append(championNames.index(champion))
                window['_BANS_TOPLANE_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['banPrio']['mid']:
                    index_list.append(championNames.index(champion))
                window['_BANS_MIDLANE_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['banPrio']['bot']:
                    index_list.append(championNames.index(champion))
                window['_BANS_ADC_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['banPrio']['sup']:
                    index_list.append(championNames.index(champion))
                window['_BANS_SUPPORT_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['banPrio']['jungle']:
                    index_list.append(championNames.index(champion))
                window['_BANS_JUNGLE_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['pickPrio']['top']:
                    index_list.append(championNames.index(champion))
                window['_PICKS_TOPLANE_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['pickPrio']['mid']:
                    index_list.append(championNames.index(champion))
                window['_PICKS_MIDLANE_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['pickPrio']['bot']:
                    index_list.append(championNames.index(champion))
                window['_PICKS_ADC_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['pickPrio']['sup']:
                    index_list.append(championNames.index(champion))
                window['_PICKS_SUPPORT_'].Update(set_to_index=index_list)

                index_list = []
                for champion in config['pickPrio']['jungle']:
                    index_list.append(championNames.index(champion))
                window['_PICKS_JUNGLE_'].Update(set_to_index=index_list)

            threadLock.acquire()
            if started:
                threadLock.release()
                threads[0] = th.Thread(target=main)
                threads[0].start()
            else:
                threadLock.release()
        elif (event == '_TABGROUP_BANS_' and values['_TABGROUP_BANS_'] == '_TAB_ORDER_BANS_') or (
                event == '_TABGROUP_PICKS_' and values['_TABGROUP_PICKS_'] == '_TAB_ORDER_PICKS_'):
            i = 0
            for champion in config['banPrio']['top']:
                if i == num_dropdowns:
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_BANS_TOPLANE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < num_dropdowns:
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions
            for champion in config['banPrio']['mid']:
                if i == (num_champions + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_BANS_MIDLANE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < (num_champions + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 2
            for champion in config['banPrio']['bot']:
                if i == ((num_champions * 2) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_BANS_ADC_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 2) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 3
            for champion in config['banPrio']['sup']:
                if i == ((num_champions * 3) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_BANS_SUPPORT_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 3) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 4
            for champion in config['banPrio']['jungle']:
                if i == ((num_champions * 4) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_BANS_JUNGLE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 4) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 5
            for champion in config['pickPrio']['top']:
                if i == ((num_champions * 5) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_PICKS_TOPLANE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 5) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 6
            for champion in config['pickPrio']['mid']:
                if i == ((num_champions * 6) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_PICKS_MIDLANE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 6) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 7
            for champion in config['pickPrio']['bot']:
                if i == ((num_champions * 7) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_PICKS_ADC_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 7) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 8
            for champion in config['pickPrio']['sup']:
                if i == ((num_champions * 8) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_PICKS_SUPPORT_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 8) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1

            i = num_champions * 9
            for champion in config['pickPrio']['jungle']:
                if i == ((num_champions * 9) + num_dropdowns):
                    break
                window['dropdown' + str(i)].Update(visible=True, values=values['_PICKS_JUNGLE_'], value=champion)
                dropdown_data[i] = champion
                i += 1
            while i < ((num_champions * 9) + num_dropdowns):
                window['dropdown' + str(i)].Update(visible=False)
                i += 1
        elif event == "role1":
            if values['role1'] != 'fill' and values['role1'] != 'random':
                if values['role1'] == values['role2']:
                    values['role2'] = roles[0]
            elif values['role1'] == 'fill':
                values['role2'] = 'fill'

            roles[0] = values['role1']
            roles[1] = values['role2']
            window['role1'].Update(value=roles[0])
            window['role2'].Update(value=roles[1])
        elif event == 'role2':
            if values['role1'] == 'fill':
                values['role2'] = 'fill'
            elif values['role2'] != 'fill' and values['role2'] != 'random' and values['role1'] == values['role2']:
                values['role1'] = roles[1]

            roles[0] = values['role1']
            roles[1] = values['role2']
            window['role1'].Update(value=roles[0])
            window['role2'].Update(value=roles[1])
        elif "dropdown" in event:
            for i in range(10):
                number = int(''.join(filter(str.isdigit, event)))
                if number < ((i + 1) * num_champions):
                    for j in range(num_dropdowns):
                        if (j + (i * num_champions)) != number:
                            if values['dropdown' + str((j + (i * num_champions)))] == values[event]:
                                window['dropdown' + str((j + (i * num_champions)))].Update(value=dropdown_data[number])
                                dropdown_data[(j + (i * num_champions))] = dropdown_data[number]
                                dropdown_data[number] = values[event]
                                break
                    break
        elif event == '_BANS_TOPLANE_' or event == '_BANS_MIDLANE_' or event == '_BANS_ADC_' or \
                event == '_BANS_SUPPORT_' or event == '_BANS_JUNGLE_' or event == '_PICKS_TOPLANE_' or \
                event == '_PICKS_MIDLANE_' or event == '_PICKS_ADC_' or event == '_PICKS_SUPPORT_' or \
                event == '_PICKS_JUNGLE_':
            i = len(values[event])
            while i > num_dropdowns:
                champions_selected = values[event]
                del champions_selected[0]
                index_list = []
                for champion in champions_selected:
                    index_list.append(championNames.index(champion))
                window[event].Update(set_to_index=index_list)
                i -= 1
        elif event == "start":
            threadLock.acquire()
            if not started:
                threadLock.release()
                threads[0] = th.Thread(target=main)
                threads[0].start()
                threadLock.acquire()
                started = True
                threadLock.release()
            else:
                threadLock.release()
        elif event == "stop":
            threadLock.acquire()
            if started:
                changed = True
                threadLock.release()
                threads[0].join()
                threadLock.acquire()
                started = False
                threadLock.release()
            else:
                threadLock.release()


initialize()
window_handle = create_gui()
gui(window_handle)