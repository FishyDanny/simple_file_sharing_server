"""
    Client for file sharing service
    Usage: python3 client.py <SERVER_IP> <SERVER_PORT>
    coding: utf-8
    Author: Danny Li
"""
from socket import *
import sys
import threading
import time
import os 

################################################################################
################################ STARTING CLIENT ###############################
################################################################################
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 client.py SERVER_IP SERVER_PORT ======\n")
    exit(0)
    
server_host = sys.argv[1]
server_port = int(sys.argv[2])
server_address = (server_host, server_port)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(server_address)

################################################################################
########################## CLIENT BACKGROUND FUNCTIONS #########################
################################################################################
def send_heartbeat():
    while True:
        time.sleep(2)
        client_socket.sendall("hbt".encode())

# Pre-processing and initiating upload to server of client upload info
def send_port_number():
    global upload_port
    upload_socket = socket(AF_INET, SOCK_STREAM)
    upload_socket.bind(('', 0))
    upload_port = upload_socket.getsockname()[1]
    upload_socket.listen(5)
    
    # Tell server about upload port
    client_socket.sendall(f"port {upload_port}".encode())
    response = client_socket.recv(1024).decode()

    if response == "port ERR":
        return
    
    while True:
        try:
            peer_socket, peer_address = upload_socket.accept()
            upload_thread = threading.Thread(target=handle_file_upload, args=(peer_socket,))
            upload_thread.daemon = True
            upload_thread.start()
        except:
            break
            
# Uplading the file
def handle_file_upload(peer_socket): # handle_single_upload
    try:
        request = peer_socket.recv(1024).decode()
        if not request.startswith("download"):
            return
    
        filename = request.split()[1]
        file_size = os.path.getsize(filename)
        peer_socket.sendall(f"size {file_size}".encode())
        
        # Wait for ready signal
        if peer_socket.recv(1024).decode() != "ready":
            return
            
        # Send file in chunks
        with open(filename, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                peer_socket.sendall(data)
                
    except Exception:
        pass
    finally:
        peer_socket.close()

# Downloading the file
def handle_file_download(peer_host, peer_port, filename): # handle_file_transfer
    try:
        # Create a new socket for peer connection
        peer_socket = socket(AF_INET, SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        
        # Send file request
        request = f"download {filename}"
        peer_socket.sendall(request.encode())
        
        # Receive file size first
        size_data = peer_socket.recv(1024).decode()
        if not size_data.startswith("size"):
            raise Exception("Invalid response from peer")
            
        file_size = int(size_data.split()[1])
        
        # Send acknowledgment
        peer_socket.sendall("ready".encode())
        
        # Receive and write file
        with open(filename, 'wb') as file:
            received_size = 0
            while received_size < file_size:
                data = peer_socket.recv(4096)
                if not data:
                    break
                file.write(data)
                received_size += len(data)
                
        if received_size == file_size:
            print(f"{filename} downloaded successfully")
        else:
            print(f"{filename} download failed")
                
    except Exception as e:
        print(f"File transfer failed 6 {str(e)}")
    finally:
        peer_socket.close()

################################################################################
############################ CLIENT INPUT FUNCTIONS ############################
################################################################################
def command_auth():
    auth_ok = "auth OK"
    auth_fail = "auth ERR"
    authenticated = False
    
    while not authenticated:
        username = input("Enter username: ")
        password = input("Enter password: ")
        credentials = f"auth {username} {password}"
        client_socket.sendall(credentials.encode())
        
        received_message = client_socket.recv(1024).decode()
        
        if received_message == auth_ok:
            authenticated = True
            print("Available commands are: get, lap, lpf, pub, sch, unp, xit")
            
            # Start heartbeat thread
            heartbeat_thread = threading.Thread(target=send_heartbeat)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
            
            # Start uploading handler thread
            upload_handler_thread = threading.Thread(target=send_port_number)
            upload_handler_thread.daemon = True
            upload_handler_thread.start()
            
            return authenticated
        elif received_message == auth_fail:
            print("Authentication failed. Please try again.")
        else:
            print("Unexpected response from server")

def command_get(fileinfo):
    try:
        _, peer_host, peer_port, filename = fileinfo.split()
    except ValueError:
        print("File not found")
        return
    
    try:
        transfer_thread = threading.Thread(target=handle_file_download,
                                           args=(peer_host, int(peer_port), filename))
        transfer_thread.daemon = True
        transfer_thread.start()
    except:
        print("File not found")
    
def command_lap(message):
    peers = ' '.join(message.split()[1:])
    if peers == "No active peers":
        print(peers)
    else:
        peers_list = peers.split()
        peer_count = len(peers_list)
        if peer_count == 1:
            print(f"1 active peer:")
        else:
            print(f"{peer_count} active peers:")
        for peer in peers_list:
            print(peer)
    return

def command_lpf(message):
    files = ' '.join(message.split()[1:])
    if files == "No files published":
        print(files)
    else:
        files_list = files.split()
        file_count = len(files_list)
        if file_count == 1:
            print(f"1 published file:")
        else:
            print(f"{file_count} published files:")
        for file in files_list:
            print(file)
    return

def command_pub(message):
    pub_ok = "pub OK"
    pub_fail = "pub ERR"
    if message == pub_ok:
        print("File published successfully")
    elif message == pub_fail:
        print("Failed to publish file")
    else:
        print("Unexpected response from server")
    return

def command_sch(message):
    files = ' '.join(message.split()[1:])
    if not files or files == "No files found" or files == "INPUT_ERR":
        print("No files found")
    else:
        files_list = files.split()
        file_count = len(files_list)
        if file_count == 1:
            print(f"1 file found:")
        else:
            print(f"{file_count} files found:")
        for file in files_list:
            print(file)
    return

def command_unp(message):
    unp_ok = "unp OK"
    unp_fail = "unp ERR"
    if message == unp_ok:
        print("File unpublished successfully")
    elif message == unp_fail:
        print("Failed to unpublish file")
    else:
        print("Unexpected response from server")
    return

################################################################################
################################## RUN CLIENT ##################################
################################################################################
authenticated = command_auth()
while authenticated:
    message = input("")
    client_socket.sendall(message.encode())
    received_message = client_socket.recv(1024).decode()
    
    if received_message == "":
        print("Message from server is empty")
    elif received_message.startswith("get"):
        command_get(received_message)
    elif received_message.startswith("lap"):
        command_lap(received_message)
    elif received_message.startswith("lpf"):
        command_lpf(received_message)
    elif received_message.startswith("pub"):
        command_pub(received_message)
    elif received_message.startswith("sch"):
        command_sch(received_message)
    elif received_message.startswith("unp"):
        command_unp(received_message)
    elif received_message.startswith("xit"):
        print("Goodbye!")
        break
    else:
        print("Invalid command")
        
client_socket.close()