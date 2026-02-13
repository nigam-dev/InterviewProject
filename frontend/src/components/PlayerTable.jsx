import './PlayerTable.css';
import RoleBadge from './RoleBadge';
import { useEffect, useMemo, useState } from 'react';

export default function PlayerTable({ players, onSelectionChange }) {
  const PAGE_SIZE = 25;
  const [page, setPage] = useState(1);
  const [selectedPlayers, setSelectedPlayers] = useState(() => new Set());
  const [searchQuery, setSearchQuery] = useState('');

  const filteredPlayers = useMemo(() => {
    if (!players || players.length === 0) return [];
    const q = searchQuery.trim().toLowerCase();
    if (!q) return players;

    return players.filter((p) => {
      const name = String(p?.name ?? '').toLowerCase();
      const role = String(p?.role ?? '').toLowerCase();
      return name.includes(q) || role.includes(q);
    });
  }, [players, searchQuery]);

  const allPlayerIds = useMemo(() => {
    if (!filteredPlayers || filteredPlayers.length === 0) return [];
    return filteredPlayers
      .map((p) => p?.id)
      .filter((id) => typeof id === 'number' && Number.isFinite(id));
  }, [filteredPlayers]);

  useEffect(() => {
    setPage(1);
  }, [players]);

  useEffect(() => {
    setPage(1);
  }, [searchQuery]);

  useEffect(() => {
    if (!players || players.length === 0) {
      setSelectedPlayers(new Set());
      return;
    }

    const validIds = new Set(
      players
        .map((p) => p?.id)
        .filter((id) => typeof id === 'number' && Number.isFinite(id))
    );

    setSelectedPlayers((prev) => {
      if (prev.size === 0) return prev;
      const next = new Set([...prev].filter((id) => validIds.has(id)));
      return next.size === prev.size ? prev : next;
    });
  }, [players]);

  useEffect(() => {
    if (typeof onSelectionChange === 'function') {
      onSelectionChange(Array.from(selectedPlayers));
    }
  }, [selectedPlayers, onSelectionChange]);

  if (!players || players.length === 0) {
    return <div className="no-data">No players available</div>;
  }

  const totalPages = Math.max(1, Math.ceil(filteredPlayers.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const endIndex = startIndex + PAGE_SIZE;

  const pagePlayers = useMemo(
    () => filteredPlayers.slice(startIndex, endIndex),
    [filteredPlayers, startIndex, endIndex]
  );

  const canPrev = safePage > 1;
  const canNext = safePage < totalPages;

  function toggleSelected(playerId) {
    if (typeof playerId !== 'number' || !Number.isFinite(playerId)) return;
    setSelectedPlayers((prev) => {
      const next = new Set(prev);
      if (next.has(playerId)) next.delete(playerId);
      else next.add(playerId);
      return next;
    });
  }

  function selectAllPlayers() {
    setSelectedPlayers(new Set(allPlayerIds));
  }

  function clearSelection() {
    setSelectedPlayers(new Set());
  }

  return (
    <div className="player-table-container">
      <h2>
        All Players ({filteredPlayers.length}
        {filteredPlayers.length !== players.length ? ` / ${players.length}` : ''})
      </h2>

      <div className="table-toolbar" aria-label="Players tools">
        <div className="search-group">
          <label className="search-label" htmlFor="playerSearch">
            Search
          </label>
          <input
            id="playerSearch"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name or role"
            className="search-input"
          />
        </div>

        <div className="selection-controls" role="group" aria-label="Player selection">
        <button
          type="button"
          className="page-btn"
          onClick={selectAllPlayers}
          disabled={allPlayerIds.length === 0 || selectedPlayers.size === allPlayerIds.length}
        >
          Select All Players
        </button>
        <button
          type="button"
          className="page-btn"
          onClick={clearSelection}
          disabled={selectedPlayers.size === 0}
        >
          Clear Selection
        </button>
        <div className="selection-info" aria-live="polite">
          Selected: <strong>{selectedPlayers.size}</strong>
        </div>
      </div>
      </div>
      <div className="player-table-max">
        <div className="table-wrapper">
          <table className="player-table">
            <thead>
              <tr>
                <th aria-label="Select player" />
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
                <tr
                  key={player.id ?? player.name}
                  className={
                    typeof player?.id === 'number' &&
                    Number.isFinite(player.id) &&
                    selectedPlayers.has(player.id)
                      ? 'is-selected'
                      : undefined
                  }
                >
                  <td>
                    <input
                      type="checkbox"
                      checked={
                        typeof player?.id === 'number' &&
                        Number.isFinite(player.id) &&
                        selectedPlayers.has(player.id)
                      }
                      disabled={!(typeof player?.id === 'number' && Number.isFinite(player.id))}
                      onChange={() => toggleSelected(player?.id)}
                      aria-label={`Select ${player?.name ?? 'player'}`}
                    />
                  </td>
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

