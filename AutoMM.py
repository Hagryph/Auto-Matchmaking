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
#################################################################################################################################################################################################################

def restoreConfig():
    file = open('config.json', 'w')
    file.write('{"roles":["top", "mid"], "dir":"C://Riot Games//League of Legends"}')
    file.close()
    print("Config restored pls check it and restart the script")
    sleep(5)
    exit()

#################################################################################################################################################################################################################

file = open('config.json','a+')
if os.path.getsize('config.json') == 0:
    file.write('{"roles":["mid", "top"], "dir":"C://Riot Games//League of Legends"}')
file.close()

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    restoreConfig()


role = {"sup": "UTILITY", "mid": "MIDDLE", "bot": "BOTTOM", "top": "TOP", "jungle": "JUNGLE", "fill": "FILL", "none": "NONE"}

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

def queue():
    request('post','/lol-lobby/v2/lobby','',{"queueId": 420})

def readyCheck():
    request('post', '/lol-matchmaking/v1/ready-check/accept')

def waitForEnd():
    sleep(10)
    return

#################################################################################################################################################################################################################

def routine():
    global kill
    global threadLock

    while True:
        sleep(1)
        r = request('get', '/lol-login/v1/session')

        if r.status_code != 200:
            print(r.status_code)
            continue

        if r.json()['state'] == 'SUCCEEDED':
            window = gw.getWindowsWithTitle('League of Legends')[0]
            window.moveTo(500, 100)
            pos_x = 1246*window.size[0]/1280
            pos_y = 205*window.size[1]/720
            break
        else:
            print(r.json()['state'])

    summonerId = r.json()['summonerId']

    accepted = False
    searching = False

    threadLock.acquire()
    while not kill:
        threadLock.release()

        try:
            r = request('get', '/lol-gameflow/v1/gameflow-phase')

            if r.status_code != 200:
                print(Back.BLACK + Fore.RED + str(r.status_code) + Style.RESET_ALL, r.text)
                continue

            phase = r.json()

            if phase == "ReadyCheck":
                searching = False
                readyCheck()
                if not accepted:
                    print("Readycheck accepted")
                    accepted = True
            else:
                accepted = False

                if phase == "None":
                    if not searching:
                        print("Searching for Game")
                        searching = True
                    queue()
                else:
                    searching = False

                    if phase == 'Lobby':
                        if getRole() == 0:
                            print("Wrong Roles set...")
                            setRole()
                            print("Now your roles fit!")
                        else:
                            if leader() == 1:
                                if not existsSearchError():
                                    search()
                                    print("Started Queue as Leader")

                    elif phase == 'InProgress':
                        waitForEnd()
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
                sleep(5)
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