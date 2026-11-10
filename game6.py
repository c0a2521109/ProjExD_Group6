import os
import sys
import random
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# =========================================================
# 【担当者1：プレイヤー拡張（ダッシュ・残像等）のエリア】
# =========================================================


# =========================================================
# 【担当者2：ボス・お邪魔ギミックのエリア】
# =========================================================

class BossManager:
    def __init__(self):
        self.active = False
        self.rect = pg.Rect(0, 50, 100, 40)
        self.beams = []
        self.timer = 0

    def update(self, player_rect):
        penalty = 0
        self.timer += 1
        if self.timer > 300 and not self.active:
            self.active = True
            self.rect.x = -100
            self.timer = 0
        if self.active:
            self.rect.x += 5
            if random.randint(1, 40) == 1:
                self.beams.append(pg.Rect(self.rect.centerx, self.rect.bottom, 10, 20))
            if self.rect.x > 800:
                self.active = False
        for b in self.beams[:]:
            b.y += 8
            if b.colliderect(player_rect):
                penalty = -20
                self.beams.remove(b)
            elif b.y > 600:
                self.beams.remove(b)
        return penalty
    
    def draw(self, screen):
        if self.active:
            pg.draw.rect(screen, (150, 0, 150), self.rect)
        for b in self.beams:
            pg.draw.rect(screen, (255, 255, 0), b)
"""ボス設定: 個々の数字を書き換えるだけで調整できる"""
 
BOSS_SCALE         = 3     # ボスの大きさ（2=64px / 3=96px / 4=128px）。攻撃エフェクトの太さも連動
 
# --- 動きのランダム設定：(最小, 最大) の範囲から、そのつどランダムに選ばれる ---
BOSS_APPEAR_RANGE      = (180, 420)  # 画面から消えてから、次に出てくるまでの間隔（60 = 約1秒）
BOSS_Y_RANGE           = (30, 140)   # 飛ぶ高さ。出てくるたびに変わる（小さいほど上）
BOSS_SPEED_RANGE       = (3, 8)      # 移動速度（大きいほど速い）。移動中にも変わる
BOSS_MOVE_CHANGE_RANGE = (40, 110)   # 速度を変える間隔（フレーム）
BOSS_REVERSE_CHANCE    = 0.25        # 速度を変えるとき、向きを反転する確率（0〜1）
BOSS_STAY_RANGE        = (240, 480)  # 画面にいる長さ（過ぎると一番近い端から退場）
BOSS_LEAVE_SPEED       = 9           # 退場するときの速度
 
# --- 攻撃のランダム設定 ---
BOSS_ATTACK_INTERVAL_RANGE = (40, 120)  # 次の攻撃を始めるまでの間隔（フレーム）
BOSS_ATTACKS = {
    # 攻撃名: weight=出やすさ(大きいほど多い) / charge=チャージ時間の範囲 / fire=発射時間の範囲
    # チャージ中はボスが止まる＝プレイヤーが避ける猶予。使いたくない攻撃は行ごと消せばOK
    "beam":   dict(weight=3, charge=(30, 60), fire=(20, 35)),   # 単発ビーム（ボスの真下）
    "triple": dict(weight=2, charge=(45, 70), fire=(20, 30)),   # 3連ビーム（左右にも出る）
    "shots":  dict(weight=2, charge=(20, 35), fire=(30, 50)),   # 連射弾（ばらまき）
}
BOSS_TRIPLE_GAP_RANGE = (90, 170)  # 3連ビームの間隔（px）
BOSS_SHOT_EVERY       = 5          # 連射弾を撃つ間隔（フレーム）
BOSS_BEAM_PENALTY     = -20        # ビームに当たったときのスコア（1回の攻撃につき1回だけ）
BOSS_SHOT_PENALTY     = -10        # 連射弾に当たったときのスコア（1発ごと）
 
# --- 攻撃エフェクトの色（外側から順に）---
BOSS_FX_OUTLINE = (170, 90, 20)     # ふちどり（明るい背景でも見えるように）
BOSS_FX_OUTER   = (255, 200, 60)    # 外側の黄色
BOSS_FX_INNER   = (255, 245, 170)   # 内側の薄い黄色
BOSS_FX_CORE    = (255, 255, 255)   # 中心の白
BOSS_FX_DIM     = (200, 120, 40)    # 火花の消えかけ
 
