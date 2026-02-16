"""
テトリス — Python + pygame
===========================
操作:
  ← →   : 左右移動
  ↑      : 回転
  ↓      : ソフトドロップ（高速落下）
  Space  : ハードドロップ（即着地）
  C      : ホールド（ピースを保留）
  R      : リスタート（ゲームオーバー時）
  ESC    : 終了
"""

import pygame
import random
import sys

# ──────────────────────────────────────
#  定数
# ──────────────────────────────────────
COLS = 10
ROWS = 20
CELL = 32          # 1 マスのピクセルサイズ
SIDE_W = 180       # サイドパネル幅
TOP_MARGIN = 40    # 上部マージン

SCREEN_W = COLS * CELL + SIDE_W + 20
SCREEN_H = ROWS * CELL + TOP_MARGIN + 10

FPS = 60

# ── 色定義 ──
BG_COLOR       = (18, 18, 30)
GRID_COLOR     = (40, 40, 60)
PANEL_BG       = (25, 25, 45)
PANEL_BORDER   = (60, 60, 100)
TEXT_COLOR      = (220, 220, 240)
TEXT_DIM        = (120, 120, 160)
GAMEOVER_BG    = (0, 0, 0, 180)

# テトリミノの色（鮮やか）
COLORS = {
    "I": (0, 220, 255),    # シアン
    "O": (255, 220, 0),    # 黄
    "T": (180, 60, 255),   # 紫
    "S": (80, 255, 80),    # 緑
    "Z": (255, 60, 60),    # 赤
    "J": (60, 100, 255),   # 青
    "L": (255, 160, 40),   # オレンジ
}

# テトリミノの形状定義 (4回転状態)
SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(0, 1), (1, 1), (2, 1), (1, 0)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

LINE_SCORES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}

