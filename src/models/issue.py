import typing
from pydantic import BaseModel, Field, ConfigDict
from src.models.base import (
    JiraStatus,
    JiraIssueType,
    JiraProjectMeta,
    JiraUser,
    JiraPriority,
    JiraStatusCategory
)

class JiraProgress(BaseModel):
    """Jira課題の進捗状況を表すPydanticモデル。"""
    progress: int = Field(..., description="現在の進捗値")
    total: int = Field(..., description="進捗の合計値")

class JiraWatches(BaseModel):
    """Jira課題のウォッチャー情報を表すPydanticモデル。"""
    self: str = Field(..., description="このウォッチャーリソースへのURL")
    watchCount: int = Field(..., description="ウォッチャーの数")
    isWatching: bool = Field(..., description="現在のユーザーがウォッチしているか")

class JiraVotes(BaseModel):
    """Jira課題の投票情報を表すPydanticモデル。"""
    self: str = Field(..., description="この投票リソースへのURL")
    votes: int = Field(..., description="投票の総数")
    hasVoted: bool = Field(..., description="現在のユーザーが投票しているか")


class JiraSubtask(BaseModel):
    """サブタスクを表す簡易Pydanticモデル (JiraIssueと同様の構造)。"""
    id: str = Field(..., description="サブタスクのユニークなID")
    key: str = Field(..., description="サブタスクのキー (例: 'AEAP-XXXX')")
    self: str = Field(..., description="このサブタスクリソースへのURL")
    fields: typing.Optional[dict] = Field(None, description="サブタスクのフィールド。詳細なパースは別途必要に応じて。")


class JiraIssueFields(BaseModel):
    """Jira課題の 'fields' 部分（主要な課題属性）を表すPydanticモデル。
    動的なカスタムフィールドに対応するため、extra='allow' を使用します。
    """
    model_config = ConfigDict(extra='allow')

    statuscategorychangedate: str = Field(..., description="ステータスカテゴリが変更された日時 (ISO 8601形式の文字列)")
    statusCategory: JiraStatusCategory = Field(..., description="課題のステータスカテゴリ")
    resolution: typing.Optional[typing.Any] = Field(None, description="課題の解決方法（オブジェクトまたはNull）")
    labels: typing.List[str] = Field(..., description="課題に設定されたラベルのリスト")
    lastViewed: typing.Optional[str] = Field(None, description="課題が最後に閲覧された日時 (ISO 8601形式の文字列)")
    priority: JiraPriority = Field(..., description="課題の優先度")
    versions: typing.List[typing.Any] = Field(..., description="課題に関連付けられたバージョンのリスト")
    fixVersions: typing.List[typing.Any] = Field(..., description="課題に関連付けられた修正バージョンのリスト")
    issuelinks: typing.List[typing.Any] = Field(..., description="課題リンクのリスト")
    assignee: typing.Optional[JiraUser] = Field(None, description="課題のアサイン先ユーザー (アサインされていない場合はNone)")
    status: JiraStatus = Field(..., description="課題の現在のステータス")
    components: typing.List[typing.Any] = Field(..., description="課題に関連付けられたコンポーネントのリスト")
    timeestimate: typing.Optional[int] = Field(None, description="残りの見積時間（秒単位）")
    aggregatetimeoriginalestimate: typing.Optional[int] = Field(None, description="集計された元の見積時間（秒単位）")
    creator: JiraUser = Field(..., description="課題を作成したユーザー")
    subtasks: typing.List[JiraSubtask] = Field(..., description="この課題のサブタスクのリスト")
    reporter: JiraUser = Field(..., description="課題を報告したユーザー")
    aggregateprogress: JiraProgress = Field(..., description="集計された進捗情報")
    progress: JiraProgress = Field(..., description="課題の進捗情報")
    votes: JiraVotes = Field(..., description="課題の投票情報") # <-- JiraVotes に変更
    issuetype: JiraIssueType = Field(..., description="課題のタイプ")
    timespent: typing.Optional[int] = Field(None, description="実際に費やされた時間（秒単位）")
    project: JiraProjectMeta = Field(..., description="課題が属するプロジェクト")
    aggregatetimespent: typing.Optional[int] = Field(None, description="集計された費やされた時間（秒単位）")
    resolutiondate: typing.Optional[str] = Field(None, description="課題が解決された日時 (ISO 8601形式の文字列)")
    workratio: int = Field(..., description="作業比率")
    watches: JiraWatches = Field(..., description="課題のウォッチャー情報")
    created: str = Field(..., description="課題が作成された日時 (ISO 8601形式の文字列)")
    updated: str = Field(..., description="課題が最後に更新された日時 (ISO 8601形式の文字列)")
    timeoriginalestimate: typing.Optional[int] = Field(None, description="元の見積時間（秒単位）")
    description: typing.Optional[typing.Any] = Field(None, description="課題の説明 (Atlassian Document Format (ADF)形式のJSONの場合がある)")
    environment: typing.Optional[typing.Any] = Field(None, description="課題の環境情報")
    duedate: typing.Optional[str] = Field(None, description="課題の期限日時")


class JiraIssue(BaseModel):
    """個々のJira課題を表すPydanticモデル。"""
    expand: str = Field(..., description="この課題に対して展開されたフィールドのリスト")
    id: str = Field(..., description="課題のユニークなID")
    self: str = Field(..., description="この課題リソースへのURL")
    key: str = Field(..., description="課題のキー (例: 'AEAP-2593')")
    fields: JiraIssueFields = Field(..., description="課題の主要な属性を含むフィールド")