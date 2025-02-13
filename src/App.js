import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadLink, setDownloadLink] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setDownloadLink('');

      const response = await axios.post('http://localhost:5000/download', {
        url: url
      }, {
        responseType: 'blob'
      });

      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      setDownloadLink(downloadUrl);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError('Error downloading video. Please check the URL and try again.');
      console.error('Download error:', err);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Video Downloader</h1>
        <p>Download videos from YouTube, Facebook, Instagram, and more</p>
      </header>

      <form onSubmit={handleSubmit} className="download-form">
        <div className="input-group">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste video URL here"
            className="url-input"
            required
          />
          <button
            type="submit"
            className="download-button"
            disabled={loading}
          >
            {loading ? 'Downloading...' : 'Download'}
          </button>
        </div>
      </form>

      {error && <p className="error-message">{error}</p>}

      {downloadLink && (
        <div className="download-section">
          <a
            href={downloadLink}
            download="video.mp4"
            className="download-link"
          >
            Click here if download doesn't start automatically
          </a>
        </div>
      )}
    </div>
  );
}

export default App;