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

// Lightweight global tracking helper (best-effort; never blocks UI).
if (typeof window !== 'undefined') {
    (function () {
        if (window.OppGridTrack) return;

        function getAnonymousId() {
            try {
                const key = 'oppgrid_anon_id';
                const existing = localStorage.getItem(key);
                if (existing) return existing;
                const id = (window.crypto && window.crypto.randomUUID)
                    ? window.crypto.randomUUID()
                    : String(Date.now()) + '_' + Math.random().toString(16).slice(2);
                localStorage.setItem(key, id);
                return id;
            } catch (e) {
                return null;
            }
        }

        function getAccessToken() {
            try { return localStorage.getItem(CONFIG.TOKEN_KEY) || localStorage.getItem('access_token'); } catch (e) { return null; }
        }

        function postEvent(event) {
            const url = `${CONFIG.API_BASE_URL}/analytics/events`;
            const body = JSON.stringify(event);

            // Prefer sendBeacon when available (doesn't block unload).
            if (navigator && navigator.sendBeacon) {
                try {
                    const blob = new Blob([body], { type: 'application/json' });
                    return navigator.sendBeacon(url, blob);
                } catch (e) {
                    // fall through
                }
            }

            const headers = { 'Content-Type': 'application/json' };
            const token = getAccessToken();
            if (token) headers['Authorization'] = `Bearer ${token}`;
            fetch(url, { method: 'POST', headers, body }).catch(() => {});
            return true;
        }

        function track(name, properties = {}) {
            const anon = getAnonymousId();
            const event = {
                name,
                path: window.location.pathname + window.location.search,
                referrer: document.referrer || null,
                anonymous_id: anon,
                properties: properties || {},
            };
            postEvent(event);
        }

        window.OppGridTrack = { track };

        // Auto page view
        try {
            track('page_view', { title: document.title });
        } catch (e) {}
    })();
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
