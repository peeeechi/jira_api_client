import typing

from pydantic import BaseModel, ConfigDict, Field

from .base import JiraIssueType, JiraPriority, JiraProjectMeta, JiraStatus, JiraStatusCategory, JiraUser

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


# AdfMediaInline モデル (media とは異なるインラインメディア)
class AdfMediaInlineAttrs(BaseModel):
    id: str
    type: typing.Literal["file", "link"]  # media と同様に file または link
    collection: str
    url: typing.Optional[str] = None  # media と同様


class AdfMediaInline(BaseModel):
    type: typing.Literal["mediaInline"]
    attrs: AdfMediaInlineAttrs


# AdfParagraphのcontentは、上記のノードのUnionのリスト
# インラインメディアも段落の子になりうるため追加
AdfParagraphChildContent = typing.Union[AdfTextContent, AdfHardBreakContent, AdfInlineCardContent, AdfMediaInline]


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
    # 循環参照を避けるため、文字列リファレンスを使用
    content: typing.List['AdfDocumentContent']


class AdfRule(BaseModel):
    type: typing.Literal["rule"]


# AdfExpand モデル
class AdfExpandAttrs(BaseModel):
    title: str


class AdfExpand(BaseModel):
    type: typing.Literal["expand"]
    content: typing.List['AdfDocumentContent']  # expand の中もドキュメントコンテンツ
    attrs: AdfExpandAttrs


# AdfCodeBlock モデル
class AdfCodeBlockAttrs(BaseModel):
    language: typing.Optional[str] = None
    syntax: typing.Optional[str] = None  # 'language' と同じ意味合いで使われることもある


class AdfCodeBlock(BaseModel):
    type: typing.Literal["codeBlock"]
    content: typing.List[AdfTextContent]  # コードブロックのコンテンツは通常テキスト
    attrs: typing.Optional[AdfCodeBlockAttrs] = None  # language などの属性


# Table 関連モデル
class AdfTableCell(BaseModel):
    type: typing.Literal["tableCell"]
    content: typing.List['AdfDocumentContent']  # セル内は任意のADFコンテンツが可能
    attrs: typing.Dict[str, typing.Any] = Field(default_factory=dict)  # colspan, rowspan など


class AdfTableHeader(BaseModel):
    type: typing.Literal["tableHeader"]
    content: typing.List['AdfDocumentContent']  # ヘッダーセル内は任意のADFコンテンツが可能
    attrs: typing.Dict[str, typing.Any] = Field(default_factory=dict)  # colspan, rowspan など


class AdfTableRow(BaseModel):
    type: typing.Literal["tableRow"]
    content: typing.List[typing.Union[AdfTableCell, AdfTableHeader]]


class AdfTableAttrs(BaseModel):
    layout: str  # 'center' が来たため、より柔軟に str に変更
    localId: typing.Optional[str] = None  # テーブルのローカルID (Confluenceで使われる)


class AdfTable(BaseModel):
    type: typing.Literal["table"]
    content: typing.List[AdfTableRow]
    attrs: typing.Optional[AdfTableAttrs] = None


# AdfMediaGroup モデル
class AdfMediaGroup(BaseModel):
    type: typing.Literal["mediaGroup"]
    # mediaGroup の content は AdfMedia だけでなく、
    # paragraph や text, hardBreak, mediaInline なども含む可能性があるため、
    # AdfMedia と AdfParagraphChildContent の Union をリストとして受け入れる
    content: typing.List[typing.Union[AdfMedia, AdfParagraphChildContent]]


# AdfListItem の content にくる可能性のある要素
AdfListItemChildContent = typing.Union[
    AdfParagraph,
    'AdfBulletList',  # 循環参照を避けるため
    'AdfOrderedList',
    AdfHeading,
    AdfMediaSingle,
    AdfBlockQuote,
    AdfRule,
    AdfExpand,
    AdfCodeBlock,
    AdfTable,
    AdfMediaGroup,
]


class AdfListItem(BaseModel):
    type: typing.Literal["listItem"]
    content: typing.List[AdfListItemChildContent]


class AdfBulletList(BaseModel):
    type: typing.Literal["bulletList"]
    content: typing.List[AdfListItem]


class AdfOrderedList(BaseModel):
    type: typing.Literal["orderedList"]
    content: typing.List[AdfListItem]


# ドキュメントのトップレベルコンテンツと、
# TableCell や TableHeader の content にも使われるため、
# より複雑な構造（メディアグループ、テーブル、コードブロック、展開パネル）を先に評価するよう順序を調整
# その後、一般的なブロックレベル要素（見出し、段落、リスト、引用、罫線）を配置
AdfDocumentContent = typing.Union[
    AdfMediaGroup,  # 最優先
    AdfTable,  # 次にテーブル
    AdfCodeBlock,  # コードブロック
    AdfExpand,  # 展開パネル
    AdfHeading,
    AdfBulletList,
    AdfOrderedList,
    AdfMediaSingle,
    AdfBlockQuote,
    AdfRule,
    AdfParagraph,  # 最も汎用的な要素を最後に
]


