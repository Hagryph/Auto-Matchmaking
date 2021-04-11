import requests
import urllib3
import json
from base64 import b64encode
from time import sleep
import os
import sys
import pygetwindow as gw
import threading as th

#################################################################################################################################################################################################################

protocol = 0
host = '127.0.0.1'
port = 0
username = 'riot'
headers = 0
s = 0

threadLock = th.Lock()

threads = {}
kill = False

champions = {"Annie":"1","Olaf":"2","Galio":"3","Twisted Fate":"4","Xin Zhao":"5","Urgot":"6","LeBlanc":"7","Vladimir":"8","Fiddlesticks":"9","Kayle":"10","Master Yi":"11","Alistar":"12","Ryze":"13","Sion":"14","Sivir":"15","Soraka":"16","Teemo":"17","Tristana":"18","Warwick":"19","Nunu":"20","Miss Fortune":"21","Ashe":"22","Tryndamere":"23","Jax":"24","Morgana":"25","Zilean":"26","Singed":"27","Evelynn":"28","Twitch":"29","Karthus":"30","Cho\'Gath":"31","Amumu":"32","Rammus":"33","Anivia":"34","Shaco":"35","Dr. Mundo":"36","Sona":"37","Kassadin":"38","Irelia":"39","Janna":"40","Gangplank":"41","Corki":"42","Karma":"43","Taric":"44","Veigar":"45","Trundle":"48","Swain":"50","Caitlyn":"51","Blitzcrank":"53","Malphite":"54","Katarina":"55","Nocturne":"56","Maokai":"57","Renekton":"58","Jarvan IV":"59","Elise":"60","Orianna":"61","Wukong":"62","Brand":"63","Lee Sin":"64","Vayne":"67","Rumble":"68","Cassiopeia":"69","Skarner":"72","Heimerdinger":"74","Nasus":"75","Nidalee":"76","Udyr":"77","Poppy":"78","Gragas":"79","Pantheon":"80","Ezreal":"81","Mordekaiser":"82","Yorick":"83","Akali":"84","Kennen":"85","Garen":"86","Leona":"89","Malzahar":"90","Talon":"91","Riven":"92","Kog\'Maw":"96","Shen":"98","Lux":"99","Xerath":"101","Shyvana":"102","Ahri":"103","Graves":"104","Fizz":"105","Volibear":"106","Rengar":"107","Varus":"110","Nautilus":"111","Viktor":"112","Sejuani":"113","Fiora":"114","Ziggs":"115","Lulu":"117","Draven":"119","Hecarim":"120","Kha\'Zix":"121","Darius":"122","Jayce":"126","Lissandra":"127","Diana":"131","Quinn":"133","Syndra":"134","Aurelion Sol":"136","Kayn":"141","Zoe":"142","Zyra":"143","Kai\'Sa":"145","Seraphine":"147","Gnar":"150","Zac":"154","Yasuo":"157","Vel\'Koz":"161","Taliyah":"163","Camille":"164","Braum":"201","Jhin":"202","Kindred":"203","Jinx":"222","Tahm Kench":"223","Senna":"235","Lucian":"236","Zed":"238","Kled":"240","Ekko":"245","Qiyana":"246","Vi":"254","Aatrox":"266","Nami":"267","Azir":"268","Yuumi":"350","Thresh":"412","Illaoi":"420","Rek\'Sai":"421","Ivern":"427","Kalista":"429","Bard":"432","Rakan":"497","Xayah":"498","Ornn":"516","Sylas":"517","Neeko":"518","Aphelios":"523","Pyke":"555","Yone":"777","Sett":"875","Lillia":"876"}

banPrio = {}
pickPrio = {}

lastPhase = ""
phase = ""

#################################################################################################################################################################################################################

def restoreConfig():
    file = open('config.json', 'w')
    file.write('{"roles":["mid", "top"], "dir":"C://Riot Games//League of Legends", "banPrio":{"mid":["Zed","Yasuo"],"top":["Aatrox","Yorick"],"jungle":["Master Yi","Nocturne"],"sup":["Morgana","Seraphine"],"bot":["Samira","Ashe"]}, "pickPrio":{"mid":["Yone","Yasuo"],"top":["Garen","Malphite"],"jungle":["Zac","Udyr"],"sup":["Lux","Brand"],"bot":["Caitlyn","Miss Fortune"]}}')
    file.close()
    print("Config restored pls check it and restart the script")
    sleep(5)
    exit()

#################################################################################################################################################################################################################

