import { app, BrowserWindow, ipcMain } from 'electron';
import * as net from 'net';
import * as path from 'path';

let mainWindow: BrowserWindow | null = null;
let clientSocket: net.Socket | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
}

// IPC: Connect to server
ipcMain.handle('connect', async (_, host: string, port: number) => {
  return new Promise((resolve) => {
    clientSocket = new net.Socket();
    clientSocket.connect(port, host, () => {
      resolve({ success: true });
    });
    clientSocket.on('error', (err) => {
      resolve({ success: false, error: err.message });
    });
  });
});

// IPC: Authenticate
ipcMain.handle('authenticate', async (_, username: string, password: string) => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write(`auth ${username} ${password}`);
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: response === 'auth OK', response });
    });
  });
});

// IPC: Disconnect
ipcMain.handle('disconnect', async () => {
  if (clientSocket) {
    clientSocket.write('xit');
    clientSocket.destroy();
    clientSocket = null;
  }
  return { success: true };
});

// IPC: Publish file
ipcMain.handle('publish', async (_, filename: string) => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write(`pub ${filename}`);
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: response === 'pub OK', response });
    });
  });
});

// IPC: Search files
ipcMain.handle('search', async (_, substring: string) => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write(`sch ${substring}`);
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: true, response });
    });
  });
});

// IPC: List active peers
ipcMain.handle('listPeers', async () => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write('lap');
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: true, response });
    });
  });
});

// IPC: List published files
ipcMain.handle('listFiles', async () => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write('lpf');
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: true, response });
    });
  });
});

// IPC: Unpublish file
ipcMain.handle('unpublish', async (_, filename: string) => {
  return new Promise((resolve) => {
    if (!clientSocket) {
      resolve({ success: false, error: 'Not connected' });
      return;
    }
    clientSocket.write(`unp ${filename}`);
    clientSocket.once('data', (data) => {
      const response = data.toString();
      resolve({ success: response === 'unp OK', response });
    });
  });
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
