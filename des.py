import sys

# creates a permutation of t using the perms list
# for each (index, entry) pair (i,n) in the perms list, the i-th bit of r is made into the n-th bit of t
# len(perms) will be the bit length of the returned value, so if len(perms) is greater than the bit length of t,
# an expansion/permutation will be done
def permutation(t, perms):
	# blank slate to construct permutation
	r = 0
	for i in range(len(perms)):
		# (t >> (perms[i] - 1)) & 1 gets the value of t at the bit specified by perms
		# then, this is shifted to the proper bit and or'ed with r to set that bit in r
		r |= ((t >> (perms[i] - 1)) & 1) << i
	return r


# performs an S-box substitution on r using S
# gets row of S-box using bits 1 and 4, and gets column using bits 2 and 3
def S_substitution(r, S):
	return S[((r >> 2) & 0x2) | (r & 0x1)][(r >> 1) & 0x3]


# The F function (with input t and key k)
def F(t, k):
	# The S-boxes being used by the F function
	S0 = [[1, 0, 3, 2],
          [3, 2, 1, 0],
          [0, 2, 1, 3],
          [3, 1, 3, 2]]
	S1 = [[0, 1, 2, 3],
          [2, 0, 1, 3],
          [3, 0, 1, 0],
          [2, 1, 0, 3]]	
	
	# do the expansion/permutation to 8 bits from 4
	r = permutation(t, [4, 1, 2, 3, 2, 3, 4, 1])
	
	# xor by the key
	r ^= k
	
	# split into the top and bottom 4 bits
	r0, r1 = r & 0xf, (r >> 4) & 0xf
	
	# perform S-box substitutions on r0 and r1
	r0 = S_substitution(r0, S0)
	r1 = S_substitution(r1, S1)

	# combine both 2-bit results into one 4-bit number
	r = r0 | (r1 << 2)

	# perform a permutation on r
	r = permutation(r, [2, 4, 3, 1])

	return r


# Uses the initial 10-bit key ki to generate all 8-bit keys
def get_keys(ki):
	keys = []

	# perform initial permutation on initial key
	kp = permutation(ki, [3, 5, 2, 7, 4, 10, 1, 9, 8, 6])

	# split into the top and bottom 5 bits
	k0, k1 = kp & 0x1f, (kp >> 5) & 0x1f

	# create keys for 2 rounds of encryption
	for i in range(2):
		# left circular shift each 5-bit number by 1
		k0 = ((k0 << 1) | (k0 & 1)) & 0x1f
		k1 = ((k1 << 1) | (k1 & 1)) & 0x1f
	
		# combine 5-bit numbers into 10 bits
		k = k0 | (k1 << 5)
	
		# perform a permutation on k to take it from 10 bits to 8
		k = permutation(k, [6, 3, 7, 4, 8, 5, 10, 9])

		# store the key
		keys.append(k)

	return keys


# Uses DES to encrypt a block of 8 bits using a 10-bit key or multiple 8-bit keys generated from a 10-bit key
def DES_block(p, keys, decrypt=False):

	# detect whether a single 10-bit key or all 8-bit keys were input
	# if only the 10-bit key, use it to find all 8-bit keys
	if not isinstance(keys, list):
		if isinstance(keys, int):
			keys = get_keys(keys)
		else:
			raise ValueError("Cannot run DES without valid keys or an initial key")

	# reverse the order of the keys to decrypt
	if decrypt:
		keys = keys[::-1]

	# perform initial permutation of bits on the plaintext
	r = permutation(p, [2, 6, 3, 1, 4, 8, 5, 7])

	# split into the top and bottom 4 bits
	r0, r1 = r & 0xf, (r >> 4) & 0xf
	
	for i in range(len(keys)):
		
		# use F function on r1 and xor result with r0, store in r0
		r0 ^= F(r1, keys[i])
		
		# swap r0 and r1 on all but the last round
		if i != 1:
			r0, r1 = r1, r0
	
	# combine the two 4-bit numbers to one 8-bit
	r = r0 | (r1 << 4)
	
	# do the inverse of the initial permutation
	c = permutation(r, [4, 1, 3, 5, 7, 2, 8, 6])

	# return the ciphertext
	return c

# Can encrypt a plaintext of any length of number (arbitrary length binary string)
def DES(p, keys, num_blocks=None, decrypt=False):
	# detect whether a single 10-bit key or all 8-bit keys were input
	# if only the 10-bit key, use it to find all 8-bit keys
	if not isinstance(keys, list):
		if isinstance(keys, int):
			keys = get_keys(keys)
		else:
			raise ValueError("Cannot run DES without valid keys or an initial key")
	
	# find the number of blocks that will be encrypted
	if num_blocks is None:
		num_blocks = p.bit_length() // 8 + (1 if p.bit_length() % 8 != 0 else 0)

	c = 0
	for i in range(num_blocks):
		# get the next 8-bit block
		r = (p >> 8*i) & 0xff
		# block encrypt it and move it back to the correct location
		c |= (DES_block(r , keys, decrypt) << 8*i)

	return c

# Use DES to encrypt
def encrypt(p, keys, num_blocks=None):
	return DES(p, keys, num_blocks=num_blocks)

# Use DES to decrypt
def decrypt(p, keys, num_blocks=None):
	return DES(p, keys, num_blocks=num_blocks, decrypt=True)


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Program requires two or three arguments: the first is the binary plaintext to be encrypted, the second is the binary 8-bit key to be used, and the third which can be set to True to decrypt")
		sys.exit(1)
	print(sys.argv)
	# convert binary string plaintext to an integer
	p = int(sys.argv[1], 2)
	# convert binary string initial key to a number
	ki = int(sys.argv[2], 2)
	decrypt = False
	# use third argument if available, make into a boolean
	if len(sys.argv) > 3:
		decrypt = bool(sys.argv[3].title())
	
	# do the encryption/decryption
	c = DES(p, ki, decrypt)
	# print the result
	print(bin(c))
