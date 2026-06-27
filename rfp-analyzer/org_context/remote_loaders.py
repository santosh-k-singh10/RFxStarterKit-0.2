"""
remote_loaders.py
-----------------
Remote context loaders for cloud storage providers.

Supports loading organizational context from:
- SharePoint Online
- OneDrive for Business
- Box
- Google Drive
- Generic HTTP/HTTPS URLs
- S3-compatible storage
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import structlog

log = structlog.get_logger(__name__)


class RemoteContextLoader:
    """Base class for remote context loaders."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize remote loader.
        
        Args:
            cache_dir: Directory to cache downloaded files (default: system temp)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "rfp_analyzer_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        log.info("remote_loader_initialized", cache_dir=str(self.cache_dir))
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load context from remote URL.
        
        Args:
            url: Remote URL to load from
            **kwargs: Provider-specific parameters
            
        Returns:
            Path to cached local file
        """
        raise NotImplementedError("Subclasses must implement load()")
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path from URL."""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"context_{url_hash}.yaml"


class SharePointLoader(RemoteContextLoader):
    """Load context from SharePoint Online."""
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load from SharePoint.
        
        Args:
            url: SharePoint file URL
            client_id: Azure AD app client ID (optional, from env)
            client_secret: Azure AD app secret (optional, from env)
            tenant_id: Azure AD tenant ID (optional, from env)
            
        Returns:
            Path to cached file
        """
        try:
            from office365.runtime.auth.client_credential import ClientCredential  # type: ignore
            from office365.sharepoint.client_context import ClientContext  # type: ignore
        except ImportError:
            raise ImportError(
                "SharePoint support requires: pip install Office365-REST-Python-Client"
            )
        
        # Get credentials from kwargs or environment
        client_id = kwargs.get('client_id') or os.getenv('SHAREPOINT_CLIENT_ID')
        client_secret = kwargs.get('client_secret') or os.getenv('SHAREPOINT_CLIENT_SECRET')
        tenant_id = kwargs.get('tenant_id') or os.getenv('SHAREPOINT_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            raise ValueError(
                "SharePoint requires client_id, client_secret, and tenant_id. "
                "Provide via kwargs or environment variables: "
                "SHAREPOINT_CLIENT_ID, SHAREPOINT_CLIENT_SECRET, SHAREPOINT_TENANT_ID"
            )
        
        log.info("loading_from_sharepoint", url=url)
        
        # Parse SharePoint URL
        parsed = urlparse(url)
        site_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Authenticate
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials)
        
        # Download file
        cache_path = self._get_cache_path(url)
        
        # Extract file path from URL
        file_path = parsed.path
        
        with open(cache_path, 'wb') as local_file:
            file = ctx.web.get_file_by_server_relative_url(file_path)
            file.download(local_file).execute_query()
        
        log.info("sharepoint_download_complete", cache_path=str(cache_path))
        return cache_path


class OneDriveLoader(RemoteContextLoader):
    """Load context from OneDrive for Business."""
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load from OneDrive.
        
        Args:
            url: OneDrive share link or file URL
            access_token: Microsoft Graph API access token (optional, from env)
            
        Returns:
            Path to cached file
        """
        try:
            import requests
        except ImportError:
            raise ImportError("OneDrive support requires: pip install requests")
        
        access_token = kwargs.get('access_token') or os.getenv('ONEDRIVE_ACCESS_TOKEN')
        
        if not access_token:
            raise ValueError(
                "OneDrive requires access_token. "
                "Provide via kwargs or ONEDRIVE_ACCESS_TOKEN environment variable"
            )
        
        log.info("loading_from_onedrive", url=url)
        
        # Convert share link to download URL if needed
        if 'sharepoint.com' in url or 'onedrive.live.com' in url:
            # Use Microsoft Graph API to get download URL
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Extract sharing token from URL
            if '?id=' in url:
                file_id = url.split('?id=')[1].split('&')[0]
                graph_url = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
            else:
                # Use sharing link
                import base64
                encoded_url = base64.b64encode(url.encode()).decode().rstrip('=')
                graph_url = f'https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem/content'
            
            response = requests.get(graph_url, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            cache_path = self._get_cache_path(url)
            cache_path.write_bytes(response.content)
            
            log.info("onedrive_download_complete", cache_path=str(cache_path))
            return cache_path
        
        raise ValueError(f"Unsupported OneDrive URL format: {url}")


class BoxLoader(RemoteContextLoader):
    """Load context from Box."""
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load from Box.
        
        Args:
            url: Box file URL or shared link
            access_token: Box API access token (optional, from env)
            
        Returns:
            Path to cached file
        """
        try:
            from boxsdk import Client  # type: ignore
            from boxsdk.auth.oauth2 import OAuth2  # type: ignore
        except ImportError:
            raise ImportError("Box support requires: pip install boxsdk")
        
        access_token = kwargs.get('access_token') or os.getenv('BOX_ACCESS_TOKEN')
        
        if not access_token:
            raise ValueError(
                "Box requires access_token. "
                "Provide via kwargs or BOX_ACCESS_TOKEN environment variable"
            )
        
        log.info("loading_from_box", url=url)
        
        # Authenticate with access token
        # For access token-only auth, we need to create a simple auth object
        class TokenAuth:
            """Simple token-based authentication for Box."""
            def __init__(self, access_token: str):
                self._access_token = access_token
            
            def refresh(self, access_token_callback):
                """Refresh is not needed for static tokens."""
                return self._access_token
            
            @property
            def access_token(self):
                return self._access_token
        
        auth = TokenAuth(access_token)
        client = Client(auth)
        
        # Extract file ID from URL
        if '/file/' in url:
            file_id = url.split('/file/')[1].split('/')[0]
        else:
            raise ValueError(f"Cannot extract file ID from Box URL: {url}")
        
        # Download file
        cache_path = self._get_cache_path(url)
        
        with open(cache_path, 'wb') as local_file:
            client.file(file_id).download_to(local_file)
        
        log.info("box_download_complete", cache_path=str(cache_path))
        return cache_path


class HTTPLoader(RemoteContextLoader):
    """Load context from generic HTTP/HTTPS URL."""
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load from HTTP/HTTPS URL.
        
        Args:
            url: HTTP/HTTPS URL
            headers: Optional HTTP headers dict
            auth: Optional tuple (username, password) for basic auth
            
        Returns:
            Path to cached file
        """
        try:
            import requests
        except ImportError:
            raise ImportError("HTTP support requires: pip install requests")
        
        log.info("loading_from_http", url=url)
        
        headers = kwargs.get('headers', {})
        auth = kwargs.get('auth')
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        
        cache_path = self._get_cache_path(url)
        cache_path.write_bytes(response.content)
        
        log.info("http_download_complete", cache_path=str(cache_path))
        return cache_path


class S3Loader(RemoteContextLoader):
    """Load context from S3-compatible storage."""
    
    def load(self, url: str, **kwargs) -> Path:
        """
        Load from S3.
        
        Args:
            url: S3 URL (s3://bucket/key)
            aws_access_key_id: AWS access key (optional, from env)
            aws_secret_access_key: AWS secret key (optional, from env)
            region_name: AWS region (optional, from env)
            endpoint_url: Custom S3 endpoint for S3-compatible storage
            
        Returns:
            Path to cached file
        """
        try:
            import boto3  # type: ignore
        except ImportError:
            raise ImportError("S3 support requires: pip install boto3")
        
        log.info("loading_from_s3", url=url)
        
        # Parse S3 URL
        if not url.startswith('s3://'):
            raise ValueError(f"Invalid S3 URL: {url}")
        
        parts = url[5:].split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        
        # Get credentials
        aws_access_key_id = kwargs.get('aws_access_key_id') or os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = kwargs.get('aws_secret_access_key') or os.getenv('AWS_SECRET_ACCESS_KEY')
        region_name = kwargs.get('region_name') or os.getenv('AWS_REGION', 'us-east-1')
        endpoint_url = kwargs.get('endpoint_url')
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )
        
        # Download file
        cache_path = self._get_cache_path(url)
        s3_client.download_file(bucket, key, str(cache_path))
        
        log.info("s3_download_complete", cache_path=str(cache_path))
        return cache_path


