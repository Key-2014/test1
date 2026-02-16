"""
関数電卓 — Python テキスト入力式
====================================
対応する演算:
  四則演算      : 4 - 4 + 9
  べき乗        : 2 ^ 8  /  2 ** 8
  自然対数      : log 4  /  ln 4
  底2対数       : log2 8
  底10対数      : log10 100
  平方根        : sqrt 6  /  sqrt(6)
  n乗根         : root(8, 3)  →  8 の 3 乗根
  三角関数      : sin / cos / tan / asin / acos / atan
  絶対値        : abs(-5)
  階乗          : fact 5  /  fact(5)
  定数          : pi, e
  終了          : exit / quit
"""

import math
import re
import sys


# ──────────────────────────────────────
#  安全に eval するための許可リスト
# ──────────────────────────────────────
SAFE_NAMES: dict = {
    # math 関数
    "sin":   math.sin,
    "cos":   math.cos,
    "tan":   math.tan,
    "asin":  math.asin,
    "acos":  math.acos,
    "atan":  math.atan,
    "log":   math.log,
    "log2":  math.log2,
    "log10": math.log10,
    "ln":    math.log,
    "sqrt":  math.sqrt,
    "abs":   abs,
    "factorial": math.factorial,
    "ceil":  math.ceil,
    "floor": math.floor,
    # 定数
    "pi":    math.pi,
    "e":     math.e,
}

# 危険なキーワードをブロック
BLOCKED_KEYWORDS = [
    "import", "exec", "eval", "open", "os", "sys",
    "subprocess", "__", "getattr", "setattr", "delattr",
    "globals", "locals", "compile", "breakpoint",
]


def preprocess(expr: str) -> str:
    """ユーザー入力を Python で評価可能な式に変換する。"""

    # ── root(x, n) → (x) ** (1 / (n)) ──
    expr = re.sub(
        r"root\(\s*(.+?)\s*,\s*(.+?)\s*\)",
        r"(\1) ** (1 / (\2))",
        expr,
    )

    # ── fact / fact(n) → factorial(n) ──
    # fact(n) の形式
    expr = re.sub(
        r"fact\(\s*(.+?)\s*\)",
        r"factorial(\1)",
        expr,
    )
    # fact n の形式 (括弧なし — 単一の数値のみ)
    expr = re.sub(
        r"fact\s+(\d+)",
        r"factorial(\1)",
        expr,
    )

    # ── ^ → ** (べき乗) ──
    expr = expr.replace("^", "**")

    # ── 関数名の直後にスペース+数値がある場合に括弧を補完 ──
    #    例: sqrt 6 → sqrt(6),  log 4 → log(4),  sin 0.5 → sin(0.5)
    func_names = (
        "sqrt", "log2", "log10", "log", "ln",
        "sin", "cos", "tan", "asin", "acos", "atan",
        "abs", "ceil", "floor",
    )
    for fn in func_names:
        # 関数名 + スペース + 数値(負の値含む) で、既に括弧がない場合
        pattern = rf"\b{fn}\s+(-?[\d.]+)"
        expr = re.sub(pattern, rf"{fn}(\1)", expr)

    return expr


def validate(expr: str) -> None:
    """危険な入力をブロックする。"""
    lower = expr.lower()
    for kw in BLOCKED_KEYWORDS:
        # 単語境界でマッチ（cos が os にヒットしないようにする）
        if re.search(rf"\b{kw}\b", lower):
            raise ValueError(f"禁止キーワードが含まれています: {kw}")


def evaluate(expr: str) -> object:
    """式を安全に評価して結果を返す。"""
    processed = preprocess(expr)
    validate(processed)

    try:
        result = eval(processed, {"__builtins__": {}}, SAFE_NAMES)  # noqa: S307
    except SyntaxError:
        raise SyntaxError(f"構文エラー: 式を確認してください → {processed}")
    except ZeroDivisionError:
        raise ZeroDivisionError("エラー: ゼロ除算です")

    return result


def format_result(value: object) -> str:
    """結果を見やすくフォーマットする。"""
    if isinstance(value, float):
        # 整数と等しい場合は整数表示
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


# ──────────────────────────────────────
#  メインループ
# ──────────────────────────────────────
def main() -> None:
    print("=" * 44)
    print("  関数電卓  (exit / quit で終了)")
    print("=" * 44)
    print("  例: 4 - 4 + 9 | log 4 | sqrt 6")
    print("      root(8, 3) | sin 0.5 | fact 5")
    print("=" * 44)

    while True:
        try:
            expr = input("\n>>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        if not expr:
            continue
        if expr.lower() in ("exit", "quit"):
            print("終了します。")
            break

        try:
            result = evaluate(expr)
            print(f"  = {format_result(result)}")
        except Exception as exc:
            print(f"  エラー: {exc}")


if __name__ == "__main__":
    main()