# --- 目と動き ---
BOSS_EYE_COLORS   = [(255, 60, 40), (255, 220, 80)]  # 目の色（順番に切り替わる）
BOSS_EYE_ATTACK   = (255, 255, 255)                  # 攻撃中の目の色
BOSS_EYE_FRAMES   = 10    # 目の色を切り替える間隔（フレーム）
BOSS_BOB_PIXELS   = 4     # 上下に揺れる幅（0で揺れなし）
BOSS_BOB_FRAMES   = 15    # 揺れを切り替える間隔（フレーム）
 
"""ボスの色: 文字と色の対応表"""
BOSS_PALETTE = {
    ".": None,               # 透明
    "K": (20, 12, 28),       # 輪郭
    "W": (240, 232, 210),    # 角・牙
    "P": (110, 40, 140),     # 紫(兜・マント)
    "p": (160, 90, 190),     # 紫ハイライト
    "D": (45, 20, 60),       # 顔の影
    "E": (255, 60, 40),      # 目 ※実際の色は BOSS_EYE_COLORS が優先される
    "G": (90, 96, 120),      # 鎧
    "g": (150, 158, 185),    # 鎧ハイライト
    "R": (220, 30, 60),      # 宝石・兜の飾り
    "Y": (250, 200, 60),     # 金の装飾(ベルト)
}
 
 
"""ボスの形：1文字=1ドット。左半分(16文字x32行)だけ描く 右半分は自動で左右反転される。
右側の行末が「体の中心」"""
BOSS_HALF = [
    "................",  #  0 余白
    ".K.........KKKKK",  #  1 角の先 / 兜の飾り
    "KWK.......KRRRRR",  #  2 角 / 兜の飾り(赤)
    "KWWK.....KKRRRRR",  #  3 角 / 兜の飾り(赤)
    "KWWWK..KKKPPPPPP",  #  4 角 / 兜
    ".KWWWKKPPPPPPPPP",  #  5 角 / 兜
    ".KWWKKPPPppPPPPP",  #  6 角 / 兜(ハイライト)
    "..KWKPPPPPPPPPPP",  #  7 角の根元 / 兜
    "..KKKPKKKKKKKKKK",  #  8 兜のふち
    "....KKDDDDDDDDDD",  #  9 顔
    "....KKDDEDDDDDDD",  # 10 顔(目:上)
    "....KKDDEEEEDDDD",  # 11 顔(目:下)
    "....KKDDDDDDDDDD",  # 12 顔
    "....KKDDWDWDWDWD",  # 13 顔(牙)
    "....KKDDDDDDDDDD",  # 14 顔
    "......KKKKKKKKKK",  # 15 あご
    ".KggGGKKKGGGGGGG",  # 16 肩 / 胸
    "KggGGGGKGGggGGGG",  # 17 肩 / 胸
    "KgGGGGGKGGGGGGGR",  # 18 肩 / 胸(宝石)
    "KKGGGGKKGGGGGGRR",  # 19 肩 / 胸(宝石)
    ".KPPPKKGGGGGGRRR",  # 20 マント / 胸(宝石)
    "..KPPKKGGGGGGGRR",  # 21 マント / 胸(宝石)
    "..KPPPKKGGGGGGGR",  # 22 マント / 胸(宝石)
    "..KPPPPKKKKKKKKK",  # 23 マント / ベルトの上線
    "..KPPPPKYGYGYGYG",  # 24 マント / ベルト(金の飾り)
    "..KPPPPPKGGGGGK.",  # 25 マント / 足
    "..KPPPPPKGGGGGK.",  # 26 マント / 足
    "..KPPPPKKGGGGGK.",  # 27 マント / 足
    "..KPPPKKGGGGGGK.",  # 28 マント / 足
    "...KKKKGGGGGGGK.",  # 29 足
    "...KGGGGGGGGGGK.",  # 30 ブーツ
    "...KKKKKKKKKKKK.",  # 31 ブーツの底
]
 
def make_boss_image(eye_color=None):
    """ドット絵データから pygame の Surface を作る"""
    pal = dict(BOSS_PALETTE)
    if eye_color:
        pal["E"] = eye_color
    w = len(BOSS_HALF[0]) * 2
    h = len(BOSS_HALF)
    surf = pg.Surface((w, h), pg.SRCALPHA)
    for y, row in enumerate(BOSS_HALF):
        for x, ch in enumerate(row + row[::-1]):  # 左右ミラー
            if pal[ch] is not None:
                surf.set_at((x, y), pal[ch])
    # transform.scale は補間なし(ドットがボケない)
    return pg.transform.scale(surf, (w * BOSS_SCALE, h * BOSS_SCALE))
 
