// API Client for RFP Analyzer

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.unsavedChanges = false;
        this.sessionId = null;
    }

    async call(method, path, body = null, isFormData = false) {
        const opts = {
            method,
            credentials: 'include', // Send cookies
        };

        if (body) {
            if (isFormData) {
                opts.body = body;
            } else {
                opts.headers = { 'Content-Type': 'application/json' };
                opts.body = JSON.stringify(body);
            }
        }

        try {
            const requestPath = this.withSession(path);
            const res = await fetch(this.baseURL + requestPath, opts);
            
            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || `Request failed: ${res.status}`);
            }

            // Check if response is JSON
            const contentType = res.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await res.json();
            }
            
            return res;
        } catch (error) {
            console.error('API Error:', error);
            showToast(error.message, 'error');
            throw error;
        }
    }

    withSession(path) {
        if (!this.sessionId) return path;
        const separator = path.includes('?') ? '&' : '?';
        return `${path}${separator}session_id=${encodeURIComponent(this.sessionId)}`;
    }

    setSession(sessionId) {
        this.sessionId = sessionId;
    }

    clearSession() {
        this.sessionId = null;
    }

    // Analysis endpoints
    async uploadRFP(file, title, domain = null, minConfidence = 0.0) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        if (domain) formData.append('domain', domain);
        formData.append('min_confidence', minConfidence);

        const result = await this.call('POST', '/api/analyze', formData, true);
        if (result?.session_id) {
            this.setSession(result.session_id);
        }
        return result;
    }

    async getStatus(sessionId) {
        return this.call('GET', `/api/status/${sessionId}`);
    }

    // Requirements endpoints
    async getRequirements(filters = {}) {
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(filters)) {
            if (value !== null && value !== undefined && value !== '') {
                params.append(key, value);
            }
        }
        const query = params.toString();
        return this.call('GET', `/api/requirements${query ? '?' + query : ''}`);
    }

    async updateRequirement(reqId, updates) {
        const result = await this.call('PATCH', `/api/requirements/${reqId}`, updates);
        showToast('Requirement updated', 'success');
        return result;
    }

    async bulkUpdate(reqIds, reviewStatus) {
        const result = await this.call('POST', '/api/requirements/bulk', { req_ids: reqIds, review_status: reviewStatus });
        showToast(`${reqIds.length} requirements updated`, 'success');
        return result;
    }

    async deleteRequirement(reqId) {
        const result = await this.call('DELETE', `/api/requirements/${reqId}`);
        showToast('Requirement deleted', 'success');
        return result;
    }

    // Clarifications
    async submitClarification(reqId, answer, answerSource) {
        const result = await this.call('POST', `/api/clarifications/${reqId}/answer`, { answer, answer_source: answerSource });
        showToast('Clarification submitted', 'success');
        return result;
    }

    // Architecture
    async generateDiagram() {
        return this.call('POST', '/api/architecture/diagram');
    }

    async identifyComponents() {
        return this.call('POST', '/api/architecture/components');
    }

    // Solution Mapping
    async mapSolutions(solutions) {
        return this.call('POST', '/api/solution-mapping', { solutions });
    }

    // Exports
    async exportExcel() {
        window.location.href = this.withSession('/api/export/excel');
        this.clearUnsaved();
    }

    async exportMarkdown() {
        window.location.href = this.withSession('/api/export/markdown');
        this.clearUnsaved();
    }

    async exportJSON() {
        window.location.href = this.withSession('/api/export/json');
        this.clearUnsaved();
    }

    async exportSolutionMap() {
        window.location.href = this.withSession('/api/export/solution-map');
    }

    // Unsaved changes tracking
    markUnsaved() {
        this.unsavedChanges = true;
        const banner = document.getElementById('unsavedBanner');
        if (banner) banner.classList.add('show');
    }

    clearUnsaved() {
        this.unsavedChanges = false;
        const banner = document.getElementById('unsavedBanner');
        if (banner) banner.classList.remove('show');
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : '✗'}</span>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Global API client instance
const api = new APIClient();