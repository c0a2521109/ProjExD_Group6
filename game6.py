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
        screen.fill((240, 255, 240))
        all_sprites.draw(screen)

        # =========================================================
        # 【各機能の描画（draw）呼び出しエリア】
        # =========================================================
        # 各担当者はここに自身のdraw処理を書く
        combo_system.draw(screen)

        boss_manager.draw(screen)

        # 共通：UI描画
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {seconds_left}", True, (0, 0, 0))
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