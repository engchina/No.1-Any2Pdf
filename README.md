# No.1 Any2Pdf

## 1. WSL-Ubuntu のインストール

1. Ubuntu-22.04 をインストール（デフォルトでCドライブにインストールされます）

```
wsl.exe --install -d Ubuntu-22.04
```

2. Ubuntu-22.04 をエクスポート

```
wsl --export Ubuntu-22.04 D:\tmp\Ubuntu-22.04.tar
```

3. Ubuntu-22.04 を削除

```
wsl --unregister Ubuntu-22.04
```

4. Ubuntu-22.04 を `D:\VirtualPCs\Ubuntu-22.04` ディレクトリにインポート

```
wsl --import Ubuntu-22.04 D:\VirtualPCs\Ubuntu-22.04 D:\tmp\Ubuntu-22.04.tar
```

5. Ubuntu-22.04 にアクセス

```
wsl
```

6. Ubuntu-22.04 から退出

```
exit
```


7. （オプション）Ubuntu-22.04 をシャットダウン

```
wsl --shutdown
```

## 2. LibreOffice のインストール

パッケージソースを更新

```
sudo apt update && sudo apt upgrade
```

LibreOffice をインストール

```
apt install -y libreoffice
```

```
apt install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-ipafont fonts-takao fonts-wqy-microhei fonts-wqy-zenhei

# fonts-noto-cjk \      # 簡体字/繁体字中国語 + 日本語
# fonts-noto-cjk-extra \# 拡張文字セット
# fonts-ipafont \       # 日本語フォント補完
# fonts-takao \         # 日本語 Gothic（ゴシック体）と Mincho（明朝体）フォント
# fonts-wqy-microhei \  # 文泉驛簡体字
# fonts-wqy-zenhei      # 文泉驛繁体字
```

## 3. Conda のインストールと仮想環境の作成

1. Conda インストールスクリプトをダウンロード

```
cd /tmp
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

2. インストールスクリプトを実行し、プロンプトに従って操作。Conda の初期化を求められた際は "yes" を入力

```
bash Miniconda3-latest-Linux-x86_64.sh

---
Please, press ENTER to continue
>>> yes

Do you accept the license terms? [yes|no]
[no] >>> yes

Miniconda3 will now be installed into this location:
/root/miniconda3

  - Press ENTER to confirm the location
  - Press CTRL-C to abort the installation
  - Or specify a different location below

[/root/miniconda3] >>> ENTER

Do you wish the installer to initialize Miniconda3
by running conda init? [yes|no]
[no] >>> yes
---
```

3. インストール完了後、Conda を有効化

```
sudo su - root
```

4. （オプション）Conda を最新バージョンに更新

```
conda update conda
```

5. ユーザーログイン時に Conda の base 環境をデフォルトで有効化するかどうかを設定

Conda の base 環境をデフォルトで有効化したい場合：

```
conda config --set auto_activate_base true
```

Conda の base 環境をデフォルトで有効化したくない場合：

```
conda config --set auto_activate_base false
```

## 4. 依存関係のインストール

仮想環境を作成

```
conda create -n no.1-any2pdf python=3.12 -y
conda activate no.1-any2pdf
```

```
pip install -r requirements.txt
# pip list --format=freeze > requirements.txt
```

