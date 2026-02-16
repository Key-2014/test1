"""
数あてゲーム
===========
1〜100 の中からランダムに選ばれた数字を当てるゲーム。
ヒント（大きい / 小さい）を頼りに、最小回数で正解を目指そう！
"""

import random


def play():
    """1回のゲームを実行する。"""
    answer = random.randint(1, 100)
    attempts = 0

    print("\n🎯  1〜100 の数字を当ててください！")
    print("─" * 36)

    while True:
        raw = input("  予想 >>> ").strip()

        if raw.lower() in ("exit", "quit"):
            print(f"  正解は {answer} でした。また遊んでね！")
            return False  # ゲーム終了

        # 数値チェック
        try:
            guess = int(raw)
        except ValueError:
            print("  ⚠  数字を入力してください")
            continue

        if guess < 1 or guess > 100:
            print("  ⚠  1〜100 の範囲で入力してください")
            continue

        attempts += 1

        if guess < answer:
            print(f"  ↑  {guess} より大きいです")
        elif guess > answer:
            print(f"  ↓  {guess} より小さいです")
        else:
            print(f"  🎉 正解！ {attempts} 回で当てました！")
            if attempts <= 4:
                print("     ★★★ すごい！天才的！ ★★★")
            elif attempts <= 7:
                print("     ★★  なかなかの勘！ ★★")
            else:
                print("     ★   次はもっと少ない回数で！ ★")
            return True  # もう一度遊ぶか確認


def main():
    print("=" * 36)
    print("   数 あ て ゲ ー ム")
    print("=" * 36)
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