def _fx_dot(screen, gx, gy, color):
    d = BOSS_SCALE
    pg.draw.rect(screen, color, (gx * d, gy * d, d, d))
 
def _fx_disc(screen, cx, cy, r, color):
    """ドット絵風の丸"""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5:
                _fx_dot(screen, x, y, color)
 
def draw_boss_orb(screen, cx, cy, r):
    """チャージ玉：ふちどり → 外側 → 内側 → 中心"""
    _fx_disc(screen, cx, cy, r + 1, BOSS_FX_OUTLINE)
    _fx_disc(screen, cx, cy, r, BOSS_FX_OUTER)
    if r >= 2:
        _fx_disc(screen, cx, cy, r - 1, BOSS_FX_INNER)
    if r >= 3:
        _fx_disc(screen, cx, cy, r - 2, BOSS_FX_CORE)
 
_SPARK_DIRS = [(0.92, 0.38), (0.38, 0.92), (-0.38, 0.92), (-0.92, 0.38),
               (-0.92, -0.38), (-0.38, -0.92), (0.38, -0.92), (0.92, -0.38)]
 
def draw_boss_sparks(screen, cx, cy, d):
    """チャージ玉に向かって集まる火花"""
    for ux, uy in _SPARK_DIRS:
        _fx_dot(screen, round(cx + d * ux), round(cy + d * uy), BOSS_FX_OUTLINE)
        _fx_dot(screen, round(cx + (d + 3) * ux), round(cy + (d + 3) * uy), BOSS_FX_DIM)
 
def draw_boss_beam(screen, cx, top_gy, end_gy, hw, seed):
    """縦のビーム。端をランダムに欠けさせてギザギザ(ちらつき)にする"""
    rnd = random.Random(seed)
    for gy in range(top_gy, end_gy + 1):
        for dx in range(-hw - 1, hw + 2):
            d = abs(dx)
            if d == 0:
                c = BOSS_FX_CORE
            elif d == 1:
                c = BOSS_FX_INNER
            elif d <= hw:
                if rnd.random() < 0.3:      # 端のドットを欠けさせる
                    continue
                c = BOSS_FX_OUTER
            else:
                c = BOSS_FX_OUTLINE
            _fx_dot(screen, cx + dx, gy, c)
 
def draw_boss_impact(screen, ix, iy, n, seed):
    """着弾の爆発：上向きに伸びる星 + 飛び散る火花（ix, iy は画面のpx座標）"""
    cx, cy = ix // BOSS_SCALE, iy // BOSS_SCALE
    for dx, dy in [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1)]:
        length = n * 2 if dx == 0 or dy == 0 else int(n * 1.5)
        for k in range(1, length + 1):
            if k <= 2:
                c = BOSS_FX_INNER
            elif k < length:
                c = BOSS_FX_OUTER
            else:
                c = BOSS_FX_OUTLINE
            _fx_dot(screen, cx + dx * k, cy + dy * k, c)
    if n <= 3:
        _fx_disc(screen, cx, cy, min(n, 3) + 1, BOSS_FX_OUTLINE)
        _fx_disc(screen, cx, cy, min(n, 3), BOSS_FX_INNER)
    if n >= 3:
        rnd = random.Random(seed)
        for _ in range(12):
            rx = rnd.randint(-(4 + n * 2), 4 + n * 2)
            ry = -rnd.randint(2, 4 + n * 2)
            _fx_dot(screen, cx + rx, cy + ry, BOSS_FX_OUTER if n == 3 else BOSS_FX_DIM)

