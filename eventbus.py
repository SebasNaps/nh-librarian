# app/eventbus.py
from pyee.base import EventEmitter

# Single shared emitter
emitter = EventEmitter()

