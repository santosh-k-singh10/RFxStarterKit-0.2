# Remote Organizational Context Guide

This guide explains how to load organizational context from remote cloud storage providers (SharePoint, OneDrive, Box, etc.) instead of local files.

## Overview

The RFP Analyzer supports loading organizational context from:
- **SharePoint Online** - Microsoft 365 SharePoint sites
- **OneDrive for Business** - Microsoft 365 OneDrive
- **Box** - Box.com cloud storage
- **HTTP/HTTPS** - Any web server with authentication
- **S3** - Amazon S3 or S3-compatible storage (MinIO, DigitalOcean Spaces, etc.)

## Benefits

1. **Centralized Management**: Single source of truth for organizational standards
2. **Version Control**: Track changes to organizational context over time
3. **Access Control**: Leverage existing cloud storage permissions
4. **Team Collaboration**: Multiple team members can update context
5. **Automatic Updates**: Always use the latest organizational standards

## Quick Start

### Basic Usage

Instead of a local file path, provide a remote URL:

```bash
# Local file (original method)
python main.py rfp.pdf --org-context org_context/config/org_config.yaml

# Remote URL (new method)
python main.py rfp.pdf --org-context "https://company.sharepoint.com/.../org_config.yaml"
```

### Environment Variables

Set credentials via environment variables to avoid passing them in code:

```bash
# SharePoint
export SHAREPOINT_CLIENT_ID="your-client-id"
export SHAREPOINT_CLIENT_SECRET="your-client-secret"
export SHAREPOINT_TENANT_ID="your-tenant-id"

# OneDrive
export ONEDRIVE_ACCESS_TOKEN="your-access-token"

# Box
export BOX_ACCESS_TOKEN="your-access-token"

# S3
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

## Provider-Specific Setup

### SharePoint Online

#### Prerequisites
```bash
pip install Office365-REST-Python-Client
```

#### Azure AD App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: "RFP Analyzer Context Loader"
4. Supported account types: "Accounts in this organizational directory only"
5. Click "Register"
6. Note the **Application (client) ID** and **Directory (tenant) ID**
7. Go to "Certificates & secrets" → "New client secret"
8. Note the **Client secret value**
9. Go to "API permissions" → "Add a permission"
10. Select "SharePoint" → "Application permissions"
11. Add: `Sites.Read.All` or `Sites.ReadWrite.All`
12. Click "Grant admin consent"

#### Usage

```python
from org_context import initialize_context_manager

# Method 1: Using environment variables
initialize_context_manager(
    "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml"
)

# Method 2: Passing credentials directly
initialize_context_manager(
    "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml",
    remote_kwargs={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "tenant_id": "your-tenant-id"
    }
)
```

#### CLI Usage

```bash
# Set environment variables
export SHAREPOINT_CLIENT_ID="abc123..."
export SHAREPOINT_CLIENT_SECRET="xyz789..."
export SHAREPOINT_TENANT_ID="def456..."

# Run analyzer
python main.py rfp.pdf \
  --org-context "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml"
```

### OneDrive for Business

#### Prerequisites
```bash
pip install requests
```

#### Getting Access Token

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Follow same steps as SharePoint
3. API permissions: Add "Microsoft Graph" → "Files.Read.All"
4. Use OAuth 2.0 flow to get access token

#### Usage

```python
from org_context import initialize_context_manager

initialize_context_manager(
    "https://company-my.sharepoint.com/personal/user_company_com/Documents/org_config.yaml",
    remote_kwargs={"access_token": "your-access-token"}
)
```

#### CLI Usage

```bash
export ONEDRIVE_ACCESS_TOKEN="your-access-token"

python main.py rfp.pdf \
  --org-context "https://company-my.sharepoint.com/personal/user_company_com/Documents/org_config.yaml"
```

### Box

#### Prerequisites
```bash
pip install boxsdk
```

#### Getting Access Token

1. Go to [Box Developer Console](https://app.box.com/developers/console)
2. Create new app → "Custom App" → "Server Authentication (with JWT)"
3. Or use "OAuth 2.0" for user authentication
4. Generate access token

#### Usage

```python
from org_context import initialize_context_manager

initialize_context_manager(
    "https://app.box.com/file/123456789",
    remote_kwargs={"access_token": "your-access-token"}
)
```

#### CLI Usage

```bash
export BOX_ACCESS_TOKEN="your-access-token"

python main.py rfp.pdf \
  --org-context "https://app.box.com/file/123456789"
```

### HTTP/HTTPS (Generic Web Server)

#### Prerequisites
```bash
pip install requests
```

#### Usage

```python
from org_context import initialize_context_manager

# Public URL
initialize_context_manager("https://config.company.com/org_config.yaml")

# With basic authentication
initialize_context_manager(
    "https://config.company.com/org_config.yaml",
    remote_kwargs={"auth": ("username", "password")}
)

# With custom headers (e.g., API key)
initialize_context_manager(
    "https://config.company.com/org_config.yaml",
    remote_kwargs={"headers": {"Authorization": "Bearer your-api-key"}}
)
```

#### CLI Usage

```bash
# Public URL
python main.py rfp.pdf \
  --org-context "https://config.company.com/org_config.yaml"

