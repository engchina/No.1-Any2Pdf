import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def safe_file_operation(func):
    """ファイル操作デコレータ - 安全なファイル処理を保証"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"ファイルが見つかりません: {e}")
            raise
        except PermissionError as e:
            logger.error(f"ファイルアクセス権限エラー: {e}")
            raise
        except Exception as e:
            logger.error(f"ファイル操作エラー: {e}")
            raise

    return wrapper
