
import re, json
from threading import Event
import os

import options
from eventbus import emitter
from backend.utils.settings import Settings
from backend.utils.logger import logger
from backend import backend_run

settings = Settings()

stop_event = Event()


def applySettings(data):
    print(data)
    for k, v in data.items():
        if k=='convert':
            settings.set('convert_to_webp', True if v==True else False)
        elif k=='autodelete':
            settings.set('delete_after_archiving', True if v==True else False)
        elif k=='live_progress':
            settings.set('save_live_progress', True if v==True else False)
        elif k=='webp' and v and int(v) in range(1,100):
            settings.set('webp_quality', int(v))
        elif k=='cbz' and v and int(data['cbz']) in range(1,9):
            settings.set('cbz_quality', int(v))
        elif k=='retry' and v and int(data['retry']) in range(1,100):
            settings.set('max_retries', int(v))
    logger.info(f"Settings now {settings.all()}")

emitter.on('settings.apply', applySettings)

def resetSettings():
    settings.reset()


emitter.on('settings.reset', resetSettings)

def setSession(data):
    with open("config/session.json",'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
emitter.on('session.set', setSession)

def setIDList(data):
    str_numbers = re.findall(r'\d+', data['id_list'])       # → ['123', '45', '6']

    # convert to ints (if you need numbers, not strings)
    id_list = list(map(lambda n: {"id": int(n)}, str_numbers))
    
    logger.info(f"ID-List received {id_list}")
    logger.info(f"Saving in dir {options.DATA_DIR}")
    logger.info(f"Saving in file {options.IDS_FILE}")
    with open(os.path.join(options.DATA_DIR,options.IDS_FILE),'w', encoding='utf-8') as f:
        json.dump(id_list, f, indent=4)

emitter.on('id_list.set', setIDList)

def start_task(mode: str='auto', id_source: str=None, run_until: str=None):
    logger.info(f"Staring task in mode: {mode}")
    logger.info(f"ID_source {id_source}")
    logger.info(f"Run until {run_until}")

    emitter.emit('backend.clear_stop')
    stop_event.clear()

    mapping = {
        'favs': 0,
        'meta': 1,
        'urls': 2,
        'down': 3,
        'cbz': 4
    }

    if stop_event and stop_event.is_set():
        logger.warning("Stopped function")
        return False

    if mode=='auto':
        success = backend_run.run()
    elif mode == 'custom':
        success = backend_run.run(run_until=mapping[run_until], id_source=id_source)
    
    if success:
        emitter.emit('backend.task.completed')
        return True
    elif not success:
        emitter.emit('backend.task.stopped')
        return False

    return True

emitter.on('backend.task.start', start_task)


def stop_tasks():
    stop_event.set()

if __name__ == '__main__':
    # Read settings
    print(settings.get("webp_quality"))  # 85

    # Change a setting
    settings.set("max_retries", 27)
    print(settings.all())

    # Reset all to default
    settings.reset()

    # View all settings
    print(settings.all())

    
