from Connection import Connection
from utils import *
import random
from des import encrypt, decrypt
import datetime

class KDC:
    # large prime with generator taken from https://datatracker.ietf.org/doc/rfc3526/?include_text=1
    # (4096 bit prime)
    DH_prime = 1044388881413152506679602719846529545831269060992135009022588756444338172022322690710444046669809783930111585737890362691860127079270495454517218673016928427459146001866885779762982229321192368303346235204368051010309155674155697460347176946394076535157284994895284821633700921811716738972451834979455897010306333468590751358365138782250372269117968985194322444535687415522007151638638141456178420621277822674995027990278673458629544391736919766299005511505446177668154446234882665961680796576903199116089347634947187778906528008004756692571666922964122566174582776707332452371001272163776841229318324903125740713574141005124561965913888899753461735347970011693256316751660678950830027510255804846105583465055446615090444309583050775808509297040039680057435342253926566240898195863631588888936364129920059308455669454034010391478238784189888594672336242763795138176353222845524644040094258962433613354036104643881925238489224010194193088911666165584229424668165441688927790460608264864204237717002054744337988941974661214699689706521543006262604535890998125752275942608772174376107314217749233048217904944409836238235772306749874396760463376480215133461333478395682746608242585133953883882226786118030184028136755970045385534758453247
    DH_prim_root = 2
    
    def __init__(self, alice_connection, bob_connection):
        self.alice_connection = Connection(alice_connection)
        self.bob_connection = Connection(bob_connection)
        self.s = {}
        self._user_keys = {}
    
    def start(self):
        # 2: kdc receives IDa, IDb, and nonce
        alice_id, bob_id, nonce = self.session_key_request()
        self.connections = { alice_id: self.alice_connection, bob_id: self.bob_connection }
        
        # 3: Do diffie hellman with alice and get her private key
        p, b = self.request_diffie_hellman(alice_id)
        self.diffie_hellman_response(alice_id, p, b)
        
        # 5: Do diffie hellman with bob and get his private key
        p, b = self.request_diffie_hellman(bob_id)
        self.diffie_hellman_response(bob_id, p, b)
        
        # 7: generate and encrypt the session key and send to Alice
        self.send_encrypted_session_key(alice_id, bob_id, nonce)
    
    @wait_for_message
    def session_key_request(self):
        message = self.alice_connection.get_message()
        if message != '':
            alice_id = stoo(message[:5])
            bob_id = stoo(message[5:10])
            nonce = message[10:]
            return alice_id, bob_id, nonce
        
    
    def request_diffie_hellman(self, user_id):
        # use the agreed upon prime and generator to send p, g, and b to the user
        p = KDC.DH_prime
        g = KDC.DH_prim_root
        b = random.randint(3, p - 2)
        B = pow(g, b, p)
        
        message = otos(p, 512) + otos(g, 512) + otos(B, 512)
        self.connections[user_id].send_message(message)
        return p, b
        
    
    @wait_for_message
    def diffie_hellman_response(self, user_id, p, b):
        message = self.connections[user_id].get_message()
        if message != '':
            # take the message from the user
            A = stoo(message[:512])
            encrypted_key = stoo(message[512:])
            
            # use it to find the shared secret
            s = pow(A, b, p)
            
            # use the shared secret to decrypt the user's key
            s %= (1 << 10)
            user_key = decrypt(encrypted_key, s)
            
            self.s[user_id] = s
            self._user_keys[user_id] = user_key
            
            return True
    
    def send_encrypted_session_key(self, alice_id, bob_id, nonce):
        session_key = random.randint(1, (1 << 10) - 1)
        timestamp = str(datetime.datetime.now())
        b_nonce = otos(generate_rand(5), 5)
        
        b_message = otos(session_key, 2) + otos(alice_id, 5) + timestamp + b_nonce
        encrypted_b_message = otos(encrypt(stoo(b_message), self._user_keys[bob_id], 38), 38)
        
        a_message = otos(session_key, 2) + otos(bob_id, 5) + timestamp + nonce + encrypted_b_message
        encrypted_a_message = otos(encrypt(stoo(a_message), self._user_keys[alice_id], 76), 76)
        
        self.alice_connection.send_message(encrypted_a_message)
        
        
    