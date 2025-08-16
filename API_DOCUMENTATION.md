# PDF変換API ドキュメント

## 概要

このAPIは、Officeファイル（Word、PowerPoint、Excel）と画像ファイル（JPEG、PNG）をPDFファイルに変換する機能を提供します。

## ベースURL

```
http://localhost:5000
```

## 認証

現在のバージョンでは認証は不要です。

## エンドポイント一覧

### 1. ヘルスチェック

**エンドポイント:** `GET /api/health`

**説明:** APIサーバーの状態を確認します。

**リクエスト例:**
```bash
curl -X GET http://localhost:5000/api/health
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "APIサーバーは正常に動作しています",
  "timestamp": "2024-01-15T10:30:00.000000",
  "data": {
    "version": "1.0.0",
    "service": "PDF変換API",
    "status": "healthy"
  }
}
```

### 2. Officeファイル変換

**エンドポイント:** `POST /api/convert/office`

**説明:** OfficeファイルをPDFに変換し、変換されたPDFファイルを直接返します。

**サポートファイル形式:**
- `.docx` - Microsoft Word文書
- `.pptx` - Microsoft PowerPoint プレゼンテーション
- `.xlsx` - Microsoft Excel スプレッドシート
- `.doc` - Microsoft Word文書（旧形式）
- `.ppt` - Microsoft PowerPoint プレゼンテーション（旧形式）
- `.xls` - Microsoft Excel スプレッドシート（旧形式）

**リクエストパラメータ:**
- `file` (必須): アップロードするOfficeファイル

**リクエスト例:**
```bash
curl -X POST \
  http://localhost:5000/api/convert/office \
  -F "file=@document.docx"
```

**成功レスポンス:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="元のファイル名.pdf"`
- PDFファイルのバイナリデータ

### 3. 画像ファイル変換

**エンドポイント:** `POST /api/convert/image`

**説明:** 画像ファイルをPDFに変換し、変換されたPDFファイルを直接返します。

**サポートファイル形式:**
- `.jpg` - JPEG画像
- `.jpeg` - JPEG画像
- `.png` - PNG画像

**リクエストパラメータ:**
- `file` (必須): アップロードする画像ファイル

**リクエスト例:**
```bash
curl -X POST \
  http://localhost:5000/api/convert/image \
  -F "file=@image.jpg"
```

**成功レスポンス:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="元のファイル名.pdf"`
- PDFファイルのバイナリデータ

## エラーレスポンス

### 共通エラー形式

```json
{
  "success": false,
  "message": "エラーメッセージ",
  "timestamp": "2024-01-15T10:45:00.000000",
  "data": {}
}
```

### エラーコード一覧

| HTTPステータス | 説明 | 例 |
|---|---|---|
| 400 | 不正なリクエスト | ファイルが指定されていない、サポートされていないファイル形式 |
| 404 | リソースが見つからない | 無効なファイルID、ファイルが存在しない |
| 413 | ファイルサイズが大きすぎる | 50MBを超えるファイル |
| 500 | 内部サーバーエラー | 変換処理中のエラー |

### エラー例

**ファイルが指定されていない場合:**
```json
{
  "success": false,
  "message": "ファイルが指定されていません",
  "timestamp": "2024-01-15T10:50:00.000000",
  "data": {}
}
```

**サポートされていないファイル形式:**
```json
{
  "success": false,
  "message": "サポートされていないファイル形式です。許可される形式: docx, pptx, xlsx, doc, ppt, xls",
  "timestamp": "2024-01-15T10:55:00.000000",
  "data": {}
}
```

**ファイルサイズ制限超過:**
```json
{
  "success": false,
  "message": "ファイルサイズが制限（50MB）を超えています",
  "timestamp": "2024-01-15T11:00:00.000000",
  "data": {}
}
```

## 使用例

### Python（requests）を使用した例

```python
import requests

# ヘルスチェック
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Officeファイル変換
with open('document.docx', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/convert/office', files=files)
    
    if response.status_code == 200:
        # PDFファイルを直接保存
        with open('converted.pdf', 'wb') as pdf_file:
            pdf_file.write(response.content)
        print('変換完了！')
    else:
        print(f'エラー: {response.status_code}')
```

### JavaScript（fetch）を使用した例

```javascript
// ヘルスチェック
fetch('http://localhost:5000/api/health')
  .then(response => response.json())
  .then(data => console.log(data));

// 画像ファイル変換
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:5000/api/convert/image', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (response.ok) {
    return response.blob();
  } else {
    throw new Error('変換に失敗しました');
  }
})
.then(blob => {
  // PDFファイルを直接ダウンロード
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'converted_image.pdf';
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
})
.catch(error => {
  console.error('エラー:', error.message);
});
```

## 制限事項

- 最大ファイルサイズ: 50MB
- 同時変換数: 制限なし（ただし、サーバーリソースに依存）
- ファイル保存期間: サーバー再起動まで（永続化されません）
- 認証: 現在未実装

## 必要な依存関係

- LibreOffice（Officeファイル変換用）
- Python 3.11+
- Flask
- Pillow（画像処理用）
- img2pdf（画像からPDF変換用）

## サーバー起動方法

```bash
# 依存関係をインストール
pip install -r requirements.txt

# APIサーバーを起動
python run_api_server.py
```

## ログ

APIサーバーは以下の場所にログを出力します：
- コンソール出力
- `api_server.log` ファイル

ログレベル: INFO

## トラブルシューティング

### LibreOfficeが見つからない

**エラー:** `LibreOffice変換エラー`

**解決方法:** LibreOfficeをインストールし、`soffice`コマンドがPATHに含まれていることを確認してください。

### ファイル変換に失敗する

**原因:**
- ファイルが破損している
- サポートされていないファイル形式
- ディスク容量不足

**解決方法:**
- ファイルの整合性を確認
- サポートされているファイル形式を使用
- ディスク容量を確認

### メモリ不足エラー

**原因:** 大きなファイルの処理時にメモリが不足

**解決方法:**
- ファイルサイズを小さくする
- サーバーのメモリを増やす
- 同時処理数を制限する

---

**開発者:** Oracle Japan  
**バージョン:** 1.0.0  
**最終更新:** 2024年1月15日