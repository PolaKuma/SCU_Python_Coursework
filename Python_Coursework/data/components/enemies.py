from .. import config as c
from ..basetypes import Vector2, Entity, State, State_Machine, Rectangle
from .. import sprites
from .. import sounds
from ..utils import accelerate
from .. import level

class Goomba(Entity):
    """Goomba类"""
    def __init__(self, rect, vel):
        super(Goomba, self).__init__(vel, rect)     # 继承速度，矩形方法
        self.animation = self.Animation()           # 实例化一个动画对象
        self.state_machine = State_Machine(self.Run_State(), self)  # 实例化一个状态管理
        self.vel.x = c.ENEMY_START_VEL_X    # 初始化敌人移动速度

        self.is_active = False      # goomba是否活动
        self.can_kill = True        # goomba是否可杀死

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)     # 获取显示范围，判断是否显示
        if c.camera.contains(self.rect):
            c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    def update(self):
        self.state_machine.update()     # 更新状态
        if self.is_active:
            if all(self.state_machine.get_state() != state for state in ['Squish_State', 'Dead_State']):
                accelerate(self, 0, c.GRAVITY)
                self.move()     # 如果goomba不处于踩扁或死亡状态就移动
        self.check_for_destroy()    # 更新goomba摧毁状态

    def check_for_destroy(self):
        """检查实例是否可以被销毁"""
        if self.pos.y > c.SCREEN_SIZE.y:    # 当goomba超出屏幕显示范围就摧毁（不显示）
            level.enemies.remove(self)

    def move(self):
        """拆分 x 和 y 运动"""
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """更新位置"""
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        if self.state_machine.get_state() != 'Knocked_State':
            self.check_collisions(dx, dy)   # 更新位置后检查碰撞

    def check_collisions(self, dx, dy):
        """检查 x 或 y 移动是否导致碰撞"""
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)   # 与砖块实体碰撞
        other_enemy = self.rect.check_collisions([enemy for enemy in level.enemies if enemy is not self and enemy.is_active])   # 与其他敌人碰撞

        if other_collider is None and other_enemy is None:
            return
        if other_collider is not None:  # 与实体砖块碰撞
            if dx > 0:
                self.pos.x = other_collider.pos.x - self.rect.w
                self.vel.x = -self.vel.x
            elif dx < 0:
                self.pos.x = other_collider.pos.x + other_collider.rect.w
                self.vel.x = -self.vel.x
            elif dy > 0:
                self.pos.y = other_collider.pos.y - self.rect.h
                self.vel.y = 0
        if hasattr(other_collider, 'state_machine') and any(other_collider.state_machine.get_state() == state for state in ['Bounce_State', 'Break_State']):
            self.state_machine.on_event('knocked')  # 如果踩扁或者移除状态就进入锁定状态，之后不检测碰撞
        if other_enemy is not None:     # 与其他敌人碰撞
            self.pos.x -= dx * c.delta_time
            self.vel.x = -self.vel.x


    class Animation():
        """包含该类的特定动画变量和函数"""
        def __init__(self):
            self.current_sprite = sprites.GOOMBA_RUN[0]     # 定义开始运动的图形

            self.anim_timer = c.INITIAL_TIMER_VALUE     # 定义运动时间
            self.anim_frame = 0

            self.squish_delay_over = False  # 是否被踩扁

        def run_anim(self):
            """跑步时动画"""
            self.current_sprite = sprites.GOOMBA_RUN[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 14 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

        def squish_delay(self):
            """goomba被踩扁的动画"""
            self.anim_timer += c.delta_time
            if self.anim_timer > 20 * c.delta_time:
                self.squish_delay_over = True

        def reset_anim_vars(self):
            """重置动画参数"""
            self.anim_timer = 0
            self.anim_frame = 0

    class Run_State(State):
        """四处移动的状态"""
        def on_event(self, event):
            if event == 'knocked':
                return Goomba.Knocked_State()
            elif event == 'squish':
                return Goomba.Squish_State()
            return self

        def update(self, owner_object):
            owner_object.animation.run_anim()

        def on_exit(self, owner_object):
            owner_object.animation.reset_anim_vars()        

    class Knocked_State(State):
        """被砖块或龟壳敲击时的状态"""
        def on_event(self, event):
            if event == 'dead':
                return Goomba.Dead_State()
            return self

        def on_enter(self, owner_object):
            owner_object.vel.y = c.GOOMBA_KNOCKED_VEL_Y
            owner_object.animation.current_sprite = sprites.GOOMBA_KNOCKED
            c.total_score += c.GOOMBA_SCORE
            sounds.kick.play()

    class Squish_State(State):
        """被压扁时的状态"""
        def on_event(self, event):
            if event == 'dead':
                return Goomba.Dead_State()
            return self
    
        def on_enter(self, owner_object):
            owner_object.animation.current_sprite = sprites.GOOMBA_SQUISHED
            owner_object.rect = Rectangle(owner_object.pos, 0, 0)
            sounds.stomp.play()
            c.total_score += c.GOOMBA_SCORE

        def update(self, owner_object):
            owner_object.animation.squish_delay()
            if owner_object.animation.squish_delay_over:
                owner_object.state_machine.on_event('dead')

    class Dead_State(State):
        """死亡时的状态，摧毁 goomba 的实例"""
        def on_enter(self, owner_object):
            level.enemies.remove(owner_object)

class Turtle(Entity):
    """Turtle类"""
    """类似于goomba类，因此部分函数不多赘述"""
    def __init__(self, rect, vel):      # 相关变量与goomba类似
        super(Turtle, self).__init__(vel, rect)
        self.animation = self.Animation()
        self.state_machine = State_Machine(self.Run_State(), self)
        self.vel.x = c.ENEMY_START_VEL_X
        self.is_active = False

        self.can_kill = True

    def update(self):
        if self.is_active:
            accelerate(self, 0, c.GRAVITY)
            self.move()
            self.state_machine.update()
        self.check_for_destroy()

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        if c.camera.contains(self.rect):
            c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)
    
    def check_for_destroy(self):
        """检查实例是否可以被销毁"""
        if self.pos.y > c.SCREEN_SIZE.y:
            level.enemies.remove(self)
    
    def move(self):
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """根据速度移动位置"""
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        if self.state_machine.get_state() != 'Knocked_State':
            self.check_collisions(dx, dy)

    def check_collisions(self, dx, dy):
        """检查 x 或 y 移动是否导致碰撞并执行相应的操作"""
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)
        other_enemy = self.rect.check_collisions([enemy for enemy in level.enemies if enemy is not self])

        if other_collider is None and other_enemy is None:
            return
        if other_collider is not None:
            if dx > 0:
                self.pos.x = other_collider.pos.x - self.rect.w
                self.vel.x = -self.vel.x
            elif dx < 0:
                self.pos.x = other_collider.pos.x + other_collider.rect.w
                self.vel.x = -self.vel.x
            elif dy > 0:
                self.pos.y = other_collider.pos.y - self.rect.h
                self.vel.y = 0

        if other_enemy is not None:
            if self.state_machine.get_state() != 'Move_Shell':
                self.pos.x -= dx * c.delta_time
                self.vel.x = -self.vel.x
            else:
                other_enemy.state_machine.on_event('knocked')
                other_enemy.is_active = True

    class Animation():
        """包含该类的特定动画变量和函数"""
        def __init__(self):
            self.current_sprite = sprites.TURTLE[0]

            self.anim_timer = 0
            self.anim_frame = 0

        def run_anim(self):
            self.current_sprite = sprites.TURTLE[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 13 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

    class Run_State(State):
        """移动状态"""
        def on_event(self, event):
            if event == 'squish':
                return Turtle.Shell_State()
            return self

        def update(self, owner_object):
            owner_object.animation.run_anim()

    class Shell_State(State):
        """缩在龟壳的状态"""
        def on_event(self, event):
            if event == 'move shell':
                return Turtle.Move_Shell()
            return self

        def on_enter(self, owner_object):
            owner_object.rect.h = 42
            owner_object.pos.y += 30
            owner_object.animation.current_sprite = sprites.TURTLE_SHELL
            owner_object.vel.x = 0
            owner_object.can_kill = False
            sounds.stomp.play()

    class Move_Shell(State):
        """乌龟在壳中"""
        def __init__(self):
            self.can_kill_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            sounds.kick.play()

        def update(self, owner_object):
            self.can_kill_timer += c.delta_time
            if self.can_kill_timer > 10 * c.delta_time:
                owner_object.can_kill = True
