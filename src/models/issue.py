import sys
import os
import typing
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# sys.path の設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# src.models.base からのインポート
try:
    from src.models.base import (
        JiraStatus,
        JiraIssueType,
        JiraProjectMeta,
        JiraUser,
        JiraPriority,
        JiraStatusCategory
    )
except ImportError:
    class JiraStatus(BaseModel):
        name: str
        id: str
        description: typing.Optional[str]
        statusCategory: dict

    class JiraIssueType(BaseModel):
        name: str
        id: str

    class JiraProjectMeta(BaseModel):
        name: str
        id: str
        key: str

    class JiraUser(BaseModel):
        displayName: str
        accountId: str

    class JiraPriority(BaseModel):
        name: str
        id: str

    class JiraStatusCategory(BaseModel):
        key: str
        colorName: str

# --- ADF構造のためのPydanticモデル定義 ---

# AdfParagraphの子要素として使用されるノードを個別に定義
class AdfTextContent(BaseModel):
    type: typing.Literal["text"]
    text: str

class AdfHardBreakContent(BaseModel):
    type: typing.Literal["hardBreak"]

class AdfInlineCardAttrs(BaseModel):
    url: str

class AdfInlineCardContent(BaseModel):
    type: typing.Literal["inlineCard"]
    attrs: AdfInlineCardAttrs

# AdfParagraphのcontentは、上記のノードのUnionのリスト
AdfParagraphChildContent = typing.Union[
    AdfTextContent, AdfHardBreakContent, AdfInlineCardContent
]

class AdfParagraph(BaseModel):
    type: typing.Literal["paragraph"]
    content: typing.List[AdfParagraphChildContent] = Field(default_factory=list)

class AdfHeadingAttrs(BaseModel):
    level: int

class AdfHeading(BaseModel):
    type: typing.Literal["heading"]
    content: typing.List[AdfTextContent]
    attrs: AdfHeadingAttrs

class AdfMediaAttrs(BaseModel):
    id: str
    type: typing.Literal["file", "link"]
    collection: str
    url: typing.Optional[str] = None

class AdfMedia(BaseModel):
    type: typing.Literal["media"]
    attrs: AdfMediaAttrs

class AdfMediaSingleAttrs(BaseModel):
    layout: typing.Literal["center", "wrap-right", "wrap-left", "align-start", "align-end", "wide", "full-width"]

class AdfMediaSingle(BaseModel):
    type: typing.Literal["mediaSingle"]
    content: typing.List[AdfMedia]
    attrs: AdfMediaSingleAttrs

class AdfBlockQuote(BaseModel):
    type: typing.Literal["blockquote"]
    content: typing.List['AdfDocumentContent']

class AdfRule(BaseModel):
    type: typing.Literal["rule"]

# AdfListItem の content にくる可能性のある要素
AdfListItemChildContent = typing.Union[
    AdfParagraph,
    'AdfBulletList',
    AdfHeading,
    AdfMediaSingle,
    'AdfBlockQuote',
    AdfRule,
]

class AdfListItem(BaseModel):
    type: typing.Literal["listItem"]
    content: typing.List[AdfListItemChildContent]

class AdfBulletList(BaseModel):
    type: typing.Literal["bulletList"]
    content: typing.List[AdfListItem]

# ドキュメントのトップレベルコンテンツ
AdfDocumentContent = typing.Union[
    AdfHeading,
    AdfParagraph,
    AdfBulletList,
    AdfMediaSingle,
    AdfBlockQuote,
    AdfRule,
]

