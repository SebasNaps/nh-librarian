

from os import path as ospath
from pathlib import Path
import json
from threading import Event


from eventbus import emitter
import options
from backend.core import favorites, metadata, image_extractor, downloader, image_converter, archiver, cover_loader
from backend.utils import append_json
from backend.utils.settings import Settings
from backend.utils.response import respond_progress, respond_metadata, respond_image
from backend.utils import logger


settings = Settings()

def getSession() -> dict:
    path = Path(ospath.join(options.CONFIG_DIR,options.SESSION_FILE))
    if not path.is_file():
        logger.error("No session settings found.")
        return None
    
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_results(results: dict):
    """
    Append parts of results to corresponding JSON files based on config.
    """

    for key in results.keys():
        data = results.get(key)
        save_result(key, data)

def save_result(type: str, result: dict):
    if not options.DATA_DIR:
        return
    data_dir = options.DATA_DIR
    mapping = {
        'favs': options.FAVORITES_FILE,
        'metadata': options.METADATA_FILE,
        'urls': options.URL_FILE,
        'cbzs': options.CBZ_LIB_FILE
    }
    filename = mapping[type]
    if filename:
        pth = ospath.join(data_dir, filename)
        append_json.append_data(pth, result)
        logger.info(f"Saved {type} to {pth}")



def load_data():
    mapping = {
        'favs': options.FAVORITES_FILE,
        'metadata': options.METADATA_FILE,
        'urls': options.URL_FILE,
        'cbzs': options.CBZ_LIB_FILE
    }
    if not options.DATA_DIR:
        return
    
    data = {k: None for k in ('metadata', 'urls', 'cbzs', 'favs')}
    data_dir = options.DATA_DIR
    for key, filename in mapping.items():
        if filename and key:
            filepath = ospath.join(data_dir, filename)
            if not ospath.exists(filepath):
                continue
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        
    return data

