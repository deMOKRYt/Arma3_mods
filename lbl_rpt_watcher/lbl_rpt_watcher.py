import time
from ast import literal_eval
import json
from file_read_backwards import FileReadBackwards
from typing import TextIO
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import os
import signal
from pywinauto import Desktop
import re
import traceback
import ctypes
import pyodbc
import datetime

def prevent_win_idle():
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)

def load_config():
    config = {"last_rpt": None,
              "rpt_dir": os.path.join(os.path.join(os.environ['USERPROFILE']), 'AppData', 'Local', 'Arma 3', 'data_store.json'),
              "seconds_betwean_scans": 20,
              "data_store_filename": os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'data_store.json'),
              "steam_group_name": None,
              "steam_group_channel": None,
              "steam_last_published_mission_datestamp": None,
              "database_address": None,
              "database_user": None,
              "database_pwd": None,
              "database_name": None
              }

    if os.path.exists('config.json'):
        with open("config.json", "r") as f:
            loaded_config = json.load(f)
            return loaded_config
    else:        
        with open("config.json", "w") as f:
            json.dump(config, f)
            return config
        
def update_config(config, k,v):
    config[k]=v
    with open("config.json", "w") as f:
            json.dump(config, f)

def load_data_store(config):
    d={}
    if os.path.exists(config['data_store_filename']):
        with open(config['data_store_filename'], "r") as f:
            loaded_config = json.load(f)
            return loaded_config
    else:        
        with open(config['data_store_filename'], "w") as f:
            json.dump(d, f)
            return d

def save_data_store_to_disc(config, data_store):
    with open(config["data_store_filename"], "w") as f:
        json.dump(data_store, f)

def eval_text (text):
    data={}
    try:
        t = literal_eval(text)
        if t[0] == "MOO":
            if "SCORE_BOARD" in t[2]:
                data["date_stamp"] = str(t[1][0])
                data["name"] = t[1][1]
                data["score_board"] = tuple(t[3])
                if "SCORE_BOARD_AFTER_MISSION_END_IS" in t[2]:
                    return (data, True)
                return (data, False)
            else:
                return None
    except:
        return None
    
        
def update_mission_data_store(config, data_store, data):
    data_from_store = data_store.get(data['date_stamp'])
    if data_from_store is None:
        data_store[data['date_stamp']]=(data['name'],data['score_board'])
        save_data_store_to_disc(config, data_store)
    else:
        if data_from_store[1] != data['score_board']:
            data_store[data['date_stamp']]=(data['name'],data['score_board'])
            save_data_store_to_disc(config, data_store)

def analyze_rpt (config, data_store):
    # ["MOO",
    # [[2025,5,26,19,59,48,146],"ACPL 12 KillHouses - Classic"],
    # "SCORE_BOARD_AFTER_MISSION_END_IS:",
    # [["deMO [ACPL]", 21], ["Jon [ACPL]", 22], ["Łysy", 23],]]
    mission_ended = False
    score = None
    if my_config['last_rpt'] is None:
        print('Update config.json - last_rpt log has not been chosen.')
        return False
    with FileReadBackwards(config['last_rpt'], encoding="utf-8") as frb:
        for line in frb:
            mission_data = eval_text(line)
            if mission_data is not None:
                scores = mission_data[0]
                mision_ended = mission_data [1]
                if not mision_ended:    
                    print(f"  mission_data is: {scores}")
                    update_mission_data_store(config, data_store, scores)
                    break
                else:
                    print(f"  mission_data is: {scores}")
                    update_mission_data_store(config, data_store, scores)
                    mission_ended = True
                    break
    return (mission_ended, scores)

class SignalHandler:
    shutdown_requested = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)

    def request_shutdown(self, *args):
        print('Shutdown request recevied. Stopping...')
        self.shutdown_requested = True
 
    def can_run(self):
        return not self.shutdown_requested

class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if (not event.is_directory):
            if str(event.src_path)[-4:]=='.rpt':
                update_config(my_config, 'last_rpt', event.src_path)
                print(f'using: {event.src_path}')

    def on_modified(self, event):
        global was_modified
        print('was modified')
        was_modified = True

