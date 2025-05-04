# app/sockets.py

from eventbus import emitter
from backend import backend_entry
from app.state_store import get_full_state, get_state, reset_state, set_state


def init_sockets(socketio):

    ## User Data Input

    @socketio.on('ids_input')
    def set_session(data):
        emitter.emit('frontend.log', "IDs list recevied.")
        # backend_entry.setIDList(data)
        emitter.emit('id_list.set', data)

    @socketio.on('cookie_input')
    def handle_cookie_input(data):
        emitter.emit('frontend.log', "Session information recevied.")
        # backend_entry.setSession(data)
        emitter.emit('session.set', data)

    ## Settings
    
    @socketio.on('apply_settings')
    def apply_settings(data):
        emitter.emit('frontend.log', f"Applying Settings: {data}")
        # backend_entry.applySettings(data)
        set_state('settings', data)
        emitter.emit('settings.apply', data)

    @socketio.on('reset_settings')
    def reset_settings():
        emitter.emit('frontend.log', f"Resetting settings")
        # backend_entry.resetSettings()
        reset_state('settings')
        emitter.emit('settings.reset')

    ## Log
    @socketio.on('log_stuff')
    def log_stuff(data):
        emitter.emit('frontend.log', {data})

    @socketio.on('frontend_log')
    def log_frontend(data):
        emitter.emit('frontend.log', {data})

    ## Load State on Page Loading
    @socketio.on('first_loaded')
    def send_state():
        emitter.emit('frontend.log', "Page freshly loaded. Applying state.")

        state = get_full_state()
        
        for stat in ['favorites','total','doujin','urls','downloads','conversion']:
            data = state['progress'][stat]
            data['type'] = stat
            socketio.emit('update.progress', data)

        socketio.emit('update.doujin_info', state['doujin_info'])

        socketio.emit('update.cover', state['doujin_cover'])

        socketio.emit('update.cover_visibility', state['show_cover'])

        sett_state = state['settings']
        socketio.emit('update.settings', sett_state)

        contrl_state = state['control']
        socketio.emit('update.control', contrl_state)
        

    
    ## Other state changes
    @socketio.on('cover_visibility')
    def set_cover_visibility(data):
        set_state('show_cover', data)

    ## Start/Stop Tasks
    @socketio.on('start_tasks')
    def handle_start_tasks(data):

        if get_state('task_running'):
            return
        
        set_state('task_running', True)

        reset_state('progress')
        reset_state('doujin_info')
        reset_state('doujin_cover')
        
        mode = data if data=='auto' else data['mode']
        id_source = data['id_source'] if not mode=='auto' else None
        run_until = data['run_until'] if not mode=='auto' else None

        set_state("control",{
            "mode": mode,
            "id_source":    id_source,
            "run_until":    run_until,
            "start_button": 'stop'
        })

        _forward_image("logo")

        emitter.emit('backend.task.start', mode, id_source, run_until)
    
    
    @socketio.on('stop_run')
    def stop_run(data):
        if(data != '9xE3XB93eFQq8Tne'):
            emitter.emit('frontend.log.error', "Incorrect key")
        emitter.emit('frontend.log.warning', f"Stopping current run...")
        emitter.emit('backend.task.stop')
        backend_entry.stop_tasks()
        socketio.emit('run_stopping')
        
    

    ## Progress updates from backend via Event-Emitter
    def _forward_button_state(button_state: str):
        set_state(key='control', subkey='start_button', update=button_state)
        if button_state == 'start':
            socketio.emit('progress_complete')
        elif button_state == 'stopped':
            socketio.emit('progress_stopped')
        elif button_state == 'stopping':
            socketio.emit('run_stopping')
    emitter.on('backend.button', _forward_button_state)

    def _forward_stopped():
        set_state('task_running', False)
        _forward_button_state('stopped')
    emitter.on('backend.task.stopped', _forward_stopped)

    
    def _forward_completed():
        set_state('task_running', False)
        _forward_button_state('start')
    emitter.on('backend.task.completed', _forward_completed)



    def _forward_progress(data):
        set_state(key='progress', subkey=data['type'], update={'current': data['current'], 'total': data['total']})
        socketio.emit('update.progress', data)
    emitter.on('backend.progress_update', _forward_progress)

    def _forward_image(image):
        set_state('doujin_cover', image)
        socketio.emit('update.cover', image)
        emitter.emit('frontend.log', f"Image update: {image}")
    emitter.on('backend.image_update', _forward_image)

    def _forward_doujin_info(meta):
        set_state('doujin_info', meta)
        socketio.emit('update.doujin_info', meta)
    emitter.on('backend.doujin_info_update', _forward_doujin_info)
    
