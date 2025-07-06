import img2pdf
import logging
import os
import shutil
import subprocess
from PIL import Image

from .decorators import safe_file_operation
from .exceptions import ConvertToPdfError
from .file_utils import validate_file_path, create_directory_safely

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# OfficeファイルをPDFに変換
@safe_file_operation
def convert_office_file_to_pdf(input_path: str, output_dir: str) -> str:
    """OfficeファイルをPDFに変換します"""
    if not validate_file_path(input_path):
        raise FileNotFoundError(f"入力ファイルが存在しません: {input_path}")

    if not create_directory_safely(output_dir):
        raise ConvertToPdfError(f"出力ディレクトリの作成に失敗しました: {output_dir}")

    cmd = [
        'soffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', str(output_dir),
        str(input_path)
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,  # 5分タイムアウト
            check=True
        )
        logger.info(f"LibreOfficeの変換が完了しました: {input_path}")
    except subprocess.TimeoutExpired:
        raise ConvertToPdfError("LibreOfficeの変換がタイムアウトしました")
    except subprocess.CalledProcessError as e:
        raise ConvertToPdfError(f"LibreOffice変換エラー: {e.stderr.decode()}")

    # 変換が成功したか確認
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    temp_pdf_path = os.path.join(output_dir, base_name + ".pdf")

    if not os.path.exists(temp_pdf_path):
        raise ConvertToPdfError("OfficeファイルをPDFに変換できません")

    # ターゲットディレクトリ構造を作成: output/ファイル名_pdf/ファイル名.pdf
    target_dir = os.path.join(output_dir, f"{base_name}_pdf")
    if not create_directory_safely(target_dir):
        raise ConvertToPdfError(f"ターゲットディレクトリの作成に失敗しました: {target_dir}")

    final_pdf_path = os.path.join(target_dir, f"{base_name}.pdf")

    # PDFファイルをターゲットの場所に移動
    shutil.move(temp_pdf_path, final_pdf_path)

    return final_pdf_path


# 画像をPDFに変換
@safe_file_operation
def convert_image_to_pdf(input_path: str, output_folder: str) -> str:
    """画像をPDFに変換します"""
    if not validate_file_path(input_path):
        raise FileNotFoundError(f"入力画像ファイルが存在しません: {input_path}")

    if not create_directory_safely(output_folder):
        raise ConvertToPdfError(f"出力フォルダの作成に失敗しました: {output_folder}")

    base_name = os.path.basename(input_path)
    pic_name, _ = os.path.splitext(base_name)

    # ターゲットディレクトリ構造を作成: output/ファイル名_pdf/ファイル名.pdf
    target_dir = os.path.join(output_folder, f"{pic_name}_pdf")
    if not create_directory_safely(target_dir):
        raise ConvertToPdfError(f"ターゲットディレクトリの作成に失敗しました: {target_dir}")

    output_path = os.path.join(target_dir, f"{pic_name}.pdf")

    try:
        # 画像の有効性を確認
        with Image.open(input_path) as img:
            # RGBモードに変換（必要な場合）
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            # 一時ファイルに保存
            temp_path = os.path.join(output_folder, f"temp_{pic_name}.jpg")
            img.save(temp_path, 'JPEG', quality=95)

            # PDFに変換
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert([temp_path]))

            # 一時ファイルを削除
            os.remove(temp_path)

    except Exception as e:
        raise ConvertToPdfError(f"画像からPDFへの変換エラー: {e}")

    return output_path
