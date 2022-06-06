from ..basetypes import Game_Object, Vector2, Entity
from .. import config as c
from .. import sprites
from .. import sounds
from .. import level
from ..utils import accelerate

class Coin(Game_Object):
    """硬币物品类别"""
    def __init__(self, rect):
        super(Coin, self).__init__(rect)    # 继承矩形类
        self.animation = self.Animation(self.pos.y)     # 定义动画实例
        self.deployed = False   # 定义是否被部署
        self.collected = False  # 定义是否被收集

    def update(self):
        self.animation.anim()
        self.pos.y = self.animation.new_y
        if self.animation.bounce_iteration > 23:
            self.collected = True

        self.check_for_destroy()

    def check_for_destroy(self):
        """检查实例是否可以被销毁"""
        if self.collected:
            level.coins.remove(self)

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    class Animation():
        """包含该类的特定动画变量和函数"""
        def __init__(self, start_height):
            self.current_sprite = sprites.COIN[0]

            self.start_height = start_height
            self.new_y = start_height
            self.anim_timer = c.INITIAL_TIMER_VALUE
            self.anim_frame = 0
            self.bounce_iteration = 0

        def anim(self):
            """旋转动画"""
            self.current_sprite = sprites.COIN[self.anim_frame % 4]
            self.anim_timer += c.delta_time
            if self.anim_timer > 3 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.bounce_iteration += 0.6

            self.new_y = self.start_height - self.anim_function(self.bounce_iteration)

        def anim_function(self, bounce_iteration):
            """根据二次函数返回新的 y 以创建反弹"""
            return -(bounce_iteration - 12) ** 2 + 144

class Super_Mushroom(Entity):
    """超级蘑菇类"""
    """类似于硬币类，故部分函数不多赘述"""
    def __init__(self, rect, vel):
        super(Super_Mushroom, self).__init__(vel, rect)

        self.deployed = False
        self.collected = False

        self.animation = self.Animation(self.pos.y)

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), sprites.SUPER_MUSHROOM)

    def update(self):
        if self.animation.has_animated:
            accelerate(self, 0, c.GRAVITY)
            self.move()
        else:
            self.animation.deploy_anim()
            self.pos.y = self.animation.new_y

        self.check_for_destroy()

    def check_for_destroy(self):
        """检查实例是否可以被销毁"""
        if self.collected:
            sounds.powerup.play()
            c.total_score += c.MUSHROOM_SCORE
            level.super_mushrooms.remove(self)

    def move(self):
        """分离 x 和 y 运动"""
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """检查 x 或 y 移动是否导致碰撞"""
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)

        if other_collider is None:
            return
        if dx > 0:
            self.pos.x = other_collider.pos.x - self.rect.w
            self.vel.x = -self.vel.x
        elif dx < 0:
            self.pos.x = other_collider.pos.x + other_collider.rect.w
            self.vel.x = -self.vel.x
        elif dy > 0:
            self.pos.y = other_collider.pos.y - self.rect.h
            self.vel.y = 0
        
    class Animation():
        """包含该类的特定动画变量和函数"""
        def __init__(self, start_height):
            self.new_y = start_height
            self.anim_iteration = 0
            self.has_animated = False

        def deploy_anim(self):
            """部署超级蘑菇时的动画"""
            if self.anim_iteration == 48:
                self.has_animated = True
            if not self.has_animated:
                self.new_y -= 1
                self.anim_iteration += 1 
