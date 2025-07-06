# 標準ライブラリのインポート
import gradio as gr
import os

# ローカルアプリケーションのインポート
from .css import custom_css
from .pdf_converter import (
    convert_office_file_to_pdf, convert_image_to_pdf
)


def create_app():
    """Gradioアプリケーションインスタンスを作成して返す"""

    # 中国語、日本語、英語フォントをサポートするカスタムテーマを作成
    theme = gr.themes.Default(
        spacing_size="sm",
        font=["Noto Sans SC", "Noto Sans JP", "Roboto", "Arial", "sans-serif"]
    )

    with gr.Blocks(title="会議記録チェックシステム", css=custom_css, theme=theme) as demo:
        gr.Markdown("# RAG精度あげたろう - 前処理", elem_classes="main_Header")
        gr.Markdown(value="### PDFをMarkdownへ変換するツール",
                    elem_classes="sub_Header")

        with gr.Tabs():
            # 新しいタブページ：ファイルをPDF変換器
            with gr.TabItem("ファイルをPDFに変換"):
                # 2列レイアウト
                with gr.Row():
                    # 左列：ファイルアップロードとコントロール
                    with gr.Column(scale=1):
                        # ファイルアップロード領域
                        file_input = gr.File(label="Officeファイルまたは画像をアップロード",
                                             file_types=[".docx", ".pptx", ".xlsx", ".doc", ".ppt", ".xls", ".jpg",
                                                         ".jpeg", ".png"])

                        # ボタンとログのレイアウト
                        with gr.Row():
                            convert_file_btn = gr.Button("➡️ 変換開始", variant="secondary")

                    # 右列：出力とステータス
                    with gr.Column(scale=3):
                        # ステータス表示
                        status_output = gr.Textbox(
                            label="変換ステータス",
                            lines=8,
                            max_lines=8,
                            interactive=False,
                            container=False,
                            placeholder="変換ステータスがここに表示されます..."
                        )

                        # ダウンロードリンク
                        download_link = gr.File(
                            label="PDFファイルをダウンロード",
                            visible=False,
                            interactive=False,
                            container=False
                        )

                        # ファイル変換を処理する関数

                def convert_file(file):
                    """アップロードされたファイルをPDFに変換する"""
                    if not file:
                        return "まずファイルをアップロードしてください", None

                    try:
                        # ファイルパスを取得
                        file_path = file.name
                        os.makedirs("output", exist_ok=True)
                        output_dir = "output"

                        # ファイルタイプを判定して変換
                        file_extension = file_path.lower().split('.')[-1]
                        if file_extension in ['docx', 'pptx', 'xlsx']:
                            # Officeファイルを変換
                            pdf_path = convert_office_file_to_pdf(file_path, output_dir)
                            status = f"✅ 変換成功\n\nファイルタイプ: Officeファイル (.{file_extension})\n出力パス: {pdf_path}\n\n変換完了、PDFファイルをダウンロードできます。"
                        elif file_extension in ['jpg', 'jpeg', 'png']:
                            # 画像を変換
                            pdf_path = convert_image_to_pdf(file_path, output_dir)
                            status = f"✅ 変換成功\n\nファイルタイプ: 画像ファイル (.{file_extension})\n出力パス: {pdf_path}\n\n変換完了、PDFファイルをダウンロードできます。"
                        else:
                            return "❌ 変換失敗\n\nエラー原因: サポートされていないファイルタイプ\nサポート形式: Officeファイル(.docx, .pptx, .xlsx)と画像(.jpg, .jpeg, .png)", None

                        # PDFをダウンロード可能にする
                        return status, gr.DownloadButton(value=pdf_path, label="PDFをダウンロード", visible=True)

                    except Exception as e:
                        return f"❌ 変換失敗\n\nエラー情報: {str(e)}", None

                # ボタンクリックイベントを設定
                convert_file_btn.click(
                    fn=convert_file,
                    inputs=file_input,
                    outputs=[status_output, download_link]
                )

        gr.Markdown(
            value="### 本ソフトウェアは検証評価用です。日常利用のための基本機能は備えていない点につきましてご理解をよろしくお願い申し上げます。",
            elem_classes="sub_Header")
        gr.Markdown(value="### Developed by Oracle Japan", elem_classes="sub_Header")

    return demo


def main():
    """アプリケーションを起動するメイン関数"""
    app = create_app()

    app.queue()
    app.launch()


if __name__ == "__main__":
    main()
