# How to Make HTML Output Collapsible

I've updated the `html_exporter_by_module.py` file to include collapsible functionality. Here's what was added:

## Features Added:

1. **Collapsible Module Sections** - Click on any module header to expand/collapse
2. **Expand All / Collapse All Buttons** - Control all modules at once
3. **Visual Indicators** - Arrow icons that rotate when collapsed
4. **Smooth Animations** - CSS transitions for better UX
5. **Hover Effects** - Interactive feedback on clickable elements

## JavaScript Functions Needed:

Add this JavaScript code before the closing `</body>` tag in the HTML output:

```javascript
<script>
function toggleModule(moduleId) {
    const content = document.getElementById(moduleId);
    const header = content.previousElementSibling;
    
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        header.classList.remove('collapsed');
    } else {
        content.classList.add('collapsed');
        header.classList.add('collapsed');
    }
}

function expandAll() {
    document.querySelectorAll('.module-content').forEach(content => {
        content.classList.remove('collapsed');
    });
    document.querySelectorAll('.module-header').forEach(header => {
        header.classList.remove('collapsed');
    });
}

function collapseAll() {
    document.querySelectorAll('.module-content').forEach(content => {
        content.classList.add('collapsed');
    });
    document.querySelectorAll('.module-header').forEach(header => {
        header.classList.add('collapsed');
    });
}
</script>
```

## CSS Classes Already Added:

- `.module-header` - Now has `cursor: pointer` and hover effects
- `.toggle-icon` - Rotates 90 degrees when collapsed
- `.module-content` - Animates height when toggled
- `.collapsed` - Applied to hide content

## To Use:

1. The current `html_exporter_by_module.py` generates static HTML
2. You need to add the JavaScript functions above to make it interactive
3. Or use the template below to modify the export function

## Complete Template:

The HTML structure should be:

```html
<div class="module-section">
    <div class="module-header" onclick="toggleModule('module-0')">
        <h3>
            <span class="toggle-icon">▼</span>
            Module Name
        </h3>
        <span class="module-count">5 Requirements</span>
    </div>
    <div class="module-content" id="module-0">
        <!-- Requirements go here -->
    </div>
</div>
```

## Next Steps:

Run the test script to see it in action:
```bash
cd rfp-analyzer
python test_collapsible_html.py
```

Then open `outputs/test_collapsible_output.html` in your browser to see the collapsible modules!