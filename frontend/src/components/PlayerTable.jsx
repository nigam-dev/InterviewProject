import './PlayerTable.css';

export default function PlayerTable({ players }) {
  if (!players || players.length === 0) {
    return <div className="no-data">No players available</div>;
  }

  return (
    <div className="player-table-container">
      <h2>All Players ({players.length})</h2>
      <div className="table-wrapper">
        <table className="player-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Runs</th>
              <th>Wickets</th>
              <th>Strike Rate</th>
              <th>Price</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => (
              <tr key={index}>
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
  );
}

