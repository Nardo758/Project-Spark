/**
 * Friction API Client
 * Connects the frontend to the backend API
 */

// Use config if available, otherwise fallback to default
const API_BASE_URL = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL) 
    ? CONFIG.API_BASE_URL 
    : 'http://localhost:8000/api/v1';

class FrictionAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('access_token');
    }

    // Helper method to get headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Helper method to handle responses
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // Authentication
    async register(email, password, name, bio = '') {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: JSON.stringify({ email, password, name, bio })
        });
        return this.handleResponse(response);
    }

    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);  // OAuth2 uses 'username' field
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await this.handleResponse(response);
        this.token = data.access_token;
        localStorage.setItem('access_token', data.access_token);
        return data;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    // Users
    async getCurrentUser() {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async updateCurrentUser(userData) {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
        return this.handleResponse(response);
    }

    async getUser(userId) {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    // Opportunities
    async createOpportunity(opportunityData) {
        const response = await fetch(`${API_BASE_URL}/opportunities/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(opportunityData)
        });
        return this.handleResponse(response);
    }

    async getOpportunities(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const url = `${API_BASE_URL}/opportunities/${queryParams ? '?' + queryParams : ''}`;

        const response = await fetch(url, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    async getOpportunity(opportunityId) {
        const response = await fetch(`${API_BASE_URL}/opportunities/${opportunityId}`, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    async updateOpportunity(opportunityId, opportunityData) {
        const response = await fetch(`${API_BASE_URL}/opportunities/${opportunityId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(opportunityData)
        });
        return this.handleResponse(response);
    }

    async deleteOpportunity(opportunityId) {
        const response = await fetch(`${API_BASE_URL}/opportunities/${opportunityId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (response.status === 204) {
            return { success: true };
        }
        return this.handleResponse(response);
    }

    async searchOpportunities(query, params = {}) {
        const queryParams = new URLSearchParams({ q: query, ...params }).toString();
        const response = await fetch(`${API_BASE_URL}/opportunities/search/?${queryParams}`, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    // Validations
    async createValidation(opportunityId) {
        const response = await fetch(`${API_BASE_URL}/validations/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ opportunity_id: opportunityId })
        });
        return this.handleResponse(response);
    }

    async deleteValidation(validationId) {
        const response = await fetch(`${API_BASE_URL}/validations/${validationId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (response.status === 204) {
            return { success: true };
        }
        return this.handleResponse(response);
    }

    async getOpportunityValidations(opportunityId) {
        const response = await fetch(`${API_BASE_URL}/validations/opportunity/${opportunityId}`, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    // Comments
    async createComment(opportunityId, content) {
        const response = await fetch(`${API_BASE_URL}/comments/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ opportunity_id: opportunityId, content })
        });
        return this.handleResponse(response);
    }

    async getOpportunityComments(opportunityId) {
        const response = await fetch(`${API_BASE_URL}/comments/opportunity/${opportunityId}`, {
            headers: this.getHeaders(false)
        });
        return this.handleResponse(response);
    }

    async updateComment(commentId, content) {
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ content })
        });
        return this.handleResponse(response);
    }

    async deleteComment(commentId) {
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        if (response.status === 204) {
            return { success: true };
        }
        return this.handleResponse(response);
    }

    async likeComment(commentId) {
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}/like`, {
            method: 'POST',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // Helper: Check if user is authenticated
    isAuthenticated() {
        return !!this.token;
    }
}

// Create a global instance
const api = new FrictionAPI();
