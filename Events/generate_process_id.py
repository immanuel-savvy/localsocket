from random import randint
from string import ascii_letters, digits

alpha_numeric = ascii_letters + digits


def generate_id():
	_id = ''
	for _ in range(randint(12, 16)):
		_id += alpha_numeric[ randint(0, len(alpha_numeric) - 1) ]
	return _id
