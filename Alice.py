from User import User
from utils import *
from des import encrypt, decrypt


class Alice(User):
    def start(self):
        self.name = 'alice'
        # 1: Alice sends IDa IDb and a nonce to the kdc
        nonce = self.request_session_key()
        
        # 4: diffie helman with kdc
        self.diffie_hellman_response()
        
        # 8: decrypt to extract session key and message to send to Bob
        session_key = self.receive_key_from_kdc(nonce)
        if session_key is False:
            return
        
        #11: decrypt the message from Bob, apply some function to it, and send back
        self.respond_to_test_message(session_key)
        
        self.session_keys[self.other_user_id] = session_key
        
    
    
    def request_session_key(self):
        nonce = otos(generate_rand(5), 5)
        message = otos(self.id) + otos(self.other_user_id) + nonce
        self.kdc_connection.send_message(message)
        return nonce
    
    @wait_for_message
    def receive_key_from_kdc(self, nonce):
        message = self.kdc_connection.get_message()
        if message != '':
            # decrypt the message
            decrypted_message = otos(decrypt(stoo(message), self._key, 76), 76)
            
            # get the session key, bob_id, timestamp, nonce, and encrypted_b_message
            session_key = stoo(decrypted_message[:2])
            bob_id = stoo(decrypted_message[2:7])
            timestamp = decrypted_message[7:33]
            received_nonce = decrypted_message[33:38]
            encrypted_b_message = decrypted_message[38:]
            
            # quit if the message from the kdc is not right
            if timestamp in self.timestamps or bob_id != self.other_user_id or nonce != received_nonce:
                return False
            
            self.timestamps.add(timestamp)
            
            # send the encrypted_b_message
            self.other_user_connection.send_message(encrypted_b_message)
            
            return session_key
    
    @wait_for_message
    def respond_to_test_message(self, session_key):
        message = self.other_user_connection.get_message()
        if message != '':
            # decrypt message
            decrypted_message = otos(decrypt(stoo(message), session_key))
            
            # use the confirmation function
            hashed_message = User.confirm(decrypted_message)
            
            # encrypt hashed result
            encrypted_message = otos(encrypt(stoo(hashed_message), session_key))
            
            # send the encrypted message to bob
            self.other_user_connection.send_message(encrypted_message)
        
            return True
            
            