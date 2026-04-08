import React from 'react';
import './PeerList.css';

interface Peer {
  name: string;
  address: string;
}

interface PeerListProps {
  peers: Peer[];
  onRefresh: () => void;
}

const PeerList: React.FC<PeerListProps> = ({ peers, onRefresh }) => {
  return (
    <div className="peer-list">
      <div className="peer-list-header">
        <h3>Active Peers</h3>
        <button onClick={onRefresh} className="refresh-btn">Refresh</button>
      </div>

      <div className="peer-items">
        {peers.length === 0 ? (
          <p className="empty-message">No active peers</p>
        ) : (
          peers.map((peer, index) => (
            <div key={index} className="peer-item">
              <span className="peer-name">{peer.name}</span>
              <span className="peer-address">{peer.address}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default PeerList;
