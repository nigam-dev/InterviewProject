import { useState, useEffect } from 'react';
import { getPlayers } from '../services/api';
import PlayerTable from '../components/PlayerTable';
import Optimize from '../components/Optimize';

export default function Home() {
  const [activeTab, setActiveTab] = useState('optimize');
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPlayers();
  }, []);

  async function loadPlayers() {
    try {
      setLoading(true);
      const data = await getPlayers();
      setPlayers(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="home-page">
      <header className="app-header">
        <h1>🏏 Cricket Team Optimizer</h1>
        <p>Build your perfect cricket team within budget constraints</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'optimize' ? 'active' : ''}`}
          onClick={() => setActiveTab('optimize')}
        >
          Optimize Team
        </button>
        <button
          className={`tab ${activeTab === 'players' ? 'active' : ''}`}
          onClick={() => setActiveTab('players')}
        >
          All Players
        </button>
      </nav>

      <main className="main-content">
        {loading && <div className="loading">Loading players...</div>}
        {error && <div className="error">Error: {error}</div>}
        {!loading && !error && (
          <>
            {activeTab === 'optimize' && <Optimize />}
            {activeTab === 'players' && <PlayerTable players={players} />}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI + React + PuLP Linear Programming</p>
      </footer>
    </div>
  );
}
