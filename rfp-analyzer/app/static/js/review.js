// Review Page Logic

let allRequirements = [];
let filteredRequirements = [];
let selectedReqIds = new Set();

const CATEGORY_OPTIONS = ['functional', 'non_functional', 'compliance', 'ambiguity', 'risk'];
const PRIORITY_OPTIONS = ['must', 'should', 'could', 'wont'];
const REVIEW_STATUS_OPTIONS = ['pending', 'accepted', 'modified', 'rejected'];

document.addEventListener('DOMContentLoaded', () => {
    // Only auto-load requirements if we're on the review page
    // Check if we have the requirements container (only exists on review page)
    const reqContainer = document.getElementById('requirementsContainer');
    if (reqContainer && window.location.pathname === '/review') {
        loadRequirements();
    }
});

async function loadRequirements() {
    try {
        console.log('🔄 Loading requirements');
        const data = await api.getRequirements();
        
        if (!data || !data.requirements) {
            throw new Error('Invalid response structure');
        }
        
        allRequirements = data.requirements;
        applyFiltersAndRender();
        
        const reqSection = document.getElementById('requirementsSection');
        if (reqSection) {
            reqSection.style.display = 'block';
            reqSection.classList.add('section-appear');
        }
        
        loadHtmlPreview();
    } catch (error) {
        console.error('Error loading requirements:', error);
        const container = document.getElementById('requirementsContainer');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <p style="color: var(--color-danger); font-size: 1.1rem; margin-bottom: 1rem;">⚠️ Error: ${error.message}</p>
                    <p style="color: #6B7280;">Please try uploading and analyzing an RFP document again.</p>
                    <button onclick="loadRequirements()" class="btn btn-primary" style="margin-top: 1rem;">
                        <span>↻</span>
                        <span>Reload Requirements</span>
                    </button>
                </div>`;
            const reqSection = document.getElementById('requirementsSection');
            if (reqSection) {
                reqSection.style.display = 'block';
            }
        }
    }
}

function getMultiSelectValues(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return [];
    return Array.from(element.selectedOptions || []).map(option => option.value).filter(Boolean);
}

function getCurrentFilters() {
    const minConfidenceEl = document.getElementById('filterMinConfidence');
    const searchEl = document.getElementById('filterSearch');

    return {
        categories: getMultiSelectValues('filterCategory'),
        priorities: getMultiSelectValues('filterPriority'),
        statuses: getMultiSelectValues('filterStatus'),
        minConfidence: minConfidenceEl ? parseFloat(minConfidenceEl.value || '0') : 0,
        search: searchEl ? searchEl.value.trim().toLowerCase() : ''
    };
}

function applyFiltersAndRender() {
    const filters = getCurrentFilters();

    filteredRequirements = allRequirements.filter(req => {
        const matchesCategory = filters.categories.length === 0 || filters.categories.includes(req.category);
        const matchesPriority = filters.priorities.length === 0 || filters.priorities.includes(req.priority);
        const matchesStatus = filters.statuses.length === 0 || filters.statuses.includes(req.review_status);
        const matchesConfidence = Number(req.confidence || 0) >= filters.minConfidence;
        const haystack = `${req.title || ''} ${req.description || ''}`.toLowerCase();
        const matchesSearch = !filters.search || haystack.includes(filters.search);

        return matchesCategory && matchesPriority && matchesStatus && matchesConfidence && matchesSearch;
    });

    renderRequirements(filteredRequirements);
    updateFilterSummary(filteredRequirements.length, allRequirements.length, filters.minConfidence);
}

function updateFilterSummary(filteredCount, totalCount, minConfidence) {
    const summary = document.getElementById('filterSummary');
    const confidenceValue = document.getElementById('filterMinConfidenceValue');

    if (confidenceValue) {
        confidenceValue.textContent = Number(minConfidence).toFixed(2);
    }

    if (summary) {
        summary.textContent = `${filteredCount} of ${totalCount} requirements visible`;
    }
}

function renderRequirements(requirements) {
    const container = document.getElementById('requirementsContainer');
    
    if (requirements.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <p style="font-size: 1.1rem; color: #6B7280; margin-bottom: 1rem;">📭 No requirements found</p>
                <p style="color: #9CA3AF; font-size: 0.9rem;">Try adjusting your filters or upload a new RFP document.</p>
            </div>
        `;
        updateSelectedCount();
        return;
    }

    const html = `
        <div style="overflow-x: auto;">
            <table class="table requirements-editor-table">
                <thead>
                    <tr>
                        <th><input type="checkbox" onchange="toggleSelectAll(this)"></th>
                        <th>req_id</th>
                        <th>category</th>
                        <th>title</th>
                        <th>description</th>
                        <th>source_section</th>
                        <th>page_ref</th>
                        <th>priority</th>
                        <th>confidence</th>
                        <th>ambiguity_flag</th>
                        <th>review_status</th>
                    </tr>
                </thead>
                <tbody>
                    ${requirements.map(req => renderRequirementRow(req)).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    updateSelectedCount();
}

function renderRequirementRow(req) {
    const reqId = req.id;
    const sourceSection = req.source_section || req.sourceSection || '';
    const pageRef = req.page_ref || req.pageRef || '';
    const ambiguityFlag = req.ambiguity_flag ?? req.ambiguityFlag ?? false;

    return `
        <tr>
            <td><input type="checkbox" value="${reqId}" onchange="toggleSelect(this)" ${selectedReqIds.has(reqId) ? 'checked' : ''}></td>
            <td><strong>${reqId}</strong></td>
            <td>${renderSelectEditor(reqId, 'category', CATEGORY_OPTIONS, req.category)}</td>
            <td>${renderTextCell(req.title)}</td>
            <td>${renderTextCell(req.description)}</td>
            <td>${renderTextCell(sourceSection)}</td>
            <td>${renderTextCell(pageRef)}</td>
            <td>${renderSelectEditor(reqId, 'priority', PRIORITY_OPTIONS, req.priority)}</td>
            <td>
                <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.05"
                    value="${Number(req.confidence || 0).toFixed(2)}"
                    class="table-input"
                    onchange="updateRequirementField('${reqId}', 'confidence', this.value)"
                >
            </td>
            <td>${ambiguityFlag ? 'Yes' : 'No'}</td>
            <td>${renderSelectEditor(reqId, 'review_status', REVIEW_STATUS_OPTIONS, req.review_status)}</td>
        </tr>
    `;
}

function renderSelectEditor(reqId, field, options, selectedValue) {
    return `
        <select class="table-select" onchange="updateRequirementField('${reqId}', '${field}', this.value)">
            ${options.map(option => `<option value="${option}" ${option === selectedValue ? 'selected' : ''}>${option}</option>`).join('')}
        </select>
    `;
}

function renderTextCell(value) {
    const safeValue = value ?? '';
    return `<div class="table-text-cell" title="${String(safeValue).replace(/"/g, '"')}">${safeValue}</div>`;
}

