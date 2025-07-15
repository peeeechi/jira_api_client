import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import typing
from pydantic import BaseModel, Field
from src.models.issue import JiraIssue # issue.py からインポート

class JiraSearchResults(BaseModel):
    """Jira APIの /search エンドポイントからの検索結果全体を表すPydanticモデル。"""
    expand: typing.Optional[str] = Field(None, description="展開されたメタデータのリスト")
    startAt: int = Field(..., description="検索結果の開始インデックス")
    maxResults: int = Field(..., description="リクエストされた最大結果数")
    total: int = Field(..., description="検索条件に一致する課題の総数")
    issues: typing.List[JiraIssue] = Field(..., description="検索結果として返されたJira課題のリスト")
