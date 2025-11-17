"""通用型別轉換函數模組"""

import decimal
from typing import Any, Optional


def safe_decimal(value: Any) -> Optional[decimal.Decimal]:
    """
    嘗試將值轉換為Decimal，用於DecimalField(max_digits=15, decimal_places=5)。
    若發生任何錯誤或超出範圍，則返回None。

    Args:
        value: 要轉換的值

    Returns:
        decimal.Decimal 或 None（轉換失敗時）

    Examples:
        >>> safe_decimal("123.45")
        Decimal('123.45000')
        >>> safe_decimal("<1")
        Decimal('0.99990')
        >>> safe_decimal("invalid")
        None
    """
    if value is None:
        return None

    # 若 value 是 int/float，就先轉成字串
    if isinstance(value, (int, float)):
        value = str(value)

    # 其餘型別，如 dict、list... 直接跳過或另做處理
    if not isinstance(value, str):
        return None

    value_str = value.strip()
    if not value_str:
        return None

    # 例：若遇到 "<1" 等，先行處理
    if value_str.startswith("<"):
        possible_num = value_str[1:].strip()
        try:
            dec = decimal.Decimal(possible_num)
            # 省略細節, 直接回傳 0.9999 之類的
            dec = dec - decimal.Decimal("0.0001")
        except Exception:
            return None
    else:
        # 嘗試 parse
        try:
            dec = decimal.Decimal(value_str)
        except Exception:
            return None

    # 量化（以你的 decimal_places=5 為例，若是其他精度請調整 "1.00000"）
    try:
        dec = dec.quantize(decimal.Decimal("1.00000"), rounding=decimal.ROUND_HALF_UP)
    except decimal.InvalidOperation:
        # 表示數值太大/太小 (e.g. Infinity, NaN, or out of range)
        return None

    # 如果還要防止絕對值大過 9999999999.99999（以 max_digits=15 為例）
    if abs(dec) >= decimal.Decimal("10000000000"):
        # 表示超出 10位整數 + 5位小數
        return None

    return dec


def safe_int(value: Any) -> Optional[int]:
    """
    嘗試將值轉換為整數。轉換失敗時返回None。

    Args:
        value: 要轉換的值

    Returns:
        int 或 None（轉換失敗時）

    Examples:
        >>> safe_int("42")
        42
        >>> safe_int("3.14")
        3
        >>> safe_int("invalid")
        None
    """
    if value is None:
        return None
    try:
        # 先轉成 float 再轉 int，是為了處理 "3.0" 或 " 3 " 之類
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_str(value: Any) -> Optional[str]:
    """
    確保值為字符串，返回trimmed版本，如果不是字符串或為空則返回None。

    Args:
        value: 要轉換的值

    Returns:
        str 或 None

    Examples:
        >>> safe_str("  hello  ")
        'hello'
        >>> safe_str("")
        None
        >>> safe_str(123)
        None
    """
    if isinstance(value, str):
        val = value.strip()
        return val if val else None
    return None