async function updateRequirementField(reqId, field, value) {
    const payload = {};
    payload[field] = field === 'confidence' ? parseFloat(value) : value;

    try {
        await api.updateRequirement(reqId, payload);
        const req = allRequirements.find(item => item.id === reqId);
        if (req) {
            req[field] = payload[field];
            if (field !== 'review_status') {
                req.review_status = 'modified';
            }
        }
        // Just re-render with updated data, don't reload from server
        applyFiltersAndRender();
    } catch (error) {
        console.error('Failed to update requirement:', error);
        // On error, reload from server to get correct state
        await loadRequirements();
    }
}

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedReqIds.add(cb.value);
        } else {
            selectedReqIds.delete(cb.value);
        }
    });
    updateSelectedCount();
}

function toggleSelect(checkbox) {
    if (checkbox.checked) {
        selectedReqIds.add(checkbox.value);
    } else {
        selectedReqIds.delete(checkbox.value);
    }
    updateSelectedCount();
}

function updateSelectedCount() {
    document.getElementById('selectedCount').textContent = 
        selectedReqIds.size > 0 ? `${selectedReqIds.size} selected` : '';
}

async function acceptRequirement(reqId) {
    try {
        await api.updateRequirement(reqId, { review_status: 'accepted' });
        showToast('Requirement accepted', 'success');
        loadRequirements();
    } catch (error) {
        // Error already shown by api.call
    }
}

