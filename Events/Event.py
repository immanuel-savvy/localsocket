class Event:
  def __init__(self):
    self.events = dict()
    self.return_values = dict()

  def emit(self, ev_id, return_value = None):
    event_listeners = self.events[ev_id]
    if not event_listeners: return

    for listener in event_listeners:
      listener(return_value)

  def listen(self, ev_id, listener, on_listen=None):

    listeners = self.events.get(ev_id)
    if not listeners:
      self.events[ev_id] = [listener]
    else:
      listeners.append(listener)
      self.events[ev_id] = listeners

    if on_listen: on_listen()

  def remove_listener(self, ev_id, listener):
    listeners = self.events[ev_id]
    if not listeners: return
    new_listeners = [listener_ != listener for listener_ in listeners]
    self.events[ev_id] = new_listeners

  def remove_listeners(self, ev_id):
    del self.events[ev_id]



