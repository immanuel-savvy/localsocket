import os
from json import JSONEncoder
from Events import generate_process_id


class Client_socket:
	def __init__(self, socket_id, connector, socket_name=''):
		self.connected = False
		self.socket_id = socket_id
		self.socket_name = socket_name
		self.connector = connector
		self.total_messages = 0

	_path = '%s/python_socket' % (os.environ[ 'HOME' ])

	def __repr__(self):
		return '<%s socket_id="%s" connector="%s" %s>' % (self.__class__.__name__, self.socket_id,
		                                                  self.connector.socket_id, 'connected' if self.connected else '')

	def disconnect(self, ):
		self.connected = False
		self.on_disconnect(self)

	def connection_handshake(self):
		self.connected = True
		filename = '%s~%s~%s' % (self.connector.socket_id, generate_process_id.generate_id(), self.socket_id)
		handshake_token = {
			"header": {
				"route": "connection_handshake",
				"sender": self.connector.socket_id,
				"receiver": self.socket_id
			},
			"filename": filename,
			"data": {
				"remote_id": self.connector.socket_id,
				"socket_id": self.socket_id,
				"connected": self.connected
			}
		}
		open(self._path + '/%s' % filename, 'w').write(JSONEncoder().encode(handshake_token))

	def message(self, data, broadcast=False, route="", meta_header=dict()):
		message_token = {
			"data": data,
			"header": {
				"route": route or "incoming_message",
				"sender": self.connector.socket_id,
				"receiver": self.socket_id
			}
		}
		if len(meta_header):
			message_token[ 'header' ].update(meta_header)

		if broadcast:
			message_token[ 'header' ][ 'broadcast' ] = True

		filename = '%s~%s~%s' % (message_token.get('header').get('from'), generate_process_id.generate_id(),
		                         self.socket_id)
		message_token[ 'filename' ] = filename

		open(self._path + '/%s' % filename, 'w').write(JSONEncoder().encode(message_token))
		self.total_messages += 1

	# handlers
	def on_disconnect(self):
		pass
# handlers
