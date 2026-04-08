import React, { useState } from 'react';
import './FileList.css';

interface File {
  name: string;
  published: boolean;
}

interface FileListProps {
  files: File[];
  onPublish: (filename: string) => void;
  onRefresh: () => void;
}

const FileList: React.FC<FileListProps> = ({ files, onPublish, onRefresh }) => {
  const [newFilename, setNewFilename] = useState('');

  const handlePublish = () => {
    if (newFilename.trim()) {
      onPublish(newFilename.trim());
      setNewFilename('');
    }
  };

  return (
    <div className="file-list">
      <div className="file-list-header">
        <h3>My Files</h3>
        <button onClick={onRefresh} className="refresh-btn">Refresh</button>
      </div>

      <div className="publish-form">
        <input
          type="text"
          value={newFilename}
          onChange={(e) => setNewFilename(e.target.value)}
          placeholder="Enter filename to publish"
        />
        <button onClick={handlePublish} className="publish-btn">Publish</button>
      </div>

      <div className="file-items">
        {files.length === 0 ? (
          <p className="empty-message">No files published</p>
        ) : (
          files.map((file, index) => (
            <div key={index} className="file-item">
              <span className="file-name">{file.name}</span>
              <span className={`file-status ${file.published ? 'published' : ''}`}>
                {file.published ? 'Published' : 'Local'}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FileList;
