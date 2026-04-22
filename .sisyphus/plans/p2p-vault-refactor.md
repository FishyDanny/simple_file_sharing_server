# P2P DB Vault: Async + SSL + Electron Refactor

## TL;DR

> **Quick Summary**: Migrate the existing threaded Python file sharing server to asyncio, add SSL/TLS encryption for secure communication, and build a React/Electron GUI to replace the CLI client.

> **Deliverables**:
> - `server_async.py` - Asyncio-based server with SSL/TLS support
> - `client_async.py` - Asyncio-based CLI client (for backwards compatibility)
> - `electron-app/` - React/Electron desktop application
> - `tests/` - Characterization tests for baseline validation
> - SSL certificates for development

> **Estimated Effort**: Large (3 major workstreams, infrastructure changes)
> **Parallel Execution**: YES - 3 waves after test baseline
> **Critical Path**: Characterization Tests → AsyncIO Server → SSL/TLS → Electron GUI → Integration Tests

---

## Context

### Original Request
Implement all items from DEVELOPMENT_PLAN.md:
1. Migrate `threading` module to `asyncio` for non-blocking I/O
2. Wrap socket connections in `ssl.wrap_socket` wrapper (SSL/TLS encryption)
3. Create React-based frontend Electron wrapper to replace CLI

### Interview Summary
**Key Discussions**:
- Server.py asyncio migration is primary focus
- Client.py migration is secondary (Electron replaces CLI anyway)
- SSL/TLS on server socket only (P2P encryption is future work)
- No existing test infrastructure - characterization tests required FIRST
- React/Electron will use main process bridge pattern for socket communication

**Research Findings**:
- Current server.py uses `threading.Thread` per client with `threading.Lock` for shared state
- Current client.py has 4 threading patterns (heartbeat, upload socket, download handler, upload handler)
- P2P file transfers are unencrypted peer-to-peer connections
- Message protocol is plaintext, space-delimited (e.g., `auth user pass` → `auth OK`)
- No graceful shutdown handling, no signal handlers

### Metis Review
**Identified Gaps** (addressed):
- P2P encryption scope: Clarified as OUT OF SCOPE (server-only SSL/TLS)
- Client.py migration: IN SCOPE (creates async CLI client for backwards compatibility)
- Tests: Characterization tests MUST be written before any migration
- Electron IPC: Main process bridge pattern confirmed
- Certificates: Self-signed for dev, document generation in README

---

## Work Objectives

### Core Objective
Transform the existing synchronous threaded Python file server into a modern async architecture with TLS encryption and a professional desktop GUI, while preserving 100% backward compatibility with the existing wire protocol.

### Concrete Deliverables
- Characterization test suite proving baseline functionality
- `server_async.py` with `asyncio.start_server()` and `asyncio.Lock()`
- SSL/TLS context with certificate generation script
- `client_async.py` using `asyncio.open_connection()` and `aiofiles`
- Electron package with React frontend and secure IPC bridge

### Definition of Done
- [ ] All characterization tests pass on new asyncio implementation
- [ ] Plaintext connections are rejected; SSL connections succeed
- [ ] React/Electron app can authenticate, publish, search, download files
- [ ] 10 concurrent connections handled without deadlock or race conditions
- [ ] Graceful shutdown on SIGINT/SIGTERM

### Must Have
- AsyncIO server replacing threaded server
- SSL/TLS encryption on client↔server communication
- React/Electron GUI with CLI feature parity (8 commands)
- Characterization tests before any changes

### Must NOT Have (Guardrails)
- ❌ PostgreSQL migration (not in task list)
- ❌ P2P encryption (server-only for this phase)
- ❌ NAT traversal fixes (future work)
- ❌ Type hints/modernization outside migration scope
- ❌ Drag-and-drop, progress bars, file preview (feature additions)
- ❌ Breaking wire protocol changes (must stay compatible)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Infrastructure
- **Infrastructure exists**: NO (no tests currently)
- **Automated tests**: Tests after (characterization tests first, then write tests alongside implementation)
- **Framework**: pytest with asyncio support
- **Test approach**: Characterization tests for baseline → Unit tests for new code

### QA Policy
Every task includes agent-executed QA scenarios with evidence capture in `.sisyphus/evidence/`.

- **Backend/CLI**: Bash commands (pytest, curl, nc) — Run commands, assert exit codes, capture output
- **Electron/GUI**: Playwright — Navigate, interact, assert DOM, screenshot
- **Integration**: Multi-process Bash — Start server, start client, verify communication

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (Foundation — MUST COMPLETE FIRST):
└── Task 0: Characterization tests [unspecified-high]
    → Blocks ALL other tasks
    → Establishes baseline behavior

Wave 1 (Core AsyncIO Server):
├── Task 1: AsyncIO server scaffolding [deep]
├── Task 2: AsyncIO client handler [deep]
├── Task 3: AsyncIO state management [unspecified-high]
└── Task 4: Graceful shutdown handling [quick]

Wave 2 (SSL/TLS Encryption):
├── Task 5: SSL certificate generation [quick]
├── Task 6: Server SSL context [unspecified-high]
├── Task 7: Client SSL connection [unspecified-high]
└── Task 8: SSL integration tests [unspecified-high]

Wave 3 (Electron GUI):
├── Task 9: Electron project setup [quick]
├── Task 10: React auth component [visual-engineering]
├── Task 11: IPC bridge implementation [deep]
├── Task 12: File operations UI [visual-engineering]
└── Task 13: Electron packaging [unspecified-high]

Wave 4 (Integration & Polish):
├── Task 14: End-to-end integration tests [deep]
├── Task 15: SSL handshake edge cases [unspecified-high]
├── Task 16: Concurrent load testing [unspecified-high]
└── Task 17: Documentation update [writing]

