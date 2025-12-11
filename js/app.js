/**
 * Friction Frontend - Main Application Logic
 * Connects UI to backend API with all features
 */

// API Configuration - uses CONFIG from config.js via api.js

let currentUser = null;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        try {
            currentUser = await api.getCurrentUser();
            updateUIForLoggedInUser();
        } catch (error) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
        }
    }

    // Load initial data
    await loadOpportunities();
    setupEventListeners();
});

// Update UI for logged in user
function updateUIForLoggedInUser() {
    const authButtons = document.querySelectorAll('.auth-required');
    authButtons.forEach(btn => btn.style.display = 'block');

    const guestButtons = document.querySelectorAll('.guest-only');
    guestButtons.forEach(btn => btn.style.display = 'none');
}

// Load opportunities with filters
async function loadOpportunities(filters = {}) {
    try {
        const params = {
            limit: 20,
            sort_by: filters.sortBy || 'recent',
            ...filters
        };

        const data = await api.getOpportunities(params);
        displayOpportunities(data.opportunities);
        updatePagination(data);
    } catch (error) {
        console.error('Error loading opportunities:', error);
        showError('Failed to load opportunities');
    }
}

// Display opportunities on the page
function displayOpportunities(opportunities) {
    const container = document.getElementById('opportunities-container');
    if (!container) return;

    container.innerHTML = '';

    opportunities.forEach(opp => {
        const card = createOpportunityCard(opp);
        container.appendChild(card);
    });
}

// Update pagination display
function updatePagination(data) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;
    
    const totalPages = Math.ceil(data.total / data.page_size);
    paginationContainer.innerHTML = `Page ${data.page} of ${totalPages} (${data.total} total)`;
}

// Create opportunity card with feasibility score
function createOpportunityCard(opp) {
    const card = document.createElement('div');
    card.className = 'opportunity-card';
    card.onclick = () => showOpportunityDetail(opp.id);

    // Calculate feasibility badge
    const feasibilityBadge = opp.feasibility_score
        ? getFeasibilityBadge(opp.feasibility_score)
        : '';

    // Geographic badge
    const geoBadge = getGeographicBadge(opp);

    card.innerHTML = `
        <div class="card-header">
            <h3>${opp.title}</h3>
            ${feasibilityBadge}
        </div>
        <p class="description">${truncate(opp.description, 150)}</p>
        <div class="card-meta">
            <span class="category">${opp.category}</span>
            ${geoBadge}
            <span class="validation-count">
                ✓ ${opp.validation_count} validations
            </span>
            ${opp.growth_rate > 0 ? `<span class="growth">↗ ${opp.growth_rate}%</span>` : ''}
        </div>
        <div class="card-footer">
            <span class="severity">Severity: ${opp.severity}/5</span>
            <span class="market-size">${opp.market_size || 'Unknown market'}</span>
        </div>
    `;

    return card;
}

// Get feasibility badge HTML
function getFeasibilityBadge(score) {
    let level, className;

    if (score >= 75) {
        level = 'High';
        className = 'feasibility-high';
    } else if (score >= 50) {
        level = 'Medium';
        className = 'feasibility-medium';
    } else if (score >= 25) {
        level = 'Low';
        className = 'feasibility-low';
    } else {
        level = 'Very Low';
        className = 'feasibility-very-low';
    }

    return `
        <div class="feasibility-badge ${className}">
            <span class="score">${score.toFixed(1)}</span>
            <span class="level">${level}</span>
        </div>
    `;
}

// Get geographic badge
function getGeographicBadge(opp) {
    const icons = {
        'local': '📍',
        'regional': '🗺️',
        'national': '🏴',
        'international': '🌍',
        'online': '💻'
    };

    const icon = icons[opp.geographic_scope] || '🌐';
    const location = opp.city || opp.region || opp.country || opp.geographic_scope;

    return `<span class="geo-badge">${icon} ${location}</span>`;
}

