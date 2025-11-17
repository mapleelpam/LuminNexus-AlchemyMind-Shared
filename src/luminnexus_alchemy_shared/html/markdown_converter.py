"""HTML to Markdown converter."""

import logging
import re
from dataclasses import dataclass
from html import unescape
from typing import Optional, Union

from bs4 import BeautifulSoup, Tag


@dataclass
class ConversionConfig:
    """配置轉換選項"""

    preserve_structure: bool = True
    preserve_tables: bool = True
    preserve_links: bool = True
    heading_style: str = "atx"  # atx (#) or setext (===)
    link_style: str = "inline"  # inline or reference
    bullet_marker: str = "-"  # -, *, or +
    code_block_style: str = "fenced"  # fenced (```) or indented
    fence_char: str = "`"  # ` or ~
    emphasis_marker: str = "*"  # * or _


class HTMLToMarkdownConverter:
    """將HTML內容轉換為Markdown格式"""

    def __init__(self, config: Optional[ConversionConfig] = None):
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(__name__)

    def convert_html(
        self, content: Union[str, BeautifulSoup, Tag], container_selector: Optional[str] = None
    ) -> str:
        """
        Convert HTML content to Markdown format. Can accept both string and BeautifulSoup/Tag objects.

        Args:
            content: HTML content (string or BeautifulSoup/Tag object)
            container_selector: CSS selector to locate main content block (optional)

        Returns:
            Converted markdown text
        """
        try:
            if isinstance(content, str):
                return self.convert_html_str(content, container_selector)
            elif isinstance(content, (BeautifulSoup, Tag)):
                return self.convert_html_soup(content, container_selector)
            else:
                raise ValueError("Content must be either a string or BeautifulSoup/Tag object")

        except Exception as e:
            self.logger.error(f"Error converting HTML: {str(e)}")
            raise

    def convert_html_str(self, html_str: str, container_selector: Optional[str] = None) -> str:
        """Convert HTML string to Markdown"""
        soup = BeautifulSoup(html_str, "html.parser")
        return self.convert_html_soup(soup, container_selector)

    def convert_html_soup(
        self, soup: Union[BeautifulSoup, Tag], container_selector: Optional[str] = None
    ) -> str:
        """Convert BeautifulSoup/Tag object to Markdown"""
        try:
            if container_selector:
                container = soup.select_one(container_selector)
                if container:
                    soup = container

            if self.config.preserve_structure:
                self._process_structure(soup)

            self._process_basic_formatting(soup)

            # 段落處理必須在基本格式處理之後，這樣才不會丟失粗體/斜體等格式
            self._process_paragraphs_final(soup)

            return self._clean_and_format(soup.get_text())

        except Exception as e:
            self.logger.error(f"Error converting HTML soup: {str(e)}")
            raise

    def _process_structure(self, soup: BeautifulSoup) -> None:
        """處理文檔結構元素"""
        self._process_headings(soup)
        self._process_lists(soup)
        if self.config.preserve_tables:
            self._process_tables(soup)
        self._process_code_blocks(soup)
        self._process_blockquotes(soup)
        self._process_horizontal_rules(soup)

    def _process_headings(self, soup: BeautifulSoup) -> None:
        """處理標題標籤"""
        for i in range(6, 0, -1):
            for header in soup.find_all(f"h{i}"):
                if self.config.heading_style == "atx":
                    header.replace_with(f'\n{"#" * i} {header.get_text().strip()}\n')
                else:
                    text = header.get_text().strip()
                    underline = "=" if i == 1 else "-"
                    header.replace_with(f"\n{text}\n{underline * len(text)}\n")

    def _process_lists(self, soup: BeautifulSoup) -> None:
        """處理列表"""
        for ol in soup.find_all("ol"):
            list_items = []
            for i, li in enumerate(ol.find_all("li", recursive=False), 1):
                list_items.append(f"{i}. {li.get_text().strip()}")
            # 列表結尾加兩個換行，確保與後續內容有空行
            ol.replace_with("\n" + "\n".join(list_items) + "\n\n")

        for ul in soup.find_all("ul"):
            list_items = []
            for li in ul.find_all("li", recursive=False):
                list_items.append(f"{self.config.bullet_marker} {li.get_text().strip()}")
            # 列表結尾加兩個換行，確保與後續內容有空行
            ul.replace_with("\n" + "\n".join(list_items) + "\n\n")

    def _process_tables(self, soup: BeautifulSoup) -> None:
        """處理表格，轉換為標準 Markdown Table 格式"""
        for table in soup.find_all("table"):
            # 先處理表格內的內聯格式（粗體、斜體、鏈接等）
            self._process_table_inline_formatting(table)

            rows = []
            header_row_index = None
            all_rows = table.find_all("tr")

            # 步驟1: 尋找表頭行（<th> 元素）
            headers = []
            for idx, tr in enumerate(all_rows):
                th_cells = tr.find_all("th")
                if th_cells:
                    header_row_index = idx
                    # 處理 colspan
                    for th in th_cells:
                        colspan = int(th.get("colspan", 1))
                        text = th.get_text().strip()
                        if colspan > 1:
                            headers.extend([text] + [""] * (colspan - 1))
                        else:
                            headers.append(text)
                    break

            # 步驟2: 如果沒有 <th>，嘗試偵測「實際上的表頭行」
            # 特徵：第一個有多個 <td> 且非 colspan=3 的行
            if not headers:
                for idx, tr in enumerate(all_rows):
                    td_cells = tr.find_all("td")
                    # 跳過 colspan 跨越整行的行（通常是標題或說明）
                    if td_cells and len(td_cells) > 1:
                        # 檢查是否所有 cell 都是 colspan=整行
                        total_colspan = sum(int(td.get("colspan", 1)) for td in td_cells)
                        if total_colspan == len(td_cells):
                            # 找到第一個「正常」的多欄位行，當作表頭
                            header_row_index = idx
                            for td in td_cells:
                                colspan = int(td.get("colspan", 1))
                                text = td.get_text().strip()
                                if colspan > 1:
                                    headers.extend([text] + [""] * (colspan - 1))
                                else:
                                    headers.append(text)
                            break

            # 步驟3: 生成 Markdown 表格
            # 如果找到表頭，先輸出表頭和分隔線
            if headers:
                rows.append("| " + " | ".join(headers) + " |")
                rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

            # 步驟4: 處理數據行
            for idx, tr in enumerate(all_rows):
                # 跳過已經作為表頭的行
                if header_row_index is not None and idx == header_row_index:
                    continue

                # 跳過只有 <th> 的行（已經處理過了）
                if tr.find_all("th"):
                    continue

                td_cells = tr.find_all("td")
                if td_cells:
                    cells = []
                    for td in td_cells:
                        colspan = int(td.get("colspan", 1))
                        text = td.get_text().strip()
                        if colspan > 1:
                            cells.append(text)
                            cells.extend([""] * (colspan - 1))
                        else:
                            cells.append(text)

                    rows.append("| " + " | ".join(cells) + " |")

            table.replace_with("\n" + "\n".join(rows) + "\n")

    def _process_table_inline_formatting(self, table: Tag) -> None:
        """處理表格內的內聯格式（粗體、斜體、鏈接等）

        這個方法必須在表格轉換之前調用，確保 cell 內的格式標記被正確轉換
        """
        # 處理粗體
        for strong in table.find_all(["strong", "b"]):
            marker = self.config.emphasis_marker * 2
            strong.replace_with(f"{marker}{strong.get_text().strip()}{marker}")

        # 處理斜體
        for em in table.find_all(["em", "i"]):
            marker = self.config.emphasis_marker
            em.replace_with(f"{marker}{em.get_text().strip()}{marker}")

        # 處理刪除線
        for s in table.find_all(["s", "del"]):
            s.replace_with(f"~~{s.get_text().strip()}~~")

        # 處理行內代碼
        for code in table.find_all("code"):
            code.replace_with(f"`{code.get_text().strip()}`")

        # 處理鏈接
        if self.config.preserve_links:
            for a in table.find_all("a"):
                href = a.get("href", "")
                text = a.get_text().strip()
                if self.config.link_style == "inline":
                    a.replace_with(f"[{text}]({href})")

    def _process_code_blocks(self, soup: BeautifulSoup) -> None:
        """處理代碼塊"""
        for pre in soup.find_all("pre"):
            code = pre.get_text().strip()
            if self.config.code_block_style == "fenced":
                fence = self.config.fence_char * 3
                pre.replace_with(f"\n{fence}\n{code}\n{fence}\n")
            else:
                # 縮進式代碼塊
                indented = "\n".join(f"    {line}" for line in code.split("\n"))
                pre.replace_with(f"\n{indented}\n")

    def _process_blockquotes(self, soup: BeautifulSoup) -> None:
        """處理引用塊"""
        for blockquote in soup.find_all("blockquote"):
            lines = blockquote.get_text().strip().split("\n")
            quoted = "\n".join(f"> {line}" for line in lines)
            blockquote.replace_with(f"\n{quoted}\n")

    def _process_horizontal_rules(self, soup: BeautifulSoup) -> None:
        """處理水平分隔線"""
        for hr in soup.find_all("hr"):
            hr.replace_with("\n---\n")

    def _process_paragraphs_final(self, soup: BeautifulSoup) -> None:
        """處理段落標籤，確保段落之間有適當間距

        這個方法必須在 _process_basic_formatting() 之後調用，
        這樣才能保留粗體、斜體等內聯格式。
        """
        from bs4 import NavigableString

        for p in soup.find_all("p"):
            # 獲取段落的所有內容（包括已處理的格式標記）
            # 使用 strings 迭代器來獲取所有文本節點
            content_parts = []
            for item in p.descendants:
                if isinstance(item, NavigableString):
                    text = str(item).strip()
                    if text:
                        content_parts.append(text)

            if content_parts:
                # 合併內容並加上適當的間距
                combined = " ".join(content_parts)
                p.replace_with(f"\n{combined}\n\n")

    def _process_basic_formatting(self, soup: BeautifulSoup) -> None:
        """處理基本文本格式"""
        # 處理粗體
        for strong in soup.find_all(["strong", "b"]):
            marker = self.config.emphasis_marker * 2
            strong.replace_with(f"{marker}{strong.get_text().strip()}{marker}")

        # 處理斜體
        for em in soup.find_all(["em", "i"]):
            marker = self.config.emphasis_marker
            em.replace_with(f"{marker}{em.get_text().strip()}{marker}")

        # 處理刪除線
        for s in soup.find_all(["s", "del"]):
            s.replace_with(f"~~{s.get_text().strip()}~~")

        # 處理行內代碼
        for code in soup.find_all("code"):
            code.replace_with(f"`{code.get_text().strip()}`")

        # 處理鏈接
        if self.config.preserve_links:
            for a in soup.find_all("a"):
                href = a.get("href", "")
                text = a.get_text().strip()
                if self.config.link_style == "inline":
                    a.replace_with(f"[{text}]({href})")
                else:
                    # reference style links (未實現)
                    pass

    def _clean_and_format(self, text: str) -> str:
        """清理和格式化文本"""
        # 移除多餘空行
        text = re.sub(r"\n\s*\n", "\n\n", text)
        # 清理空白字符
        text = re.sub(r" +", " ", text)
        # HTML實體解碼
        text = unescape(text)
        # 確保文件以換行結束
        return text.strip() + "\n"


def convert_html_to_markdown(
    html_content: str,
    container_selector: Optional[str] = None,
    config: Optional[ConversionConfig] = None,
) -> str:
    """
    便捷函數用於轉換HTML到Markdown

    Args:
        html_content: HTML內容
        container_selector: CSS選擇器，用於定位主要內容區塊 (可選)
        config: 轉換配置 (可選)

    Returns:
        轉換後的markdown文本
    """
    converter = HTMLToMarkdownConverter(config)
    return converter.convert_html(html_content, container_selector)
