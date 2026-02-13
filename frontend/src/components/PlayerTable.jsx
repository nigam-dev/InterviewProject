import './PlayerTable.css';
import RoleBadge from './RoleBadge';
import { useEffect, useMemo, useState } from 'react';

export default function PlayerTable({ players }) {
  const PAGE_SIZE = 25;
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [players]);

  if (!players || players.length === 0) {
    return <div className="no-data">No players available</div>;
  }

  const totalPages = Math.max(1, Math.ceil(players.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const endIndex = startIndex + PAGE_SIZE;

  const pagePlayers = useMemo(() => players.slice(startIndex, endIndex), [players, startIndex, endIndex]);

  const canPrev = safePage > 1;
  const canNext = safePage < totalPages;

  return (
    <div className="player-table-container">
      <h2>All Players ({players.length})</h2>
      <div className="player-table-max">
        <div className="table-wrapper">
          <table className="player-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Runs</th>
                <th>Wickets</th>
                <th>Strike Rate</th>
                <th>Price</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {pagePlayers.map((player) => (
                <tr key={player.name}>
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

          <div className="pagination" role="navigation" aria-label="Players pagination">
            <button
              type="button"
              className="page-btn"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!canPrev}
            >
              Prev
            </button>
            <div className="page-info">
              Page <strong>{safePage}</strong> of <strong>{totalPages}</strong>
            </div>
            <button
              type="button"
              className="page-btn"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={!canNext}
            >
              Next
            </button>
          </div>
      </div>
    </div>
  );
}

