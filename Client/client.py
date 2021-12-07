#Author:Alex Torres
#Date:4/30/2021
#File: client.py
#Descripton: This file is used to start the client connection and contains
#   functions used by the client to transfer files. 

#import socket programming module
import socket
import base64
import hashlib
import rsa
import math
import random
import os
from os import listdir
import pathlib
from os.path import isfile, join
#create socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#set destination port
port = 9999

#set server address
serverAddr = ('192.168.29.128', port)

#Encryption stuff
server_n = 3977
server_e = 2153
client_n = 0
client_e = 0
client_d = 0

def getKeys():
    client_p = int(input('Client p Value: '))
    client_q = int(input('Client q Value: '))
    n = (client_p * client_q)
    phin = (client_p-1)*(client_q-1)

    #get public key
    e = random.randint(1,phin)
    while( math.gcd(e,phin) != 1 and e != phin):
        e = random.randint(1,phin)
    print('Client public key:', e)

    d = rsa.getPrivateKey(client_p, client_q, e)
    client_data = [d, n, e]
    return(client_data)

while(True):

    #send server the operating mode
    print('Command Line')
    command = input('->')
    command.lower()
    s.sendto(command.encode(), serverAddr)

    # If true, run in uploading mode
    if ('put file' in command):

        # Get file name from user
        filename = input('Enter filename with extension to send to server')
        while not os.path.isfile(filename):
            filename = input("No such file! Please enter the name of a file you'd like to send")
            arr = os.listdir('.')
            print('Current Path:')
            print(pathlib.Path(__file__).parent.resolve)
        
        s.sendto(filename.encode(), serverAddr)

        # statement will return true if the file is a png
        isPNG = ('png' in filename or 'html' in filename)

        print('Uploading File {0} to server'.format(filename))

        # Wait for ready message from server to start sending info
        msg, addr = s.recvfrom(1024)


        # generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096), b""):
                sha_hash.update(byte_block)

        # send bytes to server
        with open(filename, 'rb') as f:
            j = f.read(1)

            if (isPNG):
                while j:
                    encoded = base64.b64encode(j)
                    s.sendto(encoded, serverAddr)
                    j = f.read(100)
            else:
                while j:
                    print(j)
                    s.sendto(str(ord(j.decode())).encode(), serverAddr)
                    j = f.read(1)

            s.sendto('quit'.encode(), serverAddr)
            print('Upload Complete')
            s.sendto((sha_hash.hexdigest()).encode(), serverAddr)

    elif ('get file' in command):
        print('Downloading File')

        # Get file name from user
        filename = input('Enter filename with extension to send to server')
        s.sendto(filename.encode(), serverAddr)

        isPNG = ('png' in filename or 'html' in filename)
        print('Downloading file {0} from server'.format(filename))

        # Let server know it is receive to send data
        s.sendto('ready'.encode(), serverAddr)
        with open(filename, 'wb') as f:

            while (True):
                data, addr = s.recvfrom(1024)

                if (data.decode() == 'quit'):
                    print('received quit: ')
                    data, addr = s.recvfrom(1024)
                    received_hash = data.decode()
                    break
                else:
                    if (isPNG):
                        c = base64.b64decode(data)
                        char = c
                    else:
                        char = chr(int(data.decode())).encode()

                    f.write(char)
                    s.sendto(''.encode(), serverAddr)

            print('Download Complete')

        # Open created file to generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096), b""):
                sha_hash.update(byte_block)

        # Print received/generated hash values
        print('Received Hash: ', received_hash)
        print('Generated Hash: ', sha_hash.hexdigest())













    ############################ENCRYPTED FUNCTIONS##########################

    #If true, run in uploading mode
    elif('put' in command):

        #Get file name from user
        filename = input('Enter filename with extension to send to server')

        s.sendto(filename.encode(), serverAddr)

        #statement will return true if the file is a png
        isPNG = ('png' in filename or 'html' in filename)
        print('Uploading File {0} to server'.format(filename))

        #Wait for ready message from server to start sending info
        msg, addr = s.recvfrom(1024)


        #generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)

        #send bytes to server
        with open(filename, 'rb') as f:
            j = f.read(100)

            if(isPNG):
                while j:
                    x = base64.b64encode(j)
                    encryptedJ = rsa.encrypt(x.decode(), server_e, server_n)
                    s.sendto(encryptedJ.encode(), serverAddr)
                    msg, addr = s.recvfrom(1024)
                    j = f.read(100)
            else:
                while j:
                    encryptedJ = rsa.encrypt(str(j.decode()),server_e,server_n)
                    s.sendto(encryptedJ.encode(), serverAddr)
                    msg, addr = s.recvfrom(1024)
                    j = f.read(100)

            s.sendto('quit'.encode(),serverAddr)
            print('Upload Complete')
            s.sendto((sha_hash.hexdigest()).encode(), serverAddr)



    elif ('get' in command):
        text = ''
        keys = getKeys()
        client_d = keys[0]
        client_n = keys[1]
        client_e = keys[2]



        #Get file name from user
        filename = input('Enter filename with extension to send to server')
        s.sendto(filename.encode(), serverAddr)


        isPNG = ('png' in filename or 'html' in filename)
        print('Downloading file {0} from server'.format(filename))

        # Let server know it is receive to send data
        s.sendto('ready'.encode(),serverAddr)
        s.sendto(str(client_e).encode(),serverAddr)
        s.sendto(str(client_n).encode(),serverAddr)
        with open(filename, 'wb') as f:

            while(True):
                data, addr = s.recvfrom(1024)

                if(data.decode() == 'quit'):
                    print('received quit: ')
                    data, addr = s.recvfrom(1024)
                    received_hash = data.decode()
                    break
                else:
                    if(isPNG):
                        x = rsa.encrypt(data.decode(), client_d, client_n)
                        y = x.encode()
                        y = base64.b64decode(y)
                        char = y
                        s.sendto(''.encode(), serverAddr)

                    else:

                        char = rsa.encrypt(data.decode(), client_d, client_n)
                        char = char.encode()
                    f.write(char)
            print('Download Complete')

        # Open created file to generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)

        # Print received/generated hash values
        print('Received Hash: ', received_hash)
        print('Generated Hash: ', sha_hash.hexdigest())









