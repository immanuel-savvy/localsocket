import sys
from Socket import Socket


class Connection:
	def __init__(self):
		self.my_sockets = list()

		self.Socket = Socket()
		self.Socket.on_message = self.on_message
		self.Socket.exiting = sys.excepthook = self.exiting

		self.Socket.connect()

	def on_message(self, message, client=None, header=None):
		print(message)

	def exiting(self, *args):
		self.Socket.broadcast({
			"socket_id": self.Socket.socket_id
		}, meta_header={"disconnection":True})

me = Connection()
