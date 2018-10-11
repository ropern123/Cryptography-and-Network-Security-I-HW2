from Connection import Connection
import random
from utils import *
from des import encrypt, decrypt
from hashlib import sha512



class User:
    def __init__(self, id, kdc_connection, other_user_connection, other_user_id):
        self.id = int(id)
        self.kdc_connection = Connection(kdc_connection)
        self.other_user_connection = Connection(other_user_connection)
        self.other_user_id = other_user_id
        self._key = random.randint(1, (1 << 10) - 1) # generate a random 10 bit key for DES
        self.timestamps = set()
        self.session_keys = {}
    
    
    # respond to diffie hellman request with A and the user's private key
    # encrypted with the shared secret
    @wait_for_message
    def diffie_hellman_response(self):
        message = self.kdc_connection.get_message()
        if message != '':
            p = stoo(message[:512])
            g = stoo(message[512:1024])
            B = stoo(message[1024:])
            a = random.randint(3, p - 2)
            A = pow(g, a, p)
            s = pow(B, a, p)
            s %= (1 << 10) # only need last 10 bits for DES encrypt
            encrypted_key = encrypt(self._key, s)
            message = otos(A, 512) + otos(encrypted_key, 2)
            self.kdc_connection.send_message(message)
            return True
    
    # use SHA-512 as a confirmation hash function
    @staticmethod
    def confirm(message):
        return sha512(bytes(message, 'utf-8')).hexdigest()