// Show opportunity detail
async function showOpportunityDetail(oppId) {
    try {
        const opp = await api.getOpportunity(oppId);
        const feasibility = await fetchFeasibilityAnalysis(oppId);

        displayOpportunityDetail(opp, feasibility);
    } catch (error) {
        console.error('Error loading opportunity detail:', error);
        showError('Failed to load opportunity details');
    }
}

// Fetch feasibility analysis
async function fetchFeasibilityAnalysis(oppId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/analytics/feasibility/${oppId}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching feasibility:', error);
        return null;
    }
}

// Submit new opportunity with duplicate check
async function submitOpportunity(formData) {
    try {
        // First, check for duplicates
        const duplicateCheck = await fetch(`${CONFIG.API_BASE_URL}/analytics/check-duplicate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: formData.title,
                description: formData.description
            })
        });

        const duplicateData = await duplicateCheck.json();

        if (duplicateData.is_duplicate && duplicateData.potential_duplicates.length > 0) {
            // Show duplicate warning
            const proceed = await showDuplicateWarning(duplicateData.potential_duplicates);
            if (!proceed) {
                return; // User chose not to submit
            }
        }

        // Create the opportunity
        const opportunity = await api.createOpportunity(formData);

        showSuccess('Opportunity submitted successfully!');
        await loadOpportunities();
        closeSubmitModal();
    } catch (error) {
        console.error('Error submitting opportunity:', error);
        showError('Failed to submit opportunity: ' + error.message);
    }
}

// Show duplicate warning modal
async function showDuplicateWarning(duplicates) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal duplicate-warning-modal';

        const duplicatesList = duplicates.map(dup => `
            <div class="duplicate-item" onclick="viewOpportunity(${dup.opportunity_id})">
                <h4>${dup.title}</h4>
                <p>
                    ${dup.similarity_score}% similar •
                    ${dup.validation_count} validations
                </p>
                <button class="btn-secondary" onclick="validateExisting(${dup.opportunity_id}); event.stopPropagation();">
                    Validate This Instead
                </button>
            </div>
        `).join('');

        modal.innerHTML = `
            <div class="modal-content">
                <h2>⚠️ Similar Opportunities Found</h2>
                <p>We found existing opportunities very similar to yours:</p>
                <div class="duplicates-list">
                    ${duplicatesList}
                </div>
                <div class="modal-actions">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove()">
                        Cancel
                    </button>
                    <button class="btn-primary" id="proceed-anyway">
                        My Problem is Different - Submit Anyway
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        document.getElementById('proceed-anyway').onclick = () => {
            modal.remove();
            resolve(true);
        };

        modal.querySelector('.btn-secondary').onclick = () => {
            modal.remove();
            resolve(false);
        };
    });
}

// Validate existing opportunity
async function validateExisting(oppId) {
    try {
        if (!api.isAuthenticated()) {
            showLoginPrompt();
            return;
        }

        await api.createValidation(oppId);
        showSuccess('Validation added!');
        await loadOpportunities();
    } catch (error) {
        console.error('Error validating:', error);
        showError('Failed to add validation: ' + error.message);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Geographic filters
    const geoScopeFilter = document.getElementById('geo-scope-filter');
    if (geoScopeFilter) {
        geoScopeFilter.addEventListener('change', (e) => {
            loadOpportunities({ geographic_scope: e.target.value });
        });
    }

    // Country filter
    const countryFilter = document.getElementById('country-filter');
    if (countryFilter) {
        countryFilter.addEventListener('input', debounce((e) => {
            loadOpportunities({ country: e.target.value });
        }, 500));
    }

    // Sort filter
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        sortFilter.addEventListener('change', (e) => {
            loadOpportunities({ sort_by: e.target.value });
        });
    }

    // Category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', (e) => {
            loadOpportunities({ category: e.target.value });
        });
    }

    // Completion status filter
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', (e) => {
            loadOpportunities({ completion_status: e.target.value });
        });
    }
}