# With authentication (set in code or use environment variables)
```

### Amazon S3 / S3-Compatible Storage

#### Prerequisites
```bash
pip install boto3
```

#### Usage

```python
from org_context import initialize_context_manager

# Using environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
initialize_context_manager("s3://my-bucket/configs/org_config.yaml")

# Passing credentials directly
initialize_context_manager(
    "s3://my-bucket/configs/org_config.yaml",
    remote_kwargs={
        "aws_access_key_id": "your-access-key",
        "aws_secret_access_key": "your-secret-key",
        "region_name": "us-east-1"
    }
)

# S3-compatible storage (MinIO, DigitalOcean Spaces, etc.)
initialize_context_manager(
    "s3://my-bucket/configs/org_config.yaml",
    remote_kwargs={
        "aws_access_key_id": "your-access-key",
        "aws_secret_access_key": "your-secret-key",
        "endpoint_url": "https://nyc3.digitaloceanspaces.com"
    }
)
```

#### CLI Usage

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

python main.py rfp.pdf \
  --org-context "s3://my-bucket/configs/org_config.yaml"
```

## Caching

Remote contexts are automatically cached locally to improve performance:

- **Cache Location**: System temp directory (`/tmp/rfp_analyzer_cache/` on Linux/Mac, `%TEMP%\rfp_analyzer_cache\` on Windows)
- **Cache Key**: MD5 hash of the remote URL
- **Cache Invalidation**: Manual (delete cache files) or implement TTL in your code

### Custom Cache Directory

```python
from org_context.remote_loaders import load_remote_context

# Specify custom cache directory
path = load_remote_context(
    "https://company.sharepoint.com/.../org_config.yaml",
    cache_dir="/path/to/custom/cache"
)
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate credentials** regularly
4. **Use least-privilege access** (read-only permissions)
5. **Enable audit logging** on cloud storage
6. **Use service accounts** instead of personal accounts
7. **Implement IP whitelisting** where possible
8. **Use HTTPS** for all remote URLs

## Troubleshooting

### Import Errors

If you see `ImportError: No module named 'office365'` or similar:

```bash
# Install required dependencies
pip install Office365-REST-Python-Client  # SharePoint
pip install requests                       # OneDrive, HTTP
pip install boxsdk                        # Box
pip install boto3                         # S3
```

Or install all at once:

```bash
pip install -r requirements_remote.txt
```

### Authentication Errors

**SharePoint**: Ensure app has `Sites.Read.All` permission and admin consent granted

**OneDrive**: Verify access token is valid and has `Files.Read.All` scope

**Box**: Check access token hasn't expired (Box tokens expire after 60 minutes)

**S3**: Verify IAM permissions include `s3:GetObject` for the bucket/key

### Network Errors

- Check firewall/proxy settings
- Verify URL is accessible from your network
- Test with `curl` or browser first
- Check for SSL certificate issues

### Cache Issues

Clear cache if you're not seeing updates:

```bash
# Linux/Mac
rm -rf /tmp/rfp_analyzer_cache/

# Windows
rmdir /s %TEMP%\rfp_analyzer_cache\
```

## Advanced Configuration

### Programmatic Usage

```python
from org_context import ContextManager

# Create manager with remote context
manager = ContextManager()
manager.load_context(
    "https://company.sharepoint.com/.../org_config.yaml",
    remote_kwargs={
        "client_id": "...",
        "client_secret": "...",
        "tenant_id": "..."
    }
)

# Use context
context = manager.get_context()
print(f"Organization: {context.name}")
```

### Multiple Contexts

```python
# Load different contexts for different projects
manager1 = ContextManager()
manager1.load_context("https://sharepoint.com/.../project1_config.yaml")

manager2 = ContextManager()
manager2.load_context("https://sharepoint.com/.../project2_config.yaml")
```

### Fallback to Local

```python
try:
    manager = ContextManager()
    manager.load_context("https://sharepoint.com/.../org_config.yaml")
except Exception as e:
    print(f"Failed to load remote context: {e}")
    print("Falling back to local context")
    manager = ContextManager("org_context/config/org_config.yaml")
```

## Example: Complete SharePoint Setup

### 1. Create Azure AD App

```bash
# Use Azure CLI
az ad app create \
  --display-name "RFP Analyzer Context Loader" \
  --sign-in-audience AzureADMyOrg

# Note the appId (client ID)
```

### 2. Create Client Secret

```bash
az ad app credential reset \
  --id <app-id> \
  --append

# Note the password (client secret)
```

### 3. Grant Permissions

```bash
# Add SharePoint permission
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0ff1-ce00-000000000000 \
  --api-permissions 678536fe-1083-478a-9c59-b99265e6b0d3=Role

# Grant admin consent
az ad app permission admin-consent --id <app-id>
```

### 4. Set Environment Variables

```bash
export SHAREPOINT_CLIENT_ID="<app-id>"
export SHAREPOINT_CLIENT_SECRET="<client-secret>"
export SHAREPOINT_TENANT_ID="<tenant-id>"
```

### 5. Upload Config to SharePoint

1. Go to SharePoint site
2. Navigate to document library
3. Upload `org_config.yaml`
4. Copy the file URL

### 6. Run Analyzer

```bash
python main.py rfp.pdf \
  --org-context "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml"
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `org_context/remote_loaders.py` for implementation details
- Open an issue on the project repository