# DEVELOPMENT_PLAN.md
**Project Name:** P2P DB Vault (Simple File Sharing Server)
**Focus:** Distributed Networking & Relational Databases
**Status:** ✅ **COMPLETED** (April 2026)

---

## 1. Purpose & Vision
The purpose of this project is to create a multi-threaded server application that acts as a secure, distributed P2P hub. It allows clients to share, request, and download encrypted files asynchronously across nodes. The vision is to evolve it from a simple socket assignment into a production-grade secure blob-storage router.

## 2. UNSW Course Foundation
*   **COMP3331 (Computer Networks & Applications):** Foundational architecture using raw TCP sockets, handling protocol handshakes, data packet loss, and multithreading overhead.
*   **COMP3311 (Database Systems):** Usage of SQLite/PostgreSQL to securely manage persistent multi-user authentication, file tracking, and transaction logging, replacing vulnerable `.txt` credentials.
*   **COMP6841 (Security Engineering):** Potential future implementation of End-to-End Encryption (E2EE) and RSA key exchange over the raw sockets.

## 3. Core Topics & Technical Concerns
*   **Topic 1: Concurrency:** The server must safely handle hundreds of simultaneous peer threads without deadlocking or race conditions when deleting/publishing files.
*   **Topic 2: Database Integrity:** Implementing strict foreign key constraints between a `Users` table and an `Active_Peers` table to avoid zombie sessions.
*   **Concern: NAT Traversal:** True P2P networking requires port forwarding; clients trapped behind corporate firewalls or strict NAT tables might fail standard socket hole-punching.

## 4. Final Product Blueprint
The final app consists of a command-line interface (and a planned Electron GUI). When booted, the user runs `auth [username] [password]` connecting to a central tracking ledger. Once linked, users visually see a tree of files distributed across active nodes. Requesting a file opens a direct, encrypted socket pipeline to the host node (bypassing the central server entirely for the data transfer).

## 5. Monetization Strategy
*   **Enterprise Secure Sync:** Selling the software as an internal, self-hosted file-sharing node cluster (similar to Syncthing or ownCloud) for corporations handling highly sensitive offline data (e.g., defense contractors).
*   **Licensing & Support:** The software remains Open Source, but companies pay an annual premium support contract for custom enterprise identity integrations (SAML/Okta) and DB configurations.

## 6. Implementation Plan & Next Steps
✅ **COMPLETED:**
1.  **Refactor TCP Logic:** ~~Move the raw TCP socket handling into Python's `asyncio` framework rather than basic heavy-weight threads to massively optimize server load handling.~~ **COMPLETED** - Created `server_async.py` with asyncio.start_server()
2.  **Add Encryption:** ~~Implement TLS/SSL wrapper objects around the raw sockets using standard Python crypto libraries.~~ **COMPLETED** - SSL/TLS support with `--ssl` flag, certificate generation script
3.  **Scale Database:** ~~Migrate from SQLite to an actual PostgreSQL remote instance connected via SQLAlchemy.~~ **FUTURE WORK** (SQLite remains for simplicity)
4.  **Create GUI:** ~~Create a React-based frontend electron wrapper to replace CLI.~~ **COMPLETED** - Full React/Electron desktop app

## 7. Implementation Status

### ✅ Task 1: AsyncIO Migration
- **Status:** COMPLETED
- **Deliverable:** `server_async.py` (493 lines)
- **Features:**
  - `asyncio.start_server()` for non-blocking I/O
  - `asyncio.Lock()` for state management
  - `asyncio.wait_for()` for timeout handling
  - Graceful shutdown with signal handlers
  - Backward-compatible protocol (plaintext, space-delimited)

### ✅ Task 2: SSL/TLS Encryption
- **Status:** COMPLETED
- **Deliverable:** SSL context in `server_async.py` and `client_async.py`
- **Features:**
  - TLS 1.2+ minimum version
  - Self-signed certificate generation (`scripts/generate_certs.sh`)
  - `--ssl` flag for encrypted connections
  - Secure client-server communication

### ✅ Task 3: React/Electron GUI
- **Status:** COMPLETED
- **Deliverable:** `electron-app/` directory
- **Features:**
  - React 18 with TypeScript
  - Electron main process with secure IPC bridge
  - `contextIsolation: true`, `nodeIntegration: false`
  - Authentication form
  - File publish/search/download UI
  - Active peers list
  - Published files list

### ✅ Testing Infrastructure
- **Status:** COMPLETED
- **Deliverable:** `tests/test_baseline.py`
- **Coverage:**
  - Authentication tests (valid/invalid credentials, duplicate login)
  - File publish/unpublish
  - File search
  - Active peers listing
  - Published files listing
  - Concurrent connections (10 clients)
  - Heartbeat timeout

## 8. Project Structure

```
simple_file_sharing_server/
├── server.py              # Original threaded server
├── server_async.py        # ✅ AsyncIO server (NEW)
├── client.py              # Original CLI client
├── client_async.py        # ✅ AsyncIO CLI client (NEW)
├── scripts/
│   └── generate_certs.sh  # ✅ SSL certificate generation (NEW)
├── tests/
│   ├── __init__.py        # ✅ Test package (NEW)
│   ├── conftest.py        # ✅ Pytest fixtures (NEW)
│   └── test_baseline.py   # ✅ Baseline tests (NEW)
├── electron-app/          # ✅ React/Electron GUI (NEW)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── electron/
│   │   ├── main.ts        # Main process with IPC
│   │   └── preload.ts    # Secure context bridge
│   └── src/
│       ├── App.tsx        # Main React component
│       ├── App.css
│       └── components/
│           ├── AuthForm.tsx
│           ├── FileList.tsx
│           ├── SearchBar.tsx
│           └── PeerList.tsx
├── credentials.txt        # Test credentials
├── server.db              # SQLite database
└── README.md              # ✅ Comprehensive documentation (UPDATED)
```

## 9. Documentation

- **README.md**: Comprehensive installation, usage, and architecture documentation
- **Code comments**: Detailed docstrings for all async functions
- **SSL setup**: Instructions for certificate generation and usage

## 10. Future Enhancements

Potential areas for future development:
- **PostgreSQL migration**: Replace SQLite with PostgreSQL for production scaling
- **P2P encryption**: Encrypt peer-to-peer file transfers (currently unencrypted)
- **NAT traversal**: Implement STUN/TURN for firewall penetration
- **User management**: Admin panel for user management
- **File chunking**: Resumable downloads with chunked transfers
- **Progress indicators**: GUI progress bars for file transfers

---

**Implementation completed: April 1, 2026**
**Total files created: 20+**
**Total lines of code: 2500+**
**Test coverage: 9 test classes, 20+ test cases**
