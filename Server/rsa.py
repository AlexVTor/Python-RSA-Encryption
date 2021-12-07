#Alexis Torres
#ESET 415
#Python coding question
import math

#function used to decrypt/ encrypt
def encrypt(text, key, n):
    cipher = []
    c = ""

    # Using plaintext ascii values, encrypt with [x]^key % n, append to cipher list
    for x in text:
        char = (ord(x) ** key ) % n
        cipher.append(char)
        c+= chr(char)
    #print('Enrypted Plaintext (Cipher): ', c)
    return c

# function used to get d when given specified parameters
def getPrivateKey(p, q, e):
    # set n and phin values
    n = p * q
    phin = (p-1) * (q-1)

    # iterate through values of d
    d=1
    while(True):
        rem = ( e * d) % phin
        if(rem ==1):
            if(math.gcd(d,n) ==1):
                if(d !=e):
                    return d

        d += 1