file = open('config.json','a+')
if os.path.getsize('config.json') == 0:
    file.write('{"roles":["mid", "top"], "dir":"C://Riot Games//League of Legends", "banPrio":{"mid":["Zed","Yasuo"],"top":["Aatrox","Yorick"],"jungle":["Master Yi","Nocturne"],"sup":["Morgana","Seraphine"],"bot":["Samira","Ashe"]}, "pickPrio":{"mid":["Yone","Yasuo"],"top":["Garen","Malphite"],"jungle":["Zac","Udyr"],"sup":["Lux","Brand"],"bot":["Caitlyn","Miss Fortune"]}}')
file.close()

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    restoreConfig()


role = {"sup": "UTILITY", "mid": "MIDDLE", "bot": "BOTTOM", "top": "TOP", "jungle": "JUNGLE", "fill": "FILL", "none": "NONE"}
roleName = {}
for key in role:
    roleName[role[key].lower()] = key

try:
    if config['roles'][0] == "fill":
        config['roles'][1] = "fill"

    changed = False

    if config['roles'][0] != "mid" and config['roles'][0] != "top" and config['roles'][0] != "bot" and config['roles'][0] != "jungle" and config['roles'][0] != "sup":
        if config['roles'][1] != "mid":
            config['roles'][0] = "mid"
        else:
            config['roles'][0] = "top"
        changed = True

    if config['roles'][1] != "mid" and config['roles'][1] != "top" and config['roles'][1] != "bot" and config['roles'][1] != "jungle" and config['roles'][1] != "sup":
        if config['roles'][0] != "mid":
            config['roles'][1] = "mid"
        else:
            config['roles'][1] = "top"
        changed = True

    if changed:
        with open('config.json', 'w') as f:
            json.dump(config, f)
        print("Config restored pls check it and restart the script")
        sleep(5)
        exit()
     
    rolePrio = [
        role[config['roles'][0]],
        role[config['roles'][1]]
    ]
except:
    restoreConfig()

#################################################################################################################################################################################################################
try:
    for r in config['banPrio']:
        banPrio[r] = []
        for champ in config['banPrio'][r]:
            banPrio[r].append(champions[champ])
except:
    pass

#################################################################################################################################################################################################################

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#################################################################################################################################################################################################################

def request(method, path, query='', data=''):
    
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
        r = fn(url, verify=False, headers=headers)
    else:
        r = fn(url, verify=False, headers=headers, json=data)

    return r

def getPickPrio():
    global pickPrio
    global champions

    try:
        availableChamps = request('get', '/lol-champions/v1/owned-champions-minimal').json()
        for r in config['pickPrio']:
            pickPrio[r] = []
            for champ in config['pickPrio'][r]:
                for aChamp in availableChamps:
                    if int(aChamp['id']) == int(champions[champ]):
                        if aChamp['rankedPlayEnabled']:
                            pickPrio[r].append(aChamp['id'])
    except:
        resetConfig()

def getRole():
    lobby = request('get', '/lol-lobby/v2/lobby').json()
    lobby = lobby['localMember']
    if (lobby['firstPositionPreference'] == rolePrio[0]):
        if (lobby['secondPositionPreference'] == rolePrio[1]):
            return 1
        else:
            return 0
    else:
        return 0
    

def setRole():
    request('put', '/lol-lobby/v2/lobby/members/localMember/position-preferences', '', {"firstPreference": rolePrio[0], "secondPreference": rolePrio[1]})

def leader():
    ps = request('get', '/lol-gameflow/v1/gameflow-metadata/player-status').json()
    return ps["currentLobbyStatus"]["isLeader"]

def existsSearchError():
    state = request('get', '/lol-lobby/v2/lobby/matchmaking/search-state').json()
    for error in state['errors']:
        return True
    return False

def search():
    request('post','/lol-lobby/v2/lobby/matchmaking/search')

def lobby():
    if getRole() == 0:
        print("Wrong Roles set...")
        setRole()
        print("Now your roles fit!")
    else:
        if leader() == 1:
            if not existsSearchError():
                search()
                return True
    return False

def queue():
    request('post','/lol-lobby/v2/lobby','',{"queueId": 420})

def readyCheck():
    request('post', '/lol-matchmaking/v1/ready-check/accept')

def getCellID():
    session = request('get', '/lol-champ-select/v1/session').json()
    return session['localPlayerCellId']

def getPhase():
    session = request('get', '/lol-champ-select/v1/session').json()
    for actions in session['actions']:
        for action in actions:
            if action['isInProgress']:
                return action['type']
    return False

def getPosition(ownCellID):
    session = request('get', '/lol-champ-select/v1/session').json()

    for player in session['myTeam']:
        if player['cellId'] == ownCellID:
            return player['assignedPosition']
    return False

def getBan(position):
    global banPrio

    if position:
        prio = banPrio[roleName[position.lower()]]

    session = request('get', '/lol-champ-select/v1/session').json()

    bans = []

    for action in session['actions'][0]:
        if action['completed']:
            bans.append(action['championId'])

    for id in prio:
        if not id in bans:
            return id

    return False

