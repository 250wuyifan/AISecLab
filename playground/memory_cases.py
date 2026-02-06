from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LabItem:
    """
    左侧侧栏的“二级项”。
    url 由 views 层组装（避免在此处依赖 Django reverse）。
    """

    id: str
    title: str
    subtitle: str
    kind: str  # memory / tool / rag
    slug: str
    url: str


@dataclass(frozen=True)
class LabGroup:
    """
    左侧侧栏的“一级分类”。
    intro_url：点击一级分类标题时进入的介绍页，为空则不可点击。
    """

    id: str
    title: str
    items: List[LabItem]
    expanded: bool = True
    intro_url: str = ""


def build_memory_poisoning_groups(
    *,
    memory_case_urls: List[LabItem],
    tool_case_urls: List[LabItem],
    rag_case_urls: List[LabItem],
) -> List[LabGroup]:
    """
    构造“记忆投毒”大分类下的所有 case 列表。
    """
    items: List[LabItem] = []
    items.extend(memory_case_urls)
    items.extend(tool_case_urls)
    items.extend(rag_case_urls)
    return [
        LabGroup(
            id="memory_poisoning",
            title="记忆投毒",
            items=items,
            expanded=True,
            intro_url="",  # 由 views 层按需填充
        )
    ]


def find_item(groups: List[LabGroup], item_id: str) -> Optional[LabItem]:
    for g in groups:
        for it in g.items:
            if it.id == item_id:
                return it
    return None

