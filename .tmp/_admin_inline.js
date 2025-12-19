const API_BASE_URL = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL) ? CONFIG.API_BASE_URL : '/api/v1';
        let currentUser = null;

        async function init() {
            if (!OppGridAuth.requireAuth({ redirect: 'admin.html' })) return;
            const token = OppGridAuth.getAccessToken();

            try {
                const response = await fetch(`${API_BASE_URL}/users/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) throw new Error('Not authenticated');

                currentUser = await response.json();

                if (!currentUser.is_admin) {
                    showToast('Access denied: Admin privileges required', 'error');
                    setTimeout(() => window.location.href = 'index.html', 2000);
                    return;
                }

                document.getElementById('admin-name').textContent = currentUser.name;

                setupNavigation();
                loadDashboard();
            } catch (error) {
                console.error('Auth error:', error);
                OppGridAuth.redirectToSignin({ redirect: 'admin.html' });
            }
        }

        function setupNavigation() {
            const navLinks = document.querySelectorAll('.sidebar-nav a');
            
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const section = link.dataset.section;
                    
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    
                    document.querySelectorAll('[id^="section-"]').forEach(s => s.classList.add('hidden'));
                    document.getElementById(`section-${section}`).classList.remove('hidden');
                    
                    loadSection(section);
                });
            });

            document.getElementById('user-search').addEventListener('input', debounce(() => loadUsers(), 300));
            document.getElementById('user-filter').addEventListener('change', () => loadUsers());
            document.getElementById('opp-search').addEventListener('input', debounce(() => loadOpportunities(), 300));
            document.getElementById('sub-tier-filter').addEventListener('change', () => loadSubscriptions());
            document.getElementById('report-status-filter').addEventListener('change', () => loadReports());
            document.getElementById('partner-search')?.addEventListener('input', debounce(() => loadPartners(), 300));
            document.getElementById('partner-status-filter')?.addEventListener('change', () => loadPartners());
            document.getElementById('tracking-event-filter')?.addEventListener('change', () => loadTrackingEvents());
            document.getElementById('tracking-days')?.addEventListener('change', () => loadTracking());

            document.getElementById('jobruns-name')?.addEventListener('input', debounce(() => loadJobRuns(), 300));
            document.getElementById('jobruns-status')?.addEventListener('change', () => loadJobRuns());
            document.getElementById('audit-action')?.addEventListener('input', debounce(() => loadAuditLogs(), 300));
            document.getElementById('audit-resource-type')?.addEventListener('input', debounce(() => loadAuditLogs(), 300));
            document.getElementById('audit-resource-id')?.addEventListener('input', debounce(() => loadAuditLogs(), 300));
        }

        function loadSection(section) {
            switch(section) {
                case 'dashboard': loadDashboard(); break;
                case 'tracking': loadTracking(); break;
                case 'ops': loadOps(); break;
                case 'users': loadUsers(); break;
                case 'opportunities': loadOpportunities(); break;
                case 'subscriptions': loadSubscriptions(); break;
                case 'partners': loadPartners(); break;
                case 'reports': loadReports(); break;
                case 'scraper': break;
            }
        }

        async function loadDashboard() {
            try {
                const response = await fetchWithAuth('/api/v1/admin/stats');
                const stats = await response.json();

                document.getElementById('stat-users').textContent = stats.total_users;
                document.getElementById('stat-verified').textContent = stats.verified_users;
                document.getElementById('stat-opportunities').textContent = stats.total_opportunities;
                document.getElementById('stat-banned').textContent = stats.banned_users;
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }

        async function loadTracking() {
            await Promise.all([loadTrackingSummary(), loadTrackingEvents()]);
        }

        async function loadOps() {
            await Promise.all([loadJobRuns(), loadAuditLogs()]);
        }

        function _formatDurationMs(start, end) {
            if (!start || !end) return '—';
            const ms = new Date(end).getTime() - new Date(start).getTime();
            if (!Number.isFinite(ms) || ms < 0) return '—';
            if (ms < 1000) return `${ms}ms`;
            const s = Math.round(ms / 1000);
            if (s < 60) return `${s}s`;
            const m = Math.floor(s / 60);
            const r = s % 60;
            return `${m}m ${r}s`;
        }

        async function loadJobRuns() {
            const tbody = document.getElementById('jobruns-body');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading job runs...</td></tr>';

            try {
                let url = '/api/v1/admin/job-runs?limit=50';
                const jobName = document.getElementById('jobruns-name')?.value?.trim();
                const statusFilter = document.getElementById('jobruns-status')?.value;
                if (jobName) url += `&job_name=${encodeURIComponent(jobName)}`;
                if (statusFilter) url += `&status_filter=${encodeURIComponent(statusFilter)}`;

                const response = await fetchWithAuth(url);
                const data = await response.json();
                const items = data.items || [];

                tbody.innerHTML = '';
                if (!items.length) {
                    tbody.innerHTML = '<tr><td colspan="5" class="loading">No job runs yet.</td></tr>';
                    return;
                }

                items.forEach(r => {
                    const status = (r.status || 'unknown').toLowerCase();
                    const badgeClass = ['running', 'succeeded', 'failed'].includes(status) ? status : 'pending';
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${formatDateTime(r.started_at)}</td>
                        <td><code>${escapeHtml(r.job_name || '')}</code></td>
                        <td><span class="badge badge-${escapeHtml(badgeClass)}">${escapeHtml(status)}</span></td>
                        <td>${escapeHtml(_formatDurationMs(r.started_at, r.finished_at))}</td>
                        <td style="max-width: 520px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(r.error || '—')}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (e) {
                tbody.innerHTML = '<tr><td colspan="5" class="loading">Failed to load job runs.</td></tr>';
            }
        }

        async function loadAuditLogs() {
            const tbody = document.getElementById('audit-body');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading audit logs...</td></tr>';

            try {
                let url = '/api/v1/admin/audit-logs?limit=50';
                const action = document.getElementById('audit-action')?.value?.trim();
                const rt = document.getElementById('audit-resource-type')?.value?.trim();
                const rid = document.getElementById('audit-resource-id')?.value?.trim();
                if (action) url += `&action=${encodeURIComponent(action)}`;
                if (rt) url += `&resource_type=${encodeURIComponent(rt)}`;
                if (rid) url += `&resource_id=${encodeURIComponent(rid)}`;

                const response = await fetchWithAuth(url);
                const data = await response.json();
                const items = data.items || [];

                tbody.innerHTML = '';
                if (!items.length) {
                    tbody.innerHTML = '<tr><td colspan="5" class="loading">No audit logs yet.</td></tr>';
                    return;
                }

                items.forEach(a => {
                    const actor = a.actor_user_id ? `#${a.actor_user_id} (${a.actor_type || 'user'})` : (a.actor_type || 'system');
                    const resource = a.resource_type ? `${a.resource_type}${a.resource_id ? `#${a.resource_id}` : ''}` : '—';
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${formatDateTime(a.created_at)}</td>
                        <td>${escapeHtml(actor)}</td>
                        <td><code>${escapeHtml(a.action || '')}</code></td>
                        <td>${escapeHtml(resource)}</td>
                        <td>${escapeHtml(a.ip_address || '—')}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (e) {
                tbody.innerHTML = '<tr><td colspan="5" class="loading">Failed to load audit logs.</td></tr>';
            }
        }

        async function loadTrackingSummary() {
            try {
                const days = document.getElementById('tracking-days')?.value || '7';
                const response = await fetchWithAuth(`/api/v1/admin/tracking/summary?days=${encodeURIComponent(days)}`);
                const data = await response.json();

                document.getElementById('tracking-total').textContent = data.total_events ?? '--';
                document.getElementById('tracking-pageviews').textContent = data.page_views ?? '--';
                document.getElementById('tracking-top-event').textContent = (data.top_events && data.top_events[0]) ? data.top_events[0].name : '--';
                document.getElementById('tracking-top-path').textContent = (data.top_paths && data.top_paths[0]) ? data.top_paths[0].path : '--';
            } catch (e) {
                console.error('Failed to load tracking summary', e);
            }
        }

        async function loadTrackingEvents() {
            const tbody = document.getElementById('tracking-events-body');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="4" class="loading">Loading events...</td></tr>';

            try {
                const name = document.getElementById('tracking-event-filter')?.value || '';
                const url = name
                    ? `/api/v1/admin/tracking/events?limit=50&name=${encodeURIComponent(name)}`
                    : '/api/v1/admin/tracking/events?limit=50';
                const response = await fetchWithAuth(url);
                const data = await response.json();
                const items = data.items || [];

                tbody.innerHTML = '';
                if (!items.length) {
                    tbody.innerHTML = '<tr><td colspan="4" class="loading">No events yet.</td></tr>';
                    return;
                }
                items.forEach(ev => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${formatDate(ev.created_at)}</td>
                        <td><code>${escapeHtml(ev.name || '')}</code></td>
                        <td>${escapeHtml(ev.path || '—')}</td>
                        <td>${ev.user_id ? `#${ev.user_id}` : '—'}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (e) {
                tbody.innerHTML = '<tr><td colspan="4" class="loading">Failed to load events.</td></tr>';
            }
        }

        async function loadUsers() {
            const search = document.getElementById('user-search').value;
            const filter = document.getElementById('user-filter').value;
            const tbody = document.getElementById('users-table-body');
            
            try {
                let url = '/api/v1/admin/users?limit=50';
                if (search) url += `&search=${encodeURIComponent(search)}`;
                if (filter === 'admin') url += '&is_admin=true';
                if (filter === 'banned') url += '&is_banned=true';
                if (filter === 'verified') url += '&is_verified=true';

                const response = await fetchWithAuth(url);
                const users = await response.json();

                if (users.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No users found</td></tr>';
                    return;
                }

                tbody.innerHTML = users.map(user => `
                    <tr>
                        <td>
                            <div class="user-cell">
                                <div class="user-avatar">${user.name.charAt(0).toUpperCase()}</div>
                                <div class="user-info">
                                    <span class="user-name">${escapeHtml(user.name)}</span>
                                    <span class="user-email">${escapeHtml(user.email)}</span>
                                </div>
                            </div>
                        </td>
                        <td>
                            ${user.is_verified ? '<span class="badge badge-verified">Verified</span>' : ''}
                            ${user.is_banned ? '<span class="badge badge-banned">Banned</span>' : ''}
                        </td>
                        <td>
                            ${user.is_admin ? '<span class="badge badge-admin">Admin</span>' : '<span class="badge badge-free">User</span>'}
                        </td>
                        <td>${formatDate(user.created_at)}</td>
                        <td>
                            <div class="action-btns">
                                ${!user.is_admin ? `
                                    <button class="btn-sm btn-primary" onclick="promoteUser(${user.id})">Make Admin</button>
                                ` : user.id !== currentUser.id ? `
                                    <button class="btn-sm btn-secondary" onclick="demoteUser(${user.id})">Remove Admin</button>
                                ` : ''}
                                ${!user.is_banned && user.id !== currentUser.id ? `
                                    <button class="btn-sm btn-danger" onclick="showBanModal(${user.id}, '${escapeHtml(user.name)}')">Ban</button>
                                ` : user.is_banned ? `
                                    <button class="btn-sm btn-success" onclick="unbanUser(${user.id})">Unban</button>
                                ` : ''}
                            </div>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Failed to load users:', error);
                tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to load users</td></tr>';
            }
        }

        async function loadOpportunities() {
            const search = document.getElementById('opp-search').value;
            const tbody = document.getElementById('opportunities-table-body');
            
            try {
                let url = '/api/v1/admin/opportunities?limit=50';
                if (search) url += `&search=${encodeURIComponent(search)}`;

                const response = await fetchWithAuth(url);
                const opportunities = await response.json();

                if (opportunities.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No opportunities found</td></tr>';
                    return;
                }

                tbody.innerHTML = opportunities.map(opp => `
                    <tr>
                        <td>
                            <a href="opportunity.html?id=${opp.id}" style="color: var(--violet-600); text-decoration: none;">
                                ${escapeHtml(opp.title.substring(0, 50))}${opp.title.length > 50 ? '...' : ''}
                            </a>
                        </td>
                        <td>${escapeHtml(opp.author_name)}</td>
                        <td><span class="badge badge-${opp.status === 'published' ? 'active' : 'pending'}">${opp.status}</span></td>
                        <td>${opp.validation_count}</td>
                        <td>${formatDate(opp.created_at)}</td>
                        <td>
                            <div class="action-btns">
                                <button class="btn-sm btn-danger" onclick="deleteOpportunity(${opp.id})">Delete</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Failed to load opportunities:', error);
                tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Failed to load opportunities</td></tr>';
            }
        }

        async function loadSubscriptions() {
            const tierFilter = document.getElementById('sub-tier-filter').value;
            const tbody = document.getElementById('subscriptions-table-body');
            
            try {
                let url = '/api/v1/admin/subscriptions?limit=50';
                if (tierFilter) url += `&tier_filter=${tierFilter}`;

                const response = await fetchWithAuth(url);
                const subscriptions = await response.json();

                if (subscriptions.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No subscriptions found</td></tr>';
                    return;
                }

                tbody.innerHTML = subscriptions.map(sub => `
                    <tr>
                        <td>
                            <div class="user-cell">
                                <div class="user-avatar">${sub.user_name.charAt(0).toUpperCase()}</div>
                                <div class="user-info">
                                    <span class="user-name">${escapeHtml(sub.user_name)}</span>
                                    <span class="user-email">${escapeHtml(sub.user_email)}</span>
                                </div>
                            </div>
                        </td>
                        <td><span class="badge badge-${sub.tier}">${sub.tier.toUpperCase()}</span></td>
                        <td><span class="badge badge-${sub.status}">${sub.status}</span></td>
                        <td>${sub.current_period_end ? formatDate(sub.current_period_end) : 'N/A'}</td>
                        <td>
                            <div class="action-btns">
                                <button class="btn-sm btn-secondary" onclick="showTierModal(${sub.id}, ${sub.user_id}, '${sub.tier}')">Change Tier</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Failed to load subscriptions:', error);
                tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to load subscriptions</td></tr>';
            }
        }

        async function loadReports() {
            const status = document.getElementById('report-status-filter').value;
            const tbody = document.getElementById('reports-table-body');
            
            try {
                const response = await fetchWithAuth(`/api/v1/moderation/reports?status_filter=${status}&limit=50`);
                const reports = await response.json();

                if (reports.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No reports found</td></tr>';
                    return;
                }

                tbody.innerHTML = reports.map(report => `
                    <tr>
                        <td>${report.content_type} #${report.content_id}</td>
                        <td>${report.reason}</td>
                        <td>User #${report.reporter_id}</td>
                        <td><span class="badge badge-${report.status}">${report.status}</span></td>
                        <td>${formatDate(report.created_at)}</td>
                        <td>
                            <div class="action-btns">
                                ${report.status === 'pending' || report.status === 'reviewing' ? `
                                    <button class="btn-sm btn-primary" onclick="resolveReport(${report.id})">Resolve</button>
                                    <button class="btn-sm btn-secondary" onclick="dismissReport(${report.id})">Dismiss</button>
                                ` : ''}
                            </div>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Failed to load reports:', error);
                tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Failed to load reports</td></tr>';
            }
        }

        async function promoteUser(userId) {
            if (!confirm('Are you sure you want to make this user an admin?')) return;
            
            try {
                await fetchWithAuth(`/api/v1/admin/users/${userId}/promote`, { method: 'POST' });
                showToast('User promoted to admin', 'success');
                loadUsers();
            } catch (error) {
                showToast('Failed to promote user', 'error');
            }
        }

        async function demoteUser(userId) {
            if (!confirm('Are you sure you want to remove admin privileges?')) return;
            
            try {
                await fetchWithAuth(`/api/v1/admin/users/${userId}/demote`, { method: 'POST' });
                showToast('Admin privileges removed', 'success');
                loadUsers();
            } catch (error) {
                showToast('Failed to demote user', 'error');
            }
        }

        function showBanModal(userId, userName) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <h3>Ban User: ${escapeHtml(userName)}</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="ban-reason">Reason for ban</label>
                            <textarea id="ban-reason" rows="3" placeholder="Enter the reason for banning this user..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-sm btn-secondary" onclick="closeModal()">Cancel</button>
                        <button class="btn-sm btn-danger" onclick="banUser(${userId})">Ban User</button>
                    </div>
                </div>
            `;
            document.getElementById('modal-container').appendChild(modal);
        }

        async function banUser(userId) {
            const reason = document.getElementById('ban-reason').value;
            
            try {
                await fetchWithAuth(`/api/v1/admin/users/${userId}/ban`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ban_reason: reason })
                });
                closeModal();
                showToast('User banned successfully', 'success');
                loadUsers();
            } catch (error) {
                showToast('Failed to ban user', 'error');
            }
        }

        async function unbanUser(userId) {
            if (!confirm('Are you sure you want to unban this user?')) return;
            
            try {
                await fetchWithAuth(`/api/v1/admin/users/${userId}/unban`, { method: 'POST' });
                showToast('User unbanned successfully', 'success');
                loadUsers();
            } catch (error) {
                showToast('Failed to unban user', 'error');
            }
        }

        async function deleteOpportunity(id) {
            if (!confirm('Are you sure you want to delete this opportunity? This cannot be undone.')) return;
            
            try {
                await fetchWithAuth(`/api/v1/admin/opportunities/${id}`, { method: 'DELETE' });
                showToast('Opportunity deleted', 'success');
                loadOpportunities();
            } catch (error) {
                showToast('Failed to delete opportunity', 'error');
            }
        }

        function showTierModal(subscriptionId, userId, currentTier) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <h3>Change Subscription Tier</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="new-tier">New Tier</label>
                            <select id="new-tier">
                                <option value="free" ${currentTier === 'free' ? 'selected' : ''}>Free</option>
                                <option value="pro" ${currentTier === 'pro' ? 'selected' : ''}>Pro</option>
                                <option value="business" ${currentTier === 'business' ? 'selected' : ''}>Business</option>
                                <option value="enterprise" ${currentTier === 'enterprise' ? 'selected' : ''}>Enterprise</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-sm btn-secondary" onclick="closeModal()">Cancel</button>
                        <button class="btn-sm btn-primary" onclick="updateTier(${subscriptionId}, ${userId})">Update Tier</button>
                    </div>
                </div>
            `;
            document.getElementById('modal-container').appendChild(modal);
        }

        async function updateTier(subscriptionId, userId) {
            const newTier = document.getElementById('new-tier').value;
            
            try {
                if (subscriptionId) {
                    await fetchWithAuth(`/api/v1/admin/subscriptions/${subscriptionId}/tier?tier=${newTier}`, { method: 'PATCH' });
                } else {
                    await fetchWithAuth(`/api/v1/admin/users/${userId}/grant-subscription?tier=${newTier}`, { method: 'POST' });
                }
                closeModal();
                showToast('Subscription updated', 'success');
                loadSubscriptions();
            } catch (error) {
                showToast('Failed to update subscription', 'error');
            }
        }

        async function loadPartners() {
            const tbody = document.getElementById('partners-table-body');
            if (!tbody) return;
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading partners...</td></tr>';

            try {
                window._partnersById = window._partnersById || {};
                let url = '/api/v1/admin/partners?limit=50';
                const search = document.getElementById('partner-search')?.value?.trim();
                const statusFilter = document.getElementById('partner-status-filter')?.value;
                if (search) url += `&search=${encodeURIComponent(search)}`;
                if (statusFilter) url += `&status_filter=${encodeURIComponent(statusFilter)}`;

                const response = await fetchWithAuth(url);
                const partners = await response.json();
                tbody.innerHTML = '';
                window._partnersById = {};
                (partners || []).forEach(p => { if (p && p.id != null) window._partnersById[p.id] = p; });

                if (!partners || partners.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="loading">No partners yet.</td></tr>';
                    return;
                }

                partners.forEach(p => {
                    const contact = [p.contact_name, p.contact_email].filter(Boolean).join(' • ') || '—';
                    const website = p.website_url ? `<a href="${escapeHtml(p.website_url)}" target="_blank" rel="noopener noreferrer" style="color:#2563eb;text-decoration:none;">Website</a>` : '';
                    const nameCell = `${escapeHtml(p.name)} ${website ? `<div style="font-size:12px;color:#78716c;margin-top:4px;">${website}</div>` : ''}`;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${nameCell}</td>
                        <td>${escapeHtml(p.category || '—')}</td>
                        <td><span class="badge badge-${escapeHtml(p.status || 'identified')}">${escapeHtml(p.status || 'identified')}</span></td>
                        <td>${escapeHtml(contact)}</td>
                        <td>${formatDate(p.created_at)}</td>
                        <td>
                            <button class="btn-sm btn-secondary" onclick="showPartnerEditModal(${p.id})">Edit</button>
                            <button class="btn-sm btn-danger" onclick="deletePartner(${p.id})">Delete</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (error) {
                tbody.innerHTML = '<tr><td colspan="6" class="loading">Failed to load partners.</td></tr>';
            }
        }

        function showPartnerEditModal(id) {
            const p = (window._partnersById || {})[id];
            if (!p) {
                showToast('Partner not found in list. Refreshing...', 'error');
                loadPartners();
                return;
            }
            showPartnerModal(
                p.id,
                p.name || '',
                p.category || '',
                p.website_url || '',
                p.contact_name || '',
                p.contact_email || '',
                p.status || 'identified',
                p.notes || ''
            );
        }

        function showPartnerModal(id = null, name = '', category = '', website_url = '', contact_name = '', contact_email = '', status = 'identified', notes = '') {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <h3>${id ? 'Edit Partner' : 'Add Partner'}</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="partner-name">Name</label>
                            <input id="partner-name" value="${escapeAttr(name)}" />
                        </div>
                        <div class="form-group">
                            <label for="partner-category">Category</label>
                            <input id="partner-category" value="${escapeAttr(category)}" placeholder="e.g. payments, analytics, CRM" />
                        </div>
                        <div class="form-group">
                            <label for="partner-website">Website URL</label>
                            <input id="partner-website" value="${escapeAttr(website_url)}" placeholder="https://..." />
                        </div>
                        <div class="form-group">
                            <label for="partner-contact-name">Contact name</label>
                            <input id="partner-contact-name" value="${escapeAttr(contact_name)}" />
                        </div>
                        <div class="form-group">
                            <label for="partner-contact-email">Contact email</label>
                            <input id="partner-contact-email" value="${escapeAttr(contact_email)}" />
                        </div>
                        <div class="form-group">
                            <label for="partner-status">Status</label>
                            <select id="partner-status">
                                <option value="identified" ${status === 'identified' ? 'selected' : ''}>Identified</option>
                                <option value="contacted" ${status === 'contacted' ? 'selected' : ''}>Contacted</option>
                                <option value="in_talks" ${status === 'in_talks' ? 'selected' : ''}>In talks</option>
                                <option value="active" ${status === 'active' ? 'selected' : ''}>Active</option>
                                <option value="paused" ${status === 'paused' ? 'selected' : ''}>Paused</option>
                                <option value="rejected" ${status === 'rejected' ? 'selected' : ''}>Rejected</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="partner-notes">Notes</label>
                            <textarea id="partner-notes" rows="4" placeholder="Outreach notes, dates, next step...">${escapeHtml(notes)}</textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-sm btn-secondary" onclick="closeModal()">Cancel</button>
                        <button class="btn-sm btn-primary" onclick="savePartner(${id || 'null'})">${id ? 'Save changes' : 'Add partner'}</button>
                    </div>
                </div>
            `;
            document.getElementById('modal-container').appendChild(modal);
        }

        async function savePartner(id) {
            const payload = {
                name: document.getElementById('partner-name').value.trim(),
                category: document.getElementById('partner-category').value.trim() || null,
                website_url: document.getElementById('partner-website').value.trim() || null,
                contact_name: document.getElementById('partner-contact-name').value.trim() || null,
                contact_email: document.getElementById('partner-contact-email').value.trim() || null,
                status: document.getElementById('partner-status').value,
                notes: document.getElementById('partner-notes').value.trim() || null,
            };

            if (!payload.name) {
                showToast('Partner name is required', 'error');
                return;
            }

            try {
                if (id) {
                    await fetchWithAuth(`/api/v1/admin/partners/${id}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    showToast('Partner updated', 'success');
                } else {
                    await fetchWithAuth('/api/v1/admin/partners', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    showToast('Partner added', 'success');
                }
                closeModal();
                loadPartners();
            } catch (error) {
                showToast('Failed to save partner', 'error');
            }
        }

        async function deletePartner(id) {
            if (!confirm('Delete this partner entry?')) return;
            try {
                await fetchWithAuth(`/api/v1/admin/partners/${id}`, { method: 'DELETE' });
                showToast('Partner deleted', 'success');
                loadPartners();
            } catch (error) {
                showToast('Failed to delete partner', 'error');
            }
        }

        async function resolveReport(reportId) {
            try {
                await fetchWithAuth(`/api/v1/moderation/reports/${reportId}/resolve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action_taken: 'Content reviewed and action taken', moderator_notes: '' })
                });
                showToast('Report resolved', 'success');
                loadReports();
            } catch (error) {
                showToast('Failed to resolve report', 'error');
            }
        }

        async function dismissReport(reportId) {
            try {
                await fetchWithAuth(`/api/v1/moderation/reports/${reportId}/dismiss`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ moderator_notes: 'Report dismissed' })
                });
                showToast('Report dismissed', 'success');
                loadReports();
            } catch (error) {
                showToast('Failed to dismiss report', 'error');
            }
        }

        function closeModal() {
            document.getElementById('modal-container').innerHTML = '';
        }

        async function fetchWithAuth(url, options = {}) {
            const token = OppGridAuth.getAccessToken();
            const response = await fetch(`${API_BASE_URL}${url}`, {
                ...options,
                headers: {
                    ...options.headers,
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            return response;
        }

        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            document.getElementById('toast-container').appendChild(toast);
            
            setTimeout(() => toast.remove(), 3000);
        }

        function formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }

        function formatDateTime(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function escapeAttr(text) {
            return escapeHtml(text).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        }

        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }


        async function analyzeScraperData() {
            const fileInput = document.getElementById('scraper-file');
            const autoImport = document.getElementById('auto-import-checkbox').checked;
            
            if (!fileInput.files || !fileInput.files[0]) {
                showToast('Please select a JSON file', 'error');
                return;
            }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                showToast('Analyzing scraper data...', 'info');
                
                const url = `/api/v1/scraper/analyze?auto_import=${autoImport}`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Analysis failed');
                }
                
                const result = await response.json();
                
                document.getElementById('scraper-stats').style.display = 'block';
                document.getElementById('scraper-total').textContent = result.total_posts;
                document.getElementById('scraper-valid').textContent = result.valid_opportunities;
                document.getElementById('scraper-imported').textContent = result.imported;
                document.getElementById('scraper-skipped').textContent = result.skipped;
                
                if (result.opportunities && result.opportunities.length > 0) {
                    document.getElementById('scraper-results').style.display = 'block';
                    const tbody = document.getElementById('scraper-table-body');
                    tbody.innerHTML = result.opportunities.map(opp => `
                        <tr>
                            <td><span class="badge ${opp.confidence_score >= 0.9 ? 'badge-pro' : opp.confidence_score >= 0.8 ? 'badge-plus' : 'badge-free'}">${opp.confidence_score.toFixed(2)}</span></td>
                            <td>${escapeHtml(opp.title.substring(0, 80))}${opp.title.length > 80 ? '...' : ''}</td>
                            <td>${escapeHtml(opp.category)}</td>
                            <td>r/${escapeHtml(opp.subreddit || 'unknown')}</td>
                            <td>${opp.upvotes}</td>
                        </tr>
                    `).join('');
                }
                
                if (autoImport && result.imported > 0) {
                    showToast(`Imported ${result.imported} opportunities!`, 'success');
                } else {
                    showToast(`Found ${result.valid_opportunities} valid opportunities`, 'success');
                }
                
            } catch (error) {
                console.error('Scraper analysis error:', error);
                showToast(error.message || 'Failed to analyze data', 'error');
            }
        }

        function logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('token');
            window.location.href = 'signin.html';
        }

        init();