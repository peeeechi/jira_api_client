import typing
from pydantic import BaseModel, Field
from enum import Enum

# --- 既存のEnumと基本モデル ---

class JiraStatusCategory(BaseModel):
    """Jiraのステータスカテゴリを表すPydanticモデル。"""
    self: str = Field(..., description="このステータスカテゴリリソースへのURL") # selfフィールドも追加
    id: int = Field(..., description="ステータスカテゴリのユニークなID")
    key: str = Field(..., description="ステータスカテゴリの内部キー (例: 'indeterminate')")
    colorName: str = Field(..., description="ステータスカテゴリに関連付けられた色名 (例: 'yellow')")
    name: str = Field(..., description="ステータスカテゴリの表示名 (例: '進行中')")

class JiraStatus(BaseModel):
    """Jiraの課題ステータスを表すPydanticモデル。"""
    self: str = Field(..., description="このステータスリソースへのURL")
    description: typing.Optional[str] = Field(None, description="ステータスの説明")
    iconUrl: typing.Optional[str] = Field(None, description="ステータスアイコンのURL")
    name: str = Field(..., description="ステータスの表示名 (例: '進行中')")
    id: str = Field(..., description="ステータスのユニークなID")
    statusCategory: JiraStatusCategory = Field(..., description="ステータスが属するカテゴリ")

class JiraIssueType(BaseModel):
    """Jiraの課題タイプを表すPydanticモデル。"""
    self: str = Field(..., description="この課題タイプリソースへのURL")
    id: str = Field(..., description="課題タイプのユニークなID")
    description: typing.Optional[str] = Field(None, description="課題タイプの説明")
    iconUrl: typing.Optional[str] = Field(None, description="課題タイプアイコンのURL")
    name: str = Field(..., description="課題タイプの表示名 (例: 'バグ', 'タスク')")
    subtask: bool = Field(..., description="サブタスクであるかどうかのフラグ")
    avatarId: typing.Optional[int] = Field(None, description="アバターのID")
    hierarchyLevel: typing.Optional[int] = Field(None, description="課題タイプの階層レベル")

class JiraProjectCategory(BaseModel): # <-- 新規追加: projectCategoryのモデル
    """Jiraプロジェクトのカテゴリを表すPydanticモデル。"""
    self: str = Field(..., description="このプロジェクトカテゴリリソースへのURL")
    id: str = Field(..., description="プロジェクトカテゴリのユニークなID")
    description: typing.Optional[str] = Field(None, description="プロジェクトカテゴリの説明")
    name: str = Field(..., description="プロジェクトカテゴリの表示名")

class JiraProjectMeta(BaseModel):
    """Jira課題の 'fields' 内にあるプロジェクト情報を表すPydanticモデル。"""
    self: str = Field(..., description="このプロジェクトリソースへのURL")
    id: str = Field(..., description="プロジェクトのユニークなID")
    key: str = Field(..., description="プロジェクトキー")
    name: str = Field(..., description="プロジェクトの表示名")
    projectTypeKey: str = Field(..., description="プロジェクトタイプキー (例: 'software')")
    simplified: typing.Optional[bool] = Field(None, description="簡略化されたプロジェクトビューであるかどうかのフラグ")
    avatarUrls: typing.Dict[str, str] = Field(..., description="異なるサイズのアバターURLの辞書")
    projectCategory: typing.Optional[JiraProjectCategory] = Field(None, description="プロジェクトが属するカテゴリ") # <-- 追加

class JiraUser(BaseModel):
    """Jiraのユーザー情報を表すPydanticモデル。"""
    self: str = Field(..., description="このユーザーリソースへのURL")
    accountId: str = Field(..., description="ユーザーのAtlassianアカウントID")
    emailAddress: typing.Optional[str] = Field(None, description="ユーザーのメールアドレス")
    displayName: str = Field(..., description="ユーザーの表示名")
    active: bool = Field(..., description="ユーザーがアクティブであるかどうかのフラグ")
    timeZone: typing.Optional[str] = Field(None, description="ユーザーのタイムゾーン")
    avatarUrls: typing.Dict[str, str] = Field(..., description="異なるサイズのアバターURLの辞書")
    accountType: typing.Optional[str] = Field(None, description="ユーザーアカウントのタイプ (例: 'atlassian')") # <-- 追加

class JiraPriority(BaseModel):
    """Jiraの優先度情報を表すPydanticモデル。"""
    self: str = Field(..., description="この優先度リソースへのURL")
    iconUrl: str = Field(..., description="優先度アイコンのURL")
    name: str = Field(..., description="優先度の表示名 (例: 'Lowest')")
    id: str = Field(..., description="優先度のユニークなID")

# Jira課題タイプをEnumで定義
class JiraIssueTypeEnum(str, Enum):
    """
    Jiraで利用可能な一般的な課題タイプの列挙型。
    """
    TASK = "Task"
    BUG = "Bug"
    STORY = "Story"
    EPIC = "Epic"
    SUB_TASK = "Sub-task"

# JiraステータスをEnumで定義
class JiraStatusNameEnum(str, Enum):
    """
    Jiraで利用可能なステータス名の列挙型。
    """
    NEW = "New"
    TRIAGED = "Triaged"
    INVESTIGATING = "Investigating"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    TO_BE_APPROVED = "To Be Approved"
    TO_BE_RELEASED = "To Be Released"
    CANCELLED = "Cancelled"
    BLOCKED = "Blocked"
    DONE = "Done"