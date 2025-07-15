import os

import json
import sys
from dotenv import load_dotenv 
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from src.jira_client import JiraClinet
from src.models.search import JiraSearchResults
from src.models.base import JiraIssueTypeEnum, JiraStatusNameEnum

def run_get_tickets_example():
    """
    Jiraからチケット一覧を取得する例を実行します。
    プロジェクト、課題タイプ、担当者、ステータスでフィルタリングします。
    """
    # --- 1. 環境変数からJiraの認証情報を読み込む ---
    jira_base_url = os.environ.get('JIRA_BASE_URL')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    jira_project_key = os.environ.get('JIRA_PROJECT_KEY')
    jira_assignee_account_id = os.environ.get('JIRA_ASSIGNEE_ACCOUNT_ID')

    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        print("エラー: 以下の環境変数が設定されていません。")
        print("JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY")
        print("スクリプトを実行する前に設定してください。")
        return

    # --- 2. JiraClient クラスの初期化 ---
    print("\n--- チケット取得のデモンストレーション ---")
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

    # --- チケット一覧取得のデモンストレーション ---
    try:
        # 全ての課題タイプと担当者のチケットを取得
        print(f"\n--- プロジェクト '{jira_project_key}' のチケット一覧を取得します（全タイプ・全担当者・全ステータス）。")
        search_results_all: JiraSearchResults = jira_client.get_tickets(
            project_key=jira_project_key,
            max_results=5
        )
        issues_all = search_results_all.issues
        total_count_all = search_results_all.total
        print(f"\n合計 {total_count_all} 件中、{len(issues_all)} 件のチケットが見つかりました（全タイプ・全担当者・全ステータス）。\n")
        if issues_all:
            for i, issue in enumerate(issues_all):
                key = issue.key
                summary = issue.fields.summary
                status_name = issue.fields.status.name
                assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'
                issue_type_name = issue.fields.issuetype.name
                print(f"チケット {i+1}: {key} - {summary} [タイプ: {issue_type_name}, ステータス: {status_name}, アサイン先: {assignee_name}]")
        else:
            print("条件に一致するチケットは見つかりませんでした。")

        # Bug チケットのみ取得するデモンストレーション
        print(f"\n--- プロジェクト '{jira_project_key}' の '{JiraIssueTypeEnum.BUG.value}' チケットのみ取得します ---")
        search_results_bugs: JiraSearchResults = jira_client.get_tickets(
            project_key=jira_project_key,
            issue_type=JiraIssueTypeEnum.BUG,
            max_results=5
        )
        # print(json.dumps(search_results_bugs.issues, indent=2))

        for issue in search_results_bugs.issues:
            # print(issue.model_dump_json(indent=2))
            print(issue.fields.description.to_plain_text())

        issues_bugs = search_results_bugs.issues
        total_count_bugs = search_results_bugs.total
        print(f"\n合計 {total_count_bugs} 件中、{len(issues_bugs)} 件の '{JiraIssueTypeEnum.BUG.value}' チケットが見つかりました。\n")
        if issues_bugs:
            for i, issue in enumerate(issues_bugs):
                key = issue.key
                summary = issue.fields.summary
                status_name = issue.fields.status.name
                assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'
                issue_type_name = issue.fields.issuetype.name
                print(f"Bug チケット {i+1}: {key} - {summary} [タイプ: {issue_type_name}, ステータス: {status_name}, アサイン先: {assignee_name}]")
        else:
            print("条件に一致する 'Bug' チケットは見つかりませんでした。")

        # 特定の担当者のみ取得するデモンストレーション
        if jira_assignee_account_id:
            print(f"\n--- プロジェクト '{jira_project_key}' の特定担当者 ({jira_assignee_account_id}) のチケットのみ取得します ---")
            search_results_assignee: JiraSearchResults = jira_client.get_tickets(
                project_key=jira_project_key,
                assignee_account_id=jira_assignee_account_id,
                max_results=5
            )
            issues_assignee = search_results_assignee.issues
            total_count_assignee = search_results_assignee.total
            print(f"\n合計 {total_count_assignee} 件中、{len(issues_assignee)} 件のチケットが見つかりました（担当者指定）。\n")
            if issues_assignee:
                for i, issue in enumerate(issues_assignee):
                    key = issue.key
                    summary = issue.fields.summary
                    status_name = issue.fields.status.name
                    assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'
                    issue_type_name = issue.fields.issuetype.name
                    print(f"担当者チケット {i+1}: {key} - {summary} [タイプ: {issue_type_name}, ステータス: {status_name}, アサイン先: {assignee_name}]")
            else:
                print(f"条件に一致する担当者 ({jira_assignee_account_id}) のチケットは見つかりませんでした。")
        else:
            print("\nJIRA_ASSIGNEE_ACCOUNT_ID が設定されていないため、担当者によるフィルタリングはスキップされました。")

        # 特定のステータスのチケットのみ取得するデモンストレーション
        # あなたのJiraStatusNameEnumに合わせたステータス名を使用してください
        if JiraStatusNameEnum.IN_PROGRESS in JiraStatusNameEnum: # Enumに存在するか確認
            print(f"\n--- プロジェクト '{jira_project_key}' の '{JiraStatusNameEnum.IN_PROGRESS.value}' ステータスのチケットのみ取得します ---")
            search_results_status: JiraSearchResults = jira_client.get_tickets(
                project_key=jira_project_key,
                status_name=JiraStatusNameEnum.IN_PROGRESS,
                max_results=5
            )
            issues_status = search_results_status.issues
            total_count_status = search_results_status.total
            print(f"\n合計 {total_count_status} 件中、{len(issues_status)} 件の '{JiraStatusNameEnum.IN_PROGRESS.value}' チケットが見つかりました。\n")
            if issues_status:
                for i, issue in enumerate(issues_status):
                    key = issue.key
                    summary = issue.fields.summary
                    status_name = issue.fields.status.name
                    assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'
                    issue_type_name = issue.fields.issuetype.name
                    print(f"ステータス'{JiraStatusNameEnum.IN_PROGRESS.value}'チケット {i+1}: {key} - {summary} [タイプ: {issue_type_name}, ステータス: {status_name}, アサイン先: {assignee_name}]")
            else:
                print(f"条件に一致する '{JiraStatusNameEnum.IN_PROGRESS.value}' チケットは見つかりませんでした。")
        else:
            print(f"\nJiraStatusNameEnum に '{JiraStatusNameEnum.IN_PROGRESS.value}' が定義されていないため、このフィルタリングはスキップされました。")

        # 課題タイプ、担当者、ステータスの複合フィルタリングのデモンストレーション
        if jira_assignee_account_id and JiraStatusNameEnum.IN_PROGRESS in JiraStatusNameEnum: # 両方存在するか確認
            print(f"\n--- プロジェクト '{jira_project_key}' の '{JiraStatusNameEnum.IN_PROGRESS.value}' ステータスで、担当者 ({jira_assignee_account_id}) にアサインされた '{JiraIssueTypeEnum.BUG.value}' チケットのみ取得します ---")
            search_results_complex: JiraSearchResults = jira_client.get_tickets(
                project_key=jira_project_key,
                issue_type=JiraIssueTypeEnum.BUG,
                assignee_account_id=jira_assignee_account_id,
                status_name=JiraStatusNameEnum.IN_PROGRESS,
                max_results=5
            )
            issues_complex = search_results_complex.issues
            total_count_complex = search_results_complex.total
            print(f"\n合計 {total_count_complex} 件中、{len(issues_complex)} 件の複合条件チケットが見つかりました。\n")
            if issues_complex:
                for i, issue in enumerate(issues_complex):
                    key = issue.key
                    summary = issue.fields.summary
                    status_name = issue.fields.status.name
                    assignee_name = issue.fields.assignee.displayName if issue.fields.assignee else '未アサイン'
                    issue_type_name = issue.fields.issuetype.name
                    print(f"複合条件チケット {i+1}: {key} - {summary} [タイプ: {issue_type_name}, ステータス: {status_name}, アサイン先: {assignee_name}]")
            else:
                print(f"条件に一致する複合条件チケットは見つかりませんでした。")
        else:
            print("\n複合フィルタリングの条件が満たされていないため、このデモンストレーションはスキップされました。")


    except Exception as e:
        print(f"チケット一覧の取得中にエラーが発生しました: {e}")

if __name__ == "__main__":
    load_dotenv()
    run_get_tickets_example()