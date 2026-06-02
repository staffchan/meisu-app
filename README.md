# 命数占い

GitHub Pages と Google Apps Script で公開する静的サイト版です。

## ファイル

- `index.html`: 画面
- `style.css`: 見た目
- `app.js`: 命数計算、結果表示、保存処理
- `data/`: 命数CSV、診断文章、画像
- `apps-script/Code.gs`: Googleスプレッドシートに保存するApps Script

## Google Apps Scriptの設定

1. 保存先のGoogleスプレッドシートを開く
   - 現在の保存先: `https://docs.google.com/spreadsheets/d/13PtolESY7maJJenTjgbMM8-AEW-wFkyoL7vRb-4sLyc/edit`
2. `拡張機能` → `Apps Script` を開く
3. `apps-script/Code.gs` の中身を貼り付ける
4. `SHEET_NAME` を保存先のシート名に合わせる
   - タブ名が `シート1` なら変更不要
5. `デプロイ` → `新しいデプロイ` を選ぶ
6. 種類は `ウェブアプリ`
7. 実行ユーザーは `自分`
8. アクセスできるユーザーは `全員`
9. デプロイ後に発行されるURLをコピーする
10. `app.js` の `APPS_SCRIPT_URL` にURLを入れる

## GitHub Pagesの公開

1. GitHubのリポジトリ設定を開く
2. `Pages` を開く
3. Sourceを `Deploy from a branch` にする
4. Branchを `main`、フォルダを `/root` にする
5. 保存する

## 注意

この版ではGoogleの秘密鍵を使いません。以前の `.streamlit/secrets.toml` に入っていた秘密鍵は、Google Cloud側で無効化して作り直してください。
