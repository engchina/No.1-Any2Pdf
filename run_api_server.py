#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF変換APIサーバー起動スクリプト

このスクリプトはFlaskベースのRESTful APIサーバーを起動します。
Officeファイルと画像ファイルをPDFに変換する機能を提供します。
"""

import os
import sys
import logging
from app.api_server import app

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    APIサーバーのメイン起動関数
    """
    try:
        # 必要なディレクトリを作成
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        logger.info("=" * 50)
        logger.info("PDF変換APIサーバーを起動しています...")
        logger.info("=" * 50)
        logger.info("利用可能なエンドポイント:")
        logger.info("  GET  /api/health          - ヘルスチェック")
        logger.info("  POST /api/convert/office  - Officeファイル変換")
        logger.info("  POST /api/convert/image   - 画像ファイル変換")
        logger.info("  GET  /api/download/<id>   - PDFダウンロード")
        logger.info("=" * 50)
        logger.info("サーバーURL: http://localhost:5000")
        logger.info("停止するには Ctrl+C を押してください")
        logger.info("=" * 50)
        
        # Flaskアプリケーションを起動
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # 重複起動を防ぐ
        )
        
    except KeyboardInterrupt:
        logger.info("\nサーバーが停止されました")
        sys.exit(0)
    except Exception as e:
        logger.error(f"サーバー起動エラー: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()