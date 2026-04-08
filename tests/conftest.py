import pytest
import subprocess
import socket
import time
import os
import tempfile

@pytest.fixture(scope="module")
def server_process():
    """Start server.py in subprocess for testing"""
    proc = subprocess.Popen(
        ["python3", "server.py", "12000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1)  # Wait for server to start
    yield proc
    proc.terminate()
    proc.wait()

@pytest.fixture
def client_socket():
    """Create connected socket for each test"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # 5 second timeout
    sock.connect(("127.0.0.1", 12000))
    yield sock
    sock.close()

@pytest.fixture
def authenticated_client(client_socket):
    """Create authenticated client connection"""
    client_socket.sendall(b"auth hans falcon*solo")
    response = client_socket.recv(1024).decode()
    assert response == "auth OK", f"Auth failed: {response}"
    yield client_socket

@pytest.fixture
def temp_test_file():
    """Create temporary test file for upload/download tests"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content for file transfer\n")
        filename = f.name
    yield filename
    if os.path.exists(filename):
        os.unlink(filename)
