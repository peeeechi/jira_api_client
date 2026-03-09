import typing

from pydantic import BaseModel, Field

from jira_api_client.models.issue import JiraIssue


class JiraSearchResults(BaseModel):
    """Jira APIの /search エンドポイントからの検索結果全体を表すPydanticモデル。"""
    issues: typing.List[JiraIssue] = Field(default_factory=list, description="検索結果として返されたJira課題のリスト")
    isLast: bool = Field(description="結果が最後のページであるかどうか")
    nextPageToken: typing.Optional[str] = Field(None, description="結果が最後のページで無い時はTokenが代入される")
