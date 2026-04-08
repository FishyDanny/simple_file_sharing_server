"""
    Asyncio client for P2P file sharing
    Usage: python3 client_async.py <SERVER_IP> <SERVER_PORT> [--ssl]
    coding: utf-8
    Author: Danny Li (refactored to asyncio)
"""
import asyncio
import sys
import os
import ssl
from pathlib import Path

################################################################################
################################ STARTING CLIENT ###############################
################################################################################

if len(sys.argv) < 3:
    print("\n===== Error usage, python3 client_async.py SERVER_IP SERVER_PORT [--ssl]\n")
    exit(0)

USE_SSL = "--ssl" in sys.argv
SERVER_HOST = [arg for arg in sys.argv[1:] if arg != "--ssl"][0]
SERVER_PORT = int([arg for arg in sys.argv[1:] if arg != "--ssl"][1])

async def send_heartbeat(writer):
    """Send periodic heartbeat to server"""
    while True:
        await asyncio.sleep(2)
        try:
            writer.write(b"hbt")
            await writer.drain()
        except:
            break

async def handle_file_upload(reader, writer, filename):
    """Handle file upload to peer"""
    try:
        file_size = os.path.getsize(filename)
        writer.write(f"size {file_size}".encode())
        await writer.drain()
        
        if await reader.read(1024) != b"ready":
            return
        
        with open(filename, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
    except Exception as e:
        print(f"Upload error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_file_download(peer_host, peer_port, filename):
    """Handle file download from peer"""
    try:
        reader, writer = await asyncio.open_connection(peer_host, peer_port)
        
        writer.write(f"download {filename}".encode())
        await writer.drain()
        
        size_data = await reader.read(1024)
        size_str = size_data.decode()
        if not size_str.startswith("size"):
            print(f"Invalid response from peer: {size_str}")
            return
        
        file_size = int(size_str.split()[1])
        writer.write(b"ready")
        await writer.drain()
        
        with open(filename, 'wb') as f:
            received = 0
            while received < file_size:
                data = await reader.read(4096)
                if not data:
                    break
                f.write(data)
                received += len(data)
        
        if received == file_size:
            print(f"{filename} downloaded successfully")
        else:
            print(f"{filename} download incomplete")
    except Exception as e:
        print(f"Download failed: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def upload_server(upload_port, published_files):
    """Listen for P2P download requests"""
    async def handle_peer(reader, writer):
        try:
            data = await reader.read(1024)
            if not data:
                return
            
            parts = data.decode().split()
            if len(parts) < 2 or parts[0] != "download":
                return
            
            filename = parts[1]
            if filename in published_files:
                await handle_file_upload(reader, writer, filename)
        except:
            pass
        finally:
            writer.close()
            await writer.wait_closed()
    
    server = await asyncio.start_server(handle_peer, host='0.0.0.0', port=upload_port)
    async with server:
        await server.serve_forever()

async def create_ssl_context():
    """Create SSL context for client"""
    cert_file = Path("server.crt")
    
    if not cert_file.exists():
        print("Warning: server.crt not found. SSL connection may fail.")
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    if cert_file.exists():
        ssl_context.load_verify_locations(cert_file)
    else:
        ssl_context.verify_mode = ssl.CERT_NONE
    
    return ssl_context

async def main():
    """Main client entry point"""
    if USE_SSL:
        ssl_context = await create_ssl_context()
        reader, writer = await asyncio.open_connection(
            SERVER_HOST, SERVER_PORT, ssl=ssl_context
        )
    else:
        reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    
    # Authentication
    authenticated = False
    while not authenticated:
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        writer.write(f"auth {username} {password}".encode())
        await writer.drain()
        
        response = (await reader.read(1024)).decode()
        
        if response == "auth OK":
            authenticated = True
            print("Authentication successful. Available commands: get, lap, lpf, pub, sch, unp, xit")
            
            # Start heartbeat
            asyncio.create_task(send_heartbeat(writer))
            
            # Start upload server
            upload_server_sock = await asyncio.start_server(
                lambda r, w: None, host='0.0.0.0', port=0
            )
            upload_port = upload_server_sock.sockets[0].getsockname()[1]
            upload_server_sock.close()
            await upload_server_sock.wait_closed()
            
            # Create new upload server
            upload_server = await asyncio.start_server(
                lambda r, w: None, host='0.0.0.0', port=upload_port
            )
            asyncio.create_task(upload_server.serve_forever())
            
            # Send upload port to server
            writer.write(f"port {upload_port}".encode())
            await writer.drain()
            await reader.read(1024)  # Wait for "port OK"
        else:
            print("Authentication failed. Please try again.")
    
    # Main command loop
    published_files = set()
    
    try:
        while True:
            message = input("")
            if not message:
                continue
            
            writer.write(message.encode())
            await writer.drain()
            
            response = (await reader.read(1024)).decode()
            
            if message.startswith("get"):
                parts = response.split()
                if len(parts) >= 4:
                    filename = parts[3]
                    peer_host = parts[1]
                    peer_port = int(parts[2])
                    asyncio.create_task(handle_file_download(peer_host, peer_port, filename))
            elif message.startswith("lap"):
                peers = ' '.join(parts[1:])
                if peers == "No active peers":
                    print(peers)
                else:
                    peer_list = peers.split()
                    print(f"{len(peer_list)} active peer{'s' if len(peer_list) > 1 else ''}:")
                    for peer in peer_list:
                        print(peer)
            elif message.startswith("lpf"):
                files = ' '.join(parts[1:])
                if files == "No files published":
                    print(files)
                else:
                    file_list = files.split()
                    print(f"{len(file_list)} published file{'s' if len(file_list) > 1 else ''}:")
                    for f in file_list:
                        print(f)
            elif message.startswith("pub"):
                _, filename = message.split()
                published_files.add(filename)
                print("File published successfully" if response == "pub OK" else "Failed to publish file")
            elif message.startswith("sch"):
                files = ' '.join(parts[1:])
                if files == "No files found":
                    print(files)
                else:
                    file_list = files.split()
                    print(f"{len(file_list)} file{'s' if len(file_list) > 1 else ''} found:")
                    for f in file_list:
                        print(f)
            elif message.startswith("unp"):
                _, filename = message.split()
                published_files.discard(filename)
                print("File unpublished successfully" if response == "unp OK" else "Failed to unpublish file")
            elif message.startswith("xit"):
                print("Goodbye!")
                break
            else:
                print(response)
    except KeyboardInterrupt:
        print("\nDisconnected.")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
