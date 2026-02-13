import { useState } from 'react';
import { optimizeTeam } from '../api';
import RoleBadge from './RoleBadge';
import './Optimize.css';

export default function Optimize() {
  const [budget, setBudget] = useState(175);
  const [strategy, setStrategy] = useState('MAX_SCORE');
  const [optimizedTeam, setOptimizedTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [usedBudget, setUsedBudget] = useState(null);

  const handleOptimize = async (e) => {
    e.preventDefault();
    if (loading) return;
    
    try {
      setLoading(true);
      setError(null);
      const currentBudget = budget;
      const result = await optimizeTeam(currentBudget, strategy);
      setOptimizedTeam(result);
      setUsedBudget(currentBudget);
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred during optimization');
      setOptimizedTeam(null);
      setUsedBudget(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBudgetChange = (value) => {
    setBudget(value);
    // Clear results on input change to avoid confusion
    if (optimizedTeam) {
        // Optional: keep results visible but maybe dim them? 
        // For now, simpler to just clear error
        setError(null);
    }
  };

  return (
    <div className="optimize-container">
      <h2>Optimize Team</h2>

      <div className="optimize-grid">
        <div>
          <form onSubmit={handleOptimize} className="optimize-form">
            <div className="form-group">
              <label htmlFor="budget">
                Budget: ${budget}
              </label>
              <div className="budget-controls">
                <input
                  id="budget"
                  type="range"
                  min="50"
                  max="250"
                  value={budget}
                  onChange={(e) => handleBudgetChange(Number(e.target.value))}
                  disabled={loading}
                />
                <input
                  type="number"
                  min="50"
                  max="250"
                  value={budget}
                  onChange={(e) => handleBudgetChange(Number(e.target.value))}
                  className="budget-input"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="strategy">Optimization Strategy:</label>
              <select
                id="strategy"
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="strategy-select"
                disabled={loading}
              >
                <option value="MAX_SCORE">Maximize Total Score</option>
                <option value="MAX_SCORE_PER_COST">Maximize Efficient (Score/Cost)</option>
              </select>
              <small className="strategy-desc">
                {strategy === 'MAX_SCORE'
                  ? 'Best possible team within budget'
                  : 'Best value-for-money players (Efficiency)'}
              </small>
            </div>

            <button type="submit" disabled={loading} className="optimize-button">
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Optimizing...
                </>
              ) : (
                'Optimize Team'
              )}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        <div className="results-card">
          <h3>Optimization Results</h3>

          {!optimizedTeam && (
            <div className="results-empty">
              Run optimization to see results.
            </div>
          )}

          {optimizedTeam && (
            <>
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
                  <span className="stat-value">${(usedBudget - optimizedTeam.total_cost).toFixed(2)}</span>
                </div>
              </div>

              <div className="results-players">
                <h4>Selected Players</h4>
                <div className="team-table-wrapper">
                  <table className="team-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Name</th>
                        <th>Role</th>
                        <th>Runs</th>
                        <th>Wickets</th>
                        <th>SR</th>
                        <th>Price</th>
                        <th>Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...optimizedTeam.players]
                        .sort((a, b) => b.score - a.score)
                        .map((player, index) => (
                          <tr key={player.name}>
                            <td>{index + 1}</td>
                            <td className="player-name">{player.name}</td>
                            <td><RoleBadge role={player.role} /></td>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
