import os
from loguru import logger
from pathlib import Path


def validate_file_path(file_path: str) -> bool:
    """ファイルパスの有効性を検証する"""
    if not file_path:
        return False
    path = Path(file_path)
    return path.exists() and path.is_file()


def create_directory_safely(directory: str) -> bool:
    """安全にディレクトリを作成する"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"ディレクトリ作成エラー: {e}")
        return False
