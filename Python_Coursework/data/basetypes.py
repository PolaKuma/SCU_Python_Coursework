from . import config as c
from . import sprites
import pygame as pg
import math

class Game_Object():
    """游戏对象类"""
    def __init__(self, rect):
        self.rect = rect

    def __getattr__(self, name):
        """检索位置时无需输入rect.pos，使行更短"""
        if name == 'pos':
            return self.rect.pos
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """设置位置时无需输入rect.pos，使行更短"""
        if name == 'pos':
            self.rect.pos = value
        else:
            object.__setattr__(self, name, value)
        
class Vector2():
    """坐标和速度类"""
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    """为方便对点坐标运算，故重载相关运算符"""
    def __mul__(self, other):
        """重载乘法"""
        return Vector2(self.x * other, self.y * other)

    def __add__(self, other):
        """重载加法"""
        return Vector2(self.x + other.x, self.y + other.y)

class Rectangle():
    """矩形碰撞器的矩形类"""
    def __init__(self, pos = Vector2(), w = 0, h = 0):
        self.pos = pos  # 坐标
        self.w = w      # 宽
        self.h = h      # 高

    def overlaps(self, other):
        """检查两个矩形是否重叠"""
        return not(other.pos.x + other.w <= self.pos.x or 
                   other.pos.x >= self.pos.x + self.w or
                   other.pos.y + other.h <= self.pos.y or
                   other.pos.y >= self.pos.y + self.h)

    def check_collisions(self, collider_list):
        """检查两个矩形之间的碰撞，如果在 100px 范围内，则返回单个碰撞器"""
        for collider in collider_list:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.rect.w >= 100: # 无论如何都要检查更宽的对撞机
                if self.overlaps(collider.rect):
                    return collider

    def check_entity_collisions(self, entity_list):
        """检查碰撞但返回所有碰撞实体的列表"""
        others = []
        for entity in entity_list:
            if entity.rect is not self and abs(self.pos.x - entity.pos.x) < 100:
                if self.overlaps(entity.rect):
                    others.append(entity)
        return others

class Entity(Game_Object):
    """拥有速度的游戏对象的实体类"""
    def __init__(self, vel, rect):
        super(Entity, self).__init__(rect)      # 继承矩形类
        self.vel = vel                          # 定义速度

class Camera(Rectangle):
    def __init__(self, pos, w, h):
        super(Camera, self).__init__(pos, w, h)     # 继承马里奥相应坐标以及其对应矩形长宽
    
    def contains(self, other):
        """检查相机是否水平包含一个矩形"""
        return ((other.pos.x > self.pos.x and other.pos.x < self.pos.x + c.SCREEN_SIZE.x) or 
                (other.pos.x + other.w > self.pos.x and other.pos.x + other.w < self.pos.x + c.SCREEN_SIZE.x))

    def to_view_space(self, pos):
        """返回相对于相机的位置"""
        return Vector2(pos.x - self.pos.x, pos.y)

    def update(self):
        """根据马里奥速度和位置更新相机位置"""
        if self.pos.x < c.MAXIMUM_CAMERA_SCROLL:
            if c.mario.pos.x > c.camera.pos.x + c.CAMERA_FOLLOW_X and c.mario.vel.x > 0:
                c.camera.pos.x += c.mario.vel.x * c.delta_time

class State_Machine():
    """管理状态类"""
    def __init__(self, initial_state, owner_object):
        self.state = initial_state  # 定义状态
        self.owner_object = owner_object    # 定义对象

    def on_event(self, event):
        """更新当前状态并运行 on_exit 和 on_enter获取新的状态"""
        new_state = self.state.on_event(event)
        if new_state is not self.state:
            self.state.on_exit(self.owner_object)
            self.state = new_state
            self.state.on_enter(self.owner_object)

    def update(self):
        self.state.update(self.owner_object)

    def get_state(self):
        return self.state.__class__.__name__

class State():
    """状态类"""
    def on_event(self, event):
        """处理委托给该状态的事件"""
        pass

    def on_enter(self, owner_object):
        """进入状态时执行动作"""
        pass

    def update(self, owner_object):
        """活动时执行特定于状态的操作"""
        pass

    def on_exit(self, owner_object):
        """退出状态时执行动作"""
        pass

class Digit_System():
    """用于显示和处理分数等屏幕数字的类"""
    def __init__(self, start_pos, number_of_digits, start_value = 0):
        self.total_value = start_value          # 统计总得分
        self.start_pos = start_pos              # 显示坐标
        self.number_of_digits = number_of_digits    # 数字系统处理的数字总数
        self.digit_array = []                       # 存放相关数字到列表中
        self.update_value(start_value)              # 更新得分

    def update_value(self, new_value):
        """更新数字系统的总值和数字数组"""
        self.total_value = new_value
        if new_value > 0:
            remaining_digits = self.number_of_digits - self.get_number_of_digits(new_value)
            self.digit_array = [0] * remaining_digits
            for x in str(self.total_value):
                self.digit_array.append(int(x))
        else:
            self.digit_array = [0] * self.number_of_digits
    
    def draw(self):
        """画出数字系统"""
        for i, x in enumerate(self.digit_array):
            # 数字宽度 = 24
            c.screen.blit(sprites.digits, (self.start_pos.x + 24 * i, self.start_pos.y), (24 * x, 0, 24, 21))

    def get_number_of_digits(self, value):
        """获取整数的位数"""
        if value == 0:
            return 0
        elif value == 1:
            return 1
        else:
            return math.ceil(math.log10(value))

    
