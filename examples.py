#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitQiu Client Usage Examples

This file demonstrates how to use the BitQiu client for various operations.
"""

import asyncio
from mcp_bitqiu import BitQiuClient


async def example_basic_usage():
    """Example of basic BitQiu client usage."""
    print("=== Basic BitQiu Client Usage ===")
    
    # Create client with context manager for automatic cleanup
    with BitQiuClient() as client:
        try:
            # Step 1: Authenticate
            print("1. Authenticating with BitQiu...")
            client.authenticate_with_qr_code()
            
            # Step 2: Get user information
            print("2. Getting user information...")
            user_info = client.get_user_info()
            print(f"   User ID: {user_info.user_id}")
            print(f"   Root directory: {user_info.root_dir_id}")
            print(f"   Privileged gear: {user_info.privilege.privileged_gear_name}")
            print(f"   Downloads remaining: {user_info.privilege.cloud_download_count_remain}")
            print(f"   Video plays remaining: {user_info.privilege.cloud_video_play_count_remain}")
            
            # Step 3: List resources in root directory
            print("3. Listing resources in root directory...")
            resources = client.list_resources()
            print(f"   Found {len(resources)} resources:")
            for i, resource in enumerate(resources[:10]):  # Show first 10
                prefix = "[DIR]" if resource.is_directory else "[FILE]"
                size_str = f" ({resource.size} bytes)" if not resource.is_directory else ""
                print(f"   {i+1:2d}. {prefix} {resource.name}{size_str}")
            
            # Step 4: Create a test directory
            print("4. Creating a test directory...")
            test_dir = client.create_directory("Test Directory")
            print(f"   Created directory: {test_dir.name} (ID: {test_dir.dir_id})")
            
            # Step 5: List directories only
            print("5. Listing directories...")
            directories = client.list_directories()
            print(f"   Found {len(directories)} directories:")
            for i, directory in enumerate(directories[:5]):  # Show first 5
                print(f"   {i+1:2d}. {directory.name} (ID: {directory.dir_id})")
            
            # Step 6: Daily sign-in
            print("6. Performing daily sign-in...")
            try:
                client.daily_signin()
                print("   Daily sign-in successful!")
            except Exception as e:
                print(f"   Daily sign-in failed: {e}")
            
            print("\n✅ Basic usage example completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during basic usage: {e}")


async def example_file_operations():
    """Example of file operations."""
    print("\n=== File Operations Example ===")
    
    with BitQiuClient() as client:
        try:
            # Assuming client is already authenticated from previous example
            if not client.is_authenticated:
                print("Please authenticate first...")
                client.authenticate_with_qr_code()
                client.get_user_info()
            
            # Get resources for demonstration
            resources = client.list_resources()
            files = [r for r in resources if not r.is_directory]
            directories = [r for r in resources if r.is_directory]
            
            if files:
                # Get download URL for first file
                first_file = files[0]
                print(f"1. Getting download URL for: {first_file.name}")
                try:
                    download_info = client.get_download_url(first_file.resource_id)
                    print(f"   File size: {download_info.size} bytes")
                    print(f"   MD5: {download_info.md5}")
                    print(f"   Download URL: {download_info.url[:50]}...")
                except Exception as e:
                    print(f"   Failed to get download URL: {e}")
            
            if len(files) >= 2:
                # Rename a file
                second_file = files[1]
                original_name = second_file.name
                new_name = f"renamed_{original_name}"
                print(f"2. Renaming file from '{original_name}' to '{new_name}'...")
                try:
                    client.rename_resource(second_file.resource_id, new_name, is_directory=False)
                    print("   File renamed successfully!")
                    
                    # Rename it back
                    client.rename_resource(second_file.resource_id, original_name, is_directory=False)
                    print("   File name restored!")
                except Exception as e:
                    print(f"   Failed to rename file: {e}")
            
            # Create and manage directories
            print("3. Creating nested directories...")
            try:
                parent_dir = client.create_directory("Parent Test Dir")
                child_dir = client.create_directory("Child Test Dir", parent_dir.dir_id)
                print(f"   Created: {parent_dir.name} -> {child_dir.name}")
                
                # List resources in parent directory
                child_resources = client.list_resources(parent_dir.dir_id)
                print(f"   Found {len(child_resources)} items in parent directory")
                
            except Exception as e:
                print(f"   Failed to create directories: {e}")
            
            print("✅ File operations example completed!")
            
        except Exception as e:
            print(f"❌ Error during file operations: {e}")


async def example_download_tasks():
    """Example of adding download tasks."""
    print("\n=== Download Tasks Example ===")
    
    with BitQiuClient() as client:
        try:
            if not client.is_authenticated:
                print("Please authenticate first...")
                client.authenticate_with_qr_code()
                client.get_user_info()
            
            # Example download URLs (these are just examples, may not be valid)
            example_urls = [
                "magnet:?xt=urn:btih:b2885043be3476443fa568d4a0a1ae009d2ed9e4",
            ]
            
            print(f"Adding {len(example_urls)} download tasks...")
            try:
                success = client.add_download_tasks(example_urls)
                if success:
                    print("   All download tasks added successfully!")
                else:
                    print("   Some download tasks may have failed")
            except Exception as e:
                print(f"   Failed to add download tasks: {e}")
            
            print("✅ Download tasks example completed!")
            
        except Exception as e:
            print(f"❌ Error during download tasks: {e}")


async def example_collection_management():
    """Example of collection management."""
    print("\n=== Collection Management Example ===")
    
    with BitQiuClient() as client:
        try:
            if not client.is_authenticated:
                print("Please authenticate first...")
                client.authenticate_with_qr_code()
                client.get_user_info()
            
            resources = client.list_resources()
            if resources:
                # Add to collection
                first_resource = resources[0]
                print(f"1. Adding '{first_resource.name}' to collection...")
                try:
                    if first_resource.is_directory:
                        client.manage_collection(True, dir_ids=[first_resource.resource_id])
                    else:
                        client.manage_collection(True, file_ids=[first_resource.resource_id])
                    print("   Added to collection successfully!")
                    
                    # Remove from collection
                    print("2. Removing from collection...")
                    if first_resource.is_directory:
                        client.manage_collection(False, dir_ids=[first_resource.resource_id])
                    else:
                        client.manage_collection(False, file_ids=[first_resource.resource_id])
                    print("   Removed from collection successfully!")
                    
                except Exception as e:
                    print(f"   Collection management failed: {e}")
            
            print("✅ Collection management example completed!")
            
        except Exception as e:
            print(f"❌ Error during collection management: {e}")


async def main():
    """Run all examples."""
    print("BitQiu Client Examples")
    print("=" * 50)
    
    try:
        await example_basic_usage()
        await example_file_operations()
        await example_download_tasks()
        await example_collection_management()
        
        print("\n🎉 All examples completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