async function rejectRequirement(reqId) {
    try {
        await api.deleteRequirement(reqId);
        showToast('Requirement rejected', 'success');
        loadRequirements();
    } catch (error) {
        // Error already shown by api.call
    }
}

async function bulkAccept() {
    await bulkUpdateVisible('accepted');
}

async function bulkReject() {
    await bulkUpdateVisible('rejected');
}

async function bulkUpdateVisible(reviewStatus) {
    if (filteredRequirements.length === 0) {
        showToast('No visible requirements to update', 'error');
        return;
    }

    try {
        await api.bulkUpdate(filteredRequirements.map(req => req.id), reviewStatus);
        showToast(`${filteredRequirements.length} visible requirements updated`, 'success');
        selectedReqIds.clear();
        loadRequirements();
    } catch (error) {
        // Error already shown by api.call
    }
}

function resetFilters() {
    ['filterCategory', 'filterPriority', 'filterStatus'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            Array.from(element.options).forEach(option => {
                option.selected = false;
            });
        }
    });

    const minConfidenceEl = document.getElementById('filterMinConfidence');
    if (minConfidenceEl) {
        minConfidenceEl.value = '0';
    }

    const searchEl = document.getElementById('filterSearch');
    if (searchEl) {
        searchEl.value = '';
    }

    applyFiltersAndRender();
}

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    const tabMap = {
        'requirements': 'tabRequirements',
        'architecture': 'tabArchitecture',
        'solutions': 'tabSolutions',
        'export': 'tabExport'
    };
    
    const tabId = tabMap[tabName];
    if (tabId) {
        document.getElementById(tabId).style.display = 'block';
    }
    
    // Activate clicked tab button
    event.target.classList.add('active');
}

// Architecture
async function generateArchitecture() {
    const container = document.getElementById('architectureResult');
    container.innerHTML = '<div class="spinner"></div>';
    
    try {
        const result = await api.generateDiagram();
        container.innerHTML = `
            <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 8px;">
                <h4>Mermaid Diagram Code:</h4>
                <pre style="background: white; padding: 1rem; border-radius: 4px; overflow-x: auto;">${result.mermaid_code}</pre>
                <p style="margin-top: 1rem; color: #6B7280; font-size: 0.9rem;">
                    Copy this code to <a href="https://mermaid.live" target="_blank">mermaid.live</a> to visualize the diagram.
                </p>
            </div>
        `;
        showToast('Architecture diagram generated!', 'success');
    } catch (error) {
        container.innerHTML = '<p style="color: var(--color-danger);">Failed to generate architecture diagram.</p>';
    }
}

// Solution Mapping
async function mapSolutions() {
    const checkboxes = document.querySelectorAll('#solutions input[type="checkbox"]:checked');
    const solutions = Array.from(checkboxes).map(cb => cb.value);
    
    if (solutions.length === 0) {
        showToast('Please select at least one solution', 'error');
        return;
    }
    
    const container = document.getElementById('solutionResult');
    container.innerHTML = '<div class="spinner"></div>';
    
    try {
        const result = await api.mapSolutions(solutions);
        
        // Render summary
        let html = '<h4>Solution Mapping Summary</h4>';
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">';
        
        for (const [solution, counts] of Object.entries(result.summary)) {
            html += `
                <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid var(--color-border);">
                    <h5 style="margin-bottom: 0.5rem;">${solution}</h5>
                    <div style="font-size: 0.9rem; color: #6B7280;">
                        <div>✅ Native: ${counts.native}</div>
                        <div>⚙️ Config: ${counts.configuration}</div>
                        <div>🔧 Custom: ${counts.customisation}</div>
                        <div>❌ Gap: ${counts.gap}</div>
                    </div>
                </div>
            `;
        }
        html += '</div>';
        
        container.innerHTML = html;
        showToast('Solution mapping complete!', 'success');
    } catch (error) {
        container.innerHTML = '<p style="color: var(--color-danger);">Failed to map solutions.</p>';
    }
}

