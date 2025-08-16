# -*- coding: utf-8 -*-
"""
RESTful API サーバー
Officeファイルと画像ファイルをPDFに変換するAPIエンドポイントを提供
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# ローカルアプリケーションのインポート
from .pdf_converter import convert_office_file_to_pdf, convert_image_to_pdf
from .exceptions import ConvertToPdfError
from .file_utils import validate_file_path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flaskアプリケーションの初期化
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MBの最大ファイルサイズ
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# 許可されるファイル拡張子
ALLOWED_OFFICE_EXTENSIONS = {'docx', 'pptx', 'xlsx', 'doc', 'ppt', 'xls'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# 注意: ファイル変換結果は直接返されるため、結果保存辞書は不要


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    ファイル名が許可された拡張子を持つかチェック
    
    Args:
        filename: チェックするファイル名
        allowed_extensions: 許可された拡張子のセット
    
    Returns:
        bool: 許可されている場合True
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def create_response(success: bool, message: str, data: Dict[str, Any] = None, 
                   status_code: int = 200) -> tuple:
    """
    統一されたAPIレスポンス形式を作成
    
    Args:
        success: 成功フラグ
        message: レスポンスメッセージ
        data: レスポンスデータ
        status_code: HTTPステータスコード
    
    Returns:
        tuple: (レスポンス辞書, ステータスコード)
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'data': data or {}
    }
    return jsonify(response), status_code


def save_uploaded_file(file, upload_folder: str) -> str:
    """
    アップロードされたファイルを安全に保存
    
    Args:
        file: アップロードされたファイルオブジェクト
        upload_folder: アップロード先フォルダ
    
    Returns:
        str: 保存されたファイルのパス
    """
    # アップロードフォルダが存在しない場合は作成
    os.makedirs(upload_folder, exist_ok=True)
    
    # ファイル名を安全にする
    filename = secure_filename(file.filename)
    
    # ユニークなファイル名を生成
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # ファイルを保存
    file.save(file_path)
    logger.info(f"ファイルが保存されました: {file_path}")
    
    return file_path


@app.errorhandler(413)
def too_large(e):
    """
ファイルサイズが大きすぎる場合のエラーハンドラー
    """
    logger.warning("アップロードされたファイルのサイズが制限を超えています")
    return create_response(
        success=False,
        message="ファイルサイズが制限（50MB）を超えています",
        status_code=413
    )