def post_to_steam(config, data):
    group_name = config['steam_group_name']
    group_channel = config['steam_group_channel']

    def keborderize(sentence : str):
        abc123=re.sub(r'[^ \w+]', '', sentence)
        buf=''
        for l in abc123:
            if l.isupper():
                buf+='{VK_SHIFT down}'+l+'{VK_SHIFT up}'
            elif l == ' ':
                buf+='{SPACE}'
            else:
                buf+=l
        return buf

    def pritify(data):
        mission = keborderize(data['name'])
        scores = data['score_board']
        lines=''
        lines+=mission
        lines+='{VK_SHIFT down}{ENTER}{VK_SHIFT up}'
        for i in scores:
            buf='--'
            buf+= keborderize(i[0])
            buf+='{SPACE}-{SPACE}'
            buf+=str(i[1])
            buf+='{VK_SHIFT down}{ENTER}{VK_SHIFT up}'
            lines+=buf
        lines+='{ENTER}'
        return lines
        
    try:  
        main_window = Desktop(backend='uia').window(best_match=group_name)
        a3_feedback = Desktop(backend='uia').window(best_match=group_name).child_window(title=group_channel, control_type="Group")
        main_window.set_focus()
        a3_feedback.click_input()
        a3_feedback.type_keys(pritify(data))                            
    except:
       print('Exception occured while posting results to Steam.')
       traceback.print_exc()

def db_insert_mission(config, data):
    date_str = data["date_stamp"]
    mission_name_str = data["name"]
    scores = data["score_board"]
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={config['database_address']};"
        f"DATABASE={config['database_name']};"
        f"UID={config['database_user']};"
        f"PWD={config['database_pwd']}")

    def date_str_to_datetime_str(date_string):
        # date_string = "[2025, 5, 20, 12, 33, 4, 211]"
        x=eval(date_string)
        x[6]=1000*x[6]
        date=str(datetime.datetime(*x))
        return date
    
    def chose_corect_mission(rows):
        if len(rows) > 1:
            raise NotImplementedError ("Can't handle situation where there is more than one mission with same date stamp!")
        if len(rows) == 1 :
            raise NotImplementedError ("Mission with provided time stump alrady exists in database, updating not supported yet!")
        else:
            return None    
    
    try:
        date = date_str_to_datetime_str(date_str)
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        query = f"SELECT [Id] FROM [acpl].[dbo].[Missions] WHERE [acpl].[dbo].[Missions].[DateStamp] = '{date}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        row_id = chose_corect_mission(rows)
        if row_id is None:
            query = f"INSERT INTO [acpl].[dbo].[Missions] (Name, DateStamp) OUTPUT INSERTED.Id VALUES ('{mission_name_str}', '{date}')"
            cursor.execute(query)
            row = cursor.fetchone()
            row_id = row[0]
        for player, score in scores:                
            query = f"INSERT INTO [acpl].[dbo].[Scores] VALUES ('{player}', {score}, {row_id})"
            cursor.execute(query)
        cursor.commit()        
    finally:
        if 'connection' in locals():
            connection.close()

my_config = load_config()
my_data_store = load_data_store(my_config)
was_modified = False
signal_handler = SignalHandler()
event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, my_config['rpt_dir'], recursive=False)
observer.start()

try:
    while signal_handler.can_run():
        if was_modified:
            m=analyze_rpt (my_config, my_data_store)
            print('analyze done')
            m_end=m[0]
            m_score=m[1]
            if m_end and m_score is not None:
                if my_config['steam_last_published_mission_datestamp'] != m_score['date_stamp']:
                    update_config(my_config, 'steam_last_published_mission_datestamp', m_score['date_stamp'])
                    db_insert_mission(my_config, m_score)
                    post_to_steam(my_config, m_score)
            was_modified = False
        time.sleep(my_config["seconds_betwean_scans"])
        prevent_win_idle()
finally:
    observer.stop()
    observer.join()
