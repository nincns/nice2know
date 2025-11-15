/**
 * Nice2Know - API Communication Layer
 * Handles all communication with the PHP backend
 */

const API = {
    baseUrl: './api',
    
    /**
     * Load data for a given mail_id
     * @param {string} mailId - Mail ID in format YYYYMMDD_HHMMSS
     * @returns {Promise<Object>} - Promise resolving to data object
     */
    async load(mailId) {
        try {
            const response = await fetch(`${this.baseUrl}/load.php?mail_id=${encodeURIComponent(mailId)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load data');
            }
            
            return result.data;
        } catch (error) {
            console.error('API Load Error:', error);
            throw error;
        }
    },
    
    /**
     * Save updated data
     * @param {string} mailId - Mail ID
     * @param {Object} problem - Problem data
     * @param {Object} solution - Solution data (optional)
     * @param {Object} asset - Asset data
     * @returns {Promise<Object>} - Promise resolving to save result
     */
    async save(mailId, problem, solution, asset) {
        try {
            const payload = {
                mail_id: mailId,
                problem: problem,
                solution: solution,
                asset: asset
            };
            
            const response = await fetch(`${this.baseUrl}/save.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to save data');
            }
            
            return result.data;
        } catch (error) {
            console.error('API Save Error:', error);
            throw error;
        }
    }
};

// Export for use in other scripts
window.API = API;
