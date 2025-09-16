import typing

from pydantic import BaseModel, Field

from jira_api_client.models.issue import JiraIssue


class JiraSearchResults(BaseModel):
    """Jira APIの /search エンドポイントからの検索結果全体を表すPydanticモデル。"""
    expand: typing.Optional[str] = Field(None, description="展開されたメタデータのリスト")
    startAt: typing.Optional[int] = Field(None, description="検索結果の開始インデックス")
    maxResults: typing.Optional[int] = Field(None, description="リクエストされた最大結果数")
    total: typing.Optional[int] = Field(None, description="検索条件に一致する課題の総数")
    issues: typing.List[JiraIssue] = Field(default_factory=list, description="検索結果として返されたJira課題のリスト")
    isLast: typing.Optional[bool] = Field(None, description="結果が最後のページであるかどうか")
