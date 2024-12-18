"""
    Multi-threaded server to share files built on python3
    
    Usage: python3 server.py 12000
    
    coding: utf-8
    
    Author: Danny Li
"""
from socket import *
from threading import Thread, Lock
import sys, select, time, datetime

################################################################################
################################ STARTING SERVER ###############################
################################################################################

if len(sys.argv) != 2:
    print("\n===== Error usage, python3 server.py SERVER_PORT ======\n")
    exit(0)

################################################################################
############################### SERVER FUNCTIONS ###############################
################################################################################

def read_credentials():
    credentials = {}
    with open("credentials.txt", "r") as file:
        for line in file:
            username, password = line.strip().split(" ")
            credentials[username] = password
    return credentials

def check_heartbeat():
    while True:
        time.sleep(3)
        current_time = time.time()
        lock.acquire()
        try:
            inactive_clients = [username for username, info in active_clients.items() if current_time - info["heartbeat"] > 3]
            for username in inactive_clients:
                print(f"[server] {username} timed out. Removing from active clients.")
                del active_clients[username]
        finally:
            lock.release()

################################################################################
############################### SERVER VARIABLES ###############################
################################################################################
credentials = read_credentials() # {"username": password}
active_clients = {} # {"username": address, socket, heartbeat}
published_files = {} # {"filename": [username]}
lock = Lock()

################################################################################
################################# CLIENT THREAD ################################
################################################################################

