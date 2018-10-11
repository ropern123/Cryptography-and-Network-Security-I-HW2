from threading import Thread
from Alice import Alice
from Bob import Bob
from KDS import KDS



if __name__ == '__main__':
    # ids for alice and bob
    alice_id = 757709662050
    bob_id   = 1006360536646
    
    # create names for connections
    alice_kds_connection = 'connection_alice_kds'
    bob_kds_connection   = 'connection_bob_kds'
    alice_bob_connection = 'connection_alice_bob'
    

    # create participants
    alice = Alice(alice_id, alice_kds_connection, alice_bob_connection, bob_id)
    bob = Bob(bob_id, bob_kds_connection, alice_bob_connection, alice_id)
    kds = KDS(alice_kds_connection, bob_kds_connection)
    
    
    # create threads to simulate communication between machines
    alice_thread = Thread(target=alice.start)
    bob_thread = Thread(target=bob.start)
    kds_thread = Thread(target=kds.start)
    
    # start each of the threads
    alice_thread.start()
    bob_thread.start()
    kds_thread.start()
    
    # join each of the threads
    kds_thread.join() 
    alice_thread.join()
    bob_thread.join()
    
