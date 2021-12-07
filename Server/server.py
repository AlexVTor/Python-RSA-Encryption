# This is udpserver.py file
import socket
import base64
import hashlib
import rsa
import math
# create a UDP socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Get local machine address
ip = "192.168.29.128"

# Set port number for this server
port = 9999

# Bind to the port
serversocket.bind((ip, port))
server_p = 97
server_q = 41
server_e = 2153
server_n = 3977
server_d = rsa.getPrivateKey(server_p, server_q, server_e)

while True:
    print("Waiting to receive message on port " + str(port) + '\n')

    #first message to be recieved by server contains operating mode
    data, addr = serversocket.recvfrom(1024)
    command = data.decode()




    if ('put file' in command):
        text = ''
        data, addr = serversocket.recvfrom(1024)
        message = data.decode()

        #Keep looking for 'ready' message to start transferring data
        #Next thing to be sent by client is the file name
        while(message == 'put file'):
            data, addr = serversocket.recvfrom(1024)
            message = data.decode()

        # Print file name to be downloaded
        filename = message
        print('Downloading File {0} from client'.format(filename))
        #statement will return true if the file is a png
        isPNG = ('png' in filename or 'html' in filename)
        #isPNG = ('png' in filename )

        # Let client know it is ready to recieve data
        serversocket.sendto('ready'.encode(),addr)


        with open(filename, 'wb') as f:
        #with open(fileName, 'a', encoding='utf-8') as f:
            while True:
                data, addr = serversocket.recvfrom(1024)

                if (data.decode() == 'quit'):
                    data, addr = serversocket.recvfrom(1024)
                    received_hash = data.decode()
                    break

                else:
                    if(isPNG):
                        c = base64.b64decode(data.decode())
                        char = c

                    else:
                        char = chr(int(data.decode())).encode()
                        text += char.decode()
                    f.write(char)
            print('Download Complete')
            print('Received Hash: ', received_hash)


        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)
        print('Generated Hash: ', sha_hash.hexdigest())

    elif('get file' in command):
        text = ''
        data, addr = serversocket.recvfrom(1024)

        filename = data.decode()
        isPNG = ('png' in filename or 'html' in filename)
        print('Uploading File {0} to client'.format(filename))

        #Wait for ready message from server to start sending info
        data, addr = serversocket.recvfrom(1024)


        #Generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)

        #Sent bytes to client
        with open(filename, 'rb') as f:
            j = f.read(1)

            if(isPNG):
                while j:
                    encoded = base64.b64encode(j)
                    serversocket.sendto(encoded, addr)
                    data, addr = serversocket.recvfrom(1024)
                    j = f.read(100)
            else:
                while j:
                    serversocket.sendto(str(ord(j.decode())).encode(), addr)
                    data, addr = serversocket.recvfrom(1024)
                    j = f.read(1)

            serversocket.sendto('quit'.encode(), addr)
            print('Upload Complete')
            serversocket.sendto((sha_hash.hexdigest()).encode(), addr)





############################ENCRYPTED FUNCTIONS##########################
    elif ('put' in command):
        text = ''
        data, addr = serversocket.recvfrom(1024)
        message = data.decode()

        #Keep looking for 'ready' message to start transferring data
        #Next thing to be sent by client is the file name
        while(message == 'put file'):
            data, addr = serversocket.recvfrom(1024)
            message = data.decode()

        # Print file name to be downloaded
        filename = message
        print('Downloading File {0} from client'.format(filename))
        #statement will return true if the file is a png
        isPNG = ('png' in filename or 'html' in filename)

        # Let client know it is ready to recieve data
        serversocket.sendto('ready'.encode(),addr)


        with open(filename, 'wb') as f:
        #with open(fileName, 'a', encoding='utf-8') as f:
            while True:
                data, addr = serversocket.recvfrom(1024)

                if (data.decode() == 'quit'):
                    data, addr = serversocket.recvfrom(1024)
                    received_hash = data.decode()
                    break

                else:
                    if(isPNG):
                        x = rsa.encrypt(data.decode(),server_d,server_n)
                        y = x.encode()
                        y = base64.b64decode(y)
                        char = y
                        serversocket.sendto(''.encode(),addr)

                    else:
                        char = rsa.encrypt(data.decode(), 2777, server_n)
                        char = char.encode()
                        serversocket.sendto(''.encode(),addr)
                    f.write(char)
            print('Download Complete')
            print('Received Hash: ', received_hash)


        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)
        print('Generated Hash: ', sha_hash.hexdigest())

    elif('get' in command):
        text = ''
        data, addr = serversocket.recvfrom(1024)

        filename = data.decode()
        isPNG = ('png' in filename or 'html' in filename)
        print('Uploading File {0} to client'.format(filename))

        #Wait for ready message from server to start sending info
        data, addr = serversocket.recvfrom(1024)
        #recieve clients public key
        data, addr = serversocket.recvfrom(1024)
        client_e = int(data.decode())
        data, addr = serversocket.recvfrom(1024)
        client_n = int(data.decode())
        #Generate hash value
        with open(filename, 'rb') as file:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(4096),b""):
                sha_hash.update(byte_block)

        #Sent bytes to client
        with open(filename, 'rb') as f:
            j = f.read(1)

            if(isPNG):
                while j:
                    x = base64.b64encode(j)
                    encryptedJ = rsa.encrypt(x.decode(), client_e, client_n)
                    serversocket.sendto(encryptedJ.encode(), addr)
                    data, addr = serversocket.recvfrom(1024)
                    j = f.read(100)
            else:
                while j:
                    encryptedJ = rsa.encrypt(str(j.decode()), client_e, client_n)
                    serversocket.sendto(encryptedJ.encode(), addr)
                    j = f.read(100)

            serversocket.sendto('quit'.encode(), addr)
            print('Upload Complete')
            serversocket.sendto((sha_hash.hexdigest()).encode(), addr)


