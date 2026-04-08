import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  connect: (host: string, port: number) => ipcRenderer.invoke('connect', host, port),
  authenticate: (username: string, password: string) => ipcRenderer.invoke('authenticate', username, password),
  disconnect: () => ipcRenderer.invoke('disconnect'),
  publishFile: (filename: string) => ipcRenderer.invoke('publish', filename),
  searchFiles: (substring: string) => ipcRenderer.invoke('search', substring),
  listPeers: () => ipcRenderer.invoke('listPeers'),
  listFiles: () => ipcRenderer.invoke('listFiles'),
  unpublishFile: (filename: string) => ipcRenderer.invoke('unpublish', filename),
});
