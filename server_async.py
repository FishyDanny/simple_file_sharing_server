"""
    Asyncio-based server for P2P file sharing
    Usage: python3 server_async.py <PORT> [--ssl]
    coding: utf-8
    Author: Danny Li (refactored to asyncio)
"""
import asyncio
import sys
import time
import datetime
import sqlite3
import ssl
from pathlib import Path

################################################################################
################################ STARTING SERVER ###############################
################################################################################

if len(sys.argv) < 2:
    print("\n===== Error usage, python3 server_async.py SERVER_PORT [--ssl]\n")
    exit(0)

USE_SSL = "--ssl" in sys.argv
SERVER_PORT = int([arg for arg in sys.argv[1:] if arg != "--ssl"][0])

################################################################################
############################### SERVER FUNCTIONS ###############################
################################################################################

async def init_db():
    """Initialize the SQLite database with users table"""
    conn = sqlite3.connect('server.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        try:
            with open("credentials.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        username, password = parts
                        c.execute('INSERT OR IGNORE INTO users VALUES (?, ?)', (username, password))
            conn.commit()
        except FileNotFoundError:
            pass
    conn.close()

def check_auth_db(username: str, password: str) -> bool:
    """Check if username and password match"""
    conn = sqlite3.connect('server.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == password)

def user_exists_db(username: str) -> bool:
    """Check if username exists in database"""
    conn = sqlite3.connect('server.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return bool(row)

################################################################################
############################### SERVER STATE ##################################
################################################################################

active_clients = {}  # {"username": {"reader": reader, "writer": writer, "heartbeat": float, "upload_port": int, "address": tuple}}
published_files = {}  # {"filename": set(usernames)}
state_lock = None  # Will be initialized in main

async def check_heartbeat():
    """Periodically remove inactive clients"""
    global state_lock
    while True:
        await asyncio.sleep(3)
        current_time = time.time()
        async with state_lock:
            inactive_clients = [
                username for username, info in active_clients.items()
                if current_time - info["heartbeat"] > 3
            ]
            for username in inactive_clients:
                print(f"[server] {username} timed out. Removing from active clients.")
                if username in active_clients:
                    try:
                        active_clients[username]["writer"].close()
                        await active_clients[username]["writer"].wait_closed()
                    except:
                        pass
                    del active_clients[username]

################################################################################
############################### CLIENT HANDLER ################################
################################################################################

class ClientHandler:
    """Async handler for a single client connection"""
    
    def __init__(self, reader, writer, address):
        self.reader = reader
        self.writer = writer
        self.address = address
        self.client_alive = True
        self.client_username = None
        self.client_upload_port = None
    
    def log(self, message: str):
        """Print server message with timestamp"""
        current_timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        peer_port = self.address[1]
        print(f"{current_timestamp}: {peer_port}: {message}")
    
    async def send(self, message: str):
        """Send message to client"""
        self.writer.write(message.encode())
        await self.writer.drain()
    
    async def disconnect(self):
        """Cleanly disconnect client"""
        self.client_alive = False
        if self.client_username and self.client_username in active_clients:
            async with state_lock:
                if self.client_username in active_clients:
                    del active_clients[self.client_username]
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except:
            pass
    
    async def handle(self):
        """Main message handling loop"""
        global state_lock
        
        while self.client_alive:
            try:
                data = await asyncio.wait_for(self.reader.read(1024), timeout=10.0)
                if not data:
                    await self.disconnect()
                    break
                
                message = data.decode()
                
                if message.startswith("auth"):
                    await self.process_auth(message)
                elif message.startswith("port"):
                    await self.process_port(message)
                elif message.startswith("hbt"):
                    await self.process_heartbeat()
                elif message.startswith("get"):
                    await self.process_get(message)
                elif message.startswith("lap"):
                    await self.process_lap()
                elif message.startswith("lpf"):
                    await self.process_lpf()
                elif message.startswith("pub"):
                    await self.process_pub(message)
                elif message.startswith("sch"):
                    await self.process_sch(message)
                elif message.startswith("unp"):
                    await self.process_unp(message)
                elif message.startswith("xit"):
                    await self.process_xit()
                else:
                    self.log(f"Sent ERR to {self.client_username}")
                    await self.send("INPUT_ERR")
                    
            except asyncio.TimeoutError:
                await self.disconnect()
                break
            except ConnectionResetError:
                await self.disconnect()
                break
            except Exception as e:
                self.log(f"Error with {self.client_username}: {str(e)}")
                await self.disconnect()
                break
    
    async def process_auth(self, message: str):
        """Handle authentication request"""
        try:
            parts = message.split()
            if len(parts) < 3:
                await self.send("auth ERR")
                return
            _, username, password = parts[0], parts[1], " ".join(parts[2:])
        except (ValueError, IndexError):
            await self.send("auth ERR")
            return
        
        self.client_username = username
        self.log(f"Received AUTH from {self.client_username}")
        
        if not user_exists_db(self.client_username):
            self.log(f"Sent ERR to {self.client_username}")
            await self.send("auth ERR")
            return
        
        if not check_auth_db(self.client_username, password):
            self.log(f"Sent ERR to {self.client_username}")
            await self.send("auth ERR")
            return
        
        async with state_lock:
            if self.client_username in active_clients:
                self.log(f"Sent ERR to {self.client_username}")
                await self.send("auth ERR")
                return
            
            active_clients[self.client_username] = {
                "address": self.address,
                "reader": self.reader,
                "writer": self.writer,
                "heartbeat": time.time(),
                "upload_port": None
            }
        
        self.log(f"Sent OK to {self.client_username}")
        await self.send("auth OK")
    
    async def process_port(self, message: str):
        """Handle upload port registration"""
        try:
            _, upload_port_str = message.split()
            upload_port = int(upload_port_str)
        except (ValueError, IndexError):
            await self.send("port ERR")
            return
        
        self.client_upload_port = upload_port
        
        async with state_lock:
            if self.client_username in active_clients:
                active_clients[self.client_username]["upload_port"] = upload_port
                await self.send("port OK")
            else:
                await self.send("port ERR")
    
    async def process_heartbeat(self):
        """Handle heartbeat update"""
        async with state_lock:
            if self.client_username in active_clients:
                active_clients[self.client_username]["heartbeat"] = time.time()
                self.log(f"Received HBT from {self.client_username}")
    
    async def process_get(self, message: str):
        """Handle file request"""
        self.log(f"Received GET from {self.client_username}")
        try:
            _, filename = message.split()
        except ValueError:
            await self.send("get ERR")
            return
        
        async with state_lock:
            if filename in published_files:
                peers_with_file = [
                    username for username in published_files[filename]
                    if username != self.client_username and username in active_clients
                ]
                
                if peers_with_file:
                    peer_username = peers_with_file[0]
                    peer_info = active_clients[peer_username]
                    peer_address = peer_info["address"]
                    peer_upload_port = peer_info.get("upload_port")
                    
                    if peer_upload_port:
                        await self.send(f"get {peer_address[0]} {peer_upload_port} {filename}")
                        self.log(f"Sent OK to {self.client_username}")
                        return
        
        await self.send("get ERR")
        self.log(f"Sent ERR to {self.client_username}")
    
    async def process_lap(self):
        """Handle list active peers request"""
        async with state_lock:
            self.log(f"Received LAP from {self.client_username}")
            active_peers = [
                username for username in active_clients.keys()
                if username != self.client_username
            ]
            
            if active_peers:
                await self.send(f"lap {' '.join(active_peers)}")
            else:
                await self.send("lap No active peers")
    
    async def process_lpf(self):
        """Handle list published files request"""
        async with state_lock:
            self.log(f"Received LPF from {self.client_username}")
            published_by_user = [
                file for file, users in published_files.items()
                if self.client_username in users
            ]
            
            if published_by_user:
                await self.send(f"lpf {' '.join(published_by_user)}")
            else:
                await self.send("lpf No files published")
    
    async def process_pub(self, message: str):
        """Handle file publish request"""
        try:
            _, filename = message.split()
        except ValueError:
            await self.send("pub ERR")
            return
        
        self.log(f"Received PUB from {self.client_username}")
        
        async with state_lock:
            if filename not in published_files:
                published_files[filename] = set()
            
            published_files[filename].add(self.client_username)
            self.log(f"Sent OK to {self.client_username}")
            await self.send("pub OK")
    
    async def process_sch(self, message: str):
        """Handle file search request"""
        try:
            _, substring = message.split()
        except ValueError:
            await self.send("sch No files found")
            return
        
        self.log(f"Received SCH from {self.client_username}")
        
        async with state_lock:
            search_results = []
            
            for file, users in published_files.items():
                if substring in file and self.client_username not in users:
                    search_results.append(file)
            
            if search_results:
                await self.send(f"sch {' '.join(search_results)}")
            else:
                await self.send("sch No files found")
    
    async def process_unp(self, message: str):
        """Handle file unpublish request"""
        try:
            _, filename = message.split()
        except ValueError:
            await self.send("unp ERR")
            return
        
        self.log(f"Received UNP from {self.client_username}")
        
        async with state_lock:
            if filename in published_files and self.client_username in published_files[filename]:
                published_files[filename].discard(self.client_username)
                
                if not published_files[filename]:
                    del published_files[filename]
                
                await self.send("unp OK")
                self.log(f"Sent OK to {self.client_username}")
            else:
                await self.send("unp ERR")
                self.log(f"Sent ERR to {self.client_username}")
    
    async def process_xit(self):
        """Handle exit request"""
        await self.send("xit")
        await self.disconnect()

async def handle_client(reader, writer):
    """Handle incoming client connection"""
    address = writer.get_extra_info('peername')
    handler = ClientHandler(reader, writer, address)
    await handler.handle()

def create_ssl_context():
    """Create SSL context for secure connections"""
    cert_file = Path("server.crt")
    key_file = Path("server.key")
    
    if not cert_file.exists() or not key_file.exists():
        import subprocess
        print("SSL certificates not found. Generating self-signed certificates...")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-keyout", "server.key",
            "-out", "server.crt",
            "-days", "365",
            "-subj", "/CN=localhost"
        ], check=True, capture_output=True)
        print("Self-signed certificates generated successfully.")
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_file, key_file)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    return ssl_context

async def main():
    """Main entry point for asyncio server"""
    global state_lock
    
    await init_db()
    state_lock = asyncio.Lock()
    
    if USE_SSL:
        ssl_context = create_ssl_context()
        server = await asyncio.start_server(
            handle_client,
            host="127.0.0.1",
            port=SERVER_PORT,
            ssl=ssl_context
        )
        print(f"SSL-encrypted asyncio server started on port {SERVER_PORT}")
    else:
        server = await asyncio.start_server(
            handle_client,
            host="127.0.0.1",
            port=SERVER_PORT
        )
        print(f"Asyncio server started on port {SERVER_PORT}")
    
    asyncio.create_task(check_heartbeat())
    
    address = server.sockets[0].getsockname()
    print(f"Listening on {address}")
    
    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        print("\nServer shutting down...")
    except KeyboardInterrupt:
        print("\nServer shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
