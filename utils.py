import random
from time import sleep


def stoo(s):
    """
    stoo = string to ordinal
    converts a string to a number by using the ord() of each character and creating a number from these 8 bit chunks
    inverse of otos
    """
    o = 0
    for i in range(len(s)):
        o |= ord(s[-i-1]) << (i << 3)
    return o


def otos(o, just=None):
    """
    otos = ordinals to string
    converts a number to a string by taking the chr() of each 8 bit chunk
    inverse of stoo
    """
    s = ""
    for i in range(((o.bit_length() - 1) >> 3), -1, -1):
        s += chr((o >> (i << 3)) & 255)
    if just is None:
        return s
    else:
        # option to rjust with 0s to fit a certain byte size
        return s.rjust(just, '\x00')

# Miller Rabin primality test with t trials
def MR_primality(n, t):
    if n == 2: return True
    if n % 2 == 0: return False
    k, q = 0, n - 1
    while q & 1 == 0:
        k += 1
        q >>= 1
    sample_pop_size = (n - 3) if n > 3 else 0
    sample_size = min(t, sample_pop_size)
    sample = set()
    for _ in range(sample_size):
        a = random.randint(2, n - 2)
        while a in sample:
            a = random.randint(2, n - 2)
        sample.add(a)
        x = pow(a, q, n)
        if x == 1 or x == n - 1: continue
        c = False
        for __ in range(k-1):
            x = x * x % n
            if x == n - 1:
                c = True
                break
        if c is True: continue
        return False
    return True

def generate_rand(num_bytes, start=0):
    return random.randint(start, (1 << (num_bytes << 3)) - 1)

def generate_rand_prime(num_bits):
    max_size = num_bits - 1
    num = (1 << max_size) + random.randint(1, (1 << max_size) - 1)
    while not MR_primality(num, 10):
        num = (1 << max_size) + random.randint(1, (1 << max_size) - 1)
    return num

def generate_primitive_root(prime):
    pass


def wait_for_message(message_func):
    def wrapper_wait_for_message(self, *args):
        done = False
        params = ()
        while not done:
            sleep(random.random())
            try:
                params = message_func(self, *args)
                done = params is not None
            except KeyboardInterrupt:
                done = True
                params = None
        return params
    wrapper_wait_for_message.__name__ = message_func.__name__
    wrapper_wait_for_message.__doc__  = message_func.__doc__
    return wrapper_wait_for_message
