import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Get user's history records
 * @param {string} userId - User identifier
 * @param {number} limit - Optional maximum number of records to return
 * @returns {Promise} - Promise with history records
 */
export const getUserHistory = async (userId, limit = null) => {
  try {
    let url = `${API_BASE_URL}/api/history/${userId}`;
    
    // Add limit parameter if provided
    if (limit) {
      url += `?limit=${limit}`;
    }
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching history:', error);
    throw error;
  }
};

/**
 * Save a history record
 * @param {string} userId - User identifier
 * @param {string} transcript - Transcribed text
 * @param {string} latex - Generated LaTeX code
 * @returns {Promise} - Promise with saved record
 */
export const saveHistory = async (userId, transcript, latex) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/history`, {
      user_id: userId,
      transcript,
      latex
    });
    return response.data;
  } catch (error) {
    console.error('Error saving history:', error);
    throw error;
  }
};

/**
 * Delete a history record
 * @param {string} userId - User identifier
 * @param {string} timestamp - Record timestamp
 * @returns {Promise} - Promise with deletion result
 */
export const deleteHistoryRecord = async (userId, timestamp) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api/history/${userId}/${timestamp}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting history record:', error);
    throw error;
  }
};

/**
 * Delete all history records for a user
 * @param {string} userId - User identifier
 * @returns {Promise} - Promise with deletion result
 */
export const deleteAllHistory = async (userId) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api/history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting all history records:', error);
    throw error;
  }
};
