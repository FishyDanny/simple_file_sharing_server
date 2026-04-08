import React, { useState } from 'react';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (substring: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = () => {
    if (searchTerm.trim()) {
      onSearch(searchTerm.trim());
    }
  };

  return (
    <div className="search-bar">
      <input
        id="search-input"
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search files..."
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button id="search-button" onClick={handleSearch}>Search</button>
    </div>
  );
};

export default SearchBar;
