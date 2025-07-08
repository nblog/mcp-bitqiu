#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitQiu Cloud Storage API Client

A modern Python client for interacting with BitQiu cloud storage services.
Designed with MCP (Model Context Protocol) server integration in mind.
"""

import os
import time
import json
import hashlib
import logging
from typing import List, Dict, Tuple, Optional, Union, Any
from urllib.parse import quote_plus
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel, Field


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BitQiuConfig:
    """Configuration constants for BitQiu API."""
    
    QR_CODE_API = "https://api.qrserver.com/v1/create-qr-code/?data={}"
    HOST_URL = "https://pan.bitqiu.com"
    ORG_CHANNEL = "default|default|stpan"
    SUCCESS_CODE = "10200"
    
    # API Endpoints
    ENDPOINTS = {
        "qr_code": "/loginServer/getQRCode",
        "qr_code_info": "/loginServer/getQRCodeInfo",
        "user_info": "/user/getInfo",
        "search": "/apiToken/cfi/fs/search/name",
        "resource_pages": "/apiToken/cfi/fs/resources/pages",
        "resource_copy": "/apiToken/cfi/fs/async/copy",
        "resource_list": "/resource/dirList",
        "resource_create": "/resource/create",
        "resource_delete": "/resource/delete",
        "resource_rename": "/resource/rename",
        "resource_move": "/resource/remove",
        "collection_add": "/collect/add",
        "collection_cancel": "/collect/cancel",
        "task_list": "/cloudDownload/getUserTaskList",
        "task_add": "/cloudDownload/addTasks",
        "task_cancel": "/cloudDownload/cancelTask",
        "download_url": "/download/getUrl",
        "signin": "/integral/randomSignin",
    }


class ResourceType(Enum):
    """Resource type enumeration."""
    FILE = "file"
    DIRECTORY = "directory"


class TaskStatus(Enum):
    """Download task status enumeration."""
    PENDING = "0"
    DOWNLOADING = "1"
    COMPLETED = "2"
    FAILED = "3"


@dataclass
class AuthSession:
    """Authentication session data."""
    cloud_web_sid: str = ""
    user_id: str = ""
    user_root_dir: str = ""

class UserPrivilege(BaseModel):
    """User privilege model."""
    cloud_download: bool = Field(alias="cloudDownload")
    cloud_download_count_remain: int = Field(alias="cloudDownloadCountRemain")
    cloud_video_play: bool = Field(alias="cloudVideoPlay")
    cloud_video_play_count_remain: int = Field(alias="cloudVideoPlayCountRemain")
    cloud_music_play: bool = Field(alias="cloudMusicPlay")
    cloud_music_play_count_remain: int = Field(alias="cloudMusicPlayCountRemain")
    cloud_doc_play: bool = Field(alias="cloudDocPlay")
    cloud_doc_play_count_remain: int = Field(alias="cloudDocPlayCountRemain")
    privileged_gear_name: str = Field(alias="privilegedGearName")

    class Config:
        populate_by_name = True


class UserInfo(BaseModel):
    """User information model."""
    user_id: int = Field(alias="userId")
    root_dir_id: str = Field(alias="rootDirId")
    privilege: UserPrivilege = Field(alias="privilege")
    
    class Config:
        populate_by_name = True


class FileResource(BaseModel):
    """File resource model."""
    resource_id: str
    name: str
    size: Optional[int] = None
    is_directory: bool
    create_time: int
    update_time: int


class DirectoryInfo(BaseModel):
    """Directory information model."""
    dir_id: str
    name: str
    create_time: int
    update_time: int


class DownloadInfo(BaseModel):
    """Download information model."""
    md5: str
    size: int
    url: str


class BitQiuException(Exception):
    """Base exception for BitQiu operations."""
    pass


class AuthenticationError(BitQiuException):
    """Authentication related errors."""
    pass


class ApiError(BitQiuException):
    """API request errors."""
    pass


class BitQiuClient:
    """
    BitQiu Cloud Storage Client.
    
    A modern, type-safe client for interacting with BitQiu cloud storage services.
    Designed to be easily integrated with MCP servers.
    """

    def __init__(self, timeout: float = 30.0):
        """
        Initialize the BitQiu client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self._session = AuthSession()
        self._http_client = httpx.Client(timeout=timeout)
        self._config = BitQiuConfig()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._http_client.close()

    @staticmethod
    def calculate_file_md5(file_path: str) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash as hex string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def get_timestamp_ms() -> int:
        """Get current timestamp in milliseconds."""
        return int(round(time.time() * 1000))

    @staticmethod
    def datetime_to_timestamp_ms(datetime_str: str = "2023-01-01 00:00:00") -> int:
        """
        Convert datetime string to timestamp in milliseconds.
        
        Args:
            datetime_str: Datetime string in format "YYYY-MM-DD HH:MM:SS"
            
        Returns:
            Timestamp in milliseconds
        """
        return int(round(time.mktime(time.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")) * 1000))

    def _parse_response(self, response: httpx.Response) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Parse BitQiu API response.
        
        Args:
            response: HTTP response object
            
        Returns:
            Tuple of (success, message, data)
            
        Raises:
            ApiError: If response parsing fails
        """
        try:
            if response.status_code != 200:
                raise ApiError(f"HTTP {response.status_code}: {response.text}")
            
            json_data = response.json()
            success = json_data.get("code") == self._config.SUCCESS_CODE
            message = str(json_data.get("message", ""))
            data = json_data.get("data") or {}
            
            return success, message, data
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ApiError(f"Failed to parse response: {e}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Make HTTP request to BitQiu API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Parsed response tuple
        """
        url = f"{self._config.HOST_URL}{endpoint}"
        response = self._http_client.request(method, url, **kwargs)
        return self._parse_response(response)

    def authenticate_with_qr_code(self) -> bool:
        """
        Authenticate using QR code login.
        
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Get QR code
        success, message, data = self._make_request(
            "GET", 
            self._config.ENDPOINTS["qr_code"],
            params={
                "org_channel": self._config.ORG_CHANNEL, 
                "_": self.get_timestamp_ms()
            }
        )
        
        if not success:
            raise AuthenticationError(f"Failed to get QR code: {message}")

        verify_code = data["code"]
        qr_url = self._config.QR_CODE_API.format(data["url"])
        
        logger.info(f"Please scan the QR code: {qr_url}")

        # Poll for login confirmation (5 minutes timeout)
        params = {
            "org_channel": self._config.ORG_CHANNEL,
            "_": self.get_timestamp_ms(),
            "code": verify_code
        }
        
        for attempt in range(60):  # 5 minutes with 5-second intervals
            time.sleep(5)
            logger.info("Waiting for login confirmation...")
            
            response = self._http_client.get(
                f"{self._config.HOST_URL}{self._config.ENDPOINTS['qr_code_info']}",
                params=params,
                timeout=None
            )
            
            success, message, data = self._parse_response(response)
            
            if success:
                # Extract session information from cookies
                self._session.cloud_web_sid = response.cookies.get("cloud_web_sid", "")
                self._session.user_id = response.cookies.get("cloud_web_uid", "")
                
                # Set cookies for future requests
                self._http_client.cookies.set("cloud_web_sid", self._session.cloud_web_sid)
                self._http_client.cookies.set("cloud_web_uid", self._session.user_id)
                
                logger.info("Authentication successful!")
                return True

        raise AuthenticationError("Authentication timeout - QR code not scanned within 5 minutes")

    def get_user_info(self) -> UserInfo:
        """
        Get user information.
        
        Returns:
            User information object
            
        Raises:
            AuthenticationError: If not authenticated
            ApiError: If API request fails
        """
        if not self._session.cloud_web_sid:
            raise AuthenticationError("Not authenticated - please login first")

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["user_info"],
            data={"org_channel": self._config.ORG_CHANNEL}
        )
        
        if not success:
            raise ApiError(f"Failed to get user info: {message}")

        user_info = UserInfo(**data)
        self._session.user_root_dir = user_info.root_dir_id

        return user_info

    def list_resources(self, parent_dir: Optional[str] = None, 
                      order_by: str = "name", ascending: bool = True) -> List[FileResource]:
        """
        List resources in a directory.
        
        Args:
            parent_dir: Parent directory ID (None for root)
            order_by: Sort field ("name", "updateTime", "size")
            ascending: Sort order
            
        Returns:
            List of file resources
        """
        if not self._session.user_root_dir:
            raise AuthenticationError("User info not loaded - call get_user_info() first")

        parent_id = parent_dir or self._session.user_root_dir
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "parentId": parent_id,
            "userId": self._session.user_id,
            "name": "undefined",
            "limit": "24",
            "model": "1",
            "orderType": order_by,
            "desc": "0" if ascending else "1",
            "currentPage": "1",
            "page": "1"
        }

        all_resources = []
        
        while True:
            success, message, data = self._make_request(
                "POST",
                self._config.ENDPOINTS["resource_pages"],
                data=payload
            )
            
            if not success:
                raise ApiError(f"Failed to list resources: {message}")

            # Parse resources
            for item in data.get("data", []):
                resource = FileResource(
                    resource_id=item["resourceId"],
                    name=item["name"],
                    size=item["size"],
                    is_directory=bool(item.get("dirType") is not None),
                    create_time=self.datetime_to_timestamp_ms(item["createTime"]),
                    update_time=self.datetime_to_timestamp_ms(item["updateTime"])
                )
                all_resources.append(resource)

            if not data.get("hasNext", False):
                break
                
            # Next page
            current_page = int(payload["currentPage"]) + 1
            payload["page"] = str(current_page)
            payload["currentPage"] = str(current_page)

        return all_resources

    def list_directories(self, parent_dir: Optional[str] = None) -> List[DirectoryInfo]:
        """
        List directories only.
        
        Args:
            parent_dir: Parent directory ID (None for root)
            
        Returns:
            List of directory information
        """
        if not self._session.user_root_dir:
            raise AuthenticationError("User info not loaded - call get_user_info() first")

        parent_id = parent_dir or self._session.user_root_dir
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "parentId": parent_id,
            "limit": "100",
            "currentPage": "1"
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_list"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to list directories: {message}")

        directories = []
        for item in data.get("data", []):
            directory = DirectoryInfo(
                dir_id=item["dirId"],
                name=item["name"],
                create_time=self.datetime_to_timestamp_ms(item["createTime"]),
                update_time=self.datetime_to_timestamp_ms(item["updateTime"])
            )
            directories.append(directory)

        if data.get("hasNext", False):
            logger.warning("Directory list pagination not fully supported")

        return directories

    def create_directory(self, name: str, parent_dir: Optional[str] = None) -> DirectoryInfo:
        """
        Create a new directory.
        
        Args:
            name: Directory name
            parent_dir: Parent directory ID (None for root)
            
        Returns:
            Created directory information
        """
        if not self._session.user_root_dir:
            raise AuthenticationError("User info not loaded - call get_user_info() first")

        parent_id = parent_dir or self._session.user_root_dir
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "parentId": parent_id,
            "name": name
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_create"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to create directory: {message}")

        return DirectoryInfo(
            dir_id=data["dirId"],
            name=data["name"],
            create_time=self.datetime_to_timestamp_ms(data["createTime"]),
            update_time=self.datetime_to_timestamp_ms(data["updateTime"])
        )

    def get_download_url(self, file_id: str) -> DownloadInfo:
        """
        Get download URL for a file.
        
        Args:
            file_id: File resource ID
            
        Returns:
            Download information
        """
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "fileIds": file_id
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["download_url"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to get download URL: {message}")

        return DownloadInfo(
            md5=data["md5"],
            size=data["size"],
            url=data["url"]
        )

    def delete_resources(self, dir_ids: List[str] = None, file_ids: List[str] = None) -> bool:
        """
        Delete directories and files.
        
        Args:
            dir_ids: List of directory IDs to delete
            file_ids: List of file IDs to delete
            
        Returns:
            True if successful
        """
        dir_ids = dir_ids or []
        file_ids = file_ids or []
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "dirIds": ",".join(dir_ids),
            "fileIds": ",".join(file_ids)
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_delete"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to delete resources: {message}")

        return True

    def rename_resource(self, resource_id: str, new_name: str, is_directory: bool = False) -> bool:
        """
        Rename a resource.
        
        Args:
            resource_id: Resource ID
            new_name: New name
            is_directory: Whether the resource is a directory
            
        Returns:
            True if successful
        """
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "resourceId": resource_id,
            "name": new_name,
            "type": "1" if is_directory else "2"
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_rename"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to rename resource: {message}")

        return True

    def move_resources(self, target_dir: Optional[str] = None, 
                      dir_ids: List[str] = None, file_ids: List[str] = None) -> bool:
        """
        Move resources to a different directory.
        
        Args:
            target_dir: Target directory ID (None for root)
            dir_ids: List of directory IDs to move
            file_ids: List of file IDs to move
            
        Returns:
            True if successful
        """
        if not self._session.user_root_dir:
            raise AuthenticationError("User info not loaded - call get_user_info() first")

        dir_ids = dir_ids or []
        file_ids = file_ids or []
        
        if len(dir_ids) + len(file_ids) > 50:
            raise ValueError("Cannot move more than 50 items at once")

        target_id = target_dir or self._session.user_root_dir
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "parentId": target_id,
            "dirIds": ",".join(dir_ids),
            "fileIds": ",".join(file_ids)
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_move"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to move resources: {message}")

        return True

    def copy_resources(self, target_dir: Optional[str] = None,
                      dir_ids: List[str] = None, file_ids: List[str] = None) -> bool:
        """
        Copy resources to a different directory.
        
        Args:
            target_dir: Target directory ID (None for root)
            dir_ids: List of directory IDs to copy
            file_ids: List of file IDs to copy
            
        Returns:
            True if successful
        """
        if not self._session.user_root_dir:
            raise AuthenticationError("User info not loaded - call get_user_info() first")

        dir_ids = dir_ids or []
        file_ids = file_ids or []
        target_id = target_dir or self._session.user_root_dir
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "parentId": target_id,
            "dirIds": ",".join(dir_ids),
            "fileIds": ",".join(file_ids)
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["resource_copy"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to copy resources: {message}")

        return True

    def manage_collection(self, add_to_collection: bool, 
                         dir_ids: List[str] = None, file_ids: List[str] = None) -> bool:
        """
        Add or remove resources from collection.
        
        Args:
            add_to_collection: True to add, False to remove
            dir_ids: List of directory IDs
            file_ids: List of file IDs
            
        Returns:
            True if successful
        """
        dir_ids = dir_ids or []
        file_ids = file_ids or []
        
        endpoint = self._config.ENDPOINTS["collection_add" if add_to_collection else "collection_cancel"]
        
        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "dirIds": ",".join(dir_ids),
            "fileIds": ",".join(file_ids)
        }

        success, message, data = self._make_request("POST", endpoint, data=payload)
        
        if not success:
            action = "add to" if add_to_collection else "remove from"
            raise ApiError(f"Failed to {action} collection: {message}")

        return True

    def daily_signin(self) -> bool:
        """
        Perform daily sign-in to earn points.
        
        Returns:
            True if successful
        """
        payload = {"org_channel": self._config.ORG_CHANNEL}

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["signin"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to sign in: {message}")

        return True

    def add_download_tasks(self, urls: List[str], target_dir: Optional[str] = None) -> bool:
        """
        Add URLs to download task queue.

        Args:
            urls: List of download URLs (max 20, must be magnet or ed2k links)
            target_dir: Target directory ID (None for root)

        Returns:
            True if all tasks added successfully

        Raises:
            ValueError: If any URL is not a magnet or ed2k link
        """
        # Only allow magnet or ed2k links
        for url in urls:
            if not (url.startswith("magnet:") or url.startswith("ed2k://")):
                raise ValueError("Only magnet or ed2k links are allowed")

        if len(urls) > 20:
            raise ValueError("Cannot add more than 20 download tasks at once")

        if not self._session.user_id:
            raise AuthenticationError("User ID not available - please authenticate first")

        payload = {
            "org_channel": self._config.ORG_CHANNEL,
            "userId": self._session.user_id,
            "dirId": target_dir or "", # '云下载'
            "downloadUrls": json.dumps([quote_plus(url) for url in urls])
        }

        success, message, data = self._make_request(
            "POST",
            self._config.ENDPOINTS["task_add"],
            data=payload
        )
        
        if not success:
            raise ApiError(f"Failed to add download tasks: {message}")

        success_count = len(data.get("success", []))
        return success_count == len(urls)

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return bool(self._session.cloud_web_sid and self._session.user_id)

    @property
    def session_info(self) -> AuthSession:
        """Get current session information."""
        return self._session


def main():
    """Example usage of BitQiu client."""
    with BitQiuClient() as client:
        try:
            # Authenticate
            client.authenticate_with_qr_code()
            
            # Get user info
            user_info = client.get_user_info()
            logger.info(f"Privileged gear: {user_info.privilege.privileged_gear_name}")
            logger.info(f"Downloads remaining: {user_info.privilege.cloud_download_count_remain}")
            logger.info(f"Video plays remaining: {user_info.privilege.cloud_video_play_count_remain}")
            
            # Daily sign-in
            client.daily_signin()
            logger.info("Daily sign-in completed")
            
        except (BitQiuException, Exception) as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()