Wave FINAL (Verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 0 | — | 1-17 |
| 1 | 0 | 2, 3, 4 |
| 2 | 1 | 5 |
| 3 | 1 | 5 |
| 4 | 1 | 5 |
| 5 | — | 6 |
| 6 | 5 | 7 |
| 7 | 6 | 8 |
| 8 | 7 | 14 |
| 9 | — | 10, 11 |
| 10 | 9 | 12 |
| 11 | 9 | 12 |
| 12 | 10, 11 | 13 |
| 13 | 12 | 14 |
| 14 | 8, 13 | F1-F4 |
| 15 | 8 | F1-F4 |
| 16 | 14 | F1-F4 |
| 17 | 14 | — |
| F1-F4 | 14 | — |

---

## TODOs

- [ ] 0. Characterization Tests (BASELINE - CRITICAL)

  **What to do**:
  - Create `tests/test_baseline.py` with tests for current implementation
  - Test authentication flow (auth command)
  - Test file publish flow (pub command)
  - Test file search flow (sch command)
  - Test file unpublish flow (unp command)
  - Test list active peers (lap command)
  - Test list published files (lpf command)
  - Test P2P file download (get command)
  - Test heartbeat timeout (client removed after 3+ seconds silence)
  - Test concurrent connections (10 simultaneous clients)
  - Run ALL tests against current server.py/client.py before any changes

  **Must NOT do**:
  - Do NOT modify server.py or client.py
  - Do NOT skip any command testing
  - Do NOT proceed to Task 1 until ALL tests pass

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: Testing infrastructure setup is straightforward engineering work

  **Parallelization**:
  - **Can Run In Parallel**: NO - Must complete BEFORE all other tasks
  - **Blocks**: Tasks 1-17, F1-F4
  - **Blocked By**: None (can start immediately)

  **References**:
  - `server.py:80-359` - ClientThread class handles all commands
  - `client.py:131-163` - Authentication flow
  - `client.py:164-178` - File download command
  - `credentials.txt` - Test users for authentication tests

  **QA Scenarios**:

  ```
  Scenario: Authentication baseline verification
    Tool: Bash (pytest)
    Preconditions: server.py running on port 12000, credentials.txt has user "hans" with password "falcon*solo"
    Steps:
      1. pytest tests/test_baseline.py::test_authentication -v
      2. Assert: test passes with "auth hans falcon*solo" → "auth OK"
    Expected Result: Authentication test passes
    Failure Indicators: Connection refused, wrong response format, timeout
    Evidence: .sisyphus/evidence/task-0-auth-baseline.txt

  Scenario: Concurrent connections baseline
    Tool: Bash (pytest)
    Preconditions: server.py running
    Steps:
      1. pytest tests/test_baseline.py::test_concurrent_connections -v
      2. Assert: 10 clients connect and authenticate simultaneously without error
    Expected Result: All 10 connections succeed within 5 seconds
    Evidence: .sisyphus/evidence/task-0-concurrent-baseline.txt
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all baseline tests pass
  - [ ] Server logs during test execution

  **Commit**: YES
  - Message: `test: add characterization tests for baseline`
  - Files: `tests/test_baseline.py`, `tests/conftest.py`
  - Pre-commit: `pytest tests/test_baseline.py -v`

---

- [ ] 1. AsyncIO Server Scaffolding

  **What to do**:
  - Create `server_async.py` with `asyncio.start_server()` pattern
  - Define `async def handle_client(reader, writer)` handler
  - Initialize `asyncio.Lock()` for shared state (`active_clients`, `published_files`)
  - Implement basic `async def main()` entry point
  - Add signal handlers for graceful shutdown (SIGINT, SIGTERM)
  - Keep message protocol identical: `auth`, `port`, `hbt`, `get`, `lap`, `lpf`, `pub`, `sch`, `unp`, `xit`

  **Must NOT do**:
  - Do NOT change message format (must remain compatible with existing client)
  - Do NOT modify original server.py (keep for comparison)
  - Do NOT add features beyond asyncio scaffolding

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reasoning**: Core architecture change requires deep understanding

  **Parallelization**:
  - **Can Run In Parallel**: NO - Foundation for Wave 1
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: Task 0 (characterization tests)

  **References**:
  - `server.py:80-359` - Current ClientThread implementation to mirror
  - `server.py:56-66` - Heartbeat check pattern
  - `server.py:71-74` - Global state variables
  - Python docs: `asyncio.start_server()` pattern

  **QA Scenarios**:

  ```
  Scenario: AsyncIO server starts and accepts connections
    Tool: Bash (nc)
    Preconditions: server_async.py not running, port 12001 available
    Steps:
      1. python3 server_async.py 12001 &
      2. sleep 2
      3. nc -z localhost 12001 && echo "PASS: Server listening" || echo "FAIL: Not listening"
      4. kill %1
    Expected Result: Server starts without error, accepts TCP connections
    Failure Indicators: Port already in use, import error, asyncio error
    Evidence: .sisyphus/evidence/task-1-server-start.txt

  Scenario: Message protocol unchanged
    Tool: Bash (nc)
    Preconditions: server_async.py running on port 12001
    Steps:
      1. echo "auth hans falcon*solo" | nc localhost 12001
      2. Assert response is "auth OK" or "auth ERR"
    Expected Result: Same response format as original server
    Evidence: .sisyphus/evidence/task-1-protocol.txt
  ```

  **Commit**: YES
  - Message: `feat(server): add asyncio server scaffolding`
  - Files: `server_async.py`
  - Pre-commit: `python3 server_async.py 12001 & sleep 2 && kill %1`

---

- [ ] 2. AsyncIO Client Handler Implementation

  **What to do**:
  - Implement `ClientHandler` class with async methods
  - Convert each command handler to `async def process_*()`:
    - `process_auth()` - handle authentication
    - `process_port()` - handle upload port registration
    - `process_heartbeat()` - update heartbeat timestamp
    - `process_get()` - handle file request (return peer info)
    - `process_lap()` - list active peers
    - `process_lpf()` - list published files
    - `process_pub()` - publish file
    - `process_sch()` - search files
    - `process_unp()` - unpublish file
    - `process_xit()` - handle exit
  - Use `async with state_lock:` for all shared state access
  - Handle connection errors gracefully with `try/except ConnectionResetError`

  **Must NOT do**:
  - Do NOT change business logic (keep identical to server.py)
  - Do NOT add validation beyond what exists
  - Do NOT change response messages

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reasoning**: Translating synchronous to async requires care

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 1 scaffolding
  - **Blocks**: Task 5 (SSL)
  - **Blocked By**: Task 1

  **References**:
  - `server.py:191-224` - process_auth implementation
  - `server.py:226-251` - process_get implementation
  - `server.py:253-263` - process_lap implementation
  - `server.py:265-275` - process_lpf implementation
  - `server.py:277-299` - process_pub implementation
  - `server.py:301-325` - process_sch implementation
  - `server.py:327-354` - process_unp implementation
  - `server.py:356-358` - process_xit implementation

  **QA Scenarios**:

  ```
  Scenario: All commands work over asyncio
    Tool: Bash (pytest)
    Preconditions: server_async.py running, characterization tests exist
    Steps:
      1. Run characterization tests against server_async.py
      2. Assert: All auth, pub, get, lap, lpf, sch, unp, xit tests pass
    Expected Result: All commands behave identically to threaded server
    Evidence: .sisyphus/evidence/task-2-commands.txt

  Scenario: State lock prevents race conditions
    Tool: Bash (pytest)
    Preconditions: server_async.py running
    Steps:
      1. pytest tests/test_concurrent.py -v --tb=short
      2. Run 100 concurrent publish operations
      3. Verify no duplicate entries in published_files
    Expected Result: No race conditions, clean state after concurrent ops
    Evidence: .sisyphus/evidence/task-2-race-conditions.txt
  ```

  **Commit**: YES
  - Message: `feat(server): implement async client handler`
  - Files: `server_async.py`
  - Pre-commit: `pytest tests/test_baseline.py -v`

---

- [ ] 3. AsyncIO State Management

  **What to do**:
  - Convert `check_heartbeat()` to `async def check_heartbeat()`
  - Use `async with state_lock` for all shared state modifications
  - Ensure `active_clients` dict is properly cleaned up on:
    - Client timeout (heartbeat failure)
    - Client disconnect (xit command)
    - Connection error
    - Server shutdown
  - Add `asyncio.create_task(check_heartbeat())` in main()

  **Must NOT do**:
  - Do NOT use `threading.Lock` or `threading.Thread`
  - Do NOT block the event loop with `time.sleep()`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: State management is critical for correctness

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 1 scaffolding
  - **Blocks**: Task 5 (SSL)
  - **Blocked By**: Task 1

  **References**:
  - `server.py:55-66` - Current heartbeat check implementation
  - `server.py:72-74` - Global state variables
  - `server.py:145-153` - disconnect_client implementation

  **QA Scenarios**:

  ```
  Scenario: Client removed after heartbeat timeout
    Tool: Bash (pytest)
    Preconditions: server_async.py running with 3-second timeout
    Steps:
      1. Connect and authenticate client
      2. Do NOT send heartbeat for 4 seconds
      3. Send "lap" command from another client
      4. Assert: Timed-out client not in active peers list
    Expected Result: Client removed after timeout
    Evidence: .sisyphus/evidence/task-3-heartbeat-timeout.txt

  Scenario: State cleaned up on graceful exit
    Tool: Bash (nc)
    Preconditions: server_async.py running
    Steps:
      1. Connect client, authenticate
      2. Send "xit" command
      3. From another client, run "lap"
      4. Assert: Exited client not in list
    Expected Result: State properly cleaned on exit
    Evidence: .sisyphus/evidence/task-3-cleanup.txt
  ```

  **Commit**: YES
  - Message: `feat(server): add async state management with heartbeat`
  - Files: `server_async.py`
  - Pre-commit: `pytest tests/test_baseline.py::test_heartbeat -v`

---

- [ ] 4. Graceful Shutdown Handling

  **What to do**:
  - Add signal handlers for `signal.SIGINT` and `signal.SIGTERM`
  - Create shutdown event `asyncio.Event()`
  - On signal: close all client connections cleanly, cancel heartbeat task
  - Use `try/finally` in main to ensure cleanup
  - Add `async def cleanup()` to close all active writers
  - Print shutdown message to console

  **Must NOT do**:
  - Do NOT use `sys.exit()` or `exit()` in signal handler
  - Do NOT leave connections in TIME_WAIT state

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reasoning**: Signal handling is straightforward async pattern

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 1 scaffolding
  - **Blocks**: Task 5 (SSL)
  - **Blocked By**: Task 1

  **References**:
  - Python asyncio signal handling documentation
  - `server.py:377-381` - Current server loop (no shutdown handling)

  **QA Scenarios**:

  ```
  Scenario: Graceful shutdown on SIGINT
    Tool: Bash (interactive_bash/tmux)
    Preconditions: server_async.py running with 2 connected clients
    Steps:
      1. python3 server_async.py 12001 &
      2. sleep 1
      3. Connect 2 clients and authenticate
      4. kill -INT %1
      5. sleep 2
      6. pgrep -f server_async.py && echo "FAIL: Process still running" || echo "PASS: Clean exit"
    Expected Result: Server exits cleanly, no zombie processes
    Evidence: .sisyphus/evidence/task-4-shutdown.txt
  ```

  **Commit**: YES
  - Message: `feat(server): add graceful shutdown handling`
  - Files: `server_async.py`
  - Pre-commit: `python3 server_async.py 12001 & sleep 1 && kill -INT %1`

---

- [ ] 5. SSL Certificate Generation

  **What to do**:
  - Create `scripts/generate_certs.sh` for self-signed certificate generation
  - Generate `server.crt` and `server.key` using OpenSSL
  - Add `.gitignore` entries for `*.crt`, `*.key`, `*.pem` (never commit certs)
  - Create `scripts/generate_certs.ps1` for Windows users
  - Add documentation in README.md for certificate generation
  - Certificate: 2048-bit RSA, 365-day validity, CN=localhost

  **Must NOT do**:
  - Do NOT commit certificates to repository
  - Do NOT use weak cryptography (< 2048 bits)
  - Do NOT skip certificate validation in production

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reasoning**: Shell script for OpenSSL is straightforward

  **Parallelization**:
  - **Can Run In Parallel**: YES - Can run alongside Wave 1 tasks
  - **Blocks**: Task 6 (server SSL context)
  - **Blocked By**: None

  **References**:
  - OpenSSL documentation for `req -x509`
  - Standard self-signed cert patterns

  **QA Scenarios**:

  ```
  Scenario: Certificates generated correctly
    Tool: Bash
    Preconditions: OpenSSL installed
    Steps:
      1. bash scripts/generate_certs.sh
      2. ls -la server.crt server.key
      3. openssl x509 -in server.crt -text -noout | grep "CN=localhost"
    Expected Result: Certificates exist with correct CN
    Evidence: .sisyphus/evidence/task-5-certs.txt

  Scenario: Certificates not in git
    Tool: Bash
    Preconditions: .gitignore updated
    Steps:
      1. bash scripts/generate_certs.sh
      2. git status
      3. grep -v "server.crt" git_status_output | grep -v "server.key"
    Expected Result: Certificates not tracked by git
    Evidence: .sisyphus/evidence/task-5-gitignore.txt
  ```

  **Commit**: YES
  - Message: `feat(security): add SSL certificate generation scripts`
  - Files: `scripts/generate_certs.sh`, `scripts/generate_certs.ps1`, `.gitignore`, `README.md`
  - Pre-commit: `bash scripts/generate_certs.sh && ls server.crt server.key`

---

- [ ] 6. Server SSL Context

  **What to do**:
  - Add `--ssl` flag to `server_async.py` command line
  - Create `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)` when `--ssl` is present
  - Load certificates with `context.load_cert_chain('server.crt', 'server.key')`
  - Set minimum TLS version: `context.minimum_version = ssl.TLSVersion.TLSv1_2`
  - Pass SSL context to `asyncio.start_server(ssl=ssl_context)`
  - Print "SSL-encrypted server started" message

  **Must NOT do**:
  - Do NOT disable certificate verification (`CERT_NONE`)
  - Do NOT support TLSv1.0 or TLSv1.1 (insecure)
  - Do NOT force SSL on by default (keep optional for dev)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: SSL/TLS integration requires security awareness

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 5
  - **Blocks**: Task 7 (client SSL)
  - **Blocked By**: Task 5

  **References**:
  - Python ssl module documentation
  - `server.py:368-380` - Current server socket creation

  **QA Scenarios**:

  ```
  Scenario: SSL server rejects plaintext connections
    Tool: Bash (nc)
    Preconditions: server_async.py running with --ssl flag
    Steps:
      1. python3 server_async.py 12001 --ssl &
      2. sleep 2
      3. echo "auth hans falcon*solo" | nc localhost 12001
      4. sleep 1
      5. Assert: No response (connection rejected or garbled)
    Expected Result: Plaintext rejected
    Evidence: .sisyphus/evidence/task-6-ssl-plaintext.txt

  Scenario: SSL server accepts SSL connections
    Tool: Bash (openssl s_client)
    Preconditions: server_async.py running with --ssl, certificates exist
    Steps:
      1. python3 server_async.py 12001 --ssl &
      2. sleep 2
      3. echo "auth hans falcon*solo" | openssl s_client -connect localhost:12001 -quiet
      4. Assert: Response contains "auth OK" or "auth ERR"
    Expected Result: SSL connection works
    Evidence: .sisyphus/evidence/task-6-ssl-success.txt
  ```

  **Commit**: YES
  - Message: `feat(security): add SSL/TLS support to server`
  - Files: `server_async.py`
  - Pre-commit: `pytest tests/test_ssl.py -v`

---

- [ ] 7. Client SSL Connection

  **What to do**:
  - Create `client_async.py` using `asyncio.open_connection()`
  - Add `--ssl` flag to enable SSL
  - Use `ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)` for client-side SSL
  - Set `context.check_hostname = False` and `context.verify_mode = CERT_REQUIRED` for dev
  - Convert all send/recv to `writer.write()` and `await reader.read()`
  - Use `aiofiles` for async file I/O in `handle_file_upload` and `handle_file_download`
  - Keep message protocol identical to original client

  **Must NOT do**:
  - Do NOT use `socket.socket` (use asyncio streams)
  - Do NOT change message format
  - Do NOT skip SSL verification in production

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: Async client migration requires careful stream handling

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 6
  - **Blocks**: Task 8 (SSL integration tests)
  - **Blocked By**: Task 6

  **References**:
  - `client.py:24-25` - Current socket connection
  - `client.py:30-33` - Heartbeat thread
  - `client.py:36-57` - Upload socket listener
  - `client.py:59-85` - File upload handler
  - `client.py:87-126` - File download handler

  **QA Scenarios**:

  ```
  Scenario: Client connects over SSL
    Tool: Bash (pytest)
    Preconditions: server_async.py running with --ssl, client_async.py built
    Steps:
      1. python3 client_async.py 127.0.0.1 12001 --ssl
      2. Enter: hans, falcon*solo
      3. Assert: "Authentication successful"
    Expected Result: SSL connection works, authentication succeeds
    Evidence: .sisyphus/evidence/task-7-client-ssl.txt

  Scenario: Async file upload works
    Tool: Bash (pytest)
    Preconditions: server_async.py and client_async.py running
    Steps:
      1. Authenticate client A
      2. Create test file "test_upload.txt"
      3. Run: pub test_upload.txt
      4. Assert: "File published successfully"
    Expected Result: File published without blocking event loop
    Evidence: .sisyphus/evidence/task-7-async-upload.txt
  ```

  **Commit**: YES
  - Message: `feat(client): add asyncio SSL client`
  - Files: `client_async.py`, `requirements.txt` (add aiofiles)
  - Pre-commit: `pytest tests/test_client_ssl.py -v`

---

- [ ] 8. SSL Integration Tests

  **What to do**:
  - Create `tests/test_ssl_integration.py`
  - Test: Server without SSL flag accepts plaintext
  - Test: Server with SSL flag rejects plaintext
  - Test: Server with SSL flag accepts SSL connections
  - Test: Certificate validation (invalid cert rejected)
  - Test: End-to-end auth over SSL
  - Test: End-to-end file transfer over SSL

  **Must NOT do**:
  - Do NOT test with production certificates (use self-signed)
  - Do NOT skip certificate validation in tests

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: Integration tests verify security requirements

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Tasks 6, 7
  - **Blocks**: Task 14 (E2E integration)
  - **Blocked By**: Task 7

  **References**:
  - `tests/test_baseline.py` - Test patterns to follow

  **QA Scenarios**:

  ```
  Scenario: All SSL tests pass
    Tool: Bash (pytest)
    Preconditions: server_async.py and client_async.py built
    Steps:
      1. bash scripts/generate_certs.sh
      2. pytest tests/test_ssl_integration.py -v
      3. Assert: 6 tests pass, 0 failures
    Expected Result: All SSL integration tests pass
    Evidence: .sisyphus/evidence/task-8-ssl-tests.txt
  ```

  **Commit**: YES
  - Message: `test(ssl): add SSL integration tests`
  - Files: `tests/test_ssl_integration.py`
  - Pre-commit: `pytest tests/test_ssl_integration.py -v`

---

- [ ] 9. Electron Project Setup

  **What to do**:
  - Initialize Electron project in `electron-app/` directory
  - Create `package.json` with dependencies:
    - `electron` (latest)
    - `react`, `react-dom`
    - `typescript`, `@types/react`, `@types/node`
    - `vite` (build tool)
  - Create `electron/main.ts` (main process)
  - Create `electron/preload.ts` (context bridge)
  - Create `src/App.tsx` (React root)
  - Create `vite.config.ts` for build
  - Create `tsconfig.json` for TypeScript
  - Configure `contextIsolation: true`, `nodeIntegration: false` in BrowserWindow

  **Must NOT do**:
  - Do NOT enable `nodeIntegration` (security risk)
  - Do NOT skip `contextIsolation` (security risk)
  - Do NOT include unnecessary Electron features

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`frontend-design`]
  - **Reasoning**: Project setup is straightforward with standard patterns
  - Why frontend-design: Electron + Vite + React is frontend tooling

  **Parallelization**:
  - **Can Run In Parallel**: YES - Can run concurrently with Wave 2
  - **Blocks**: Tasks 10, 11 (IPC bridge, React components)
  - **Blocked By**: None

  **References**:
  - Electron security best practices (contextIsolation, preload)
  - Vite + React + TypeScript setup patterns

  **QA Scenarios**:

  ```
  Scenario: Electron app starts
    Tool: Bash (npm)
    Preconditions: Node.js 18+ installed
    Steps:
      1. cd electron-app && npm install
      2. npm run dev
      3. Assert: Window opens without error
    Expected Result: Electron window displays "Hello World" placeholder
    Evidence: .sisyphus/evidence/task-9-electron-start.png

  Scenario: TypeScript compiles
    Tool: Bash (tsc)
    Preconditions: electron-app setup complete
    Steps:
      1. cd electron-app && npx tsc --noEmit
      2. Assert: No type errors
    Expected Result: TypeScript compilation succeeds
    Evidence: .sisyphus/evidence/task-9-typescript.txt
  ```

  **Commit**: YES
  - Message: `feat(electron): initialize project with Vite + React + TypeScript`
  - Files: `electron-app/package.json`, `electron-app/vite.config.ts`, `electron-app/tsconfig.json`, `electron-app/electron/main.ts`, `electron-app/electron/preload.ts`, `electron-app/src/App.tsx`
  - Pre-commit: `cd electron-app && npm install && npm run build`

---

- [ ] 10. React Authentication Component

  **What to do**:
  - Create `src/components/AuthForm.tsx` with username/password inputs
  - Add login button that calls `window.electronAPI.authenticate(username, password)`
  - Style with basic CSS (inline or `AuthForm.css`)
  - Handle success: show "Connected" status, transition to main app
  - Handle failure: show "Authentication failed" error message
  - Store authenticated state in React context or local state
  - Add logout button that calls `window.electronAPI.disconnect()`

  **Must NOT do**:
  - Do NOT use localStorage for passwords (security)
  - Do NOT add OAuth/SSO features (out of scope)
  - Do NOT add remember-me functionality (out of scope)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-design`]
  - **Reasoning**: React component design requires UI/UX skill
  - Why frontend-design: Form layout, error states, transitions

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 9
  - **Blocks**: Task 12 (file operations UI)
  - **Blocked By**: Task 9

  **References**:
  - Standard React form patterns
  - Electron IPC with contextBridge

  **QA Scenarios**:

  ```
  Scenario: Auth form renders
    Tool: Playwright
    Preconditions: electron-app running
    Steps:
      1. Launch app
      2. await page.locator('#username').toBeVisible()
      3. await page.locator('#password').toBeVisible()
      4. await page.locator('#login-button').toBeVisible()
    Expected Result: All auth form elements visible
    Evidence: .sisyphus/evidence/task-10-auth-form.png

  Scenario: Auth form submits to IPC
    Tool: Playwright
    Preconditions: electron-app running, IPC bridge implemented
    Steps:
      1. Launch app
      2. await page.fill('#username', 'hans')
      3. await page.fill('#password', 'falcon*solo')
      4. await page.click('#login-button')
      5. await expect(page.locator('.status')).toContainText('Connected')
    Expected Result: Auth success shows Connected status
    Evidence: .sisyphus/evidence/task-10-auth-success.png
  ```

  **Commit**: YES
  - Message: `feat(ui): add authentication component`
  - Files: `electron-app/src/components/AuthForm.tsx`, `electron-app/src/App.tsx`
  - Pre-commit: `cd electron-app && npm run build`

