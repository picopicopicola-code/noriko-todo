# のりこ Todo アプリ

スマホ・PC両対応のTodoアプリです。

---

## ✅ 機能一覧

- タスクの追加・編集・削除・完了
- カテゴリ分け（Niere / Misfits / ウェブフリ など）
- 優先度設定（高・中・低）
- 期限日設定
- タグ機能
- メモ機能
- スマホ対応デザイン

---

## 🚀 STEP 1：Macでローカル起動する

### 1-1. Claude Codeを開く

ターミナルまたはClaude Codeで、このフォルダを開きます。

### 1-2. Claude Codeに以下を貼り付けて送信

```
このフォルダのTodoアプリをセットアップして起動してください。
Pythonの仮想環境を作って、requirements.txtをインストールして、
uvicornでapp.pyを起動してください。
```

### 1-3. ブラウザで開く

Claude Codeが起動したら、ブラウザで以下にアクセス：

```
http://localhost:8000
```

### 1-4. スマホからアクセスする（同じWi-Fi内）

1. Macのターミナルで以下を入力してMacのIPアドレスを確認：
   ```
   ipconfig getifaddr en0
   ```
2. 表示されたIPアドレス（例：192.168.1.5）を使って、スマホのブラウザで：
   ```
   http://192.168.1.5:8000
   ```
   ※ ポート番号8000を変えた場合はそちらを使ってください

---

## 🌐 STEP 2：Railwayで外出先からも使えるようにする

### 2-1. GitHubにアップロードする

1. [GitHub](https://github.com) にアカウント作成（すでにある場合はスキップ）
2. 「New repository」をクリック
3. Repository name に `noriko-todo` と入力
4. 「Create repository」をクリック
5. Claude Codeに以下を貼り付け：

```
このフォルダをGitHubにアップロードしてください。
リポジトリURLは [GitHubで作ったURL] です。
```

### 2-2. Railwayにデプロイする

1. [railway.app](https://railway.app) にアクセス
2. 「Login with GitHub」でログイン
3. 「New Project」→「Deploy from GitHub repo」をクリック
4. `noriko-todo` を選択
5. 自動でデプロイが始まります（2〜3分待つ）
6. 完了したら「Settings」→「Domains」→「Generate Domain」をクリック
7. 表示されたURL（例：`noriko-todo-xxx.railway.app`）でどこからでもアクセス可能！

### 2-3. スマホのホーム画面に追加する（アプリっぽくする）

**iPhoneの場合：**
1. Safariでアプリを開く
2. 下の「共有」ボタン（四角から矢印が出てるアイコン）をタップ
3. 「ホーム画面に追加」をタップ
4. 「追加」をタップ

これでアプリアイコンとしてホーム画面に追加されます！

---

## ❓ よくある質問

### Q: データはどこに保存されますか？
A: `todo.db` というファイルに保存されます。このファイルを削除するとデータも消えます。

### Q: カテゴリを追加したい
A: Claude Codeに「カテゴリに〇〇を追加して」と伝えてください。

### Q: エラーが出た
A: Claude Codeにエラーメッセージをそのまま貼り付けて「直して」と伝えてください。

---

## 📁 ファイル構成

```
todo-app/
├── app.py          # サーバーのメインファイル
├── database.py     # データベース操作
├── requirements.txt # 必要なライブラリ一覧
├── Procfile        # Railway用設定
├── railway.json    # Railway用設定
├── static/
│   └── index.html  # 画面（UI）
└── README.md       # この説明書
```