def load_ids(filepath: str) -> list:
    
    data = []

    if filepath:
        if not ospath.exists(filepath):
            return data
        with open(filepath, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
            data = [item['id'] for item in data_json if 'id' in item]

    return data


def fetch_favorites(stop=None) -> dict:
    session = getSession()
    if session==None:
        return None
    favs = favorites.fetch_all_favorites(session=session, stop=stop)

    ## Check stop and Respond progress
    if not cont(stop): return None
    return favs

def cont(stop):
    if stop and stop.is_set():
        logger.warning("Stopped function")
        emitter.emit('backend.task.stopped')
        return False
    else:
        return True


stop = Event()

def stop_task():
    stop.set()
emitter.on('backend.task.stop', stop_task)

def clear_stop():
    stop.clear()
emitter.on('backend.clear_stop', clear_stop)


def run(id_source=None, run_until=None):

    prev_data = load_data()

    prev_meta = prev_data['metadata'] if prev_data else []
    prev_urls = prev_data['urls'] if prev_data else []
    prev_cbzs = prev_data['cbzs'] if prev_data else []

    results = {k: [] for k in ('metadata', 'urls', 'cbzs', 'favs')}
    
    
    if not id_source or id_source=='favs':
        favs = fetch_favorites(stop=stop)
        if favs == None:
            return False
        logger.info(favs)
        results['favs'] = favs
        doujin_ids = [item['id'] for item in favs if 'id' in item]
        save_result(type='favs', result=favs)
    elif id_source=='pre_fetched_favs':
        doujin_ids = load_ids(ospath.join(options.DATA_DIR,options.FAVORITES_FILE))
        if doujin_ids == None:
            return False
    elif id_source=='id_list':
        doujin_ids = load_ids(ospath.join(options.DATA_DIR,options.IDS_FILE))
        if doujin_ids == None:
            return False
    

    
    ### Checkpoint 
    # Run until stop
    if run_until==0:
        return True
    
    # Check stop
    if not cont(stop): return False
    
    total = len(doujin_ids)

    for idx, did in enumerate(doujin_ids, start=1):
        
        # Check stop
        if not cont(stop): return False
        logger.info(f"--- Processing {idx+1}/{total}: ID {did}")
        respond_progress('total', idx-1, total)
        respond_progress('doujin', 0, run_until if run_until else 5)
        respond_progress('urls','-','-')
        respond_progress('downloads','-','-')
        respond_progress('conversion','-','-')

        if prev_cbzs and any(d['id'] == did for d in prev_cbzs) and (not run_until or run_until==4):
            logger.info('Already processed into .cbz before; skipping.')
            continue
        
        respond_progress('doujin', 0, run_until+1 if run_until else 5)
        
        existing_meta =  next(
            (item for item in prev_meta if item.get('id') == did), 
            None) if prev_meta else None
        
        if not existing_meta:
            meta = metadata.get_metadata(did)
            # Check stop
            if not cont(stop): return False
            if meta == None:
                logger.error("No metadata found; skipping to next doujin.")
                respond_progress('error',0,total)
                continue
            results['metadata'].append(meta)
        else:
            logger.info('Metadata already retrieved; skipping.')
            meta = existing_meta
        
        ### Checkpoint
        
        respond_progress('doujin', 2, run_until if run_until else 5)
        if settings.get("save_live_progress") and not existing_meta:
            save_result(type='metadata', result=meta)
        
        respond_metadata(meta)
        # Run until stop
        if run_until==1:
            continue
        try:
            cover_path = cover_loader.download_cover(doujin_id=did)
        except Exception as e:
            logger.error(f"Cover for id {did} not loaded {e}")
        
        respond_image(ospath.basename(cover_path))
        existing_urls = next(
            (item for item in prev_urls if item.get('id') == did), 
            None) if prev_urls else None
        if not existing_urls:
            urls = image_extractor.extract_image_urls(
                doujin_id=did, 
                retry_errors=settings.get('max_retries'),
                stop=stop)
            # Check stop
            if not cont(stop): return False
            if urls == None:
                logger.error("No URL fetching failed; skipping to next doujin.")
                respond_progress('error',0,total)
                continue
            results['urls'].append(urls)
        else:
            logger.info('URLs already retrieved; skipping.')
            urls = existing_urls
            respond_progress('urls', urls['urls'].__len__(), urls['urls'].__len__())
        
        
        ### Checkpoint 
        # Check stop
        respond_progress('doujin', 3, run_until if run_until else 5)
        if settings.get("save_live_progress") and not existing_urls:
            save_result(type='urls',result=urls)
        # Run until stop
        if not cont(stop):
            save_result(type='urls',result=urls)
            return False
        if run_until==2:
            continue
        
        
        paths = downloader.download_images(
            doujin_id=did, 
            image_urls=urls['urls'],
            retry_errors=settings.get('max_retries'),
            stop=stop)
        
        if not cont(stop):
            return False    
        
        if paths == None:
            logger.error("File download failed; skipping to next doujin.")
            respond_progress('error',0,total)
            continue
        
        
        ### Checkpoint 
        # Check stop
        if not cont(stop): return False
        respond_progress('doujin', 4, run_until if run_until else 5)
        if settings.get("save_live_progress") and not existing_urls:
            save_result(type='urls',result=urls)
        # Run until stop
        if run_until==3:
            continue

        paths = image_converter.convert_images_to_webp(
            doujin_id=paths['id'], 
            image_paths=paths['paths'], 
            quality=settings.get('webp_quality'))

        ### Checkpoint 
        # Check stop
        if not cont(stop): return False
        respond_progress('doujin', 5, run_until if run_until else 5)
        
        
        cbz_path = archiver.create_cbz(meta=meta, image_paths=paths, 
                                       cbz_dir=options.CBZ_DIR, autodelete_images=settings.get('delete_after_archiving'))
        results['cbzs'].append({'id': did, 'cbz_path': str(cbz_path)})

        ### Checkpoint 
        # Check stop
        if settings.get("save_live_progress") and not existing_urls:
            save_result(type='cbzs',result=results['cbzs'])
        if not cont(stop):
            save_result(type='cbzs',result=results['cbzs'])
            return False
        
        
    respond_progress('total', total, total)
    save_results(results=results)
    
    emitter.emit('backend.task.completed')
        

    

if __name__ == '__main__':
    print(run(id_source='id_list'))