---

- [ ] 11. IPC Bridge Implementation

  **What to do**:
  - Implement `preload.ts` with `contextBridge.exposeInMainWorld('electronAPI', {...})`
  - Expose IPC methods:
    - `authenticate(username, password)` → returns Promise<boolean>
    - `disconnect()` → returns Promise<void>
    - `publishFile(filename)` → returns Promise<boolean>
    - `searchFiles(substring)` → returns Promise<string[]>
    - `downloadFile(filename)` → returns Promise<boolean>
    - `listActivePeers()` → returns Promise<string[]>
    - `listPublishedFiles()` → returns Promise<string[]>
    - `unpublishFile(filename)` → returns Promise<boolean>
  - Implement `main.ts` IPC handlers that connect to asyncio server
  - Use Node.js `net` module for raw socket communication (or use child process to run client_async.py)
  - Add TypeScript type definitions in `src/electron.d.ts`

  **Must NOT do**:
  - Do NOT expose full `fs` or `net` modules (security)
  - Do NOT use `remote` module (deprecated/insecure)
  - Do NOT block renderer during socket I/O (use async)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reasoning**: IPC bridge is complex async integration work

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 9
  - **Blocks**: Task 12 (file operations UI)
  - **Blocked By**: Task 9

  **References**:
  - Electron contextBridge documentation
  - Node.js net module for TCP sockets

  **QA Scenarios**:

  ```
  Scenario: IPC bridge exposes API
    Tool: Playwright
    Preconditions: electron-app running
    Steps:
      1. Launch app
      2. const api = await page.evaluate(() => window.electronAPI)
      3. Assert: api.authenticate is a function
      4. Assert: api.disconnect is a function
      5. Assert: api.publishFile is a function
      6. Assert: api.searchFiles is a function
    Expected Result: All IPC methods exposed
    Evidence: .sisyphus/evidence/task-11-ipc-api.txt

  Scenario: IPC connects to asyncio server
    Tool: Playwright
    Preconditions: server_async.py running, electron-app running
    Steps:
      1. Launch app
      2. await page.evaluate(() => window.electronAPI.authenticate('hans', 'falcon*solo'))
      3. Assert: returns true
    Expected Result: IPC successfully communicates with server
    Evidence: .sisyphus/evidence/task-11-ipc-connect.txt
  ```

  **Commit**: YES
  - Message: `feat(ipc): implement IPC bridge for socket communication`
  - Files: `electron-app/electron/preload.ts`, `electron-app/electron/main.ts`, `electron-app/src/electron.d.ts`
  - Pre-commit: `cd electron-app && npx tsc --noEmit`

