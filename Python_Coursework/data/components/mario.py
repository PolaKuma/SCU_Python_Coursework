from ..basetypes import Game_Object, Vector2, Entity, Rectangle, State_Machine, State
from .. import config as c
from .. import sprites
from .. import sounds
from ..utils import accelerate, clamp, get_flipped_sprite
from .. import level
import pygame as pg
import random

"""马里奥类"""
class Mario(Entity):
    def __init__(self, rect, vel = Vector2()):
        super(Mario, self).__init__(vel, rect)
        self.animation = self.Animation()   # 马里奥显示动画效果
        self.action_states = State_Machine(self.Idle_State(), self)     # 马里奥此时动作状态
        self.mario_states = State_Machine(self.Small_Mario(), self)     # 马里奥此时人物状态

        self.pressed_left = False       # 检测是否按下左键
        self.pressed_right = False      # 检测是否按下右键
        self.spacebar = False           # 检测是否按下跳跃
        self.crouch = False             # 检测是否按下蹲下
        self.freeze_movement = False    # 检测是否需要停止运动
        self.freeze_input = False       # 检测是否需要停止输入（到达边界等上限）

        self.flip_sprites = False       # 检测是否需要水平翻转
        self.to_menu = False            # 检测是否回到主菜单

        self.start_height = 0           # 定义马里奥刚开始的高度（无跳跃）

    def __getattr__(self, name):
        """获取马里奥属性"""
        if name == 'current_action_state':      # 获取马里奥此时运动状态
            return self.action_states.get_state()
        elif name == 'pos':                     # 获取马里奥此时坐标
            return self.rect.pos
        elif name == 'current_mario_state':     # 获取马里奥此时人物状态
            return self.mario_states.get_state()
        return object.__getattribute__(self, name)

    def draw(self):
        """从图中提取马里奥的图片并进行绘制"""
        if c.camera.contains(self.rect):    # 调整显示画面的坐标
            view_pos = c.camera.to_view_space(self.pos)
            if self.flip_sprites:           # 绘制反向运动的马里奥
                flipped_sprite = get_flipped_sprite(self.animation.current_sprite)
                c.screen.blit(sprites.tile_set_flipped, (view_pos.x, view_pos.y), flipped_sprite)
            else:                           # 绘制正向运动的马里奥
                c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    def update(self):
        """获取输入，并改变人物运动状态"""
        if not self.freeze_input:       # 首先判断此时是可输入状态
            if c.keys[pg.K_a] and not c.keys[pg.K_d]:   # 左移
                self.pressed_left = True
                c.ACCELERATION = -c.MARIO_ACCELERATION  # 调整马里奥速度为反向
            elif c.keys[pg.K_d] and not c.keys[pg.K_a]: # 右移
                self.pressed_right = True
                c.ACCELERATION = c.MARIO_ACCELERATION   # 调整马里奥速度为正向
            else:
                c.ACCELERATION = 0                      # 马里奥速度为0（不移动）

            """当不按下时，就停止人物运动，否则马里奥会一直动"""
            if not c.keys[pg.K_a]:
                self.pressed_left = False
            if not c.keys[pg.K_d]:
                self.pressed_right = False

            if c.keys[pg.K_SPACE] and not self.spacebar:    # 马里奥跳跃
                self.spacebar = True
                self.action_states.on_event('jump')
            if not c.keys[pg.K_SPACE]:
                self.spacebar = False

            if c.keys[pg.K_s]:                          # 马里奥蹲下
                self.crouch = True
            else:
                self.crouch = False

    def physics_update(self):
        """根据输入执行操作"""
        if self.current_mario_state != 'Invincible_Mario':      # 马里奥普通状态时
            self.mario_states.update()

        if not self.freeze_movement:                            # 保证键盘输入有效，获取输入信息
            self.state_events()
            self.action_states.update()
            self.movement()

            # 确保马里奥在跑下窗台时不会跳跃
            if self.pos.y > self.start_height:
                self.action_states.on_event('no jump')
                
            self.check_flip_sprites()       # 检查是否要翻转马里奥

        if self.current_mario_state == 'Invincible_Mario':      # 马里奥无敌状态时
            self.mario_states.update()

        self.rect.h = self.animation.current_sprite[3]          # 放大马里奥为原来三倍

        if self.pos.y > c.SCREEN_SIZE.y:                        # 确保马里奥在屏幕范围内，否则死亡
            self.mario_states.on_event('dead')

    def movement(self):
        """定义屏幕显示移动"""
        accelerate(self, c.ACCELERATION, c.GRAVITY, c.MAX_VEL)
        self.vel.x *= c.FRICTION
        self.move()

    def check_flip_sprites(self):
        """检查是否水平翻转马里奥"""
        if self.vel.x < 0:
            self.flip_sprites = True
        elif self.vel.x > 0:
            self.flip_sprites = False

    def state_events(self):
        """定义马里奥移动，减速，刹车，静止四个过程"""
        if any(self.current_action_state == state for state in ['Move_State', 'Decel_State', 'Brake_State', 'Idle_State']):
            self.start_height = self.pos.y      # 如果马里奥属于任何状态那么高度即为马里奥坐标

        if self.vel.y == 0:     # 马里奥在平底的移动
            if self.pressed_left or self.pressed_right:
                self.action_states.on_event('move')     # 移动状态

            if ((self.vel.x < 0 and not self.pressed_left) or
                (self.vel.x > 0 and not self.pressed_right)):
                self.action_states.on_event('decel')    # 停止按键，减速状态
            
            if ((self.vel.x < 0 and self.pressed_right) or
                (self.vel.x > 0 and self.pressed_left)):
                self.action_states.on_event('brake')    # 反向按键，刹车状态

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State':
                self.vel.x = 0
                self.action_states.on_event('idle')     # 静止状态

        if all(self.current_action_state != state for state in ['Decel_State', 'Brake_State', 'Crouch_State']):
            c.FRICTION = 1      # 增加摩擦力参数用于减速等运动

        if any(self.current_action_state == state for state in ['Jump_State', 'No_Jump_State']):    # 更新跳跃动画
            if self.animation.mario_size == 'Small_Mario':
                self.animation.current_sprite = sprites.SMALL_MARIO_JUMP
            else:
                self.animation.current_sprite = sprites.BIG_MARIO_JUMP

        if self.current_mario_state == 'Big_Mario':     # 大马里奥蹲下动画
            if self.crouch:
                self.action_states.on_event('crouch')

    def move(self):
        """分离x和y运动"""
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """根据速度移动并根据新位置检查碰撞"""
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time

        self.collider_collisions(dx, dy)
        if self.current_mario_state != 'Invincible_Mario':
            self.check_entity_collisions()

        self.check_backtrack()

    def check_backtrack(self):
        """阻止马里奥在关卡中往回走"""
        if self.pos.x < c.camera.pos.x:
            self.pos.x = clamp(self.pos.x, c.camera.pos.x, c.SCREEN_SIZE.x)     # 约束马里奥的坐标
            self.vel.x = 0   
            if all(self.current_action_state != state for state in ["Jump_State", "No_Jump_State"]):
                self.action_states.on_event('idle')      

    def collider_collisions(self, dx, dy):
        """检查与瓷砖的碰撞"""
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)

        if other_collider is None:
            return
        """碰撞后人物不能再升高"""
        if dx > 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x - self.rect.w
            self.vel.x = 0
        elif dx < 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x + other_collider.rect.w
            self.vel.x = 0
        elif dy > 0:
            if self.current_action_state == 'No_Jump_State':
                self.action_states.on_event('idle')
            self.pos.y = other_collider.pos.y - self.rect.h
            self.vel.y = 0
        elif dy < 0:
            self.interact_with_tile(other_collider)
            self.action_states.on_event('no jump')
            self.pos.y = other_collider.pos.y + other_collider.rect.h
            self.vel.y = c.BOUNCE_VEL

    def check_entity_collisions(self):
        """检查与实体的碰撞"""
        entities = self.rect.check_entity_collisions(level.super_mushrooms + level.enemies)

        for entity in entities:
            if entity.__class__.__name__ == 'Super_Mushroom' and entity.deployed:   # 遇到蘑菇时变大
                self.mario_states.on_event('grow')
                entity.collected = True

            if hasattr(entity, 'state_machine') and entity.state_machine.get_state() != 'Knocked_State':
                if entity.state_machine.get_state() == 'Shell_State':
                    if self.pos.x + self.rect.w < entity.pos.x + entity.rect.w / 2:
                        entity.vel.x = 0.5
                    elif self.pos.x + self.rect.w > entity.pos.x + entity.rect.w / 2:
                        entity.vel.x = -0.5
                    elif self.vel.x < 0:
                        entity.vel.x = -0.5
                    elif self.vel.x > 0:
                        entity.vel.x = 0.5
                    else:
                        entity.vel.x = random.choice([-0.5, 0.5])
                    entity.state_machine.on_event('move shell')

                elif self.pos.y + self.rect.h - self.vel.y * c.delta_time < entity.pos.y:       # 踩扁敌人交互
                    if entity.state_machine.get_state() == 'Run_State':
                        self.vel.y = c.STOMP_VEL
                        self.pos.y = entity.pos.y - self.rect.h
                        entity.state_machine.on_event('squish')
                        return
                else:   # 变大遇到敌人交互后缩小
                    if entity.state_machine.get_state() != 'Shell_State' and entity.can_kill:
                        self.mario_states.on_event('shrink')

    def interact_with_tile(self, tile):
        """根据当前马里奥状态与瓷砖交互"""
        if self.current_mario_state == 'Small_Mario':
            tile.state_machine.on_event('bounce')
            if tile.__class__.__name__ == 'Brick':
                sounds.bump.play()
        elif self.current_mario_state == 'Big_Mario':
            tile.state_machine.on_event('break')
            if tile.__class__.__name__ == 'Question':
                tile.state_machine.on_event('bounce')

    class Animation():
        """马里奥的特定动画变量和函数"""
        def __init__(self):
            self.current_sprite = sprites.SMALL_MARIO_IDLE

            self.mario_size = 'Small_Mario'
            self.anim_frame = 0
            self.anim_timer = c.INITIAL_TIMER_VALUE
            self.invincible_timer = 0

            self.start_height = None
            self.new_y = self.start_height

            self.grow_frames = [0, 1, 0, 1, 2, 0, 1, 2]
            self.shrink_frames = [0, 1, 0, 1, 2, 1, 2, 1]
            self.run_frames = [0, 1, 2, 1]
            self.start_sprite_height = 0

        def reset_anim_vars(self):
            """重置动画参数"""
            self.anim_frame = 0
            self.anim_timer = c.INITIAL_TIMER_VALUE

        def grow_anim(self):
            """马里奥变大动画"""
            self.current_sprite = sprites.GROW_SPRITES[self.grow_frames[self.anim_frame]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.new_y = self.start_height - (self.current_sprite[3] - 48)

        def run_anim(self):
            """马里奥跑步动画"""
            if self.mario_size == 'Small_Mario':
                self.current_sprite = sprites.SMALL_MARIO_RUN[self.run_frames[self.anim_frame % 4]]
            else:
                self.current_sprite = sprites.BIG_MARIO_RUN[self.run_frames[self.anim_frame % 4]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

        def shrink_anim(self):
            """马里奥缩小动画"""
            self.current_sprite = sprites.SHRINK_SPRITES[self.shrink_frames[self.anim_frame]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.new_y = self.start_height + (self.start_sprite_height - self.current_sprite[3])

        def win_anim_on_flag(self):
            """旗杆滑下时的动画"""
            if self.mario_size == 'Small_Mario':
                self.current_sprite = sprites.WIN_SPRITES_SMALL[self.anim_frame % 2]
            else:
                self.current_sprite = sprites.WIN_SPRITES_BIG[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 8 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

    class Idle_State(State):
        """在地上不动时的状态"""
        def on_enter(self, owner_object):
            if owner_object.animation.mario_size == 'Small_Mario':
                owner_object.animation.current_sprite = sprites.SMALL_MARIO_IDLE
            else:
                owner_object.animation.current_sprite = sprites.BIG_MARIO_IDLE
        
        def on_event(self, event):
            if event == 'jump':
                return Mario.Jump_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            return self

    class Jump_State(State):
        """空格键输入影响速度时跳跃时的状态"""
        def on_event(self, event):
            if event == 'no jump':
                return Mario.No_Jump_State()
            return self

        def on_enter(self, owner_object):
            if owner_object.current_mario_state == 'Small_Mario':
                sounds.small_jump.play()
            else:
                sounds.big_jump.play()
        
        def update(self, owner_object):
            owner_object.vel.y = c.JUMP_VELOCITY
            if (not owner_object.spacebar or 
                owner_object.pos.y < owner_object.start_height - c.MAX_JUMP_HEIGHT):
                owner_object.action_states.on_event('no jump')
        
    class No_Jump_State(State):
        """处于半空中但空格键输入不影响速度时的状态"""
        def on_event(self, event):
            if event == 'idle':
                return Mario.Idle_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'move':
                return Mario.Move_State()
            return self

    class Move_State(State):
        """在地面上移动且不刹车或减速时的状态"""
        def on_event(self, event):
            if event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def update(self, owner_object):
            if owner_object.pressed_left:
                c.ACCELERATION = -c.MARIO_ACCELERATION
            elif owner_object.pressed_right:
                c.ACCELERATION = c.MARIO_ACCELERATION
            owner_object.animation.run_anim()

    class Brake_State(State):
        """输入与速度相反时的状态"""
        def on_event(self, event):
            if event == 'move':
                return Mario.Move_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def on_enter(self, owner_object):
            c.ACCELERATION = 0
            c.FRICTION = c.BRAKE_FRICTION
            if owner_object.animation.mario_size == 'Small_Mario':
                owner_object.animation.current_sprite = sprites.SMALL_MARIO_BRAKE
            else:
                owner_object.animation.current_sprite = sprites.BIG_MARIO_BRAKE

    class Decel_State(State):
        """没有任何输入时移动时的状态"""
        def on_event(self, event):
            if event == 'idle':
                return Mario.Idle_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            return self

        def on_enter(self, owner_object):
            c.ACCELERATION = 0
            c.FRICTION = c.DECEL_FRICTION

        def update(self, owner_object):
            owner_object.animation.run_anim()

    class Invincible_Mario(State):
        """马里奥无敌时缩小后的状态"""
        def __init__(self):
            self.invincible_timer = 0
            self.blink_timer = 0

        def on_event(self, event):
            if event == 'small mario':
                return Mario.Small_Mario()
            return self

        def update(self, owner_object):
            self.invincible_timer += c.delta_time
            if self.invincible_timer > 40 * c.delta_time:
                owner_object.mario_states.on_event('small mario')

            self.blink_timer += c.delta_time
            if self.blink_timer > 7 * c.delta_time:
                owner_object.animation.current_sprite = sprites.EMPTY_SPRITE
                if self.blink_timer > 14 * c.delta_time:
                    self.blink_timer = 0

        def on_exit(self, owner_object):
            owner_object.animation.reset_anim_vars()

    class Small_Mario(State):
        """小马里奥状态"""
        def on_event(self, event):
            if event == 'grow':
                return Mario.Grow_Mario()
            elif event == 'shrink':
                return Mario.Dead_Mario()
            elif event == 'win':
                return Mario.Win_State()
            elif event == 'dead':
                return Mario.Dead_Mario()
            return self
        
    class Grow_Mario(State):
        """马里奥成长的状态"""
        def on_event(self, event):
            if event == 'big mario':
                return Mario.Big_Mario()
            if event == 'shrink':
                return Mario.Shrink_Mario()
            return self

        def on_enter(self, owner_object):
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = True

        def update(self, owner_object):
            owner_object.animation.grow_anim()
            owner_object.pos.y = owner_object.animation.new_y
            if owner_object.animation.anim_frame > 7:
                owner_object.mario_states.on_event('big mario')

        def on_exit(self, owner_object):
            owner_object.rect.h = 96
            owner_object.animation.mario_size = 'Big_Mario'
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = False

    class Big_Mario(State):
        """大马里奥状态"""
        def on_event(self, event):
            if event == 'shrink':
                return Mario.Shrink_Mario()
            elif event == 'dead':
                return Mario.Dead_Mario()
            elif event == 'win':
                return Mario.Win_State()
            return self

    class Shrink_Mario(State):
        """马里奥正在缩小的状态"""
        def on_event(self, event):
            if event == 'invincible':
                return Mario.Invincible_Mario()
            if event == 'grow mario':
                return Mario.Grow_Mario()
            return self

        def on_enter(self, owner_object):
            owner_object.animation.reset_anim_vars()
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.start_sprite_height = owner_object.animation.current_sprite[3]
            owner_object.freeze_movement = True
            sounds.pipe.play()

        def update(self, owner_object):
            owner_object.animation.shrink_anim()
            owner_object.pos.y = owner_object.animation.new_y
            if owner_object.animation.anim_frame > 7:
                owner_object.mario_states.on_event('invincible')

        def on_exit(self, owner_object):
            owner_object.rect.h = 48
            owner_object.animation.mario_size = 'Small_Mario'
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = False

    class Crouch_State(State):
        """马里奥蹲下时的状态"""
        def on_event(self, event):
            if event == 'brake':
                return Mario.Brake_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def on_enter(self, owner_object):
            c.FRICTION = c.BRAKE_FRICTION
            c.ACCELERATION = 0
            owner_object.animation.current_sprite = sprites.MARIO_CROUCH
            owner_object.pos.y += 30
            owner_object.rect.h = owner_object.animation.current_sprite[3]

        def update(self, owner_object):
            c.ACCELERATION = 0
            if owner_object.vel.x == 0:
                if owner_object.pressed_left:
                    owner_object.flip_sprites = True
                if owner_object.pressed_right:
                    owner_object.flip_sprites = False

        def on_exit(self, owner_object):
            owner_object.pos.y -= 31
            owner_object.start_height = owner_object.pos.y
        
    class Dead_Mario(State):
        """马里奥死亡状态"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            owner_object.animation.current_sprite = sprites.DEAD_MARIO
            owner_object.vel.y = c.DEATH_VEL_Y
            owner_object.vel.x = 0
            owner_object.freeze_movement = True
            owner_object.freeze_input = True
            pg.mixer.music.stop()
            pg.mixer.music.set_endevent(c.DEATH_SONG_END)
            pg.mixer.music.load(sounds.death)
            pg.mixer.music.play()

        def update(self, owner_object):
            self.death_timer += c.delta_time
            if self.death_timer > 20 * c.delta_time:
                accelerate(owner_object, 0, c.GRAVITY)
                owner_object.pos += owner_object.vel * c.delta_time

    class Win_State(State):
        """马里奥何时获胜、运行和管理与最终获胜动画相关的事件的状态"""
        def __init__(self):
            self.animation_step = 0
            self.timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            owner_object.animation.reset_anim_vars()
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.new_y = owner_object.pos.y
            owner_object.pos.x = c.flagpole.pos.x - 16
            owner_object.freeze_movement = True
            owner_object.freeze_input = True
            owner_object.vel = Vector2()
            pg.mixer.music.stop()
            sounds.flagpole_sound.play()

        def update(self, owner_object):

            if self.animation_step == 0:
                owner_object.animation.win_anim_on_flag()
                owner_object.pos.y += 4
                if owner_object.pos.y > c.flagpole.pos.y + c.flagpole.rect.h - 100:
                    self.animation_step = 1

            elif self.animation_step == 1:
                owner_object.pos.x = c.flagpole.pos.x + 24
                owner_object.flip_sprites = True
                self.timer += c.delta_time
                if self.timer > 20 * c.delta_time:
                    owner_object.flip_sprites = False
                    owner_object.freeze_movement = False
                    owner_object.pos.x = c.flagpole.pos.x + c.flagpole.rect.w
                    self.animation_step = 2
                    pg.mixer.music.set_endevent(c.WIN_SONG_END)
                    pg.mixer.music.load(sounds.stage_clear)
                    pg.mixer.music.play()

            elif self.animation_step == 2:
                c.ACCELERATION = c.MARIO_ACCELERATION
                owner_object.pressed_right = True
                if owner_object.pos.x > c.LEVEL_END_X:
                    owner_object.freeze_movement = True
                    c.final_count_down = True