class BossManager:
    """ボス本体。状態は move(移動) → charge(チャージ) → fire(発射) → move ... と回る
    出てくるたびに「向き・速さ・高さ」が、攻撃のたびに「種類・タイミング」がランダムに決まる"""
 
    def __init__(self):
        self.active = False
        # 目の色ごとに画像を用意して、交互に切り替える
        self.images = [make_boss_image(c) for c in BOSS_EYE_COLORS]
        self.image_attack = make_boss_image(BOSS_EYE_ATTACK)
        self.rect = self.images[0].get_rect(topleft=(0, BOSS_Y_RANGE[0]))
        self.timer = 0
        self.next_appear = random.randint(*BOSS_APPEAR_RANGE)
        self.anim = 0
        # 動き
        self.dir = 1              # 進む向き（1=右 / -1=左）
        self.speed = 0
        self.entered = False      # 一度でも画面内に入ったか
        self.leaving = False      # 退場モードか
        self.life = 0             # 画面にいる残り時間
        self.move_timer = 0       # 次に速度を変えるまで
        # 攻撃
        self.state = "move"
        self.state_t = 0
        self.atk_timer = 0
        self.next_attack_in = 0
        self.attack = "beam"      # 今の攻撃の種類
        self.charge_frames = 1
        self.fire_frames = 1
        self.beam_xs = []         # ビーム（や玉）のx座標
        self.impacts = []         # 着弾位置
        self.hit_done = False
        self.shots = []           # 連射弾 [x, y, vx, vy]
        self.fade = 0
 
    # --- 補助 ---
    def _orb_gpos(self):
        """チャージ玉・ビームの発射位置（ドット単位）"""
        d = BOSS_SCALE
        return self.rect.centerx // d, (self.rect.bottom + 3 * d) // d
 
    def _beam_half_width(self):
        """ビームの太さ：細 → 太 → 細 と変化する"""
        ratio = self.state_t / self.fire_frames
        if ratio < 0.15:
            return 1
        if ratio < 0.3:
            return 2
        if ratio < 0.75:
            return 3
        if ratio < 0.9:
            return 2
        return 1
 
    def _appear(self):
        """出現：向き・速さ・高さ・滞在時間をランダムに決める"""
        self.active = True
        self.dir = random.choice((-1, 1))
        self.rect.x = -self.rect.width if self.dir == 1 else 800
        self.rect.y = random.randint(*BOSS_Y_RANGE)
        self.speed = random.randint(*BOSS_SPEED_RANGE)
        self.life = random.randint(*BOSS_STAY_RANGE)
        self.move_timer = random.randint(*BOSS_MOVE_CHANGE_RANGE)
        self.next_attack_in = random.randint(*BOSS_ATTACK_INTERVAL_RANGE)
        self.entered = False
        self.leaving = False
        self.timer = 0
        self.anim = 0
        self.state = "move"
        self.atk_timer = 0
 
    def _start_attack(self):
        """攻撃の種類・チャージ時間・発射時間をランダムに決めてチャージ開始"""
        names = list(BOSS_ATTACKS)
        weights = [BOSS_ATTACKS[n]["weight"] for n in names]
        self.attack = random.choices(names, weights)[0]
        cfg = BOSS_ATTACKS[self.attack]
        self.charge_frames = random.randint(*cfg["charge"])
        self.fire_frames = random.randint(*cfg["fire"])
        cx = self.rect.centerx
        if self.attack == "triple":
            gap = random.randint(*BOSS_TRIPLE_GAP_RANGE)
            self.beam_xs = [cx - gap, cx, cx + gap]
        else:
            self.beam_xs = [cx]
        self.state = "charge"
        self.state_t = 0
 
    def _update_move(self):
        self.rect.x += self.dir * self.speed
        if not self.entered and 0 < self.rect.centerx < 800:
            self.entered = True
        if self.entered:
            self.atk_timer += 1
            on_screen = 60 < self.rect.centerx < 740
            if not self.leaving:
                self.life -= 1
                self.move_timer -= 1
                if self.life <= 0:
                    # 退場：一番近い端へ向かう
                    self.leaving = True
                    self.dir = 1 if self.rect.centerx >= 400 else -1
                    self.speed = BOSS_LEAVE_SPEED
                elif self.move_timer <= 0:
                    # 速度をランダムに変える（ときどき向きも反転）
                    self.speed = random.randint(*BOSS_SPEED_RANGE)
                    if on_screen and random.random() < BOSS_REVERSE_CHANCE:
                        self.dir *= -1
                    self.move_timer = random.randint(*BOSS_MOVE_CHANGE_RANGE)
                if (BOSS_ATTACKS and not self.leaving and on_screen
                        and self.atk_timer >= self.next_attack_in):
                    self._start_attack()
            # 画面の外に出たら退場完了
            if self.rect.x > 800 or self.rect.right < 0:
                self.active = False
                self.timer = 0                     # 消えてから次の出現までを数え直す
                self.next_appear = random.randint(*BOSS_APPEAR_RANGE)
 
    # --- 更新 ---
    def update(self, player_rect):
        penalty = 0
        d = BOSS_SCALE
        self.timer += 1
        if self.timer > self.next_appear and not self.active:
            self._appear()
 
        if self.active:
            self.anim += 1
 
            if self.state == "move":
                self._update_move()
 
            elif self.state == "charge":
                self.state_t += 1
                if self.state_t >= self.charge_frames:
                    self.state = "fire"
                    self.state_t = 0
                    self.hit_done = False
                    self.impacts = ([] if self.attack == "shots"
                                    else [(bx, 592) for bx in self.beam_xs])
 
            elif self.state == "fire":
                self.state_t += 1
                _, ogy = self._orb_gpos()
                top = ogy * d
                if self.attack == "shots":
                    # ランダムな向き・速さの弾を一定間隔でばらまく
                    if self.state_t % BOSS_SHOT_EVERY == 0:
                        self.shots.append([float(self.rect.centerx), float(top),
                                           random.uniform(-4, 4), random.uniform(5, 9)])
                else:
                    hw = self._beam_half_width()
                    self.impacts = []
                    for bx in self.beam_xs:
                        gx = bx // d
                        beam_rect = pg.Rect((gx - hw - 1) * d, top, (2 * hw + 3) * d, 600 - top)
                        hit_now = beam_rect.colliderect(player_rect)
                        # 着弾位置：プレイヤーに当たっていればその上、外れていれば床
                        self.impacts.append((bx, max(top, player_rect.top if hit_now else 592)))
                        if hit_now and not self.hit_done:
                            penalty += BOSS_BEAM_PENALTY   # 1回の攻撃で1回だけ
                            self.hit_done = True
                if self.state_t >= self.fire_frames:
                    self.state = "move"
                    self.atk_timer = 0
                    self.next_attack_in = random.randint(*BOSS_ATTACK_INTERVAL_RANGE)
                    if self.attack != "shots":
                        self.fade = 10                   # 着弾の余韻
 
        # 連射弾：ボスが退場したあとも飛び続ける
        for s in self.shots[:]:
            s[0] += s[2]
            s[1] += s[3]
            if pg.Rect(int(s[0]) - 6, int(s[1]) - 6, 12, 12).colliderect(player_rect):
                penalty += BOSS_SHOT_PENALTY
                self.shots.remove(s)
            elif s[1] > 620 or s[0] < -20 or s[0] > 820:
                self.shots.remove(s)
 
        if self.fade > 0:
            self.fade -= 1
        return penalty
 
    # --- 描画 ---
    def draw(self, screen):
        d = BOSS_SCALE
        if self.active:
            # 状態ごとの目の色
            if self.state == "move":
                img = self.images[(self.anim // BOSS_EYE_FRAMES) % len(self.images)]
            elif self.state == "charge":
                img = self.images[-1] if (self.anim // 6) % 2 else self.image_attack
            else:
                img = self.image_attack
            bob = -BOSS_BOB_PIXELS if (self.anim // BOSS_BOB_FRAMES) % 2 else 0
            shake = (d if (self.state_t // 2) % 2 else -d) if self.state == "fire" else 0
            screen.blit(img, (self.rect.x + shake, self.rect.y + bob))
 
            _, ogy = self._orb_gpos()
            if self.state == "charge":
                ratio = self.state_t / self.charge_frames
                for bx in self.beam_xs:
                    draw_boss_sparks(screen, bx // d, ogy, int(10 - 8 * ratio))
                    draw_boss_orb(screen, bx // d, ogy, 1 + int(3 * ratio))
            elif self.state == "fire":
                if self.attack != "shots":
                    hw = self._beam_half_width()
                    for bx, iy in self.impacts:
                        draw_boss_beam(screen, bx // d, ogy, iy // d, hw, self.anim + bx)
                for bx in self.beam_xs:
                    draw_boss_orb(screen, bx // d, ogy, 4)
                for ix, iy in self.impacts:
                    draw_boss_impact(screen, ix, iy, min(3, self.state_t // 4 + 1), self.anim)
 
        # 発射が終わったあとの着弾の余韻
        if self.fade > 0 and self.state != "fire":
            for ix, iy in self.impacts:
                draw_boss_impact(screen, ix, iy, 4, self.anim)
 
        # 連射弾
        for s in self.shots:
            draw_boss_orb(screen, int(s[0]) // d, int(s[1]) // d, 2)


# =========================================================
# 【担当者3：特殊アイテム（金のリンゴ等）のエリア】
# =========================================================


# =========================================================
# 【担当者4：コンボシステムのエリア】
class ComboSystem:
    def __init__(self):
        self.combo = 0
        self.last_time = 0
        self.font = pg.font.SysFont(None, 50)
        self.effects = []
    def update(self):
        if self.combo > 0 and (pg.time.get_ticks() - self.last_time) > 2000:
            self.combo = 0
        for e in self.effects[:]:
            e['y'] -= 2
            e['life'] -= 1
            if e['life'] <= 0:
                self.effects.remove(e)
    def add_combo(self):
        self.combo += 1
        self.last_time = pg.time.get_ticks()
        bonus = 0
        if self.combo > 1:
            bonus = self.combo * 2
            self.effects.append({'text': f"{self.combo} COMBO! +{bonus}", 'y': 300, 'life': 30})
        return bonus
    def draw(self, screen):
        for e in self.effects:
            text = self.font.render(e['text'], True, (255, 100, 50))
            screen.blit(text, (400 - text.get_width()//2, e['y']))
# =========================================================


# =========================================================
# 【担当者5：シーン・UI演出（タイトル等）のエリア】
# =========================================================


# =========================================================
# ▼▼▼ 共通ベースクラス（代表者が作成。基本はいじらない） ▼▼▼
# =========================================================
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((80, 20))
        self.image.fill((0, 100, 255))
        self.rect = self.image.get_rect(center=(400, 550))

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 8
        if keys[pg.K_RIGHT] and self.rect.right < 800:
            self.rect.x += 8

class Apple(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(random.randint(20, 780), 0))
        self.speed = random.randint(4, 7)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()
# =========================================================
# ▲▲▲ 共通ベースクラス ここまで ▲▲▲
# =========================================================

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("アイテムキャッチ・パニック - 共同開発ベース")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 36)

    all_sprites = pg.sprite.Group()
    apples = pg.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    start_ticks = pg.time.get_ticks()
    game_duration = 60000 # 60秒

    # =========================================================
    # 【各機能の初期化（インスタンス生成）エリア】
    # =========================================================
    # 各担当者はここに自分のクラスをインスタンス化するコードを書く
    combo_system = ComboSystem()
    
    boss_manager = BossManager()

    score = 0
    start_ticks = pg.time.get_ticks()
    game_duration = 60000 # 60秒
    
    # 担当者5用：ゲームの進行状態
    game_state = "PLAY" 

    # --- 背景画像の読み込みとサイズ調整（これを追記） ---
    bg_image = pg.image.load("haikei1.png")
    bg_image = pg.transform.scale(bg_image, (800, 600))
    while True:
        # --- イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            # =========================================================
            # 【各機能のイベントハンドラ呼び出しエリア】
            # =========================================================
            # 担当者5などはここにキー入力処理を書く

        seconds_left = max(0, (game_duration - (pg.time.get_ticks() - start_ticks)) // 1000)

        # --- 更新処理 (Update) ---
        if seconds_left > 0:
            all_sprites.update()
            
            # =========================================================
            # 【各機能の更新（update）呼び出しエリア】
            # =========================================================
            # 各担当者はここに自身のupdate処理を書く
            combo_system.update()


            score += boss_manager.update(player.rect)

            score += boss_manager.update(player.rect)

            # 共通：アイテムのランダム生成
            if random.randint(1, 30) == 1:
                apple = Apple()
                all_sprites.add(apple)
                apples.add(apple)

            # 共通：当たり判定（キャッチ）
            caught_apples = pg.sprite.spritecollide(player, apples, True)
            for apple in caught_apples:
                score += 10
                # =========================================================
                # 【キャッチ時の追加イベント呼び出しエリア】
                # =========================================================
                # 担当者4（コンボ）などはここに処理を書く
                score += combo_system.add_combo()
        
        # --- 描画処理 (Draw) ---
        #screen.fill((240, 255, 240))
        screen.blit(bg_image, (0, 0))
        all_sprites.draw(screen)

        # =========================================================
        # 【各機能の描画（draw）呼び出しエリア】
        # =========================================================
        # 各担当者はここに自身のdraw処理を書く
        combo_system.draw(screen)

        boss_manager.draw(screen)

        boss_manager.draw(screen)

        # 共通：UI描画
        score_text = font.render(f"Score: {score}", True, (0, 255, 255))
        time_text = font.render(f"Time: {seconds_left}", True, (0, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (680, 10))

        if seconds_left == 0:
            end_text = font.render("TIME UP!", True, (255, 0, 0))
            screen.blit(end_text, (350, 300))

        # =========================================================
        # 【最前面UI・シーンの描画エリア】
        # =========================================================
        # 担当者5（シーン）はここに最終的な画面オーバーレイを描く

        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()