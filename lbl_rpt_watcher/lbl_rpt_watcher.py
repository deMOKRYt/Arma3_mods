import time
from ast import literal_eval
import json
from file_read_backwards import FileReadBackwards
from typing import TextIO
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import os

def load_config():
    config = {"last_rpt": None,
              "rpt_dir": None,
              "mission_datestamp_stop": None,
              "current_mission_datestamp": None,
              "seconds_betwean_scans": 20,
              "data_store_filename": os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'data_store.json')
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
    print(f'data_store is: {data_store}')
    with open(config["data_store_filename"], "w") as f:
        json.dump(data_store, f)

def eval_text (text):
    data={}
    try:
        t = literal_eval(text[9:])
        if t[0] == "MOO":
            if "SCORE_BOARD" in t[2]:
                data["date_stamp"] = str(t[1][0])
                data["name"] = t[1][1]
                data["score_board"] = tuple(t[3])
                return data
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
    with FileReadBackwards(config['last_rpt'], encoding="utf-8") as frb:
        for line in frb:
            mission_data = eval_text(line)
            if mission_data is not None:
                print(f"  mission_data is: {mission_data}")
                update_mission_data_store(config, data_store, mission_data)
                break


my_config = load_config()
my_data_store = load_data_store(my_config)
was_modified = False

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

event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, my_config['rpt_dir'], recursive=False)
observer.start()


try:
    while True:
        if was_modified:
            analyze_rpt (my_config, my_data_store)
            print('analyze done')
            was_modified = False
        time.sleep(my_config["seconds_betwean_scans"])
finally:
    observer.stop()
    observer.join()