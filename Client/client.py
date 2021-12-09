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

def regularUpload():

    #Prompt user for file name, sending to server after ensuring it exists
    filename = input('Enter filename with extension to send to server\n')
    while not os.path.isfile(filename):
        filename = input("No such file! Please enter the name of a file you'd like to send")
    
    # Update server with file name, wait for ready message from server to start sending info
    s.sendto(filename.encode(), serverAddr)
    msg, addr = s.recvfrom(1024)
    print('Uploading File {0} to server'.format(filename))

    #FIXME is this needed?
    # statement will return true if the file is a png
    #isPNG = ('png' in filename or 'html' in filename or 'jpg' in filename)

    # Generate hash value for file. This will later be used by server to check for correctness
    with open(filename, 'rb') as file:
        sha_hash = hashlib.sha256()
        for byte_block in iter(lambda: file.read(4096), b""):
            sha_hash.update(byte_block)

    # Start sending file to server byte-wise
    with open(filename, 'rb') as f:
        j = f.read(1)

        if (True):
            while j:
                encoded = base64.b64encode(j)
                s.sendto(encoded, serverAddr)
                j = f.read(100)
        #FIXME is this needed?
        #else:
        #    while j:
        #        print(j)
        #        s.sendto(str(ord(j.decode())).encode(), serverAddr)
        #        j = f.read(1)
        print('Upload Complete')
        s.sendto('quit'.encode(), serverAddr)
        s.sendto((sha_hash.hexdigest()).encode(), serverAddr)

def regularDownload():

    #Prompt user for file name, sending to server after ensuring it exists
    filename = input('Enter filename with extension to send to server')
    s.sendto(filename.encode(), serverAddr)
    print('Downloading file {0} from server'.format(filename))


    #FIXME is this needed?
    #isPNG = ('png' in filename or 'html' in filename)

    # Signal server to start sending file bytewise
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
                if (True):
                    c = base64.b64decode(data)
                    char = c
                #FIXME is this needed?
                #else:
                #    char = chr(int(data.decode())).encode()

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

def encryptedUpload():
     #Get file name from user
        filename = input('Enter filename with extension to send to server')
        s.sendto(filename.encode(), serverAddr)

        #FIXME do I need this?
        #statement will return true if the file is a png
        isPNG = True
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

            if(True):
                while j:
                    x = base64.b64encode(j)
                    encryptedJ = rsa.encrypt(x.decode(), server_e, server_n)
                    s.sendto(encryptedJ.encode(), serverAddr)
                    msg, addr = s.recvfrom(1024)
                    j = f.read(100)
            #FIXME do I need this alternate encoding?
            #else:
            #    while j:
            #        encryptedJ = rsa.encrypt(str(j.decode()),server_e,server_n)
            #        s.sendto(encryptedJ.encode(), serverAddr)
            #        msg, addr = s.recvfrom(1024)
            #        j = f.read(100)

            s.sendto('quit'.encode(),serverAddr)
            print('Upload Complete')
            s.sendto((sha_hash.hexdigest()).encode(), serverAddr)

def encryptedDownload():
    text = ''
    keys = getKeys()
    client_d = keys[0]
    client_n = keys[1]
    client_e = keys[2]



    #Get file name from user
    filename = input('Enter filename with extension to send to server')
    s.sendto(filename.encode(), serverAddr)


    isPNG = True
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

                #FIXME Do I need this alternate encoding?
                #else:
                #
                #    char = rsa.encrypt(data.decode(), client_d, client_n)
                #    char = char.encode()
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


while(True):

    #send server the operating mode
    print('Select operating mode\n1. Upload\n2. Download\n3. RSA Encrypted Upload\n4. RSA Encrypted Download')

    command = input('->')
    s.sendto(command.encode(), serverAddr)

    # If true, run in uploading mode
    if ('1' in command):
        regularUpload()

    elif ('2' in command):
        regularDownload()

    elif('3' in command):
        encryptedUpload()
       
    elif ('4' in command):
        encryptedDownload()









