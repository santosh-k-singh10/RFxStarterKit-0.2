# Output Templates

This directory contains custom templates for generating RFP analysis outputs.

## Template Types

### Requirement Templates
Define how individual requirements should be formatted and presented.

### Excel Templates
Custom Excel workbook templates with your organization's branding and structure.

### Markdown Templates
Markdown report templates for generating analysis documents.

## Usage

Templates use Jinja2 syntax and can reference organizational context variables:
- `{{ org_name }}` - Organization name
- `{{ tech_stack }}` - Technology preferences
- `{{ compliance_frameworks }}` - Compliance requirements
- etc.

## Example Files

```
templates/
├── requirement_templates.yaml
├── excel_templates/
│   └── default_template.xlsx
└── markdown_templates/
    └── default_report.md