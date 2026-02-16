"""
ヒットアンドブロー（数字版 Wordle）
=====================================
ランダムな 3 桁の数字を当てるゲーム。
  🟩 緑 : 数字も位置も正解
  🟨 黄 : 数字は合っているが位置が違う
  🟥 赤 : その数字は含まれていない

各桁は 0〜9（重複なし）。最大 10 回まで挑戦可能。
"""

import random

MAX_ATTEMPTS = 10
NUM_DIGITS = 3

# ── ANSI カラーコード ──
GREEN  = "\033[92m"   # 緑（ヒット）
YELLOW = "\033[93m"   # 黄（ブロー）
RED    = "\033[91m"   # 赤（ミス）
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"


def generate_answer() -> list[int]:
    """重複なしの 3 桁をランダム生成する。"""
    digits = list(range(10))
    random.shuffle(digits)
    return digits[:NUM_DIGITS]


def evaluate(guess: list[int], answer: list[int]) -> list[str]:
    """
    各桁を評価して結果リストを返す。
      "green"  — 数字も位置も一致
      "yellow" — 数字は含まれるが位置が違う
      "red"    — 数字が含まれていない
    """
    result = []
    for i, g in enumerate(guess):
        if g == answer[i]:
            result.append("green")
        elif g in answer:
            result.append("yellow")
        else:
            result.append("red")
    return result


def colorize(digit: int, status: str) -> str:
    """数字をステータスに応じて色付き文字列にする。"""
    color = {"green": GREEN, "yellow": YELLOW, "red": RED}[status]
    return f"{color}{BOLD} {digit} {RESET}"


def display_result(guess: list[int], result: list[str], attempt: int):
    """評価結果を色付きで表示する。"""
    colored = "".join(colorize(g, r) for g, r in zip(guess, result))
    status_icons = "".join(
        {"green": "🟩", "yellow": "🟨", "red": "🟥"}[r] for r in result
    )
    print(f"  {attempt:2d} |{colored}| {status_icons}")


def play():
    """1回のゲームを実行する。"""
    answer = generate_answer()

    print(f"\n🔢  {NUM_DIGITS} 桁の数字を当ててください！（各桁 0〜9、重複なし）")
    print("─" * 42)
    print(f"  {DIM}🟩 = 位置も数字も正解  🟨 = 数字だけ正解  🟥 = ハズレ{RESET}")
    print("─" * 42)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        remaining = MAX_ATTEMPTS - attempt + 1
        raw = input(f"  ({remaining:2d}回) >>> ").strip()

        if raw.lower() in ("exit", "quit"):
            print(f"  正解は {''.join(map(str, answer))} でした。")
            return False

        # 入力チェック
        if len(raw) != NUM_DIGITS or not raw.isdigit():
            print(f"  ⚠  {NUM_DIGITS} 桁の数字を入力してください（例: 123）")
            attempt_rollback = True
        else:
            digits = [int(c) for c in raw]
            if len(set(digits)) != NUM_DIGITS:
                print("  ⚠  同じ数字は使えません")
                attempt_rollback = True
            else:
                attempt_rollback = False

        if attempt_rollback:
            # 無効入力は回数を消費しない — for文は進むので再帰的に処理
            continue

        result = evaluate(digits, answer)
        display_result(digits, result, attempt)

        if all(r == "green" for r in result):
            print(f"\n  🎉 正解！ {attempt} 回で当てました！")
            if attempt <= 3:
                print("     ★★★ 天才的！ ★★★")
            elif attempt <= 6:
                print("     ★★  お見事！ ★★")
            else:
                print("     ★   クリア！ ★")
            return True

    # 規定回数オーバー
    answer_str = "".join(map(str, answer))
    print(f"\n  💔 残念！正解は {BOLD}{answer_str}{RESET} でした。")
    return True


def main():
    print("=" * 42)
    print("   ヒ ッ ト ア ン ド ブ ロ ー")
    print("=" * 42)
    print(f"  {NUM_DIGITS} 桁の数字を {MAX_ATTEMPTS} 回以内に当てよう！")
    print("  exit / quit で終了")

    while True:
        result = play()
        if result is False:
            break

        again = input("\n  もう一度遊ぶ？ (y/n) >>> ").strip().lower()
        if again not in ("y", "yes", "はい"):
            print("  お疲れさまでした！")
            break

    print()


if __name__ == "__main__":
    main()
