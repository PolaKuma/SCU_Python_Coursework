from . import config as c
from . import level
from . import sprites
from . import sounds
from .basetypes import Camera, Vector2, Rectangle, Digit_System
import pygame as pg
from .components import mario

class Main():
    """包含主循环并处理游戏"""
    def __init__(self):
        c.camera = Camera(Vector2(), c.SCREEN_SIZE.x, c.SCREEN_SIZE.y)  # 实例化屏幕
        c.mario = mario.Mario(Rectangle(c.MARIO_START_POSITION, 36, 48))    # 实例化马里奥

        pg.mixer.music.load(sounds.main_theme)      # 载入音乐
        pg.mixer.music.play()                       # 播放音乐

        self.quit_state = None      # 退出参数
        self.out_of_time = False    # 超时参数

        self.score_system = Digit_System(Vector2(66, 49), 6)    # 在屏幕上显示总分
        self.coin_score = Digit_System(Vector2(306, 49), 2)     # 在屏幕上显示收集的硬币
        self.time = Digit_System(Vector2(610, 49), 3, 300)      # 在屏幕上显示时间
        self.timer = 0                                          # 用于倒计时游戏时间的计时器

    def draw(self):
        """画出所有对象到当前屏幕中"""
        c.screen.fill(c.BACKGROUND_COLOR)
        self.draw_background()
        
        for item in (level.coins + level.super_mushrooms):
            if item.deployed:
                item.draw()

        for tile in level.dynamic_colliders:
            if c.camera.contains(tile.rect):
                view_pos = c.camera.to_view_space(tile.pos)
                tile.draw(view_pos)

        for enemy in level.enemies:
            if enemy.is_active:
                enemy.draw()

        for fragment in level.brick_fragments:
            fragment.draw()

        c.flagpole.draw_flag()

        c.mario.draw()

        self.draw_foreground()
        self.draw_digit_systems()

    def draw_background(self):
        """根据相机位置从背景图像中提取矩形"""
        c.screen.blit(sprites.background, 
                      (0, 0), 
                      (c.camera.pos.x, c.camera.pos.y, c.SCREEN_SIZE.x, c.SCREEN_SIZE.y))

    def draw_foreground(self):
        """在关卡的最后绘制前景，使马里奥消失在城堡后面"""
        view_pos = c.camera.to_view_space(c.FOREGROUND_POS)
        if view_pos.x < c.camera.pos.x + c.SCREEN_SIZE.x:
            c.screen.blit(sprites.foreground, (view_pos.x, view_pos.y))
        c.screen.blit(sprites.text_image, (0,0))

    def draw_digit_systems(self):
        """在屏幕上绘制所有数字系统"""
        self.score_system.draw()
        self.coin_score.draw()
        self.time.draw()

    def handle_digit_systems(self):
        """更新所有屏幕数字系统"""
        if not c.mario.current_mario_state == 'Dead_Mario':
            self.handle_time()
            self.score_system.update_value(c.total_score)
            self.coin_score.update_value(c.collected_coins)

    def handle_time(self):
        """处理委派给屏幕计时器的事件"""

        # 倒计时
        self.timer += c.delta_time
        if not c.final_count_down and self.timer > 14 * c.delta_time:
            self.time.update_value(self.time.total_value - 1)
            self.timer = 0

        # 如果计时器低于 100，则播放超时音乐
        if not c.mario.current_mario_state == 'Win_State':
            if not c.final_count_down and self.time.total_value < 100 and not self.out_of_time:
                pg.mixer.music.stop()
                pg.mixer.music.set_endevent(c.OUT_OF_TIME_END)
                pg.mixer.music.load(sounds.out_of_time)
                pg.mixer.music.play()
                self.out_of_time = True

        # 如果计时器用完并且马里奥没有获胜，杀死马里奥
        if not c.final_count_down and self.time.total_value == 0:
            c.mario.mario_states.on_event('dead')

        # 如果马里奥赢了并且时间仍然 > 0，倒计时并加分
        if c.final_count_down and self.time.total_value > 0:
            self.time.update_value(self.time.total_value - 1)
            c.total_score += c.TIME_SCORE
            sounds.count_down.play()
            sounds.count_down.set_volume(0.15)
            if self.time.total_value == 0:
                sounds.count_down.stop()
                sounds.coin.play()

    def update_level(self):
        """更新关卡中的所有游戏对象"""
        c.mario.update()
        c.mario.physics_update()
        c.camera.update()
        for tile in level.dynamic_colliders:
            tile.update()

        for item in (level.coins + level.super_mushrooms):
            if item.deployed:
                item.update()

        if not c.mario.freeze_movement:
            for enemy in level.enemies:
                if enemy.pos.x < c.camera.pos.x + c.SCREEN_SIZE.x:
                    enemy.is_active = True
                enemy.update()

        for fragment in level.brick_fragments:
            fragment.update()

        c.flagpole.update()

    def check_for_quit(self):
        """用于退出应用程序或返回菜单的事件管理器"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == c.WIN_SONG_END and self.time.total_value == 0:
                self.quit_state = 'menu'
                return False

            if event.type == c.DEATH_SONG_END:
                self.quit_state = 'menu'
                return False

            if event.type == c.OUT_OF_TIME_END:
                pg.mixer.music.stop()
                pg.mixer.music.load(sounds.main_theme_sped_up)
                pg.mixer.music.play()

        if c.mario.to_menu:
            self.quit_state = 'menu'
            return False

        if c.keys[pg.K_ESCAPE]:
            return False
        return True


    def main_loop(self):
        """主游戏循环，每帧更新和绘制关卡"""
        while True:
            c.delta_time = c.clock.tick(60)     # 定义游戏为60帧
            c.keys = pg.key.get_pressed()

            self.update_level()
            self.handle_digit_systems()
            self.draw()

            if not self.check_for_quit():
                break

            pg.display.update()