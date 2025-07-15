import os
import sys
import requests
import typing
import json
import base64
import os.path
from pydantic import ValidationError

# sys.path の設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.base import JiraIssueTypeEnum, JiraStatusNameEnum
from src.models.search import JiraSearchResults
from src.models.ticket_create import JiraCreatedIssue
from src.models.attachment import JiraAttachment

class JiraClinet(object):
    """
    Jira REST API と通信するためのクライアントクラス。

    環境変数から認証情報を取得するのではなく、
    インスタンス化時に直接ベースURL、メールアドレス、APIトークンを受け取ります。
    """

    __headers: typing.Dict[str, typing.Any]
    __base_url: str

    def __init__(self, base_url: str, email: str, token: str):
        """
        JiraClinet の新しいインスタンスを初期化します。

        Args:
            base_url (str): Jira REST APIのベースURL (例: 'https://your-company.atlassian.net/rest/api/3/').
                            末尾にスラッシュがあってもなくても対応します。
            email (str): Jiraアカウントのメールアドレス。
            token (str): Jiraで生成されたAPIトークン。
        """
        self.__base_url = base_url

        auth_string = f"{email}:{token}"
        encoded_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        self.__headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_auth_string}"
        }
        self.__upload_headers = {
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check", # 添付ファイルアップロードには必須
            "Authorization": f"Basic {encoded_auth_string}"
        }


    def get_tickets(
        self,
        project_key: str,
        issue_type: typing.Optional[JiraIssueTypeEnum] = None,
        assignee_account_id: typing.Optional[str] = None,
        status_name: typing.Optional[JiraStatusNameEnum] = None,
        max_results: int = 100,
        start_at: int = 0
    ) -> JiraSearchResults:
        """
        Jiraから特定のプロジェクトのチケット一覧を取得します。
        オプションで課題タイプおよび担当者によるフィルタリングも可能です。

        Args:
            project_key (str): 取得したいチケットが属するJiraプロジェクトのキー (例: 'PROJ')。
            issue_type (JiraIssueTypeEnum, optional): 取得したい課題のタイプ (例: JiraIssueTypeEnum.BUG)。
                                                    指定しない場合、すべての課題タイプが取得されます。
            assignee_account_id (str, optional): フィルタしたい担当者のaccountId。
                                                 指定しない場合、担当者でフィルタしません。
            status_name (str, optional): フィルタしたいステータスの表示名 (例: '完了', 'In Progress')。
                                         指定しない場合、ステータスでフィルタしません。
            max_results (int): 取得するチケットの最大数 (デフォルト: 100)。
                               Jira APIの制限により、最大値は1000など異なる場合があります。
            start_at (int): 取得を開始するチケットのオフセット (ページネーション用、デフォルト: 0)。

        Returns:
            JiraSearchResults: Jira APIからの検索結果を表すPydanticオブジェクト。
                               total (合計数) と issues (課題リスト) を含みます。

        Raises:
            requests.exceptions.RequestException: リクエスト中にネットワークまたはHTTPエラーが発生した場合。
            json.JSONDecodeError: Jira APIからのレスポンスが有効なJSONでない場合。
            pydantic.ValidationError: レスポンスJSONが定義されたPydanticモデルの構造と一致しない場合。
            Exception: その他の予期せぬエラーが発生した場合。
        """
        jql_parts = [f'project = "{project_key}"'] # JQLクエリの部品リスト

        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type.value}"')

        if assignee_account_id:
            # アカウントIDでフィルタするのが最も確実です
            jql_parts.append(f'assignee = "{assignee_account_id}"')
            # もしログインユーザーにアサインされているチケットをフィルタしたい場合は
            # jql_parts.append('assignee = currentUser()')

        if status_name: # <-- ステータス名でフィルタリングする条件を追加
            jql_parts.append(f'status = "{status_name.value}"')

        jql_query = ' AND '.join(jql_parts) # AND で結合
        jql_query += ' ORDER BY created DESC' # ソート順序は維持

        params = {
            "jql": jql_query,
            "maxResults": max_results,
            "startAt": start_at,
        }
        search_endpoint = os.path.join(self.__base_url, "search")

        try:
            response = requests.get(search_endpoint, headers=self.__headers, params=params)
            response.raise_for_status()

            data = response.json()
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return JiraSearchResults(**data)
        except requests.exceptions.RequestException as err:
            print(f"Jira API 'search' リクエストエラー: {err}")
            if hasattr(err, 'response') and err.response is not None:
                print(f"レスポンス詳細: {err.response.text}")
            raise
        except json.JSONDecodeError as e:
            print(f"Jira API 'search' レスポンスのJSONデコードに失敗しました: {e}")
            print(f"レスポンステキスト: {response.text if 'response' in locals() else 'レスポンスなし'}")
            raise
        except ValidationError as e:
            print(f"Jira API 'search' Pydanticバリデーションエラー: {e}")
            print(f"エラー詳細: {e.errors()}")
            raise
        except Exception as e:
            print(f"Jira API 'search' 予期せぬエラー: {e}")
            raise


    def create_ticket(
        self,
        project_key: str,
        summary: str,
        description: typing.Optional[str] = None,
        issue_type: JiraIssueTypeEnum = JiraIssueTypeEnum.TASK,
        assignee_account_id: typing.Optional[str] = None,
        priority_name: typing.Optional[str] = None,
        custom_fields: typing.Optional[typing.Dict[str, typing.Any]] = None # <-- 新しい引数
    ) -> JiraCreatedIssue:
        """
        Jiraに新しいチケットを作成します。

        Args:
            project_key (str): チケットを作成するプロジェクトのキー (例: 'PROJ')。
            summary (str): チケットの要約（タイトル）。
            description (str, optional): チケットの説明。デフォルトはNone。
            issue_type (JiraIssueTypeEnum): 作成するチケットの課題タイプ。JiraIssueTypeEnumから選択。
                                           デフォルトは 'Task'。
            assignee_account_id (str, optional): チケットをアサインするユーザーのaccountId。
                                                 デフォルトはNone（アサインなし）。
            priority_name (str, optional): チケットの優先度名 (例: 'High', 'Low')。
                                           デフォルトはNone。
            custom_fields (Dict[str, Any], optional): 設定したいカスタムフィールドの辞書。
                                                     キーはカスタムフィールドのID (例: 'customfield_10140')、
                                                     値はそのフィールドに設定する値。
                                                     値の形式はカスタムフィールドのタイプによって異なります。
                                                     例: {"customfield_10140": {"value": "test team"}}
                                                     例: {"customfield_10141": "Some text"}

        Returns:
            JiraCreatedIssue: 作成されたチケットのID、キー、URLを含むPydanticオブジェクト。

        Raises:
            requests.exceptions.RequestException: リクエスト中にネットワークまたはHTTPエラーが発生した場合。
            json.JSONDecodeError: Jira APIからのレスポンスが有効なJSONでない場合。
            pydantic.ValidationError: レスポンスJSONが定義されたPydanticモデルの構造と一致しない場合。
            Exception: その他の予期せぬエラーが発生した場合。
        """
        create_endpoint = os.path.join(self.__base_url, "issue")

        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "issuetype": {
                    "name": issue_type.value
                }
            }
        }
        if description:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
        if assignee_account_id:
            payload["fields"]["assignee"] = {
                "accountId": assignee_account_id
            }
        if priority_name:
            payload["fields"]["priority"] = {
                "name": priority_name
            }

        # --- カスタムフィールドをペイロードに追加 ---
        if custom_fields:
            for field_id, field_value in custom_fields.items():
                payload["fields"][field_id] = field_value
                # 注意: field_value の形式はカスタムフィールドのタイプに厳密に依存します。
                # 例: 単一選択リストの場合: {"value": "オプション名"}
                # 例: テキストフィールドの場合: "テキスト値"
                # 例: 複数選択リストの場合: [{"value": "オプション1"}, {"value": "オプション2"}]
                # 例: ユーザーピッカーの場合: {"accountId": "ユーザーID"}

        try:
            response = requests.post(create_endpoint, headers=self.__headers, data=json.dumps(payload))
            response.raise_for_status()

            data = response.json()
            return JiraCreatedIssue(**data)
        except requests.exceptions.RequestException as err:
            print(f"Jira API 'create_ticket' リクエストエラー: {err}")
            if hasattr(err, 'response') and err.response is not None:
                print(f"レスポンス詳細: {err.response.text}")
            raise
        except json.JSONDecodeError as e:
            print(f"Jira API 'create_ticket' レスポンスのJSONデコードに失敗しました: {e}")
            print(f"レスポンステキスト: {response.text if 'response' in locals() else 'レスポンスなし'}")
            raise
        except ValidationError as e:
            print(f"Jira API 'create_ticket' Pydanticバリデーションエラー: {e}")
            print(f"エラー詳細: {e.errors()}")
            raise
        except Exception as e:
            print(f"Jira API 'create_ticket' 予期せぬエラー: {e}")
            raise

    def upload_attachment(self, issue_key_or_id: str, file_path: str, filename: typing.Optional[str] = None) -> typing.List[JiraAttachment]:
        """
        指定されたJiraチケットにファイルをアップロードします。

        Args:
            issue_key_or_id (str): ファイルを添付するJiraチケットのキーまたはID (例: 'PROJ-123', '10000')。
            file_path (str): アップロードするローカルファイルのパス。
            filename (str, optional): Jiraに表示されるファイル名。指定しない場合、file_pathから自動抽出。

        Returns:
            typing.List[JiraAttachment]: アップロードされた添付ファイルの情報を表すPydanticオブジェクトのリスト。
                                         通常は1つのファイルに対して1つのオブジェクト。

        Raises:
            FileNotFoundError: 指定されたファイルパスにファイルが存在しない場合。
            requests.exceptions.RequestException: リクエスト中にネットワークまたはHTTPエラーが発生した場合。
            json.JSONDecodeError: Jira APIからのレスポンスが有効なJSONでない場合。
            pydantic.ValidationError: レスポンスJSONが定義されたPydanticモデルの構造と一致しない場合。
            Exception: その他の予期せぬエラーが発生した場合。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        upload_endpoint = os.path.join(self.__base_url, f"issue/{issue_key_or_id}/attachments")

        if filename is None:
            filename = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'application/octet-stream')
                }
                response = requests.post(upload_endpoint, headers=self.__upload_headers, files=files)
                response.raise_for_status()

            data = response.json()
            return [JiraAttachment(**item) for item in data]
        except requests.exceptions.RequestException as err:
            print(f"Jira API 'upload_attachment' リクエストエラー: {err}")
            if hasattr(err, 'response') and err.response is not None:
                print(f"レスポンス詳細: {err.response.text}")
            raise
        except json.JSONDecodeError as e:
            print(f"Jira API 'upload_attachment' レスポンスのJSONデコードに失敗しました: {e}")
            print(f"レスポンステキスト: {response.text if 'response' in locals() else 'レスポンスなし'}")
            raise
        except ValidationError as e:
            print(f"Jira API 'upload_attachment' Pydanticバリデーションエラー: {e}")
            print(f"エラー詳細: {e.errors()}")
            raise
        except Exception as e:
            print(f"Jira API 'upload_attachment' 予期せぬエラー: {e}")
            raise