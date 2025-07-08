
"""
MCP BitQiu - A Model Context Protocol server for BitQiu cloud storage.

This package provides a BitQiu cloud storage client and MCP server implementation
for seamless integration with AI assistants and other MCP-compatible tools.
"""


# Core client and exceptions
from .bitqiu import (
    BitQiuClient,
    BitQiuException,
    AuthenticationError,
    ApiError,
    BitQiuConfig,
)

# Data models and enums
from .bitqiu import (
    ResourceType,
    TaskStatus,
    AuthSession,
    UserPrivilege,
    UserInfo,
    FileResource,
    DirectoryInfo,
    DownloadInfo,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    
    # Core client
    "BitQiuClient",
    
    # Exceptions
    "BitQiuException",
    "AuthenticationError",
    "ApiError",
    
    # Configuration
    "BitQiuConfig",
    
    # Enums
    "ResourceType",
    "TaskStatus",
    
    # Data models
    "AuthSession",
    "UserPrivilege",
    "UserInfo",
    "FileResource",
    "DirectoryInfo",
    "DownloadInfo",
]