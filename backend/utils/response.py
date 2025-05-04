
from eventbus import emitter

def respond_progress(type: str, current: int, total: bool|int):
    emitter.emit('backend.progress_update', {
        'type': type,
        'current': current,
        'total': total
    })
    return 'progress' , {
        'type': type,
        'current': current,
        'total': total
    }

def respond_metadata(meta: dict):
    emitter.emit('backend.doujin_info_update', {
        'title': meta['title'],
        'id': meta['id'],
        'author': meta['author'],
        'tags': meta['tags']
    })
    return 'metadata' , meta

def respond_image(path: dict):
    emitter.emit('backend.image_update', path)
    return 'image' , path

