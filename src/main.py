import os
import typing
from dotenv import load_dotenv 
from jira_client import JiraClinet
from models.search import JiraSearchResults
from models.ticket_create import JiraCreatedIssue
from models.attachment import JiraAttachment
from models.base import JiraIssueTypeEnum

# .env ファイルから環境変数をロード
load_dotenv()

def main():
    jira_base_url = os.environ.get('JIRA_BASE_URL')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    jira_project_key = os.environ.get('JIRA_PROJECT_KEY')
    # jira_assignee_account_id = os.environ.get('JIRA_ASSIGNEE_ACCOUNT_ID')
    print(jira_base_url, jira_email, jira_api_token, jira_project_key)

    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        print("エラー: 以下の環境変数が設定されていません。")
        print("JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY")
        print("スクリプトを実行する前に設定してください。")
        return

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

    created_ticket_key = None
    custom_fields_for_task = {
      "customfield_10140": {"value": "System Integration - Inoue"}
    }

    try:
        print(f"新しい '{JiraIssueTypeEnum.TASK.value}' チケットを作成します...")
        created_task_issue: JiraCreatedIssue = jira_client.create_ticket(
            project_key=jira_project_key,
            summary="test task ticket",
            description="このタスクはJira APIを使って自動的に作成されました。",
            issue_type=JiraIssueTypeEnum.TASK,
            # assignee_account_id=jira_assignee_account_id
            custom_fields=custom_fields_for_task
        )
        created_ticket_key = created_task_issue.key
        print(f"タスクが正常に作成されました: {created_task_issue.key} ({created_task_issue.self})")

        print(f"\n新しい '{JiraIssueTypeEnum.BUG.value}' チケットを作成します...")
        created_bug_issue: JiraCreatedIssue = jira_client.create_ticket(
            project_key=jira_project_key,
            summary="test bug ticket",
            description="詳細な手順と期待される動作、実際の結果を記載してください。",
            issue_type=JiraIssueTypeEnum.BUG,
            priority_name="Highest",
            custom_fields=custom_fields_for_task
        )
        created_ticket_key = created_bug_issue.key
        print(f"バグが正常に作成されました: {created_bug_issue.key} ({created_bug_issue.self})")

    except Exception as e:
        print(f"チケット作成中にエラーが発生しました: {e}")

    # --- 4. ファイルアップロードのデモンストレーション ---
    if created_ticket_key:
        print(f"\n--- 添付ファイルアップロードのデモンストレーション ({created_ticket_key}へ) ---")
        dummy_file_name = "sample_attachment.txt"
        with open(dummy_file_name, "w") as f:
            f.write("This is a test attachment from Python script (with Enum).\n")
            f.write(f"Timestamp: {os.times()}\n")

        try:
            print(f"ファイル '{dummy_file_name}' をチケット '{created_ticket_key}' にアップロードします...")
            uploaded_attachments: typing.List[JiraAttachment] = jira_client.upload_attachment(
                issue_key_or_id=created_ticket_key,
                file_path=dummy_file_name
            )
            for attachment in uploaded_attachments:
                print(f"添付ファイルのアップロードに成功しました: {attachment.filename} (ID: {attachment.id})")
        except FileNotFoundError as e:
            print(f"エラー: {e}")
        except Exception as e:
            print(f"添付ファイルのアップロード中にエラーが発生しました: {e}")
        finally:
            if os.path.exists(dummy_file_name):
                os.remove(dummy_file_name)
                print(f"テストファイル '{dummy_file_name}' を削除しました。")
    else:
        print("\nチケット作成に失敗したため、添付ファイルのアップロードはスキップされました。")

    # --- 5. チケット一覧取得のデモンストレーション ---
    print("\n--- チケット一覧取得のデモンストレーション ---")
    try:
        print(f"プロジェクト '{jira_project_key}' のチケット一覧を取得します...")
        search_results: JiraSearchResults = jira_client.get_tickets(
            project_key=jira_project_key,
            issue_type=JiraIssueTypeEnum.BUG,
            max_results=200
        )

        issues = search_results.issues
        total_count = search_results.total

        print(f"\n合計 {total_count} 件中、{len(issues)} 件のチケットが見つかりました。\n")

        if issues:
            for i, issue in enumerate(issues):
                key = issue.key
                summary = issue.fields.summary
                status_name = issue.fields.status.name
                assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'

                # print(f"チケット {i+1}: {key} - {summary} [ステータス: {status_name}, アサイン先: {assignee_name}], {issue.model_dump_json(indent=2)}")
        else:
            print("条件に一致するチケットは見つかりませんでした。")

    except Exception as e:
        print(f"チケット一覧の取得中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()