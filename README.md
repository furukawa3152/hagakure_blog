# hagakure_blog

## これはなに
Wagtail 6/Django 4.2 で動く HAGAKUREプログラミング塾のブログサイト「Scroll」。和紙や巻物をモチーフにしたUIで、塾生が学びや気づきを気軽に共有できるようにする。

## コンセプト
### 全体方針・要件
- ユーザーフレンドリーな投稿環境  
  - 「ゆるさ」を重視した投稿システム  
  - スマートフォンからも簡単に投稿可能な設計  
  - 完成度よりも気軽さを優先した仕組み  
- 参加障壁の低減  
  - GitHubのような技術的ハードルを避ける  
  - Slackのように「皆に見られる」プレッシャーを軽減  
  - 「見に行かないと見られない」安心感のある空間設計  

### ポリシー
- かわいさやゆるさを出す
- 手書き風フォントの要素を加える
- 丸みを持たせる
- 隙間や余白を確保（詰め込みすぎない）
- 色数を抑える
- スマホ（iOS）アクセスを重視し、必ずレスポンシブ対応を用意

## 追加実装・カスタム箇所
- 認証: Google OAuth ホワイトリスト + 自動 Editors 付与（`adapters.py`, `mysite/settings/google_email_whitelist.py`, `mysite/settings/read_account_sheet.py`）
- 管理画面制御: Editors はブログ記事のみ作成可にするメニューカスタム（`blog/customize.py`, `blog/wagtail_hooks.py`）
- モデル/フォーム: ブログページ・タグ制約などの独自仕様（`blog/models.py`, `blog/forms.py`, `blog/blocks.py`）
- リアクション: IP 単位いいねカウントと重複防止（`blog/models.py`, `blog/views.py`, `blog/templates/blog/*.html`）
- 公開フック: Slack通知 + OpenAIレビュー + Google Sheet ログ（`blog/signals.py`, `blog/utils/openai_review.py`, `blog/utils/slack.py`, `blog/utils/sheet_logger.py`）
- UI: 巻物/和紙テーマのテンプレートとスタイル（`mysite/templates/*.html`, `blog/templates/blog/*.html`, `mysite/static/*`, `blog/static/*`）

## 追加済みの主要機能
- 認証・権限
  - Google OAuth（allauth）。許可メール一覧をGoogle Spreadsheetから読み込み、ホワイトリスト外は拒否（`adapters.py`）。
  - 許可されたユーザーは自動で`Editors`グループに参加。Editorsは管理画面でブログ記事以外を作れないよう制限（`blog/customize.py` / `blog/wagtail_hooks.py`）。
- コンテンツモデル
  - `HomePage`配下に`BlogIndexPage`、その子に`BlogPage`を作成する階層。
  - `BlogPage`にはサムネイル、チャンネル（スニペット）、タグ（最大4個・文字数制限）、本文StreamFieldを実装。
  - 本文ブロック: リッチテキスト（h2/h3/blockquote等）、Markdown（カスタムツールバー）、キャプション付き画像ブロック、コードブロック。
  - タイトルは26文字以内、スラッグは作成時にIDへ固定してURLの整合性を担保。
- 記事閲覧・検索
  - 一覧は公開日時降順で12件ずつページネート。タグスラッグとタグ名キーワードの両方でフィルタ可能（`BlogIndexPage.get_context`）。
  - 著者名/アバター、投稿日、タグバッジ、サムネイルを表示。OGP/Twitterカードを埋め込み。
- リアクション
  - IPアドレス単位での「いいね」を実装（重複防止付き、上限999）。非同期で `/like/<page_id>/` にPOSTし総数を更新。
- 通知・自動ログ
  - 公開時にSlackへ投稿通知＋OpenAIによる「HAGAKURE君」キャラのレビューを送信（`blog/signals.py` → `utils/openai_review.py` / `utils/slack.py`）。
  - 同時にGoogle Spreadsheet「log_for_x」に投稿者・タイトル・URL・AI要約（30文字以内）を追記（`utils/sheet_logger.py`）。重複投稿はスキップ。
- 画像まわり
  - Wagtail画像フォーマットを上書きし、altをキャプションにできる`captioned_image`と`no_caption_image`を用意（`blog/image_formats.py`）。
  - キャプション付き画像ブロックは`blog/templates/blocks/image_with_caption.html`で`<figure>`に出力。

## UI/デザインコンセプト
- テーマ: 巻物と和紙をベースにした和風トーン。「Scroll」ロゴや紐のモチーフで記事カードと本文を装飾。
- カラーパレット: 背景 #fefbf6、本文文字 #625651、アクセントに金色 #EDCF3B とピンク系のハート。
- タイポグラフィ: Google Fonts「Zen Maru Gothic」を全体で使用し、丸みのある親しみやすさを演出。
- レイアウト:
  - 一覧: 最大1040px幅の3カラム（レスポンシブで2/1カラムに切り替え）。カード上部に紐・巻物ヘッダを重ねる装飾。
  - 記事詳細: 巻物の布地背景＋和紙パネルの上にサムネイル、タグバッジ、日付、著者情報、本文を配置。下部に著者プロフィールと「いいね」を配置。
  - モバイル対応: 768px/470px/440pxブレークポイントで余白とカラム数を調整。

## セットアップ（ローカル開発）
1) Python 3.12 系を用意し、`pip install -r requirements.txt` を実行。  
2) ルートに `.env` か `env` を置き、少なくとも以下を設定  
   - `OPENAI_API_KEY`（Slack通知レビューとシート要約で使用）  
   - `SLACK_WEBHOOK_URL`（新規公開通知）  
   - GoogleサービスアカウントJSON: `mysite/settings/hagakurewagtailauth-fbf65e104bc8.json` を配置し、対象Spreadsheetにアクセス権を付与。  
3) `python manage.py migrate` でDB初期化、必要なら `createsuperuser`。  
4) `python manage.py runserver` で起動。  
   - Docker利用時は `docker build -t hagakure_blog .` → `docker run -p 8000:8000 hagakure_blog`。イメージ内で `collectstatic` と `migrate` が走る。  

## 運用時の補足
- Googleアカウントのホワイトリストは Spreadsheet で管理。変更すると次回ログインから即時反映（キャッシュなし）。
- Editors権限ユーザーはブログ記事以外のサブページ作成を不可にすることで運用ミスを防止。
- 本番ドメイン想定: `hagakurepgm.net`（`mysite/settings/production.py`）。`DEBUG` が True のため、リリース前に適宜変更すること。

## 主要ディレクトリ
- `blog/` … Wagtailページモデル、ビュー、シグナル、静的ファイル（一覧/詳細のCSS・JS・画像）。
- `home/` … サイトトップや各種LPテンプレート・静的アセット。
- `mysite/` … 設定、URL ルーティング、共通テンプレート（`base.html`、404/500、ガイドライン）。
- `media/` … 開発用のアップロード済み画像サンプル。
