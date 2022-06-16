import os
from Events import generate_process_id
from json import JSONDecoder, JSONEncoder
from threading import Thread
from Client_socket import Client_socket


class Socket:
	def __init__(self, socket_id=None, name=''):
		self.socket_id = socket_id or generate_process_id.generate_id()
		self.name = name
		self.treated_payloads = list()
		self.clients = dict()

		print('Socket ID ::: %s' % self.socket_id)

		self.sock_file()

		self.socket_thread = Thread(name=self.socket_id, target=self.watch_file, except_hook=self.exiting)
		self.socket_thread.start()

	_path = '%s/python_socket' % (os.environ[ 'HOME' ])

	def treat_payload(self, payload):
		if not payload:
			return

		if type(payload) == str:
			payload = JSONDecoder().decode(payload)

		self.treated_payloads.append(payload[ 'filename' ])

		try:
			if payload[ 'header' ][ 'receiver' ] == self.socket_id:
				os.remove(self._path + '/%s' % payload[ 'filename' ])

			if payload[ 'header' ][ "route" ] == 'connection':
				self.connection(payload[ 'data' ])
			elif payload[ 'header' ][ "route" ] == 'connection_handshake':
				self.connection_handshake(payload[ 'data' ])
			elif payload[ 'header' ][ 'disconnection' ]:
				self.disconnect_client(payload[ 'data' ])
			elif payload[ 'header' ][ 'route' ] == 'incoming_message':
				self.on_message(payload[ 'data' ], header=payload[ 'header' ], client=self.clients.get(payload[ 'header' ][
					                                                                                       'sender' ], None))
		except KeyError:
			print('Incomplete payload')

	def disconnect_client(self, client_data):
		del self.clients[ client_data[ 'socket_id' ] ]
		print('\nClient %s disconnected.\nTotal connections remain %d' % (client_data[ 'socket_id' ], len(self.clients)))

	def sock_file(self):
		try:
			os.mkdir(self._path)
		except FileExistsError:
			pass

	def connection_handshake(self, data):
		client = Client_socket(data[ 'remote_id' ], self)
		client.connected = True
		client.on_disconnect = self.on_client_disconnect
		self.clients[ client.socket_id ] = client
		print('\nConnected.\nTotal connections ::: %d' % len(self.clients))

	def connection(self, data):
		client = Client_socket(data[ 'socket_id' ], self)
		client.connection_handshake()
		client.on_disconnect = self.on_client_disconnect

		self.clients[ client.socket_id ] = client
		self.on_connection(client)
		print('\nNew connection.\nTotal clients %d' % len(self.clients))

	def message(self, client_id, data):
		client = self.clients.get(client_id, None)
		if not client:
			return

		client.message(data)

	def broadcast(self, data, route="", meta_header=dict()):
		for client_id in self.clients:
			self.clients[ client_id ].message(data, broadcast=True, route=route, meta_header=meta_header)

	def watch_file(self):
		while True:
			files = os.listdir(self._path)
			for file in files:
				if file in self.treated_payloads:
					return

				if (file.endswith(self.socket_id) and not file.startswith(self.socket_id)):
					self.treat_payload(open(self._path + '/%s' % (file)).read())
				elif (file.startswith('broadcast') and not file.endswith(self.socket_id)):
					self.treat_payload(open(self._path + '/%s' % (file)).read())

	def connect(self, remote_id='', remote_name=''):
		if not remote_id:
			remote_id = input('Remote ID: \n').strip()
		if not remote_id:
			return

		filename = '%s~%s~%s' % (self.socket_id, generate_process_id.generate_id(), remote_id)
		connection_token = {
			"header": {
				"route": "connection",
				"receiver": remote_id,
				"sender": self.socket_id
			},
			"data": {
				"socket_id": self.socket_id,
				"name": self.name,
				"remote_id": remote_id,
				"remote_name": remote_name,
				"connection": True,
			},
			"filename": filename
		}
		open(self._path + '/%s' % (filename), 'w').write(
			JSONEncoder().encode(connection_token))

	# handlers
	def on_client_disconnect(self, client):
		del self.clients[ client.socket_id ]

	def on_connection(self, client):
		pass

	def on_connection_handshake(self, client):
		pass

	def on_message(self, message_data, client=None, header=None):
		pass

	def exiting(self):
		pass

	def on_close(self):
		pass
# handlers
