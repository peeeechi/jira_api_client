import typing

from pydantic import BaseModel, Field

from .base import JiraUser


class JiraAttachment(BaseModel):
    """Jiraにアップロードされた添付ファイルの情報を表すPydanticモデル。"""
    id: str = Field(..., description="添付ファイルのユニークなID")
    self: str = Field(..., description="添付ファイルリソースへのURL")
    filename: str = Field(..., description="添付ファイルの名前")
    author: JiraUser = Field(..., description="ファイルをアップロードしたユーザー")
    created: str = Field(..., description="添付ファイルが作成された日時")
    size: int = Field(..., description="添付ファイルのサイズ（バイト単位）")
    mimeType: str = Field(..., description="添付ファイルのMIMEタイプ")
    content: typing.Optional[str] = Field(None, description="添付ファイルのダウンロードURL")
    thumbnail: typing.Optional[str] = Field(None, description="添付ファイルのサムネイルURL（画像の場合）")
