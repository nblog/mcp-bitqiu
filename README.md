# MCP BitQiu

A modern Python client for BitQiu cloud storage services, designed with Model Context Protocol (MCP) server integration in mind.

## Features

- 🔐 **QR Code Authentication** - Easy login using QR code scanning
- 📁 **File Management** - List, create, rename, move, and delete files and directories
- ⬇️ **Download Management** - Get download URLs and manage download tasks
- 📊 **User Information** - View account details and usage statistics
- ⭐ **Collection Management** - Add/remove items from favorites
- 🎯 **Daily Sign-in** - Automated point earning
- 🔌 **MCP Server** - Ready-to-use Model Context Protocol server

## Quick Start

```bash
# Install the package
pip install -e .

# Or using uv
uv pip install -e .
```

### Basic Usage

```python
from mcp_bitqiu import BitQiuClient

# Use with context manager for automatic cleanup
with BitQiuClient() as client:
    # Authenticate with QR code
    client.authenticate_with_qr_code()
    
    # Get user information
    user_info = client.get_user_info()
    print(f"Downloads remaining: {user_info.privilege.cloud_download_count_remain}")
    print(f"Video plays remaining: {user_info.privilege.cloud_video_play_count_remain}")
    
    # Daily sign-in
    client.daily_signin()
```

### MCP Server Usage

The package includes a ready-to-use MCP server that can be integrated with AI assistants:

```bash
# Start the MCP server
mcp-bitqiu-server
```

Available MCP tools:
- `bitqiu_authenticate` - Authenticate with BitQiu
- `bitqiu_get_user_info` - Get user account information
- `bitqiu_list_resources` - List files and directories
- `bitqiu_create_directory` - Create new directories
- `bitqiu_get_download_url` - Get download URLs for files
- `bitqiu_delete_resources` - Delete files and directories
- `bitqiu_rename_resource` - Rename files and directories
- `bitqiu_move_resources` - Move files and directories
- `bitqiu_add_download_tasks` - Add download tasks
- `bitqiu_daily_signin` - Perform daily sign-in

## API Reference

### BitQiuClient

The main client class for interacting with BitQiu services.

#### Authentication

```python
client = BitQiuClient()

# Authenticate using QR code (interactive)
client.authenticate_with_qr_code()

# Check authentication status
if client.is_authenticated:
    print("Ready to use!")
```

#### User Information

```python
# Get user info (required before most operations)
user_info = client.get_user_info()
print(f"Privileged gear: {user_info.privilege.privileged_gear_name}")
print(f"Downloads remaining: {user_info.privilege.cloud_download_count_remain}")
print(f"Video plays remaining: {user_info.privilege.cloud_video_play_count_remain}")
```

#### File Operations

```python
# List resources
resources = client.list_resources(
    parent_dir=None,  # None for root directory
    order_by="name",  # "name", "updateTime", or "size"
    ascending=True
)

# Create directory
directory = client.create_directory("New Folder", parent_dir=None)

# Get download URL
download_info = client.get_download_url("file_id")
print(f"Download URL: {download_info.url}")

# Rename resource
client.rename_resource("resource_id", "New Name", is_directory=False)

# Move resources
client.move_resources(
    target_dir="target_directory_id",
    file_ids=["file1", "file2"],
    dir_ids=["dir1"]
)

# Delete resources
client.delete_resources(
    file_ids=["file1", "file2"],
    dir_ids=["dir1"]
)
```

#### Collection Management

```python
# Add to collection
client.manage_collection(
    add_to_collection=True,
    file_ids=["file1"],
    dir_ids=["dir1"]
)

# Remove from collection
client.manage_collection(
    add_to_collection=False,
    file_ids=["file1"]
)
```

#### Download Tasks

```python
# Add download tasks
urls = [
    "http://example.com/file1.zip",
    "http://example.com/file2.pdf"
]
success = client.add_download_tasks(urls, target_dir="optional_dir_id")
```

#### Utilities

```python
# Daily sign-in for points
client.daily_signin()

# Calculate file MD5
md5_hash = BitQiuClient.calculate_file_md5("/path/to/file")

# Get current timestamp
timestamp = BitQiuClient.get_timestamp_ms()
```

## Data Models

The package uses Pydantic models for type safety:

- `UserInfo` - User account information
- `FileResource` - File/directory metadata
- `DirectoryInfo` - Directory information
- `DownloadInfo` - Download URL and metadata
- `AuthSession` - Authentication session data

## Error Handling

The package defines custom exceptions:

- `BitQiuException` - Base exception for all BitQiu operations
- `AuthenticationError` - Authentication-related errors
- `ApiError` - API request failures

```python
from mcp_bitqiu import BitQiuClient, AuthenticationError, ApiError

try:
    with BitQiuClient() as client:
        client.authenticate_with_qr_code()
        # ... operations
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ApiError as e:
    print(f"API error: {e}")
```

## Examples

See `examples.py` for comprehensive usage examples:

```bash
python examples.py
```

## Architecture

The redesigned architecture focuses on:

1. **Separation of Concerns** - Clear separation between HTTP client, business logic, and data models
2. **Type Safety** - Full type annotations and Pydantic models
3. **Error Handling** - Proper exception hierarchy and error messages
4. **Testability** - Easy to mock and test individual components
5. **Extensibility** - Easy to add new features and endpoints
6. **MCP Integration** - Built-in support for Model Context Protocol servers

## Configuration

All BitQiu-specific constants are centralized in the `BitQiuConfig` class:

```python
from mcp_bitqiu import BitQiuConfig

print(f"API Host: {BitQiuConfig.HOST_URL}")
print(f"Success Code: {BitQiuConfig.SUCCESS_CODE}")
```

## Development

### Key Improvements from Original

1. **Modern Python Practices** - Type hints, dataclasses, enums
2. **Better Error Handling** - Custom exceptions with meaningful messages
3. **Code Organization** - Logical separation of functionality
4. **Documentation** - Comprehensive docstrings and examples
5. **MCP Integration** - Built-in MCP server support
6. **Resource Management** - Context managers for cleanup
7. **Extensibility** - Easy to add new features

## License

This project maintains the same license as the original implementation.

## Contributing

Contributions are welcome! Please ensure:

1. Code follows the established patterns
2. Type hints are included
3. Tests are added for new functionality
4. Documentation is updated

## Changelog

### v0.1.0 (Current)

- Complete rewrite with modern Python practices
- Added comprehensive type annotations
- Implemented Pydantic models for data validation
- Added MCP server integration
- Improved error handling and logging
- Added comprehensive documentation and examples