def _parse_content_recursive(
    node_list: typing.List[typing.Any],
    indent_level: int = 0
) -> typing.List[str]:
    output_lines = []
    

    for node in node_list:
        indent_str = "  " * indent_level
        node_type = type(node).__name__

        if isinstance(node, AdfParagraph):
            paragraph_text = ""
            for sub_node in node.content:
                if isinstance(sub_node, AdfTextContent):
                    paragraph_text += sub_node.text
                elif isinstance(sub_node, AdfHardBreakContent):
                    paragraph_text += "\n"
                elif isinstance(sub_node, AdfInlineCardContent):
                    paragraph_text += f"<{sub_node.attrs.url}>"
            
            lines = paragraph_text.strip().splitlines()
            if not lines:
                output_lines.append(indent_str)
            else:
                for line in lines:
                    output_lines.append(f"{indent_str}{line.strip()}")

        elif isinstance(node, AdfHeading):
            heading_text = "".join([s.text for s in node.content if isinstance(s, AdfTextContent)])
            output_lines.append(f"{indent_str}{'#' * node.attrs.level} {heading_text.strip()}")

        elif isinstance(node, AdfMediaSingle):
            media_info = "".join([f"<{m.attrs.url or m.attrs.id}> ({m.attrs.type})" for m in node.content if isinstance(m, AdfMedia)])
            output_lines.append(f"{indent_str}[メディア: {media_info.strip()} (レイアウト: {node.attrs.layout})]")
            
        elif isinstance(node, AdfBlockQuote):
            output_lines.append(f"{indent_str}>")
            output_lines.extend(_parse_content_recursive(node.content, indent_level + 1))
            
        elif isinstance(node, AdfRule):
            output_lines.append(f"{indent_str}---")

        elif isinstance(node, AdfBulletList):
            for item in node.content:
                if isinstance(item, AdfListItem):
                    
                    parsed_item_lines = _parse_content_recursive(item.content, indent_level + 1)
                    
                    if parsed_item_lines:
                        # 箇条書き記号を最初の行に追加
                        parsed_item_lines[0] = f"{indent_str}● {parsed_item_lines[0].lstrip()}"
                        
                        # 後続の行はインデントを調整
                        for i in range(1, len(parsed_item_lines)):
                            parsed_item_lines[i] = f"{indent_str}  {parsed_item_lines[i].lstrip()}"
                    
                    output_lines.extend(parsed_item_lines)
                else:
                    output_lines.append(f"{indent_str}[未知のリストアイテム: {type(item).__name__}]")
        else:
            output_lines.append(f"{indent_str}[未知のノード: {node_type}]")

    return output_lines

class AdfDocument(BaseModel):
    """Atlassian Document Format (ADF) のルートモデル"""
    type: typing.Literal["doc"] = Field(..., description="ドキュメントのタイプ: 'doc'")
    version: int = Field(..., description="ADFのバージョン")
    content: typing.List[AdfDocumentContent] = Field(..., description="ドキュメントのコンテンツのリスト")

    def to_plain_text(self) -> str:
        """このADFドキュメントを整形されたプレーンテキストに変換します。"""
        parsed_lines = _parse_content_recursive(self.content, 0)
        return "\n".join(parsed_lines)

AdfBlockQuote.model_rebuild()
AdfDocument.model_rebuild()

# --- 既存のJiraモデルにADFを組み込む ---

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
    key: str = Field(..., description="サブタスクのキー")
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
    votes: JiraVotes = Field(..., description="課題の投票情報")
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
    description: typing.Optional[AdfDocument] = Field(None, description="課題の説明 (Atlassian Document Format (ADF)形式のJSON)")
    environment: typing.Optional[typing.Any] = Field(None, description="課題の環境情報")
    duedate: typing.Optional[str] = Field(None, description="課題の期限日時")

class JiraIssue(BaseModel):
    """個々のJira課題を表すPydanticモデル。"""
    expand: str = Field(..., description="この課題に対して展開されたフィールドのリスト")
    id: str = Field(..., description="課題のユニークなID")
    self: str = Field(..., description="この課題リソースへのURL")
    key: str = Field(..., description="課題のキー")
    fields: JiraIssueFields = Field(..., description="課題の主要な属性を含むフィールド")