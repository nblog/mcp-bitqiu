# MCP BitQiu

A modern Python client for BitQiu cloud storage services.

## Features

- 🔐 **QR Code Authentication** - Easy login using QR code scanning
- 📁 **File Management** - List, create, rename, move, and delete files and directories
- ⬇️ **Download Management** - Get download URLs and manage download tasks
- 📊 **User Information** - View account details and usage statistics
- ⭐ **Collection Management** - Add/remove items from favorites
- 🎯 **Daily Sign-in** - Automated point earning
- 🔌 **MCP Server (WIP)** - Ready-to-use Model Context Protocol server

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

## Contributing

Contributions are welcome! Please ensure:

1. Code follows the established patterns
2. Type hints are included
3. Tests are added for new functionality
4. Documentation is updated

## License

This project maintains the same license as the original implementation.