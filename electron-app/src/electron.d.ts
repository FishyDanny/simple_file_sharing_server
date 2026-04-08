export interface ElectronAPI {
  connect: (host: string, port: number) => Promise<{ success: boolean; error?: string }>;
  authenticate: (username: string, password: string) => Promise<{ success: boolean; response: string }>;
  disconnect: () => Promise<{ success: boolean }>;
  publishFile: (filename: string) => Promise<{ success: boolean; response: string }>;
  searchFiles: (substring: string) => Promise<{ success: boolean; response: string }>;
  listPeers: () => Promise<{ success: boolean; response: string }>;
  listFiles: () => Promise<{ success: boolean; response: string }>;
  unpublishFile: (filename: string) => Promise<{ success: boolean; response: string }>;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