// HTML Preview Functions
async function loadHtmlPreview() {
    const previewSection = document.getElementById('htmlPreviewSection');
    const previewContainer = document.getElementById('htmlPreviewContainer');
    
    if (!previewSection || !previewContainer) {
        console.log('HTML preview elements not found');
        return;
    }
    
    try {
        console.log('Loading HTML preview...');
        
        // Fetch the HTML preview from the API
        const response = await fetch('/api/requirements/html-preview', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'text/html'
            }
        });
        
        if (!response.ok) {
            // Handle specific error cases
            if (response.status === 404) {
                // No requirements found - show friendly message
                previewContainer.innerHTML = `
                    <div style="padding: 3rem; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
                        <h3 style="font-size: 1.5rem; margin-bottom: 1rem; font-weight: 600;">No Requirements Yet</h3>
                        <p style="font-size: 1rem; margin-bottom: 2rem; opacity: 0.9;">
                            Upload an RFP document to see a beautiful categorized view of extracted requirements here.
                        </p>
                        <a href="/" class="btn" style="background: white; color: #667eea; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; transition: transform 0.2s;">
                            📄 Upload RFP Document
                        </a>
                    </div>
                `;
                previewSection.style.display = 'block';
                return;
            } else if (response.status === 401) {
                // No session
                previewContainer.innerHTML = `
                    <div style="padding: 2rem; text-align: center; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                        <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem; color: #495057;">Session Expired</h3>
                        <p style="color: #6c757d; margin-bottom: 1.5rem;">Please start a new analysis session.</p>
                        <a href="/" class="btn btn-primary" style="text-decoration: none;">
                            Go to Home
                        </a>
                    </div>
                `;
                previewSection.style.display = 'block';
                return;
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const htmlContent = await response.text();
        
        // Parse the HTML to extract just the body content
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        
        // Extract the styles and content from the HTML
        const styles = doc.querySelectorAll('style');
        const bodyContent = doc.querySelector('body').innerHTML;
        
        // Inject styles and content directly into the container
        let finalHTML = '';
        styles.forEach(style => {
            finalHTML += style.outerHTML;
        });
        finalHTML += bodyContent;
        
        previewContainer.innerHTML = finalHTML;
        
        // Show the preview section
        previewSection.style.display = 'block';
        
        console.log('HTML preview loaded successfully');
        showToast('📊 Categorized view loaded', 'success');
        
    } catch (error) {
        console.error('Error loading HTML preview:', error);
        previewContainer.innerHTML = `
            <div style="padding: 2rem; text-align: center; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem; color: #856404;">Could Not Load Preview</h3>
                <p style="color: #856404; margin: 0;">
                    ${error.message}
                </p>
                <p style="color: #856404; margin-top: 1rem; font-size: 0.9rem;">
                    Please try refreshing the page or uploading a new RFP document.
                </p>
            </div>
        `;
        previewSection.style.display = 'block';
    }
}

function toggleHtmlPreview() {
    const container = document.getElementById('htmlPreviewContainer');
    const icon = document.getElementById('previewToggleIcon');
    const text = document.getElementById('previewToggleText');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        icon.textContent = '▼';
        text.textContent = 'Hide Preview';
    } else {
        container.style.display = 'none';
        icon.textContent = '▶';
        text.textContent = 'Show Preview';
    }
}
