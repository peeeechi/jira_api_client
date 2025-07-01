import os
import sys # sys.path の操作のためにインポート
from dotenv import load_dotenv 
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
# プロジェクトのルートディレクトリのパスを取得 (例: /home/.../jira_api/)
project_root = os.path.dirname(src_dir)
# プロジェクトのルートディレクトリを sys.path に追加
if project_root not in sys.path:
    sys.path.insert(0, project_root) # 先頭に追加することで優先的に参照させる
from src.jira_client import JiraClinet # src を起点とした絶対パスでインポート
from src.models.ticket_create import JiraCreatedIssue # src を起点とした絶対パスでインポート
from src.models.base import JiraIssueTypeEnum # src を起点とした絶対パスでインポート

def run_create_ticket_example():
    """
    Jiraにチケットを作成する例を実行します。
    様々な課題タイプとカスタムフィールドの指定を含みます。
    """
    # --- 1. 環境変数からJiraの認証情報を読み込む ---
    jira_base_url = os.environ.get('JIRA_BASE_URL')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    jira_project_key = os.environ.get('JIRA_PROJECT_KEY')
    # jira_assignee_account_id = os.environ.get('JIRA_ASSIGNEE_ACCOUNT_ID')

    # 担当チームのカスタムフィールド情報
    # あなたのJira環境に合わせて実際のIDと値を確認・設定してください。
    # 例: "customfield_10140" が単一選択リストで、"test team" がそのオプションの場合
    team_field_id_for_create = "customfield_10140"
    team_name_for_create = "test team"

    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        print("エラー: 以下の環境変数が設定されていません。")
        print("JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY")
        print("スクリプトを実行する前に設定してください。")
        return

    # --- 2. JiraClient クラスの初期化 ---
    print("\n--- チケット作成のデモンストレーション ---")
    print("JiraClient を初期化しています...")
    try:
        jira_client = JiraClinet(
            base_url=jira_base_url,
            email=jira_email,
            token=jira_api_token
        )
        print("JiraClient の初期化に成功しました。")
    except Exception as e:
        print(f"JiraClient の初期化中にエラーが発生しました: {e}")
        return

    # --- 3. チケット作成の実行 ---
    try:
        # custom_fields 辞書を構築
        # "test team" が単一選択リストのオプションとして存在する場合を想定した形式
        custom_fields_for_task = {
            team_field_id_for_create: {"value": team_name_for_create}
        }
        # もし customfield_10140 が単なるテキストフィールドであれば、以下のように変更:
        # custom_fields_for_task = {
        #     team_field_id_for_create: team_name_for_create
        # }


        # 新しい 'Task' チケットを作成（カスタムフィールド指定あり）
        print(f"新しい '{JiraIssueTypeEnum.TASK.value}' チケットを作成します（担当チーム: {team_name_for_create}）...")
        created_task_issue: JiraCreatedIssue = jira_client.create_ticket(
            project_key=jira_project_key,
            summary="Pythonスクリプトから作成された新しいタスク（カスタムフィールド経由）",
            description="このタスクはJira APIを使って自動的に作成されました。",
            issue_type=JiraIssueTypeEnum.TASK,
            # assignee_account_id=jira_assignee_account_id,
            custom_fields=custom_fields_for_task
        )
        print(f"タスクが正常に作成されました: {created_task_issue.key} ({created_task_issue.self})")

        # 新しい 'Bug' チケットを作成（優先度も指定）
        print(f"\n新しい '{JiraIssueTypeEnum.BUG.value}' チケットを作成します...")
        created_bug_issue: JiraCreatedIssue = jira_client.create_ticket(
            project_key=jira_project_key,
            summary="Pythonスクリプトから作成されたバグ: ○○機能が動作しない",
            description="詳細な手順と期待される動作、実際の結果を記載してください。",
            issue_type=JiraIssueTypeEnum.BUG,
            priority_name="Highest"
        )
        print(f"バグが正常に作成されました: {created_bug_issue.key} ({created_bug_issue.self})")

        # もしJiraインスタンスに'Story'課題タイプがあるなら
        if JiraIssueTypeEnum.STORY in JiraIssueTypeEnum:
            print(f"\n新しい '{JiraIssueTypeEnum.STORY.value}' チケットを作成します...")
            created_story_issue: JiraCreatedIssue = jira_client.create_ticket(
                project_key=jira_project_key,
                summary="Enumを使って作成された新しいストーリー",
                description="自動化されたストーリー作成のテストです。",
                issue_type=JiraIssueTypeEnum.STORY
            )
            print(f"ストーリーが正常に作成されました: {created_story_issue.key} ({created_story_issue.self})")

    except Exception as e:
        print(f"チケット作成中にエラーが発生しました: {e}")

if __name__ == "__main__":
  run_create_ticket_example()