def get_loader(url: str, **kwargs) -> RemoteContextLoader:
    """
    Get appropriate loader for URL.
    
    Args:
        url: Remote URL
        **kwargs: Loader-specific parameters
        
    Returns:
        RemoteContextLoader instance
    """
    parsed = urlparse(url)
    
    if 'sharepoint.com' in parsed.netloc:
        return SharePointLoader(**kwargs)
    elif 'onedrive' in parsed.netloc or '1drv.ms' in parsed.netloc:
        return OneDriveLoader(**kwargs)
    elif 'box.com' in parsed.netloc:
        return BoxLoader(**kwargs)
    elif parsed.scheme == 's3':
        return S3Loader(**kwargs)
    elif parsed.scheme in ('http', 'https'):
        return HTTPLoader(**kwargs)
    else:
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")


def load_remote_context(url: str, **kwargs) -> Path:
    """
    Load organizational context from remote URL.
    
    Args:
        url: Remote URL (SharePoint, OneDrive, Box, HTTP, S3)
        **kwargs: Provider-specific parameters
        
    Returns:
        Path to cached local file
        
    Examples:
        # SharePoint
        path = load_remote_context(
            "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml",
            client_id="...",
            client_secret="...",
            tenant_id="..."
        )
        
        # OneDrive
        path = load_remote_context(
            "https://company-my.sharepoint.com/personal/user/Documents/org_config.yaml",
            access_token="..."
        )
        
        # Box
        path = load_remote_context(
            "https://app.box.com/file/123456789",
            access_token="..."
        )
        
        # HTTP with auth
        path = load_remote_context(
            "https://config.company.com/org_config.yaml",
            auth=("username", "password")
        )
        
        # S3
        path = load_remote_context(
            "s3://my-bucket/configs/org_config.yaml",
            aws_access_key_id="...",
            aws_secret_access_key="..."
        )
    """
    loader = get_loader(url, **kwargs)
    return loader.load(url, **kwargs)

# Made with Bob
