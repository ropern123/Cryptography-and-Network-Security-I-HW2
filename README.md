# Cryptography-and-Network-Security-I-HW2
Homework 2 for Cryptography and Network Security 1

# Description of program:
To use the program, run ns.py. This will go through the steps listed below and generate and verify a session key for Alice and Bob.

There are multiple classes that have been created:

KDC is the key distribution center.
It is set up to be able to receive requests from Users and process them according to the Needham-Schroeder protocol.

User represents a person who is utlizing the Needham-Schroeder protocol. It also has a method for doing Diffie-Hellman with the KDC.

Alice and Bob inherit from User, with Alice being the person who is asking for a session key with Bob.
Alice is set up to interact with Bob and the KDC and Bob is set up to interact with Alice
(Bob does interact with the KDC, but this is only for Diffie-Hellman).

The hash function being used is SHA-512.

The general steps are as follows:

1: alice sends IDa IDb and a nonce to the kdc

2: kdc receives IDa, IDb, and nonce

3: kdc sends diffie hellman info to alice

4: alice sends diffie hellman info and her private key encrypted with the Diffie-Hellman secret to kdc

5: kdc sends diffie hellman info to bob

6: bob sends diffie hellman info and his private key encrypted with the Diffie-Hellman secret to kdc

7: generate and encrypt the session key and send to alice

8: alice decrypts to extract session key and message to send to bob

9: bob decrypts to extract session key and alice's id

10: bob generates and encrypts a message using the session key and sends to alice

11: alice decrypts the message from bob, hashes it, encrypts, and sends back to bob

12: bob confirms that the decryption of the message alice sent matches the hash of the message bob generated

Though this is all running on one program, I have set up each of Alice, Bob, and the KDC to be running on different threads
and communicating only through files as to help make it clear exactly what information is being transferred,
as the exact flow of information might be difficult to follow otherwise.


# Description of implementation of Diffie-Hellman Protocol:
A large prime with a generator of 2 was taken from https://datatracker.ietf.org/doc/rfc3526/?include_text=1 (the 4096 bit prime).

We use this prime/generator pair for each exchange
as to avoid the need to find new ones every time, and this remains computationally secure.

Thus, to start, we have a prime and a generator.

The KDC generates a random number b less than the prime and remembers this number.

Then, it computes B=g<sup>b</sup> mod p and sends B, g, p to the User.

The User generates a random number a less than the prime and computes A=g<sup>a</sup> mod p and s=B<sup>a</sup> mod p. 

Then, the User sends A to the KDC

The KDC computes s=A<sup>b</sup> mod p, and then both the KDC and the User have a shared secret s

Any attacker viewing the exchange of information during this implementation of Diffie-Hellman will see g, p, B, and A.
However, due to the intractability of the discrete log problem and the large size of the chosen prime, this is not an issue as the attacker cannot find the secret s in a reasonable amount of time. 
