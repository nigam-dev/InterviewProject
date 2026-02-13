import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get all players from the backend
 * @returns {Promise<Array>} List of players with scores
 */
export async function getPlayers() {
  try {
    const response = await api.get('/players');
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data.detail || 'Failed to fetch players';
      throw new Error(message);
    } else if (error.request) {
      throw new Error('No response from server. Is the backend running?');
    } else {
      throw new Error(error.message);
    }
  }
}

/**
 * Optimize team based on budget
 * @param {number} budget - Total budget
 * @param {string} strategy - Optimization strategy (MAX_SCORE or MAX_SCORE_PER_COST)
 * @param {Array<number>} player_ids - Optional list of player IDs to restrict optimization pool
 * @returns {Promise<Object>} Optimized team with players, total_cost, total_score
 */
export async function optimizeTeam(budget, strategy = 'MAX_SCORE', player_ids = []) {
  try {
    const response = await api.post('/optimize', { 
      budget: parseInt(budget, 10),
      strategy: strategy,
      player_ids: Array.isArray(player_ids) ? player_ids : []
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data.detail || 
                     (error.response.data.detail?.[0]?.msg) ||
                     'Optimization failed';
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Is the backend running?');
    } else {
      // Something else happened
      throw new Error(error.message);
    }
  }
}
