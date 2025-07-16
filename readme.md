# Jira API Client (jira_api_client)

## 概要

`jira_api_client` は、Python で Jira REST API と連携するためのシンプルで堅牢なクライアントライブラリです。Pydantic を利用した厳密なデータ型定義、環境変数によるセキュアな認証情報管理、およびモジュール化された構造により、Jira との連携を効率的かつ安全に実装できます。

## 特徴

* **Pydantic を利用した強力な型チェック**: Jira API レスポンスの複雑な JSON 構造を、扱いやすい Python オブジェクトに自動変換し、データアクセス時のタイプミスやエラーを軽減します。
* **セキュアな認証情報管理**: Jira のベースURL、メールアドレス、APIトークンなどの機密情報を環境変数から読み込み、コードにハードコードするリスクを排除します。
* **柔軟なチケット操作**:
    * プロジェクト、課題タイプ、担当者、ステータスでフィルタリング可能な**チケット一覧取得**。
    * 標準フィールド（要約、説明、課題タイプ、アサイン先、優先度）および**動的なカスタムフィールド**を指定した**チケット作成**。
    * 既存のチケットへの**ファイルアップロード**。
* **明確なモジュール構造**:
    * `src/jira_client.py`: Jira API との通信ロジックをカプセル化。
    * `src/models/`: Jira API のデータ構造に対応する Pydantic モデルと共通の Enum を定義。
    * `src/examples/`: 各機能の具体的な使用方法を示すサンプルスクリプトを提供。
* **高い再利用性**: Python パッケージとして設計されており、`pip` の VCS 連携機能や Git submodule として他のプロジェクトに簡単に組み込むことが可能です。
* **開発者体験の向上**: VS Code などでのコード補完やホバー時のドキュメント表示により、開発効率を高めます。

## プロジェクト構造

jira_api_client/
├── docs/                           # ドキュメンテーション関連ファイル
│   └── project_structure.puml      # PlantUML 図
├── src/                            # ソースコード
│   ├── models/                     # Pydantic モデル定義
│   │   ├── init.py
│   │   ├── attachment.py           # 添付ファイル関連モデル
│   │   ├── base.py                 # 共通基底モデル (User, Status, Enumなど)
│   │   ├── issue.py                # 課題 (Issue) 関連モデル
│   │   ├── search.py               # 検索結果関連モデル
│   │   └── ticket_create.py        # チケット作成関連モデル
│   ├── examples/                   # 使用例スクリプト
│   │   ├── init.py
│   │   ├── get_tickets.py          # チケット取得例
│   │   ├── create_ticket.py        # チケット作成例
│   │   └── upload_attachment.py    # ファイルアップロード例
│   ├── jira_client.py              # Jira API クライアントクラス
│   └── init.py                 # src パッケージの初期化ファイル
├── .env.example                    # 環境変数のサンプルファイル
├── pyproject.toml                  # Pythonパッケージ設定 (プロジェクト名, 依存関係など)
└── README.md                       # このファイル
└── LICENSE                         # ライセンス情報

## セットアップ

### 前提条件

* Python 3.9 以上
* `pip` (Python のパッケージインストーラ)
* Jira アカウントと Jira REST API へのアクセス権限
* Jira API トークン (Jira Cloud の場合)

### 依存関係のインストール

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
pip install -r requirements.txt
# または pyproject.toml を使って
# pip install .
```

requirements.txt がない場合は、pyproject.toml の dependencies セクションにあるライブラリを手動でインストールしてください。
`pip install requests pydantic python-dotenv`
