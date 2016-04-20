class EventEmitter:
    """Rudimentary EventEmitter class that somewhat mimics the NodeJS EventEmitter class"""
    def __init__(self):
        self.listeners = dict()
    def add_listener(self, event, func):
        """Adds func as a listener for event"""
        self.listeners.setdefault(event, set()).add(func)
    def on(self, event, func):
        """Adds func as a listener for event"""
        self.add_listener(event, func)
    def remove_listener(self, event, func):
        """Removes func as a listener for event"""
        if event in self.listeners and func in self.listeners[event]:
            self.listeners[event].remove(func)
    def remove_all_listeners(self, event):
        """Removes all listeners from event"""
        if event in self.listeners:
            del self.listeners[event]
    def emit(self, event, *args):
        """Emits event causing all listeners to be called with *args"""
        if event in self.listeners:
            listener_copy = self.listeners[event].copy()
            for func in listener_copy:
                func(*args)
