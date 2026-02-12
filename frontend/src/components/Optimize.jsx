import { useState } from 'react';
import { optimizeTeam } from '../api';
import './Optimize.css';

export default function Optimize() {
  const [budget, setBudget] = useState(175);
  const [optimizedTeam, setOptimizedTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleOptimize = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      const result = await optimizeTeam(budget);
      setOptimizedTeam(result);
    } catch (err) {
      setError(err.message);
      setOptimizedTeam(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="optimize-container">
      <h2>Optimize Team</h2>
      
      <form onSubmit={handleOptimize} className="optimize-form">
        <div className="form-group">
          <label htmlFor="budget">
            Budget: ${budget}
          </label>
          <input
            id="budget"
            type="range"
            min="50"
            max="250"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
          />
          <input
            type="number"
            min="50"
            max="250"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="budget-input"
          />
        </div>

        <button type="submit" disabled={loading} className="optimize-button">
          {loading ? 'Optimizing...' : 'Optimize Team'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {optimizedTeam && (
        <div className="results">
          <div className="results-summary">
            <h3>Optimization Results</h3>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Total Cost:</span>
                <span className="stat-value">${optimizedTeam.total_cost.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Score:</span>
                <span className="stat-value">{optimizedTeam.total_score.toFixed(1)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Players:</span>
                <span className="stat-value">{optimizedTeam.players.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Budget Remaining:</span>
                <span className="stat-value">${(budget - optimizedTeam.total_cost).toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="selected-players">
            <h4>Selected Players</h4>
            <table className="team-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Runs</th>
                  <th>Wickets</th>
                  <th>SR</th>
                  <th>Price</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {optimizedTeam.players
                  .sort((a, b) => b.score - a.score)
                  .map((player, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td className="player-name">{player.name}</td>
                      <td>{player.runs}</td>
                      <td>{player.wickets}</td>
                      <td>{player.strike_rate.toFixed(1)}</td>
                      <td>${player.price.toFixed(0)}</td>
                      <td className="score">{player.score.toFixed(1)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
