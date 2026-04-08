import React, { useState } from 'react';
import './AuthForm.css';

interface AuthFormProps {
  onAuthenticate: (username: string) => void;
}

const AuthForm: React.FC<AuthFormProps> = ({ onAuthenticate }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [host, setHost] = useState('127.0.0.1');
  const [port, setPort] = useState('12000');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Connect to server
      const connectResult = await window.electronAPI.connect(host, parseInt(port));
      if (!connectResult.success) {
        setError(`Connection failed: ${connectResult.error || 'Unknown error'}`);
        setLoading(false);
        return;
      }

      // Authenticate
      const authResult = await window.electronAPI.authenticate(username, password);
      if (authResult.success) {
        onAuthenticate(username);
      } else {
        setError('Authentication failed. Please check your credentials.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <div className="auth-form">
        <h2>P2P Vault - Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Server Host:</label>
            <input
              type="text"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              placeholder="127.0.0.1"
              required
            />
          </div>

          <div className="form-group">
            <label>Server Port:</label>
            <input
              type="text"
              value={port}
              onChange={(e) => setPort(e.target.value)}
              placeholder="12000"
              required
            />
          </div>

          <div className="form-group">
            <label>Username:</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button id="login-button" type="submit" disabled={loading}>
            {loading ? 'Connecting...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthForm;
