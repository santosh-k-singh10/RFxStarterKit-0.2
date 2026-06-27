# HTML Viewer Implementation Guide

## Overview
This guide explains how to add a collapsible/expandable HTML output viewer at the bottom of the RFP Analyzer web interface.

## Implementation Steps

### 1. Add CSS Styles for the Bottom Panel

Add these styles to your HTML `<style>` section:

```css
/* HTML Output Viewer - Fixed at Bottom */
.html-output-viewer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 3px solid #667eea;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
    z-index: 1000;
    transition: max-height 0.3s ease;
    max-height: 60vh;
}

.html-output-viewer.collapsed {
    max-height: 50px;
}

.html-output-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 20px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
}

.html-output-header:hover {
    opacity: 0.9;
}

.html-output-title {
    font-weight: 600;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.toggle-icon {
    font-size: 24px;
    transition: transform 0.3s ease;
}

.html-output-viewer.collapsed .toggle-icon {
    transform: rotate(180deg);
}

.html-output-content {
    padding: 20px;
    overflow-y: auto;
    max-height: calc(60vh - 50px);
    background: #f8f9fa;
}

.html-output-viewer.collapsed .html-output-content {
    display: none;
}

.html-output-iframe {
    width: 100%;
    min-height: 500px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
}

.no-output-message {
    text-align: center;
    color: #999;
    padding: 60px 20px;
    font-size: 1.1em;
}

.view-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.view-btn {
    padding: 8px 16px;
    border: 2px solid #667eea;
    background: white;
    color: #667eea;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
}

.view-btn.active {
    background: #667eea;
    color: white;
}

.view-btn:hover {
    background: #667eea;
    color: white;
}
```

### 2. Add HTML Structure

Add this HTML before the closing `</body>` tag:

```html
<!-- HTML Output Viewer (Fixed at Bottom) -->
<div class="html-output-viewer collapsed" id="htmlViewer">
    <div class="html-output-header" onclick="toggleHtmlViewer()">
        <div class="html-output-title">
            <span>📄</span>
            <span>HTML Output Preview</span>
        </div>
        <div class="toggle-icon">▼</div>
    </div>
    <div class="html-output-content" id="htmlViewerContent">
        <div class="view-selector">
            <button class="view-btn active" onclick="switchView('category')" id="categoryBtn">
                By Category
            </button>
            <button class="view-btn" onclick="switchView('module')" id="moduleBtn">
                By Module
            </button>
        </div>
        <div id="htmlOutputContainer">
            <div class="no-output-message">
                No HTML output available yet. Complete an analysis to see results here.
            </div>
        </div>
    </div>
</div>
```

### 3. Add JavaScript Functions

Add these JavaScript functions:

```javascript
let currentJobId = null;
let currentView = 'category';

function toggleHtmlViewer() {
    const viewer = document.getElementById('htmlViewer');
    viewer.classList.toggle('collapsed');
}

function switchView(viewType) {
    currentView = viewType;
    
    // Update button states
    document.getElementById('categoryBtn').classList.toggle('active', viewType === 'category');
    document.getElementById('moduleBtn').classList.toggle('active', viewType === 'module');
    
    // Load the appropriate view
    if (currentJobId) {
        loadHtmlOutput(currentJobId, viewType);
    }
}

function loadHtmlOutput(jobId, viewType) {
    const container = document.getElementById('htmlOutputContainer');
    const format = viewType === 'category' ? 'html_category' : 'html_module';
    const url = `/api/download/${jobId}/${format}`;
    
    // Create iframe to display HTML
    container.innerHTML = `
        <iframe 
            src="${url}" 
            class="html-output-iframe"
            frameborder="0"
        ></iframe>
    `;
}

function showHtmlOutput(jobId) {
    currentJobId = jobId;
    const viewer = document.getElementById('htmlViewer');
    
    // Expand the viewer
    viewer.classList.remove('collapsed');
    
    // Load the default view
    loadHtmlOutput(jobId, currentView);
}
```

### 4. Update the pollStatus Function

Modify the existing `pollStatus` function to show HTML output when analysis completes:

```javascript
if (status.status === 'completed') {
    clearInterval(interval);
    results.style.display = 'block';
    document.getElementById('downloadHtmlCategory').href = `/api/download/${jobId}/html_category`;
    document.getElementById('downloadHtmlCategory').target = '_blank';
    document.getElementById('downloadHtmlModule').href = `/api/download/${jobId}/html_module`;
    document.getElementById('downloadHtmlModule').target = '_blank';
    document.getElementById('downloadMarkdown').href = `/api/download/${jobId}/markdown`;
    document.getElementById('downloadExcel').href = `/api/download/${jobId}/excel`;
    document.getElementById('downloadJson').href = `/api/download/${jobId}/json`;
    analyzeBtn.disabled = false;
    
    // NEW: Show HTML output in bottom panel
    showHtmlOutput(jobId);
}
```

## Features

✅ **Fixed Bottom Position** - The HTML viewer stays at the bottom of the screen
✅ **Collapsible/Expandable** - Click the header to toggle visibility
✅ **Two View Modes** - Switch between "By Category" and "By Module" views
✅ **Smooth Animations** - CSS transitions for a polished UX
✅ **Auto-Display** - Automatically shows when analysis completes
✅ **Iframe Display** - Safely displays HTML content in an iframe
✅ **Responsive** - Adapts to different screen sizes

## Usage

1. Run the enhanced web app:
   ```bash
   cd rfp-analyzer
   python web_app.py
   ```

2. Open browser to `http://localhost:8080`

3. Upload and analyze an RFP document

4. When analysis completes:
   - The HTML viewer will automatically expand at the bottom
   - You'll see the HTML output displayed in an iframe
   - Switch between "By Category" and "By Module" views
   - Click the header to collapse/expand the viewer

## Customization Options

### Change Panel Height
Modify the `max-height` in CSS:
```css
.html-output-viewer {
    max-height: 70vh; /* Change from 60vh to 70vh for taller panel */
}
```

### Change Colors
Update the gradient colors:
```css
.html-output-header {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

### Auto-Collapse After Time
Add this JavaScript:
```javascript
// Auto-collapse after 30 seconds
setTimeout(() => {
    document.getElementById('htmlViewer').classList.add('collapsed');
}, 30000);
```

## Troubleshooting

**Issue**: HTML not displaying
- Check that the analysis completed successfully
- Verify the HTML files were generated in the outputs directory
- Check browser console for errors

**Issue**: Iframe not loading
- Ensure CORS is properly configured in FastAPI
- Check that the download endpoint is accessible
- Verify the file paths are correct

**Issue**: Panel overlaps content
- Increase `padding-bottom` on the body element
- Adjust the `max-height` of the viewer

## Complete Example

See `web_app.py` for the original implementation, or create a new file `web_app_enhanced.py` with all these changes integrated.

---

**Made with ❤️ for the RFP Analyzer project**