def getBanID(ownCellID):
    session = request('get', '/lol-champ-select/v1/session').json()
    
    for actions in session['actions']:
        for action in actions:
            if action['actorCellId'] == ownCellID:
                if action['type'] == "ban":
                    if action['isInProgress'] and not action['completed']:
                        return action['id']
    return False


def ban(id, ownCellID, banID):
    url = '/lol-champ-select/v1/session/actions/%d' % banID
    data = {'championId': id}
    request('patch', url, '', data)
    request('post', url+'/complete', '', data)

def getPickID(ownCellID):
    session = request('get', '/lol-champ-select/v1/session').json()
    
    for actions in session['actions']:
        for action in actions:
            if action['actorCellId'] == ownCellID:
                if action['type'] == "pick":
                    if action['isInProgress'] and not action['completed']:
                        return action['id']
    return False

def getPick(position):
    global pickPrio

    if position:
        prio = pickPrio[roleName[position.lower()]]

    session = request('get', '/lol-champ-select/v1/session').json()

    notAvailable = []

    for actions in session['actions']:
        for action in actions:
            if action['completed']:
                notAvailable.append(action['championId'])

    for id in prio:
        if not id in notAvailable:
            return id

    return False

def pick(id, ownCellID, pickID):
    url = '/lol-champ-select/v1/session/actions/%d' % pickID
    data = {'championId': id}
    request('patch', url, '', data)
    request('post', url+'/complete', '', data)

def pick_ban():
    phase = getPhase()
    if phase:
        ownCellID = getCellID()
        if ownCellID != -1:
            position = getPosition(ownCellID)
            if phase == "ban":
                banID = getBanID(ownCellID)
                if banID:
                    id = getBan(position)
                    if id:
                        ban(id, ownCellID, banID)
            elif phase == "pick":
                pickID = getPickID(ownCellID)
                if pickID:
                    id = getPick(position)
                    if id:
                        pick(id, ownCellID, pickID)

#################################################################################################################################################################################################################

def routine():
    global kill
    global threadLock
    global lastPhase
    global phase

    while True:
        sleep(1)
        r = request('get', '/lol-login/v1/session')

        if r.status_code != 200:
            print(r.status_code)
            continue

        if r.json()['state'] == 'SUCCEEDED':
            window = gw.getWindowsWithTitle('League of Legends')[0]
            window.moveTo(500, 100)
            break

    summonerId = r.json()['summonerId']

    accepted = False
    searching = False
    
    getPickPrio()

    threadLock.acquire()
    while not kill:
        threadLock.release()

        try:
            r = request('get', '/lol-gameflow/v1/gameflow-phase')

            if r.status_code != 200:
                print(str(r.status_code), r.text)
                continue

            phase = r.json()

            if phase == "ReadyCheck":
                readyCheck()
                if phase != lastPhase:
                    print("Readycheck accepted")

            elif phase == 'ChampSelect':
                pick_ban()

            elif phase == "None" or phase == "EndOfGame":
                if phase != lastPhase:
                    print("Searching for Game")
                queue()

            elif phase == 'Lobby':
                if lobby() and phase != lastPhase:
                    print("Searching for game ...")

            elif phase == 'InProgress':
                sleep(10)

            lastPhase = phase
        except:
            pass
        
        sleep(1)
        threadLock.acquire()
           
    kill = False
    threadLock.release()

def main():
    global kill
    global protocol
    global username
    global port
    global headers
    global threadLock
    global s
    global threads
    global config

    while True:
        lockfile = None
        print('Waiting for League of Legends to start ..')

        try:
            while not lockfile:
                lockpath = r'%s\lockfile' % config["dir"]

                if not os.path.isfile(lockpath):
                    continue

                print('Found running League of Legends, dir', config["dir"])
                lockfile = open(r'%s\lockfile' % config["dir"], 'r')
                sleep(20)
        except:
            restoreConfig()

        lockdata = lockfile.read()
        lockfile.close()

        lock = lockdata.split(':')

        procname = lock[0]
        pid = lock[1]

        protocol = lock[4]
        port = lock[2]

        password = lock[3]
    
        userpass = b64encode(bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')
        headers = { 'Authorization': 'Basic %s' % userpass }

        s = requests.session()

        threads[1] = th.Thread(target=routine)
        threads[1].start()

        while True:
            if not os.path.isfile(lockpath):
                threadLock.acquire()
                kill = True
                threadLock.release()
                threads[1].join()
                break

            sleep(1)

#################################################################################################################################################################################################################

threads[0] = th.Thread(target=main)
threads[0].start()
threads[0].join()