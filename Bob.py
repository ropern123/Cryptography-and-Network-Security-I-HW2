from User import User
from utils import *
from des import encrypt, decrypt


class Bob(User):
    def start(self):
        # 6: diffie helman wth kds
        self.diffie_hellman_response()
        
        # 9: decrypt to extract session key and Alice's id
        session_key = self.receive_key_from_alice()
        
        if session_key is False:
            return
        
        #10: encrypt a message using the session key and send to Alice
        test_message = self.send_test_message(session_key)
        
        #12: confirm that the function applied to the message is correct
        if self.confirm_message_from_alice(session_key, test_message) is False:
            return
        
        self.session_keys[self.other_user_id] = session_key
        print('session key established for Alice and Bob')
        
        
    
    @wait_for_message
    def receive_key_from_alice(self):
        message = self.other_user_connection.get_message()
        if message != '':
            # decrypt the message
            decrypted_message = otos(decrypt(stoo(message), self._key, 38), 38)
            
            session_key = stoo(decrypted_message[:2])
            alice_id = stoo(decrypted_message[2:7])
            timestamp = decrypted_message[7:33]
            
            # quit if the message from Alice is not right
            if timestamp in self.timestamps or alice_id != self.other_user_id:
                return False
            self.timestamps.add(timestamp)
            
            return session_key
    
    def send_test_message(self, session_key):
        # generate a test message
        test_message = generate_rand(32)
        
        # encrypt the message and make it a string
        encrypted_message = encrypt(test_message, session_key)
        encrypted_message = otos(encrypted_message, 32)
        
        self.other_user_connection.send_message(encrypted_message)
        
        return test_message
    
    @wait_for_message
    def confirm_message_from_alice(self, session_key, test_message):
        message = self.other_user_connection.get_message()
        if message != '':
            # decrypt the message
            decrypted_message = otos(decrypt(stoo(message), session_key))         
            # quit if the decrypted hash does not match that of the test message
            if decrypted_message != User.confirm(otos(test_message, 32)):
                return False
            return True
    
    
    