// Load top feasible opportunities
async function loadTopFeasible() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/analytics/top-feasible?limit=10&min_score=60`);
        const opportunities = await response.json();

        displayTopFeasible(opportunities);
    } catch (error) {
        console.error('Error loading top feasible:', error);
    }
}

// Display top feasible opportunities
function displayTopFeasible(opportunities) {
    const container = document.getElementById('top-feasible-container');
    if (!container) return;

    container.innerHTML = '<h2>🔥 Top Feasible Opportunities</h2>';

    opportunities.forEach((opp, index) => {
        const item = document.createElement('div');
        item.className = 'feasible-item';
        item.onclick = () => showOpportunityDetail(opp.id);

        item.innerHTML = `
            <div class="rank">#${index + 1}</div>
            <div class="content">
                <h4>${opp.title}</h4>
                <p>${opp.category} • ${opp.validation_count} validations</p>
            </div>
            ${getFeasibilityBadge(opp.feasibility_score)}
        `;

        container.appendChild(item);
    });
}

// Load geographic distribution
async function loadGeographicDistribution() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/analytics/geographic/distribution`);
        const data = await response.json();

        displayGeographicDistribution(data);
    } catch (error) {
        console.error('Error loading geographic distribution:', error);
    }
}

// Display geographic distribution
function displayGeographicDistribution(data) {
    const container = document.getElementById('geo-distribution-container');
    if (!container) return;

    const scopeData = data.scope_distribution;
    const total = Object.values(scopeData).reduce((a, b) => a + b, 0);

    container.innerHTML = `
        <h3>Geographic Distribution</h3>
        <div class="distribution-chart">
            ${Object.entries(scopeData).map(([scope, count]) => {
                const percentage = (count / total * 100).toFixed(1);
                return `
                    <div class="distribution-item">
                        <span class="label">${scope}</span>
                        <div class="bar-container">
                            <div class="bar" style="width: ${percentage}%"></div>
                        </div>
                        <span class="count">${count} (${percentage}%)</span>
                    </div>
                `;
            }).join('')}
        </div>

        <h4>Top Countries</h4>
        <div class="top-countries">
            ${data.top_countries.map(item => `
                <div class="country-item">
                    <span>${item.country}</span>
                    <span class="count">${item.count}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Load completion statistics
async function loadCompletionStats() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/analytics/completion-stats`);
        const stats = await response.json();

        displayCompletionStats(stats);
    } catch (error) {
        console.error('Error loading completion stats:', error);
    }
}

// Display completion statistics
function displayCompletionStats(stats) {
    const container = document.getElementById('completion-stats-container');
    if (!container) return;

    container.innerHTML = `
        <h3>Completion Progress</h3>
        <div class="completion-overview">
            <div class="stat-card">
                <div class="stat-value">${stats.completion_rate}%</div>
                <div class="stat-label">Completion Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.completion_breakdown.solved}</div>
                <div class="stat-label">Solved</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.recently_solved_count}</div>
                <div class="stat-label">Solved This Month</div>
            </div>
        </div>

        <div class="completion-breakdown">
            <h4>Status Breakdown</h4>
            ${Object.entries(stats.completion_breakdown).map(([status, count]) => `
                <div class="status-item">
                    <span class="status-label">${status}</span>
                    <span class="status-count">${count}</span>
                </div>
            `).join('')}
        </div>

        ${stats.recently_solved.length > 0 ? `
            <div class="recently-solved">
                <h4>Recently Solved</h4>
                ${stats.recently_solved.map(item => `
                    <div class="solved-item" onclick="showOpportunityDetail(${item.id})">
                        <div class="title">${item.title}</div>
                        <div class="solver">Solved by ${item.solved_by || 'Unknown'}</div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
}

// Utility functions
function truncate(text, length) {
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showError(message) {
    // Implement your error notification
    console.error(message);
    alert(message);
}

function showSuccess(message) {
    // Implement your success notification
    console.log(message);
    alert(message);
}

function showLoginPrompt() {
    window.location.href = 'login.html';
}

// Export for global use
window.FrictionApp = {
    loadOpportunities,
    submitOpportunity,
    validateExisting,
    showOpportunityDetail,
    loadTopFeasible,
    loadGeographicDistribution,
    loadCompletionStats
};