def _parse_content_recursive(node_list: typing.List[typing.Any], indent_level: int = 0) -> typing.List[str]:
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
                elif isinstance(sub_node, AdfMediaInline):
                    media_url = sub_node.attrs.url or f"ID:{sub_node.attrs.id}"
                    paragraph_text += f"[インラインメディア: {media_url} ({sub_node.attrs.type})]"

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
            media_info = "".join(
                [f"<{m.attrs.url or m.attrs.id}> ({m.attrs.type})" for m in node.content if isinstance(m, AdfMedia)])
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

        # 追加: AdfOrderedList の処理 (bulletList と同様のロジック)
        elif isinstance(node, AdfOrderedList):
            for i, item in enumerate(node.content):
                if isinstance(item, AdfListItem):
                    parsed_item_lines = _parse_content_recursive(item.content, indent_level + 1)
                    if parsed_item_lines:
                        parsed_item_lines[0] = f"{indent_str}{i + 1}. {parsed_item_lines[0].lstrip()}"
                        for j in range(1, len(parsed_item_lines)):
                            parsed_item_lines[j] = f"{indent_str}   {parsed_item_lines[j].lstrip()}"  # 番号分のインデント調整
                    output_lines.extend(parsed_item_lines)
                else:
                    output_lines.append(f"{indent_str}[未知のリストアイテム: {type(item).__name__}]")

        # 追加: AdfExpand の処理
        elif isinstance(node, AdfExpand):
            output_lines.append(f"{indent_str}--- 展開パネル: {node.attrs.title} ---")
            output_lines.extend(_parse_content_recursive(node.content, indent_level + 1))
            output_lines.append(f"{indent_str}--- 展開パネル終了 ---")

        # 追加: AdfCodeBlock の処理
        elif isinstance(node, AdfCodeBlock):
            lang = node.attrs.language if node.attrs and node.attrs.language else "plaintext"
            code_text = "".join([s.text for s in node.content if isinstance(s, AdfTextContent)])
            output_lines.append(f"{indent_str}``` {lang}")
            output_lines.extend([f"{indent_str}{line}" for line in code_text.splitlines()])
            output_lines.append(f"{indent_str}```")

        # 追加: AdfTable の処理
        elif isinstance(node, AdfTable):
            table_lines = []
            max_col_widths = {}

            # 最初に全てのセルの内容と最大幅を計算
            parsed_rows = []
            for row_idx, row in enumerate(node.content):
                parsed_cells = []
                for col_idx, cell in enumerate(row.content):
                    cell_text = "\n".join(_parse_content_recursive(cell.content, 0)).strip()
                    parsed_cells.append(cell_text)

                    # 各セルの幅を計算
                    current_width = max(len(line) for line in cell_text.splitlines()) if cell_text else 0
                    max_col_widths[col_idx] = max(max_col_widths.get(col_idx, 0), current_width)
                parsed_rows.append(parsed_cells)

            # ヘッダー行 (存在する場合、通常最初の行) の区切り線を追加
            if parsed_rows and any(isinstance(cell_obj, AdfTableHeader) for cell_obj in node.content[0].content):
                header_line = "|" + "|".join(
                    ["-" * (max_col_widths.get(col_idx, 0) + 2) for col_idx in range(len(parsed_rows[0]))]) + "|"
                table_lines.append(f"{indent_str}{header_line}")

            # 各行を整形して出力
            for row_idx, parsed_cells in enumerate(parsed_rows):
                formatted_row_lines = []
                # 各セルの内容を複数行に分割し、行ごとに揃える
                cell_content_lines = [cell.splitlines() for cell in parsed_cells]

                max_lines_in_row = max(len(lines) for lines in cell_content_lines) if cell_content_lines else 1

                for line_idx in range(max_lines_in_row):
                    current_line_parts = []
                    for col_idx, cell_lines in enumerate(cell_content_lines):
                        text = cell_lines[line_idx] if line_idx < len(cell_lines) else ""
                        current_line_parts.append(text.ljust(max_col_widths.get(col_idx, 0)))
                    formatted_row_lines.append(f"| {' | '.join(current_line_parts)} |")

                table_lines.extend([f"{indent_str}{line}" for line in formatted_row_lines])

                # ヘッダー行の後にもう一度区切り線
                if row_idx == 0 and any(isinstance(cell_obj, AdfTableHeader) for cell_obj in node.content[0].content):
                    table_lines.append(f"{indent_str}{header_line}")

            output_lines.extend(table_lines)

        # 追加: AdfMediaGroup の処理
        elif isinstance(node, AdfMediaGroup):
            media_group_info_lines = []
            # mediaGroup の content は AdfMedia だけではないので、再帰的にパースする
            # メディアグループ内のコンテンツもインデントを深くしてパース
            media_group_info_lines.extend(_parse_content_recursive(node.content, indent_level + 1))
            output_lines.append(f"{indent_str}--- メディアグループ ---")
            output_lines.extend(media_group_info_lines)
            output_lines.append(f"{indent_str}--- メディアグループ終了 ---")

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
    description: typing.Optional[AdfDocument] = Field(None,
                                                      description="課題の説明 (Atlassian Document Format (ADF)形式のJSON)")
    environment: typing.Optional[typing.Any] = Field(None, description="課題の環境情報")
    duedate: typing.Optional[str] = Field(None, description="課題の期限日時")


class JiraIssue(BaseModel):
    """個々のJira課題を表すPydanticモデル。"""
    expand: str = Field(..., description="この課題に対して展開されたフィールドのリスト")
    id: str = Field(..., description="課題のユニークなID")
    self: str = Field(..., description="この課題リソースへのURL")
    key: str = Field(..., description="課題のキー")
    fields: JiraIssueFields = Field(..., description="課題の主要な属性を含むフィールド")


# 循環参照のモデルを再構築
# これらのモデルは、他のモデルの定義を参照しているため、すべてのモデルがロードされた後に再構築が必要です。
AdfBlockQuote.model_rebuild()
AdfListItem.model_rebuild()
AdfBulletList.model_rebuild()
AdfOrderedList.model_rebuild()
AdfExpand.model_rebuild()
AdfCodeBlock.model_rebuild()
AdfTableCell.model_rebuild()
AdfTableHeader.model_rebuild()
AdfTableRow.model_rebuild()
AdfTable.model_rebuild()
AdfMediaInline.model_rebuild()
AdfMediaGroup.model_rebuild()
AdfDocument.model_rebuild()
