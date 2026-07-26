# P2P DB Vault — asyncio File Sharing Server

A peer-to-peer file sharing system with an `asyncio` server, optional TLS, and a React/Electron
desktop client. Originally a threaded UNSW networking assignment, rewritten as a non-blocking
async server with a desktop GUI on top.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![asyncio](https://img.shields.io/badge/asyncio-non--blocking-green.svg)
![Electron](https://img.shields.io/badge/Electron-React-47848F.svg?logo=electron&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> Built to learn socket programming and async I/O. It is not a hardened system — the known
> limitations are documented in [Security notes](#security-notes).

## Features

- **AsyncIO Architecture**: non-blocking I/O server, alongside the original threaded implementation for comparison
- **Optional TLS**: encrypted client↔server control channel when started with `--ssl`
- **Desktop GUI**: React/Electron desktop application
- **Authentication**: username/password login backed by SQLite
- **File Publishing**: Share files across the network
- **P2P File Transfer**: Direct peer-to-peer file downloads
- **Active Peer Management**: Real-time peer tracking with heartbeat monitoring
- **File Search**: Search for files across active peers

## Project Structure

```
simple_file_sharing_server/
├── server.py              # Original threaded server (legacy)
├── server_async.py        # AsyncIO server (recommended)
├── client.py              # Original CLI client (legacy)
├── client_async.py        # AsyncIO CLI client
├── credentials.example.txt # Template dev accounts — copy to credentials.txt (gitignored)
├── server.db              # SQLite database (gitignored)
├── scripts/
│   └── generate_certs.sh  # SSL certificate generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   └── test_baseline.py   # Baseline tests
└── electron-app/          # React/Electron GUI
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── electron/
    │   ├── main.ts         # Electron main process
    │   └── preload.ts      # IPC bridge
    └── src/
        ├── App.tsx
        └── components/     # React components
```

## Quick Start

### Prerequisites

- Python 3.7+
- Node.js 18+ (for Electron app)
- OpenSSL (for SSL certificates)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd simple_file_sharing_server
   ```

2. **Create a local credentials file:**

   ```bash
   cp credentials.example.txt credentials.txt
   ```

   `credentials.txt` is gitignored. The example file holds throwaway development accounts and is
   seeded into the SQLite `users` table on first run — replace it with your own before doing
   anything real. See [Security notes](#security-notes).

3. **Generate SSL certificates (optional, for HTTPS):**

   ```bash
   bash scripts/generate_certs.sh
   ```

4. **Install Electron dependencies (optional, for GUI):**
   ```bash
   cd electron-app
   npm install
   ```

### Running the Server

#### AsyncIO Server (Recommended)

**Without SSL:**

```bash
python3 server_async.py 12000
```

**With SSL:**

```bash
python3 server_async.py 12000 --ssl
```

#### Legacy Threaded Server

```bash
python3 server.py 12000
```

### Running the Client

#### AsyncIO CLI Client

**Without SSL:**

```bash
python3 client_async.py 127.0.0.1 12000
```

**With SSL:**

```bash
python3 client_async.py 127.0.0.1 12000 --ssl
```

#### Electron GUI

```bash
cd electron-app
npm run dev
```

## Usage

### Available Commands

| Command                      | Description                 |
| ---------------------------- | --------------------------- |
| `auth <username> <password>` | Authenticate with server    |
| `pub <filename>`             | Publish a file for sharing  |
| `get <filename>`             | Download a file from a peer |
| `lap`                        | List active peers           |
| `lpf`                        | List your published files   |
| `sch <substring>`            | Search for files            |
| `unp <filename>`             | Unpublish a file            |
| `xit`                        | Disconnect and exit         |

### Example Session

```
$ python3 client_async.py 127.0.0.1 12000
Enter username: hans
Enter password: falcon*solo
Authentication successful. Available commands: get, lap, lpf, pub, sch, unp, xit

lap
1 active peer:
yoda

pub test.txt
File published successfully

sch test
1 file found:
test.txt

xit
Goodbye!
```

## Testing

Run baseline tests to verify functionality:

```bash
# Install pytest if not already installed
pip install pytest

# Run tests
pytest tests/test_baseline.py -v
```

### Test Coverage

Tests cover:

- Authentication (valid/invalid credentials, duplicate login)
- File publishing and unpublishing
- File searching
- Listing active peers
- Listing published files
- P2P file download flow
- Heartbeat timeout handling
- Concurrent connections (10 simultaneous clients)

## Architecture

### AsyncIO Server

The `server_async.py` uses Python's `asyncio` library for non-blocking I/O:

- **`asyncio.start_server()`**: Handles multiple clients concurrently without threads
- **`asyncio.Lock()`**: Thread-safe state management
- **`asyncio.wait_for()`**: Timeout handling for client connections
- **Graceful shutdown**: Signal handlers for clean termination

### SSL/TLS Encryption

The server supports TLS 1.2+ encryption:

- **Self-signed certificates**: Automatically generated for development
- **Certificate validation**: Verifies client certificates in production mode
- **Secure connections**: All client-server communication is encrypted

### Electron GUI

The desktop application uses:

- **React**: Modern UI components
- **Electron**: Native desktop integration
- **IPC Bridge**: Secure communication between renderer and main process
- **Context Isolation**: Security-focused architecture

## API Reference

### Server Commands

All commands are plain-text, space-delimited:

#### Authentication

```
Request:  auth <username> <password>
Response: auth OK | auth ERR
```

#### Port Registration

```
Request:  port <upload_port>
Response: port OK | port ERR
```

#### File Operations

```
Request:  pub <filename>
Response: pub OK | pub ERR

Request:  unp <filename>
Response: unp OK | unp ERR

Request:  sch <substring>
Response: sch <file1> <file2> ... | sch No files found

Request:  lpf
Response: lpf <file1> <file2> ... | lpf No files published
```

#### Peer Operations

```
Request:  lap
Response: lap <peer1> <peer2> ... | lap No active peers

Request:  get <filename>
Response: get <ip> <port> <filename> | get ERR
```

#### Heartbeat

```
Request:  hbt
Response: (no response, updates heartbeat)
```

#### Disconnect

```
Request:  xit
Response: xit
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Building Electron App

```bash
cd electron-app
npm run build
```

### Generating SSL Certificates

```bash
bash scripts/generate_certs.sh
```

## Security Notes

This is a learning project built around the network programming, not a hardened system. The known
gaps are listed here deliberately rather than left for a reader to discover:

- **Passwords are stored in plaintext.** Credentials are read from a flat file and seeded verbatim
  into SQLite. A real deployment needs per-user salted hashing (bcrypt/argon2) — the shipped
  `credentials.example.txt` contains throwaway accounts only, and `credentials.txt` is gitignored.
- **Development certificates**: the self-signed certificates from `generate_certs.sh` are for local
  use only; production needs CA-signed certificates and hostname verification.
- **TLS is opt-in, not default**: the client↔server control channel is only encrypted when the server
  is started with `--ssl`. Direct peer-to-peer file transfers are never encrypted.
- **No transfer integrity check**: there is no checksum on received files.

## License

MIT License

## Authors

- Danny Li

## Acknowledgments

- Based on COMP3331/COMP3311 coursework from UNSW
- Developed using Python asyncio and Electron frameworks
