import React, { useState } from 'react';
import AuthForm from './components/AuthForm';
import FileList from './components/FileList';
import SearchBar from './components/SearchBar';
import PeerList from './components/PeerList';
import './App.css';

interface File {
  name: string;
  published: boolean;
}

interface Peer {
  name: string;
  address: string;
}

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [peers, setPeers] = useState<Peer[]>([]);
  const [status, setStatus] = useState('Disconnected');

  const handleAuthenticate = async (user: string) => {
    setIsAuthenticated(true);
    setUsername(user);
    setStatus(`Connected as ${user}`);
  };

  const handleDisconnect = async () => {
    await window.electronAPI.disconnect();
    setIsAuthenticated(false);
    setUsername('');
    setFiles([]);
    setPeers([]);
    setStatus('Disconnected');
  };

  const handlePublish = async (filename: string) => {
    const result = await window.electronAPI.publishFile(filename);
    if (result.success) {
      const newFile = { name: filename, published: true };
      setFiles([...files, newFile]);
      setStatus(`Published ${filename}`);
    } else {
      setStatus(`Failed to publish: ${result.response}`);
    }
  };

  const handleSearch = async (substring: string) => {
    const result = await window.electronAPI.searchFiles(substring);
    if (result.success) {
      if (result.response.startsWith('sch ')) {
        const foundFiles = result.response.substring(4).split(' ').filter(f => f);
        // Display found files
        setStatus(`Found ${foundFiles.length} files`);
      } else {
        setStatus('No files found');
      }
    }
  };

  const handleRefreshPeers = async () => {
    const result = await window.electronAPI.listPeers();
    if (result.success) {
      // Parse peers from response
      setStatus('Peers refreshed');
      // Would parse actual peers from response
    }
  };

  const handleRefreshFiles = async () => {
    const result = await window.electronAPI.listFiles();
    if (result.success) {
      // Parse files from response
      setStatus('Files refreshed');
      // Would parse actual files from response
    }
  };

  if (!isAuthenticated) {
    return <AuthForm onAuthenticate={handleAuthenticate} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>P2P Vault</h1>
        <div className="status">{status}</div>
        <button onClick={handleDisconnect} className="disconnect-btn">
          Disconnect
        </button>
      </header>

      <main className="app-main">
        <div className="left-panel">
          <SearchBar onSearch={handleSearch} />
          <FileList files={files} onPublish={handlePublish} onRefresh={handleRefreshFiles} />
        </div>

        <div className="right-panel">
          <PeerList peers={peers} onRefresh={handleRefreshPeers} />
        </div>
      </main>
    </div>
  );
};

export default App;