# ── SRS ウォールキックオフセット ──
# (from_rotation, to_rotation) → [(dx, dy), ...]
# J, L, S, T, Z 用
SRS_KICKS_JLSTZ = {
    (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
}
# I ピース用
SRS_KICKS_I = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
    (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
}

# T-Spin 判定用: T ピースの中心からの 4 隅オフセット
T_CORNERS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
# T ピースの "前方" コーナー（回転方向の前面 2 つ）
T_FRONT_CORNERS = {
    0: [(-1, -1), (1, -1)],   # 上向き
    1: [(1, -1), (1, 1)],     # 右向き
    2: [(-1, 1), (1, 1)],     # 下向き
    3: [(-1, -1), (-1, 1)],   # 左向き
}


# ──────────────────────────────────────
#  テトリミノ
# ──────────────────────────────────────
class Tetromino:
    def __init__(self, shape_name: str):
        self.name = shape_name
        self.color = COLORS[shape_name]
        self.rotation = 0
        # ボード上の位置 (左上基準)
        self.x = COLS // 2 - 2
        self.y = -1

    def cells(self) -> list[tuple[int, int]]:
        """現在の回転状態でのセル座標 (ボード座標)"""
        return [
            (self.x + dx, self.y + dy)
            for dx, dy in SHAPES[self.name][self.rotation]
        ]

    def rotated_cells(self, direction: int = 1) -> list[tuple[int, int]]:
        """回転後のセル座標 (実際には回転しない)"""
        new_rot = (self.rotation + direction) % 4
        return [
            (self.x + dx, self.y + dy)
            for dx, dy in SHAPES[self.name][new_rot]
        ]

    def rotate(self, direction: int = 1):
        self.rotation = (self.rotation + direction) % 4

    def shape_cells(self) -> list[tuple[int, int]]:
        """形状のみのセル座標 (位置オフセットなし)"""
        return SHAPES[self.name][self.rotation]


# ──────────────────────────────────────
#  ゲーム本体
# ──────────────────────────────────────
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        # ボード: None = 空, tuple = 色
        self.board: list[list[tuple | None]] = [
            [None] * COLS for _ in range(ROWS)
        ]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False

        self.bag: list[str] = []
        self.current = self._next_piece()
        self.next_piece = self._next_piece()

        # ホールド
        self.hold_piece: Tetromino | None = None
        self.hold_used = False      # 1ターンに1回だけホールド可能

        self.fall_interval = self._calc_interval()
        self.fall_timer = 0
        self.lock_delay = 500       # ms
        self.lock_timer = 0
        self.on_ground = False

        # T-Spin 判定用
        self.last_action = ""       # "rotate" or "move"
        self.last_kick_index = 0    # 使用した SRS キックのインデックス
        self.last_tspin = ""        # 直前の消去で判定された T-Spin 種別

        # アニメーション
        self.clearing_rows: list[int] = []
        self.clear_timer = 0
        self.clear_duration = 250   # ms

    def _refill_bag(self):
        """7-bag ランダム生成"""
        bag = list(SHAPES.keys())
        random.shuffle(bag)
        self.bag = bag

    def _next_piece(self) -> Tetromino:
        if not self.bag:
            self._refill_bag()
        return Tetromino(self.bag.pop())

    def _calc_interval(self) -> int:
        """レベルに応じた落下間隔 (ms)"""
        return max(80, 800 - (self.level - 1) * 70)

    def _valid_pos(self, cells: list[tuple[int, int]]) -> bool:
        for x, y in cells:
            if x < 0 or x >= COLS:
                return False
            if y >= ROWS:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    # ── 操作 ──
    def move(self, dx: int, dy: int) -> bool:
        self.current.x += dx
        self.current.y += dy
        if not self._valid_pos(self.current.cells()):
            self.current.x -= dx
            self.current.y -= dy
            return False
        self.last_action = "move"
        return True

    def rotate(self, direction: int = 1):
        """SRS ウォールキック付き回転"""
        piece = self.current
        from_rot = piece.rotation
        to_rot = (from_rot + direction) % 4

        # キックテーブル選択
        if piece.name == "O":
            # O ピースは回転不要
            return
        if piece.name == "I":
            kicks = SRS_KICKS_I.get((from_rot, to_rot), [(0, 0)])
        else:
            kicks = SRS_KICKS_JLSTZ.get((from_rot, to_rot), [(0, 0)])

        for i, (kick_dx, kick_dy) in enumerate(kicks):
            test_cells = [
                (piece.x + dx + kick_dx, piece.y + dy - kick_dy)
                for dx, dy in SHAPES[piece.name][to_rot]
            ]
            if self._valid_pos(test_cells):
                piece.rotation = to_rot
                piece.x += kick_dx
                piece.y -= kick_dy    # SRS の dy は上が正
                self.last_action = "rotate"
                self.last_kick_index = i
                return

    def hold(self):
        """現在のピースをホールドし、保留中のピースと交換する。"""
        if self.hold_used:
            return  # 1ターンに1回のみ

        self.hold_used = True
        if self.hold_piece is None:
            # 初回ホールド: current を保管し、次のピースを出す
            self.hold_piece = Tetromino(self.current.name)
            self.current = self.next_piece
            self.next_piece = self._next_piece()
        else:
            # 2回目以降: current と hold を交換
            old_name = self.hold_piece.name
            self.hold_piece = Tetromino(self.current.name)
            self.current = Tetromino(old_name)

        # 状態リセット
        self.on_ground = False
        self.lock_timer = 0
        self.fall_timer = 0
        self.last_action = "hold"

        if not self._valid_pos(self.current.cells()):
            self.game_over = True

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self._lock()

    def ghost_y(self) -> int:
        """ゴーストピースの Y オフセット"""
        dy = 0
        while True:
            test = [(x, y + dy + 1) for x, y in self.current.cells()]
            if not self._valid_pos(test):
                return dy
            dy += 1

    # ── T-Spin 判定 ──
    def _check_tspin(self) -> str:
        """T-Spin の種類を判定する。"" → '', 'mini', 'full'"""
        if self.current.name != "T" or self.last_action != "rotate":
            return ""

        # T ピースの中心座標を算出（回転状態に応じて）
        # T の形状は常に (1,1) が中心
        cx = self.current.x + 1
        cy = self.current.y + 1

        # 4 隅のうち埋まっている数をカウント
        filled = 0
        for dx, dy in T_CORNERS:
            nx, ny = cx + dx, cy + dy
            if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                filled += 1  # 壁/床もブロック扱い
            elif self.board[ny][nx] is not None:
                filled += 1

        if filled < 3:
            return ""

        # 前方 2 隅が埋まっているなら正規 T-Spin
        front_filled = 0
        for dx, dy in T_FRONT_CORNERS[self.current.rotation]:
            nx, ny = cx + dx, cy + dy
            if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                front_filled += 1
            elif self.board[ny][nx] is not None:
                front_filled += 1

        if front_filled == 2:
            return "full"

        # キックインデックスが 4（最後のオフセット）なら正規 T-Spin
        if self.last_kick_index == 4:
            return "full"

        return "mini"

    # ── 固定 & ライン消去 ──
    def _lock(self):
        # T-Spin 判定（ボードにセットする前に行う）
        tspin = self._check_tspin()

        for x, y in self.current.cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.board[y][x] = self.current.color
            elif y < 0:
                self.game_over = True
                return

        # ライン消去チェック
        full_rows = [
            r for r in range(ROWS)
            if all(self.board[r][c] is not None for c in range(COLS))
        ]
        if full_rows:
            self.clearing_rows = full_rows
            self.clear_timer = self.clear_duration
            self.last_tspin = tspin
        else:
            # ライン消去なしでも T-Spin 0 行ボーナス
            if tspin == "full":
                self.score += 400
                self.last_tspin = tspin
            elif tspin == "mini":
                self.score += 100
                self.last_tspin = tspin
            else:
                self.last_tspin = ""
            self._spawn_next()

    def _clear_lines(self):
        num = len(self.clearing_rows)
        tspin = self.last_tspin
        for r in sorted(self.clearing_rows):
            del self.board[r]
            self.board.insert(0, [None] * COLS)

        self.lines += num

        # スコア計算 (T-Spin ボーナス)
        if tspin == "full":
            # T-Spin Single=800, Double=1200, Triple=1600
            tspin_scores = {1: 800, 2: 1200, 3: 1600}
            self.score += tspin_scores.get(num, 800)
        elif tspin == "mini":
            # T-Spin Mini Single=200, Double=400
            mini_scores = {1: 200, 2: 400}
            self.score += mini_scores.get(num, 200)
        else:
            self.score += LINE_SCORES.get(num, 800)

        self.level = self.lines // 10 + 1
        self.fall_interval = self._calc_interval()
        self.clearing_rows = []
        self.last_tspin = ""
        self._spawn_next()

    def _spawn_next(self):
        self.current = self.next_piece
        self.next_piece = self._next_piece()
        self.on_ground = False
        self.lock_timer = 0
        self.hold_used = False   # 新しいピースでホールド解禁

        if not self._valid_pos(self.current.cells()):
            self.game_over = True

    # ── 更新 ──
    def update(self, dt: int):
        if self.game_over:
            return

        # ライン消去アニメーション中
        if self.clearing_rows:
            self.clear_timer -= dt
            if self.clear_timer <= 0:
                self._clear_lines()
            return

        # 自然落下
        self.fall_timer += dt
        if self.fall_timer >= self.fall_interval:
            self.fall_timer = 0
            if not self.move(0, 1):
                # 地面に到達
                if self.on_ground:
                    self.lock_timer += self.fall_interval
                    if self.lock_timer >= self.lock_delay:
                        self._lock()
                else:
                    self.on_ground = True
                    self.lock_timer = 0
            else:
                self.on_ground = False
                self.lock_timer = 0


# ──────────────────────────────────────
#  描画
# ──────────────────────────────────────
class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.board_x = 10
        self.board_y = TOP_MARGIN
        self.font_large = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 16)

    def draw(self, game: Game):
        self.screen.fill(BG_COLOR)
        self._draw_board_bg()
        self._draw_grid(game)
        self._draw_ghost(game)
        self._draw_current(game)
        self._draw_clearing(game)
        self._draw_side_panel(game)
        if game.game_over:
            self._draw_game_over()

    def _draw_board_bg(self):
        rect = pygame.Rect(
            self.board_x, self.board_y,
            COLS * CELL, ROWS * CELL
        )
        pygame.draw.rect(self.screen, (12, 12, 22), rect)
        pygame.draw.rect(self.screen, PANEL_BORDER, rect, 2)

    def _draw_cell(self, x: int, y: int, color: tuple, alpha: int = 255):
        px = self.board_x + x * CELL
        py = self.board_y + y * CELL

        if alpha < 255:
            surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            # ベース
            surf.fill((*color, alpha))
            # ハイライト (上・左)
            hl = tuple(min(c + 60, 255) for c in color)
            pygame.draw.line(surf, (*hl, alpha), (0, 0), (CELL - 1, 0), 2)
            pygame.draw.line(surf, (*hl, alpha), (0, 0), (0, CELL - 1), 2)
            # シャドウ (下・右)
            sh = tuple(max(c - 80, 0) for c in color)
            pygame.draw.line(surf, (*sh, alpha), (0, CELL - 1), (CELL - 1, CELL - 1), 2)
            pygame.draw.line(surf, (*sh, alpha), (CELL - 1, 0), (CELL - 1, CELL - 1), 2)
            self.screen.blit(surf, (px, py))
        else:
            rect = pygame.Rect(px, py, CELL, CELL)
            pygame.draw.rect(self.screen, color, rect)
            # ハイライト
            hl = tuple(min(c + 60, 255) for c in color)
            pygame.draw.line(self.screen, hl, (px, py), (px + CELL - 1, py), 2)
            pygame.draw.line(self.screen, hl, (px, py), (px, py + CELL - 1), 2)
            # シャドウ
            sh = tuple(max(c - 80, 0) for c in color)
            pygame.draw.line(self.screen, sh, (px, py + CELL - 1), (px + CELL - 1, py + CELL - 1), 2)
            pygame.draw.line(self.screen, sh, (px + CELL - 1, py), (px + CELL - 1, py + CELL - 1), 2)
            # 内側の光沢
            inner = pygame.Rect(px + 4, py + 4, CELL - 8, CELL - 8)
            gl = tuple(min(c + 30, 255) for c in color)
            pygame.draw.rect(self.screen, gl, inner)

    def _draw_grid(self, game: Game):
        for r in range(ROWS):
            for c in range(COLS):
                color = game.board[r][c]
                if color is not None:
                    # 消去アニメーション行には描画しない
                    if r not in game.clearing_rows:
                        self._draw_cell(c, r, color)

                # グリッド線
                px = self.board_x + c * CELL
                py = self.board_y + r * CELL
                pygame.draw.rect(self.screen, GRID_COLOR, (px, py, CELL, CELL), 1)

    def _draw_ghost(self, game: Game):
        if game.game_over or game.clearing_rows:
            return
        dy = game.ghost_y()
        for x, y in game.current.cells():
            gy = y + dy
            if 0 <= gy < ROWS and 0 <= x < COLS:
                self._draw_cell(x, gy, game.current.color, alpha=50)

    def _draw_current(self, game: Game):
        if game.clearing_rows:
            return
        for x, y in game.current.cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self._draw_cell(x, y, game.current.color)

    def _draw_clearing(self, game: Game):
        """消去行のフラッシュアニメーション"""
        if not game.clearing_rows:
            return
        progress = 1.0 - game.clear_timer / game.clear_duration
        flash = int(255 * abs((progress * 4) % 2 - 1))
        for r in game.clearing_rows:
            for c in range(COLS):
                px = self.board_x + c * CELL
                py = self.board_y + r * CELL
                pygame.draw.rect(
                    self.screen, (flash, flash, flash),
                    (px, py, CELL, CELL)
                )

    def _draw_side_panel(self, game: Game):
        panel_x = self.board_x + COLS * CELL + 10
        panel_y = self.board_y

        # パネル背景
        panel_rect = pygame.Rect(panel_x, panel_y, SIDE_W - 20, ROWS * CELL)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel_rect, 2, border_radius=8)

        cx = panel_x + (SIDE_W - 20) // 2
        y = panel_y + 15

        # タイトル
        title = self.font_large.render("TETRIS", True, (100, 200, 255))
        self.screen.blit(title, (cx - title.get_width() // 2, y))
        y += 45

        # SCORE
        self._draw_label_value(cx, y, "SCORE", str(game.score))
        y += 55

        # LEVEL
        self._draw_label_value(cx, y, "LEVEL", str(game.level))
        y += 55

        # LINES
        self._draw_label_value(cx, y, "LINES", str(game.lines))
        y += 70

        # HOLD
        label = self.font_mid.render("HOLD", True, TEXT_DIM)
        self.screen.blit(label, (cx - label.get_width() // 2, y))
        y += 30
        if game.hold_piece is not None:
            self._draw_preview(game.hold_piece, cx, y)
        else:
            empty = self.font_small.render("---", True, TEXT_DIM)
            self.screen.blit(empty, (cx - empty.get_width() // 2, y + 10))
        y += 75

        # NEXT
        label = self.font_mid.render("NEXT", True, TEXT_DIM)
        self.screen.blit(label, (cx - label.get_width() // 2, y))
        y += 30

        # Next ピース描画
        self._draw_preview(game.next_piece, cx, y)

    def _draw_label_value(self, cx: int, y: int, label: str, value: str):
        lbl = self.font_small.render(label, True, TEXT_DIM)
        self.screen.blit(lbl, (cx - lbl.get_width() // 2, y))
        val = self.font_mid.render(value, True, TEXT_COLOR)
        self.screen.blit(val, (cx - val.get_width() // 2, y + 20))

    def _draw_preview(self, piece: Tetromino, cx: int, top_y: int):
        cells = SHAPES[piece.name][0]
        # 中央揃え
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        w = (max_x - min_x + 1) * (CELL - 4)
        h = (max_y - min_y + 1) * (CELL - 4)
        off_x = cx - w // 2
        off_y = top_y

        small = CELL - 4
        for dx, dy in cells:
            px = off_x + (dx - min_x) * small
            py = off_y + (dy - min_y) * small
            rect = pygame.Rect(px, py, small, small)
            pygame.draw.rect(self.screen, piece.color, rect)
            hl = tuple(min(c + 60, 255) for c in piece.color)
            pygame.draw.line(self.screen, hl, (px, py), (px + small - 1, py), 2)
            pygame.draw.line(self.screen, hl, (px, py), (px, py + small - 1), 2)
            sh = tuple(max(c - 80, 0) for c in piece.color)
            pygame.draw.line(self.screen, sh,
                             (px, py + small - 1), (px + small - 1, py + small - 1), 2)
            pygame.draw.line(self.screen, sh,
                             (px + small - 1, py), (px + small - 1, py + small - 1), 2)
            inner = pygame.Rect(px + 3, py + 3, small - 6, small - 6)
            gl = tuple(min(c + 30, 255) for c in piece.color)
            pygame.draw.rect(self.screen, gl, inner)

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        go_text = self.font_large.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(go_text, (cx - go_text.get_width() // 2, cy - 30))

        hint = self.font_small.render("Press R to Restart", True, TEXT_COLOR)
        self.screen.blit(hint, (cx - hint.get_width() // 2, cy + 15))


# ──────────────────────────────────────
#  メインループ
# ──────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("テトリス")
    clock = pygame.time.Clock()

    game = Game()
    renderer = Renderer(screen)

    # キーリピート: 初回 170ms, 以降 50ms
    pygame.key.set_repeat(170, 50)

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if game.game_over:
                    if event.key == pygame.K_r:
                        game.reset()
                    continue

                if game.clearing_rows:
                    continue

                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    if game.move(0, 1):
                        game.score += 1
                        game.fall_timer = 0
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()
                elif event.key == pygame.K_c:
                    game.hold()

        game.update(dt)
        renderer.draw(game)
        pygame.display.flip()


if __name__ == "__main__":
    main()
