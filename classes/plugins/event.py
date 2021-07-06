import os
import builtins
import logging
import pickle
import typing
import inspect
_pickleLevel_ = 5 #pickle level to use when compressing and storing events
def _save_(events):
    folder = os.path.dirname(os.path.realpath(__file__))
    with open(f'{folder}/events.pickle',"wb") as file:
        pickle.dump(events,file,protocol=_pickleLevel_)

def _getEvents_():
    folder = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(f'{folder}/events.pickle',"rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
def _reset_():
    folder = os.path.dirname(os.path.realpath(__file__))
    with open(f'{folder}/events.pickle',"wb") as file:
        pickle.dump({},file,protocol=_pickleLevel_)

def registerEvent(name: str):
    events = _getEvents_()
    try:
        tmp = events[name]
        logging.info(f"event '{name}' was allready registered")
    except KeyError:
        logging.info(f"registering event '{name}'")
        events[name] = []
    _save_(events)

def register(event: str,func: typing.Callable):
    events = _getEvents_()
    try:
        events[event].append(func)
    except KeyError:
        registerEvent(event)
        events = _getEvents_()
        events[event].append(func)
    _save_(events)

def fire(event: str,*args,**kwargs) -> list:
    import traceback
    events = _getEvents_()
    ret = []
    for func in events[event]:
        funcArgs = inspect.signature(func).parameters
        hasArgs = False
        hasKwargs = False
        for k in funcArgs:
            param = funcArgs[k]
            if param.kind == param.VAR_POSITIONAL:
                logging.debug("function has *args")
                hasArgs = True
            if param.kind == param.VAR_KEYWORD:
                logging.debug("function has **kwargs")
                hasKwargs = True
        if ((len(args) + len(kwargs)) == len(funcArgs)) or hasArgs or hasKwargs:
            ret.append(func(*args,**kwargs))
        else:
            logging.error(f"a plugin connected to event '{event}' takes a incorrect amount of arguments: expected {len(args)+len(kwargs)} got {len(funcArgs)}")
    return ret
