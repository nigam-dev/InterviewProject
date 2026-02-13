import { useState, useEffect } from 'react';
import { getPlayers } from './api';
import PlayerTable from './components/PlayerTable';
import Optimize from './components/Optimize';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('optimize');
  const [players, setPlayers] = useState([]);
  const [selectedPlayerIds, setSelectedPlayerIds] = useState([]);
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
    <div className="app">
      <header className="app-header">
        <div className="content-container">
          <h1>🏏 Cricket Team Optimizer</h1>
          <p>Build your perfect cricket team within budget constraints</p>
        </div>
      </header>

      <nav className="tabs" aria-label="Application sections">
        <div className="container tabs-inner">
          <button
            className={`tab ${activeTab === 'optimize' ? 'active' : ''}`}
            onClick={() => setActiveTab('optimize')}
            type="button"
          >
            Optimize Team
          </button>
          <button
            className={`tab ${activeTab === 'players' ? 'active' : ''}`}
            onClick={() => setActiveTab('players')}
            type="button"
          >
            All Players
          </button>
        </div>
      </nav>

      <main className="main" role="main">
        <div className="main-container">
          <div className="content-container main-content">
            {loading && <div className="loading">Loading players...</div>}
            {error && <div className="error">Error: {error}</div>}
            {!loading && !error && (
              <>
                {activeTab === 'optimize' && <Optimize selectedPlayers={selectedPlayerIds} />}
                {activeTab === 'players' && (
                  <PlayerTable
                    players={players}
                    onSelectionChange={setSelectedPlayerIds}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>Powered by FastAPI + React + PuLP Linear Programming</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

