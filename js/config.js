/**
 * Frontend Configuration
 * Update these values based on your environment
 */

const CONFIG = {
    // Backend API URL - uses relative path for same-origin requests
    API_BASE_URL: '/api/v1',
    
    // Application Settings
    APP_NAME: 'OppGrid',
    VERSION: '1.0.0',
    
    // Token storage key
    TOKEN_KEY: 'access_token',
    
    // Pagination
    DEFAULT_PAGE_SIZE: 20,
    
    // Features
    ENABLE_COMMENTS: true,
    ENABLE_VALIDATIONS: true,
};

// Backwards-compatible global (many pages reference API_BASE_URL directly).
// Keep this in sync with CONFIG.API_BASE_URL.
if (typeof window !== 'undefined') {
    window.API_BASE_URL = CONFIG.API_BASE_URL;
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
