from pydantic import BaseModel, Field

class JiraCreatedIssue(BaseModel):
    """Jiraに新しく作成された課題の簡易情報を示すPydanticモデル。"""
    id: str = Field(..., description="作成された課題のユニークなID")
    key: str = Field(..., description="作成された課題のキー (例: 'PROJ-456')")
    self: str = Field(..., description="作成された課題リソースへのURL")

