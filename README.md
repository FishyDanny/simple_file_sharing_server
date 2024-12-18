# Simple File Share Server

## Overview

The **Simple File Share Server** is a multi-threaded application designed for efficient file sharing between clients using a TCP connection. It allows users to upload, download, publish, search, and unpublish files, all while maintaining a list of active peers. The system is built with Python 3 and leverages the `socket` library for communication and threading for concurrent operations.

---

## Features

- **Authentication:** Ensures secure access to the server with a username-password system.
- **File Publishing:** Clients can publish files, making them available for others to download.
- **File Downloading:** Enables file transfer between peers directly.
- **Peer Activity Tracking:** Lists active clients connected to the server.
- **File Search:** Search for files published by other peers using a substring query.
- **Unpublish Files:** Allows clients to remove their files from the shared pool.
- **Heartbeat Monitoring:** Maintains connection health by checking client activity periodically.

---

## Components

### Server (`server.py`)

- Runs a multi-threaded TCP server to handle multiple clients simultaneously.
- Manages user authentication, file publication, and peer-to-peer file transfer coordination.
- Periodically checks for inactive clients using a heartbeat system.

### Client (`client.py`)

- Provides a user-friendly interface for interacting with the server.
- Supports commands for file operations and peer management.
- Facilitates peer-to-peer file transfers via direct TCP connections.

---

## Prerequisites

- Python 3.x
- Ensure that `credentials.txt` is available in the server's working directory for user authentication.
  - Format: `<username> <password>` (one per line)

---

## Usage

### Server

Run the server script with the desired port number:

```bash
python3 server.py <PORT>
```

Example:

```bash
python3 server.py 12000
```

### Client

Run the client script, specifying the server's IP and port:

```bash
python3 client.py <SERVER_IP> <SERVER_PORT>
```

Example:

```bash
python3 client.py 127.0.0.1 12000
```

---

## Available Client Commands

- `auth <username> <password>`: Authenticate with the server.
- `pub <filename>`: Publish a file for sharing.
- `get <filename>`: Download a file from a peer.
- `lap`: List all active peers.
- `lpf`: List files published by the client.
- `sch <substring>`: Search for files containing the given substring.
- `unp <filename>`: Unpublish a file.
- `xit`: Exit the client application.

---

## File Sharing Process

1. **Publishing Files:**
   - Clients publish files, making them available for others.
2. **Searching for Files:**
   - Other clients can search for and locate files using substring queries.
3. **Downloading Files:**
   - Clients download files directly from peers via a TCP connection.
4. **Unpublishing Files:**
   - Files can be removed from sharing when no longer needed.

---

## Notes

- Use a secure network for communication to avoid interception of sensitive data.
- Ensure proper file permissions when publishing files to allow access for downloading clients.
- Currently only works with localhost
