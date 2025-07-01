import os
import sys # sys.path の操作のためにインポート
import typing
from dotenv import load_dotenv 
current_script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_script_path)
src_dir = os.path.dirname(current_dir) # src/examples の一つ上が src
project_root = os.path.dirname(src_dir) # src の一つ上がプロジェクトルート

if project_root not in sys.path:
    sys.path.insert(0, project_root)
from src.jira_client import JiraClinet # src を起点とした絶対パスでインポート
from src.models.attachment import JiraAttachment # src を起点とした絶対パスでインポート

def run_upload_attachment_example():
    """
    Jiraチケットにファイルをアップロードする例を実行します。
    """
    # --- 1. 環境変数からJiraの認証情報を読み込む ---
    jira_base_url = os.environ.get('JIRA_BASE_URL')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    # ファイルを添付する既存のチケットのキー
    # !!!!!!! ここを実際に存在するチケットキーに置き換えてください !!!!!!!
    target_issue_key = os.environ.get('JIRA_TARGET_ISSUE_KEY_FOR_ATTACHMENT')

    if not all([jira_base_url, jira_email, jira_api_token, target_issue_key]):
        print("エラー: 以下の環境変数が設定されていません。")
        print("JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_TARGET_ISSUE_KEY_FOR_ATTACHMENT")
        print("スクリプトを実行する前に、ファイルを添付したい既存のチケットキーを設定してください。")
        return

    # --- 2. JiraClient クラスの初期化 ---
    print("\n--- 添付ファイルアップロードのデモンストレーション ---")
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

    # --- 3. ファイルアップロードの実行 ---
    # テスト用のダミーファイルを作成
    dummy_file_name = "sample_attachment.txt"
    try:
        with open(dummy_file_name, "w") as f:
            f.write("This is a test attachment from Python script.\n")
            f.write(f"Timestamp: {os.times()}\n")

        print(f"ファイル '{dummy_file_name}' をチケット '{target_issue_key}' にアップロードします...")
        uploaded_attachments: typing.List[JiraAttachment] = jira_client.upload_attachment(
            issue_key_or_id=target_issue_key,
            file_path=dummy_file_name
        )
        for attachment in uploaded_attachments:
            print(f"添付ファイルのアップロードに成功しました: {attachment.filename} (ID: {attachment.id})")
    except FileNotFoundError as e:
        print(f"エラー: {e}")
    except Exception as e:
        print(f"添付ファイルのアップロード中にエラーが発生しました: {e}")
    finally:
        # テストファイルをクリーンアップ
        if os.path.exists(dummy_file_name):
            os.remove(dummy_file_name)
            print(f"テストファイル '{dummy_file_name}' を削除しました。")

if __name__ == "__main__":
  load_dotenv()
  run_upload_attachment_example()