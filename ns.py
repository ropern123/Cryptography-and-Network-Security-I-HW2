from threading import Thread
from Alice import Alice
from Bob import Bob
from KDC import KDC



if __name__ == '__main__':
    # ids for alice and bob
    alice_id = 757709662050
    bob_id   = 1006360536646
    
    # create names for connections
    alice_kdc_connection = 'connection_alice_kdc'
    bob_kdc_connection   = 'connection_bob_kdc'
    alice_bob_connection = 'connection_alice_bob'
    

    # create participants
    alice = Alice(alice_id, alice_kdc_connection, alice_bob_connection, bob_id)
    bob = Bob(bob_id, bob_kdc_connection, alice_bob_connection, alice_id)
    kdc = KDC(alice_kdc_connection, bob_kdc_connection)
    
    
    # create threads to simulate communication between machines
    alice_thread = Thread(target=alice.start)
    bob_thread = Thread(target=bob.start)
    kdc_thread = Thread(target=kdc.start)
    
    # start each of the threads
    alice_thread.start()
    bob_thread.start()
    kdc_thread.start()
    
    # join each of the threads
    kdc_thread.join()
    alice_thread.join()
    bob_thread.join()
    
