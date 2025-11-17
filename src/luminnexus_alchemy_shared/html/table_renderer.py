"""HTML table to Rich table converter."""

import textwrap
from typing import Optional

from bs4 import BeautifulSoup
from rich import box
from rich.console import Console
from rich.table import Table


def convert_html_to_table(html_string: Optional[str]) -> str:
    """
    Convert HTML table to Rich table format for terminal display.

    Args:
        html_string: HTML string containing a table

    Returns:
        String representation of Rich table, or empty string if no table found

    Examples:
        >>> html = "<table><tr><td>Hello</td><td>World</td></tr></table>"
        >>> table_str = convert_html_to_table(html)
        >>> print(table_str)
    """
    if html_string == "" or html_string is None:
        return html_string or ""

    # 解析HTML
    soup = BeautifulSoup(html_string, "html.parser")

    if len(soup.find_all("tr")) == 0:
        return ""

    # 創建Rich表格
    rich_table = Table(box=box.SQUARE, show_header=False, show_lines=True)

    # 添加列
    max_columns = max(len(row.find_all(["td", "th"])) for row in soup.find_all("tr"))
    for _ in range(max_columns):
        rich_table.add_column(justify="left")

    # 處理每一行
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        row_data = []
        for cell in cells:
            # 獲取單元格文本並移除多餘的空白
            text = " ".join(cell.stripped_strings)
            # 如果文本超過200個字符，進行換行
            if len(text) > 200:
                text = "\n".join(textwrap.wrap(text, 200))
            row_data.append(text)

        # 如果單元格少於最大列數，用空字符串填充
        while len(row_data) < max_columns:
            row_data.append("")

        rich_table.add_row(*row_data)

    # 創建Console對象並打印表格到字符串
    console = Console()
    with console.capture() as capture:
        console.print(rich_table)

    # 返回字符串結果
    return capture.get()
