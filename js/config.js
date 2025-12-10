/**
 * Frontend Configuration
 * Update these values based on your environment
 */

const CONFIG = {
    // Backend API URL
    // Development: Use http://localhost:8000 when running backend locally
    // Production: Replace with your deployed backend URL
    API_BASE_URL: 'https://project-spark.onrender.com/api/v1',
    
    // Application Settings
    APP_NAME: 'Friction',
    VERSION: '1.0.0',
    
    // Token storage key
    TOKEN_KEY: 'access_token',
    
    // Pagination
    DEFAULT_PAGE_SIZE: 20,
    
    // Features
    ENABLE_COMMENTS: true,
    ENABLE_VALIDATIONS: true,
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
