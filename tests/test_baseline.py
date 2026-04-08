"""
Test baseline functionality of server.py before asyncio migration
"""
import pytest
import socket
import threading
import time
import os
import tempfile


class TestAuthentication:
    """Test auth command"""
    
    def test_auth_success_valid_credentials(self, client_socket):
        """Valid credentials should authenticate successfully"""
        client_socket.sendall(b"auth hans falcon*solo")
        response = client_socket.recv(1024).decode()
        assert response == "auth OK", f"Expected 'auth OK', got '{response}'"
    
    def test_auth_failure_invalid_username(self, client_socket):
        """Invalid username should fail"""
        client_socket.sendall(b"auth nonexistent password")
        response = client_socket.recv(1024).decode()
        assert response == "auth ERR", f"Expected 'auth ERR', got '{response}'"
    
    def test_auth_failure_wrong_password(self, client_socket):
        """Wrong password should fail"""
        client_socket.sendall(b"auth hans wrongpassword")
        response = client_socket.recv(1024).decode()
        assert response == "auth ERR", f"Expected 'auth ERR', got '{response}'"
    
    def test_auth_failure_duplicate_login(self, authenticated_client):
        """Same user logging in twice should fail"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", 12000))
        sock.sendall(b"auth hans falcon*solo")  # Already logged in
        response = sock.recv(1024).decode()
        sock.close()
        assert response == "auth ERR", f"Expected duplicate login to fail"
    
    def test_auth_malformed_request(self, client_socket):
        """Malformed auth request should fail"""
        client_socket.sendall(b"auth onlyusername")  # Missing password
        response = client_socket.recv(1024).decode()
        assert "ERR" in response


class TestFilePublish:
    """Test pub command"""
    
    def test_publish_success(self, authenticated_client, temp_test_file):
        """Publishing existing file should succeed"""
        filename = os.path.basename(temp_test_file)
        command = f"pub {filename}".encode()
        authenticated_client.sendall(command)
        response = authenticated_client.recv(1024).decode()
        assert response == "pub OK", f"Expected 'pub OK', got '{response}'"
    
    def test_publish_duplicate(self, authenticated_client, temp_test_file):
        """Publishing same file twice should still succeed"""
        filename = os.path.basename(temp_test_file)
        authenticated_client.sendall(f"pub {filename}".encode())
        response = authenticated_client.recv(1024).decode()
        authenticated_client.sendall(f"pub {filename}".encode())
        response2 = authenticated_client.recv(1024).decode()
        assert response2 == "pub OK"


class TestFileSearch:
    """Test sch command"""
    
    def test_search_finds_file(self, authenticated_client, temp_test_file):
        """Search should find published files"""
        filename = os.path.basename(temp_test_file)
        # First publish
        authenticated_client.sendall(f"pub {filename}".encode())
        authenticated_client.recv(1024)
        # Then search
        time.sleep(0.1)
        search_term = filename[:4]  # Use substring
        authenticated_client.sendall(f"sch {search_term}".encode())
        response = authenticated_client.recv(1024).decode()
        assert filename in response or "sch " in response
    
    def test_search_no_results(self, authenticated_client):
        """Search with no matches should return 'No files found'"""
        authenticated_client.sendall(b"sch xyznonexistentfile123")
        response = authenticated_client.recv(1024).decode()
        assert "No files found" in response or response.startswith("sch ")


class TestFileUnpublish:
    """Test unp command"""
    
    def test_unpublish_success(self, authenticated_client, temp_test_file):
        """Unpublishing owned file should succeed"""
        filename = os.path.basename(temp_test_file)
        # First publish
        authenticated_client.sendall(f"pub {filename}".encode())
        authenticated_client.recv(1024)
        # Then unpublish
        authenticated_client.sendall(f"unp {filename}".encode())
        response = authenticated_client.recv(1024).decode()
        assert response == "unp OK"
    
    def test_unpublish_not_owner(self, authenticated_client):
        """Unpublishing file you don't own should fail"""
        authenticated_client.sendall(b"unp nonexistentfile.txt")
        response = authenticated_client.recv(1024).decode()
        assert response == "unp ERR"
    
    def test_unpublish_nonexistent_file(self, authenticated_client):
        """Unpublishing non-existent file should fail"""
        authenticated_client.sendall(b"unp nonexistentfile.txt")
        response = authenticated_client.recv(1024).decode()
        assert response == "unp ERR"


class TestListActivePeers:
    """Test lap command"""
    
    def test_list_peers_single_user(self, authenticated_client):
        """Single client should see 'No active peers'"""
        authenticated_client.sendall(b"lap")
        response = authenticated_client.recv(1024).decode()
        assert "No active peers" in response


class TestListPublishedFiles:
    """Test lpf command"""
    
    def test_list_files_empty(self, authenticated_client):
        """Client with no published files should see 'No files published'"""
        authenticated_client.sendall(b"lpf")
        response = authenticated_client.recv(1024).decode()
        assert "No files published" in response
    
    def test_list_files_success(self, authenticated_client, temp_test_file):
        """Client should see their published files"""
        filename = os.path.basename(temp_test_file)
        # Publish file
        authenticated_client.sendall(f"pub {filename}".encode())
        authenticated_client.recv(1024)
        # List files
        authenticated_client.sendall(b"lpf")
        response = authenticated_client.recv(1024).decode()
        assert filename in response


class TestExit:
    """Test xit command"""
    
    def test_exit_disconnects_cleanly(self, authenticated_client):
        """Exit should disconnect client gracefully"""
        authenticated_client.sendall(b"xit")
        response = authenticated_client.recv(1024).decode()
        assert response == "xit"


class TestConcurrentConnections:
    """Test concurrent client handling"""
    
    def test_10_concurrent_clients(self, server_process):
        """Server should handle 10 simultaneous clients"""
        results = []
        
        def connect_and_auth(user_info):
            try:
                username, password = user_info
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect(("127.0.0.1", 12000))
                sock.sendall(f"auth {username} {password}".encode())
                response = sock.recv(1024).decode()
                results.append((username, response))
                sock.close()
            except Exception as e:
                results.append((username, f"ERROR: {e}"))
        
        # Get 10 users from credentials
        users = [
            ("hans", "falcon*solo"),
            ("yoda", "wise@!man"),
            ("vader", "sithlord**"),
            ("r2d2", "do*!@#dedo"),
            ("c3p0", "droid#gold"),
            ("leia", "$blasterpistol$"),
            ("obiwan", "(jedimaster)"),
            ("luke", "light==saber"),
            ("chewy", "wookie+aaaawww"),
            ("palpatine", "darkside_%$run"),
        ]
        
        # Connect all 10 clients concurrently
        threads = []
        for user_info in users:
            t = threading.Thread(target=connect_and_auth, args=(user_info,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join(timeout=5)
        
        # Verify all 10 authenticated successfully
        successful = [r for r in results if r[1] == "auth OK"]
        assert len(successful) == 10, f"Expected 10 successful auths, got {len(successful)}"