---

- [ ] 12. File Operations UI

  **What to do**:
  - Create `src/components/FileList.tsx` for displaying files
  - Create `src/components/SearchBar.tsx` for searching files
  - Create `src/components/PeerList.tsx` for active peers
  - Create `src/components/PublishForm.tsx` for publishing files
  - Create `src/components/DownloadButton.tsx` for downloading
  - Create `src/components/UnpublishButton.tsx` for unpublishing
  - Wire all components to IPC methods
  - Add status indicators (Connected, Disconnected, Error)
  - Add refresh buttons for peer list and file list

  **Must NOT do**:
  - Do NOT add drag-and-drop (out of scope)
  - Do NOT add progress bars (out of scope)
  - Do NOT add file preview (out of scope)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-design`]
  - **Reasoning**: Multiple UI components require design decisions
  - Why frontend-design: Layout, spacing, component hierarchy

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Tasks 10, 11
  - **Blocks**: Task 13 (packaging)
  - **Blocked By**: Tasks 10, 11

  **References**:
  - IPC methods from Task 11
  - React component patterns

  **QA Scenarios**:

  ```
  Scenario: File list displays published files
    Tool: Playwright
    Preconditions: Authenticated, files published
    Steps:
      1. Authenticate as 'hans'
      2. Publish 'test.txt'
      3. await page.locator('.file-list').toContainText('test.txt')
    Expected Result: Published file appears in list
    Evidence: .sisyphus/evidence/task-12-file-list.png

  Scenario: Search finds files
    Tool: Playwright
    Preconditions: Authenticated, files published by other users
    Steps:
      1. Authenticate as 'hans'
      2. await page.fill('#search-input', 'test')
      3. await page.click('#search-button')
      4. await expect(page.locator('.search-results')).toContainText('test')
    Expected Result: Search returns matching files
    Evidence: .sisyphus/evidence/task-12-search.png

  Scenario: Download file from peer
    Tool: Playwright
    Preconditions: Two clients, file published by peer
    Steps:
      1. Client A publishes 'shared.txt'
      2. Client B (Electron) searches for 'shared'
      3. Client B clicks download
      4. Assert: File appears in downloads
    Expected Result: File downloaded successfully
    Evidence: .sisyphus/evidence/task-12-download.png
  ```

  **Commit**: YES
  - Message: `feat(ui): add file operations components`
  - Files: `electron-app/src/components/FileList.tsx`, `SearchBar.tsx`, `PeerList.tsx`, `PublishForm.tsx`, `DownloadButton.tsx`, `UnpublishButton.tsx`
  - Pre-commit: `cd electron-app && npm run build`

---

- [ ] 13. Electron Packaging

  **What to do**:
  - Install `electron-builder` in devDependencies
  - Configure `build` section in `package.json`:
    - App ID: `com.p2p-vault.file-share`
    - Product name: "P2P Vault"
    - Include all dependencies, exclude devDependencies
  - Add `npm run make` script to build distributable
  - Add `npm run dist` script to create installer
  - Add platform-specific builds (macOS, Windows, Linux)
  - Bundle Python runtime or use `child_process` to launch `server_async.py`

  **Must NOT do**:
  - Do NOT bundle Python globally (use virtualenv or embed)
  - Do NOT hardcode paths (use app.getPath())
  - Do NOT skip code signing (production)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: Electron packaging requires build configuration

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Tasks 10, 11, 12
  - **Blocks**: Task 14 (integration tests)
  - **Blocked By**: Task 12

  **References**:
  - electron-builder documentation
  - App bundling patterns

  **QA Scenarios**:

  ```
  Scenario: Build creates executable
    Tool: Bash (npm)
    Preconditions: All components implemented
    Steps:
      1. cd electron-app && npm run make
      2. ls -la out/
      3. Assert: Platform-specific executable exists
    Expected Result: Executable in out/ directory
    Evidence: .sisyphus/evidence/task-13-build.txt

  Scenario: Packaged app runs
    Tool: Bash
    Preconditions: Build complete
    Steps:
      1. ./out/p2p-vault-darwin-x64/P2P_Vault.app/Contents/MacOS/P2P_Vault &
      2. sleep 5
      3. Assert: Window opens, auth form appears
    Expected Result: Packaged app starts successfully
    Evidence: .sisyphus/evidence/task-13-run.png
  ```

  **Commit**: YES
  - Message: `feat(build): add Electron packaging configuration`
  - Files: `electron-app/package.json`, `electron-app/electron-builder.yml`
  - Pre-commit: `cd electron-app && npm run make`

---

- [ ] 14. End-to-End Integration Tests

  **What to do**:
  - Create `tests/test_e2e_integration.py`
  - Test: Full workflow - auth → publish → search → download
  - Test: Multiple clients concurrent operations
  - Test: AsyncIO server handles 50+ concurrent connections
  - Test: SSL connection end-to-end
  - Test: Electron app can connect to SSL server

  **Must NOT do**:
  - Do NOT use production certificates
  - Do NOT skip cleanup (kill processes after tests)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reasoning**: E2E tests require full stack understanding

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on all previous tasks
  - **Blocks**: Tasks F1-F4 (final verification)
  - **Blocked By**: Tasks 8, 13

  **References**:
  - `tests/test_baseline.py` - Pattern to follow

  **QA Scenarios**:

  ```
  Scenario: Full E2E workflow succeeds
    Tool: Bash (pytest)
    Preconditions: All components built
    Steps:
      1. Start server_async.py with --ssl
      2. Start Electron app
      3. pytest tests/test_e2e_integration.py::test_full_workflow -v
      4. Assert: Auth, publish, search, download all succeed
    Expected Result: Complete workflow succeeds
    Evidence: .sisyphus/evidence/task-14-e2e-full.txt

  Scenario: 50 concurrent connections
    Tool: Bash (pytest)
    Preconditions: Server running
    Steps:
      1. pytest tests/test_e2e_integration.py::test_concurrent_50 -v
      2. Assert: All 50 clients connect and operate without deadlock
    Expected Result: High concurrency handled
    Evidence: .sisyphus/evidence/task-14-concurrent.txt
  ```

  **Commit**: YES
  - Message: `test(e2e): add integration tests`
  - Files: `tests/test_e2e_integration.py`
  - Pre-commit: `pytest tests/test_e2e_integration.py -v`

---

- [ ] 15. SSL Handshake Edge Cases

  **What to do**:
  - Test: SSL handshake timeout handling
  - Test: Invalid certificate rejection
  - Test: Expired certificate handling
  - Test: Wrong hostname in certificate
  - Test: Client disconnect during SSL handshake
  - Add error messages for SSL failures

  **Must NOT do**:
  - Do NOT bypass certificate validation
  - Do NOT log sensitive data (passwords, keys)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reasoning**: Security edge cases need careful handling

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 8
  - **Blocks**: Tasks F1-F4
  - **Blocked By**: Task 8

  **References**:
  - SSL/TLS error handling patterns

  **QA Scenarios**:

  ```
  Scenario: Invalid certificate rejected
    Tool: Bash (openssl)
    Preconditions: Server with valid cert
    Steps:
      1. Generate client with wrong cert
      2. Attempt connection
      3. Assert: Connection rejected with error
    Expected Result: Invalid cert rejected
    Evidence: .sisyphus/evidence/task-15-invalid-cert.txt

  Scenario: Graceful SSL error message
    Tool: Playwright
    Preconditions: Electron app, invalid cert server
    Steps:
      1. Configure server with self-signed cert not in trust store
      2. Attempt auth
      3. Assert: Error dialog shows "Certificate verification failed"
    Expected Result: User-friendly error message
    Evidence: .sisyphus/evidence/task-15-error-message.png
  ```

  **Commit**: YES
  - Message: `feat(ssl): add edge case handling for SSL handshake`
  - Files: `server_async.py`, `client_async.py`, `electron-app/electron/main.ts`
  - Pre-commit: `pytest tests/test_ssl_edge_cases.py -v`

---

- [ ] 16. Concurrent Load Testing

  **What to do**:
  - Create `tests/test_load.py` for stress testing
  - Test: 100 concurrent connections
  - Test: 1000 concurrent connections
  - Test: Rapid connect/disconnect cycles
  - Test: Memory usage under load (check for leaks)
  - Test: CPU usage under load
  - Add performance benchmark logging

  **Must NOT do**:
  - Do NOT run load tests in CI (too heavy)
  - Do NOT skip memory leak checks

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`performance-benchmarker`]
  - **Reasoning**: Performance testing requires benchmarking skill
  - Why performance-benchmarker: Load testing, memory analysis

  **Parallelization**:
  - **Can Run In Parallel**: NO - Depends on Task 14
  - **Blocks**: Tasks F1-F4
  - **Blocked By**: Task 14

  **References**:
  - Python `tracemalloc` for memory tracking
  - AsyncIO performance patterns

  **QA Scenarios**:

  ```
  Scenario: 100 concurrent connections succeed
    Tool: Bash (pytest)
    Preconditions: Server running
    Steps:
      1. pytest tests/test_load.py::test_100_concurrent -v
      2. Assert: All connections succeed, no errors
    Expected Result: High concurrency handled gracefully
    Evidence: .sisyphus/evidence/task-16-load-100.txt

  Scenario: No memory leaks under load
    Tool: Bash (pytest + tracemalloc)
    Preconditions: Server running
    Steps:
      1. pytest tests/test_load.py::test_memory_leak -v
      2. Assert: Memory growth < 10MB per 100 connections
    Expected Result: Minimal memory growth
    Evidence: .sisyphus/evidence/task-16-memory.txt
  ```

  **Commit**: YES
  - Message: `test(load): add concurrent load tests`
  - Files: `tests/test_load.py`
  - Pre-commit: `pytest tests/test_load.py -v --skip-heavy`

---

- [ ] 17. Documentation Update

  **What to do**:
  - Update `README.md` with:
    - AsyncIO server usage: `python3 server_async.py <PORT> [--ssl]`
    - AsyncIO client usage: `python3 client_async.py <IP> <PORT> [--ssl]`
    - SSL certificate generation instructions
    - Electron app launch instructions
    - Architecture diagram (ASCII)
  - Add `docs/ARCHITECTURE.md` explaining asyncio migration
  - Add `docs/SSL.md` explaining SSL setup
  - Add `docs/ELECTRON.md` explaining GUI usage
  - Update `DEVELOPMENT_PLAN.md` to mark tasks complete

  **Must NOT do**:
  - Do NOT include sensitive data in documentation
  - Do NOT document future work as implemented

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: [`technical-writer`]
  - **Reasoning**: Documentation quality affects usability
  - Why technical-writer: Clear, accurate documentation

  **Parallelization**:
  - **Can Run In Parallel**: YES - Can run after Task 14
  - **Blocks**: None
  - **Blocked By**: Task 14

  **References**:
  - Current `README.md`
  - Current `DEVELOPMENT_PLAN.md`

  **QA Scenarios**:

  ```
  Scenario: README has all usage patterns
    Tool: Bash
    Steps:
      1. grep "python3 server_async.py" README.md
      2. grep "python3 client_async.py" README.md
      3. grep "--ssl" README.md
      4. grep "npm run" README.md
      5. Assert: All patterns documented
    Expected Result: Complete usage documentation
    Evidence: .sisyphus/evidence/task-17-readme.txt
  ```

  **Commit**: YES
  - Message: `docs: update README and add architecture documentation`
  - Files: `README.md`, `docs/ARCHITECTURE.md`, `docs/SSL.md`, `docs/ELECTRON.md`
  - Pre-commit: None (docs only)

---

## Final Verification Wave (MANDATORY)

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [18/18] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `pytest tests/ -v` + `npx tsc --noEmit` + `pylint server_async.py client_async.py`. Review all changed files for: `any` types, empty catches, hardcoded credentials, `console.log` in Python. Check AI slop: excessive comments, generic names.
  Output: `Tests [N pass/N fail] | TypeScript [PASS/FAIL] | Python [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test cross-task integration: auth → publish → search → download. Test edge cases: empty input, invalid credentials, offline server. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Characterization tests**: `test: add characterization tests for baseline`
- **AsyncIO server**: `feat(server): migrate to asyncio with graceful shutdown`
- **SSL/TLS**: `feat(security): add SSL/TLS encryption`
- **Electron**: `feat(gui): add React/Electron desktop client`
- **Integration tests**: `test(e2e): add end-to-end integration tests`
- **Final**: `feat: complete asyncio + SSL + Electron migration`

---

## Success Criteria

### Verification Commands
```bash
# AsyncIO server starts
python3 server_async.py 12000 &
sleep 2
nc -z localhost 12000 && echo "PASS: Server listening" || echo "FAIL"

# Characterization tests pass
pytest tests/test_baseline.py -v

# SSL works
python3 server_async.py 12001 --ssl &
python3 client_async.py 127.0.0.1 12001 --ssl
# Enter credentials, verify auth succeeds

# Electron app launches
cd electron-app && npm start
# Verify GUI opens and can authenticate
```

### Final Checklist
- [ ] All Must Have features implemented
- [ ] All Must NOT Have absent (no PostgreSQL, no P2P encryption, no type hints)
- [ ] All characterization tests pass
- [ ] SSL integration tests pass
- [ ] Electron app launches and connects
- [ ] 100+ concurrent connections handled
- [ ] No memory leaks under load