@app.errorhandler(500)
def internal_error(e):
    """
    内部サーバーエラーのハンドラー
    """
    logger.error(f"内部サーバーエラー: {str(e)}")
    return create_response(
        success=False,
        message="内部サーバーエラーが発生しました",
        status_code=500
    )


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    ヘルスチェックエンドポイント
    APIサーバーの状態を確認
    """
    logger.info("ヘルスチェックが要求されました")
    return create_response(
        success=True,
        message="APIサーバーは正常に動作しています",
        data={
            'version': '1.0.0',
            'service': 'PDF変換API',
            'status': 'healthy'
        }
    )


@app.route('/api/convert/office', methods=['POST'])
def convert_office_to_pdf():
    """
    OfficeファイルをPDFに変換するエンドポイント
    
    Returns:
        JSON: 変換結果とファイルID
    """
    logger.info("Officeファイル変換リクエストを受信しました")
    
    # ファイルがリクエストに含まれているかチェック
    if 'file' not in request.files:
        logger.warning("ファイルがリクエストに含まれていません")
        return create_response(
            success=False,
            message="ファイルが指定されていません",
            status_code=400
        )
    
    file = request.files['file']
    
    # ファイルが選択されているかチェック
    if file.filename == '':
        logger.warning("ファイルが選択されていません")
        return create_response(
            success=False,
            message="ファイルが選択されていません",
            status_code=400
        )
    
    # ファイル拡張子をチェック
    if not allowed_file(file.filename, ALLOWED_OFFICE_EXTENSIONS):
        logger.warning(f"サポートされていないファイル形式: {file.filename}")
        return create_response(
            success=False,
            message=f"サポートされていないファイル形式です。許可される形式: {', '.join(ALLOWED_OFFICE_EXTENSIONS)}",
            status_code=400
        )
    
    try:
        # ファイルを保存
        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        # PDFに変換
        pdf_path = convert_office_file_to_pdf(file_path, app.config['OUTPUT_FOLDER'])
        
        # 一時ファイルを削除
        os.remove(file_path)
        
        logger.info(f"Officeファイルの変換が完了しました: {file.filename} -> {pdf_path}")
        
        # PDFファイルのパスを絶対パスに変換
        absolute_pdf_path = os.path.abspath(pdf_path)
        
        # ファイルの存在確認
        if not os.path.exists(absolute_pdf_path):
            logger.error(f"変換されたPDFファイルが見つかりません: {absolute_pdf_path}")
            return create_response(
                success=False,
                message="PDF変換は完了しましたが、ファイルが見つかりません",
                status_code=500
            )
        
        # ダウンロード用のファイル名を生成
        original_name = os.path.splitext(file.filename)[0]
        download_name = f"{original_name}.pdf"
        
        logger.info(f"PDFファイルを送信します: {absolute_pdf_path}")
        
        # PDFファイルを直接返す
        return send_file(
            absolute_pdf_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )
        
    except ConvertToPdfError as e:
        logger.error(f"PDF変換エラー: {str(e)}")
        return create_response(
            success=False,
            message=f"PDF変換中にエラーが発生しました: {str(e)}",
            status_code=500
        )
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return create_response(
            success=False,
            message="予期しないエラーが発生しました",
            status_code=500
        )


@app.route('/api/convert/image', methods=['POST'])
def convert_image_to_pdf():
    """
    画像ファイルをPDFに変換するエンドポイント
    
    Returns:
        JSON: 変換結果とファイルID
    """
    logger.info("画像ファイル変換リクエストを受信しました")
    
    # ファイルがリクエストに含まれているかチェック
    if 'file' not in request.files:
        logger.warning("ファイルがリクエストに含まれていません")
        return create_response(
            success=False,
            message="ファイルが指定されていません",
            status_code=400
        )
    
    file = request.files['file']
    
    # ファイルが選択されているかチェック
    if file.filename == '':
        logger.warning("ファイルが選択されていません")
        return create_response(
            success=False,
            message="ファイルが選択されていません",
            status_code=400
        )
    
    # ファイル拡張子をチェック
    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        logger.warning(f"サポートされていないファイル形式: {file.filename}")
        return create_response(
            success=False,
            message=f"サポートされていないファイル形式です。許可される形式: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
            status_code=400
        )
    
    try:
        # ファイルを保存
        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        # PDFに変換
        pdf_path = convert_image_to_pdf(file_path, app.config['OUTPUT_FOLDER'])
        
        # 一時ファイルを削除
        os.remove(file_path)
        
        logger.info(f"画像ファイルの変換が完了しました: {file.filename} -> {pdf_path}")
        
        # PDFファイルのパスを絶対パスに変換
        absolute_pdf_path = os.path.abspath(pdf_path)
        
        # ファイルの存在確認
        if not os.path.exists(absolute_pdf_path):
            logger.error(f"変換されたPDFファイルが見つかりません: {absolute_pdf_path}")
            return create_response(
                success=False,
                message="PDF変換は完了しましたが、ファイルが見つかりません",
                status_code=500
            )
        
        # ダウンロード用のファイル名を生成
        original_name = os.path.splitext(file.filename)[0]
        download_name = f"{original_name}.pdf"
        
        logger.info(f"PDFファイルを送信します: {absolute_pdf_path}")
        
        # PDFファイルを直接返す
        return send_file(
            absolute_pdf_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )
        
    except ConvertToPdfError as e:
        logger.error(f"PDF変換エラー: {str(e)}")
        return create_response(
            success=False,
            message=f"PDF変換中にエラーが発生しました: {str(e)}",
            status_code=500
        )
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return create_response(
            success=False,
            message="予期しないエラーが発生しました",
            status_code=500
        )


# 注意: ダウンロードエンドポイントは削除されました
# PDFファイルは変換エンドポイントから直接返されます


if __name__ == '__main__':
    # 必要なディレクトリを作成
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    logger.info("PDF変換APIサーバーを起動しています...")
    app.run(host='0.0.0.0', port=5000, debug=True)