class ClientThread(Thread):
    """
        Running the client thread - init and check which methods to run
    """
    
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_alive = True
        self.client_username = None
        self.client_upload_port_number = None
    
    def run(self):
        ERR_MSG = "INPUT_ERR"
        message = ''    
        while self.client_alive:
            try:
                message = self.client_socket.recv(1024).decode()
                if message == '':
                    self.disconnect_client()
                elif message.startswith("auth"):
                    self.process_auth(message)
                elif message.startswith("port"):
                    self.auth_process_uploading_port(message)
                elif message.startswith("hbt"):
                    self.process_heartbeat()
                elif message.startswith("get"):
                    self.process_get(message)
                elif message.startswith("lap"):
                    self.process_lap()
                elif message.startswith("lpf"):
                    self.process_lpf()
                elif message.startswith("pub"):
                    self.process_pub(message)
                elif message.startswith("sch"):
                    self.process_sch(message)
                elif message.startswith("unp"):
                    self.process_unp(message)
                elif message.startswith("xit"):
                    self.process_xit()
                else:
                    self.print_server_message(f"Sent ERR to {self.client_username}")
                    self.send_client_message(ERR_MSG)
            except Exception as e:
                self.print_server_message(f"Error with {self.client_username}: {str(e)}")
                self.disconnect_client()
                break
                    
    """
        Helper functions and background functions
        - send_client_message
        - print_server_message
        - disconnect_client
        - process_heartbeat
        - auth_process_uploading_port
    """ 
    def send_client_message(self, message):
        self.client_socket.send(message.encode())
    
    def print_server_message(self, message):
        current_timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        peer_port = self.client_address[1]
        print(f"{current_timestamp}: {peer_port}: {message}")
    
    def disconnect_client(self):
        self.client_alive = False
        if self.client_username and self.client_username in active_clients:
            lock.acquire()
            try:
                del active_clients[self.client_username]
            finally:
                lock.release()
        self.client_socket.close()

    def process_heartbeat(self):
        if self.client_username in active_clients:
            lock.acquire()
            try:
                active_clients[self.client_username]["heartbeat"] = time.time()
                self.print_server_message(f"Received HBT from {self.client_username}")
            finally:
                lock.release()

    def auth_process_uploading_port(self, message):
        try:
            _, upload_port = message.split()
        except ValueError:
            self.send_client_message("port ERR")
            return
        
        self.client_upload_port_number = int(upload_port)
        lock.acquire()
        try:
            if self.client_username in active_clients:
                active_clients[self.client_username]["upload_port"] = self.client_upload_port_number
                self.send_client_message("port OK")
        finally:
            lock.release()
        return
    """
        User input methods
        - process_auth
        - process_get
        - process_lap
        - process_lpf
        - process_pub
        - process_sch
        - process_unp
        - process_xit
    """
    def process_auth(self, message):
        auth_ok = "auth OK"
        auth_fail = "auth ERR"
        try:
            _, username, password = message.split()
        except ValueError:
            self.send_client_message(auth_fail)
            return
        
        self.client_username = username
        self.print_server_message(f"Received AUTH from {self.client_username}")
        if self.client_username not in credentials:
            self.print_server_message(f"Sent ERR to {self.client_username}")
            self.send_client_message(auth_fail)
            return 
    
        if credentials[self.client_username] != password:
            self.print_server_message(f"Sent ERR to {self.client_username}")
            self.send_client_message(auth_fail)
            return
        
        if self.client_username in active_clients:
            self.print_server_message(f"Sent ERR to {self.client_username}")
            self.send_client_message(auth_fail)
            return
        
        self.print_server_message(f"Sent OK to {self.client_username}")
        self.send_client_message(auth_ok)
        active_clients[self.client_username] = {
            "address": self.client_address,
            "socket": self.client_socket,
            "heartbeat": time.time()
        }
        return
        
    def process_get(self, message):
        self.print_server_message(f"Received GET from {self.client_username}")
        try:
            _, filename = message.split()
        except ValueError:
            self.send_client_message("get ERR")
            return
    
        if filename:
            lock.acquire()
            try:
                peers_with_file = [username for username in published_files[filename] if username != self.client_username]
                if peers_with_file:
                    peer_username = peers_with_file[0]
                    peer_address = active_clients[peer_username]["address"]
                    peer_upload_port = active_clients[peer_username]["upload_port"]
                    self.send_client_message(f"get {peer_address[0]} {peer_upload_port} {filename}")
                    self.print_server_message(f"Sent OK to {self.client_username}")
                else:
                    self.send_client_message("get ERR")
                    self.print_server_message(f"Sent ERR to {self.client_username}")
            finally:
                lock.release()
        else:
            self.send_client_message("get ERR")
            self.print_server_message(f"Sent ERR to {self.client_username}")
                
    def process_lap(self):
        lock.acquire()
        self.print_server_message(f"Received LAP from {self.client_username}")
        try:
            active_peers = [username for username in active_clients.keys() if username != self.client_username]
            if active_peers:
                self.send_client_message(f"lap {' '.join(active_peers)}")
            else:
                self.send_client_message("lap No active peers")
        finally:
            lock.release()
    
    def process_lpf(self):
        lock.acquire()
        self.print_server_message(f"Received LPF from {self.client_username}")
        try:
            published_by_user = [file for file, users in published_files.items() if self.client_username in users]
            if published_by_user:
                self.send_client_message(f"lpf {' '.join(published_by_user)}")
            else:
                self.send_client_message("lpf No files published")
        finally:
            lock.release()
    
    def process_pub(self, message):
        pub_success = "pub OK"
        pub_failure = "pub ERR"
        try:
            _, filename = message.split()
        except ValueError:
            self.send_client_message(pub_failure)
            return
        self.print_server_message(f"Received PUB from {self.client_username}")
        if filename:
            lock.acquire()
            try:
                if filename not in published_files:
                    published_files[filename] = set()  # Set will prevent duplicate values for key

                published_files[filename].add(self.client_username)
                self.print_server_message(f"Sent OK to {self.client_username}")
                self.send_client_message(pub_success)
            finally:
                lock.release()
        else:
            self.send_client_message(pub_failure)
            self.print_server_message(f"Sent ERR to {self.client_username}")
            
    def process_sch(self, message):
        try:
            _, substring = message.split()
        except ValueError:
            self.send_client_message("sch No files found")
            return

        search_results = []
        lock.acquire()
        self.print_server_message(f"Received SCH from {self.client_username}")
        try:
            if not substring:
                self.send_client_message("sch No files found")
                return
            
            for file, users in published_files.items():
                if substring in file and self.client_username not in users:
                    search_results.append(file)
                    
            if search_results:
                self.send_client_message(f"sch {' '.join(search_results)}")
            else:
                self.send_client_message("sch No files found")
        finally:
            lock.release()
    
    def process_unp(self, message):
        unp_success = "unp OK"
        unp_failure = "unp ERR"
        try:
            _, filename = message.split()
        except ValueError:
            self.send_client_message(unp_failure)
            return 

        self.print_server_message(f"Received UNP from {self.client_username}")
        if filename:
            lock.acquire()
            try:
                if filename in published_files and self.client_username in published_files[filename]:
                    published_files[filename].remove(self.client_username)
                    # If no users have the file published, remove the file from the published_files map
                    if not published_files[filename]:
                        del published_files[filename]
                    self.send_client_message(unp_success)
                    self.print_server_message(f"Sent OK to {self.client_username}")
                else:
                    self.send_client_message(unp_failure)
                    self.print_server_message(f"Sent ERR to {self.client_username}")
            finally:
                lock.release()
        else:
            self.send_client_message(unp_failure)
            self.print_server_message(f"Sent ERR to {self.client_username}")
    
    def process_xit(self):
        self.send_client_message("xit")
        self.disconnect_client()
    
################################################################################
################################## RUN SERVER ##################################
################################################################################
server_host = "127.0.0.1"
server_port = int(sys.argv[1])
server_address = (server_host, server_port)

# define socket for the server side and bind address
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)

# Start the heartbeat checking thread
heartbeat_checking_thread = Thread(target=check_heartbeat)
heartbeat_checking_thread.daemon = True
heartbeat_checking_thread.start()

# Start listening to server socket and make new threads for clients
while True:
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    client_thread = ClientThread(client_socket, client_address)
    client_thread.start()