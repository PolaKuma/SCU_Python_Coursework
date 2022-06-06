from . import config as c
from .basetypes import Vector2
import math

def clamp(x, a, b):
    """将值 x 限制在 a 和 b 之间"""
    return max(a, min(b, x))

def accelerate(obj, accel_x, accel_y, limit_x = None):
    """加速直到达到极限"""
    obj.vel += Vector2(accel_x, accel_y) * c.delta_time
    if limit_x != None:
        if obj.vel.x > 0:
            obj.vel.x = clamp(obj.vel.x, 0, limit_x)
        elif obj.vel.x < 0:
            obj.vel.x = clamp(obj.vel.x, -limit_x, 0)

def get_flipped_sprite(sprite):
    """返回翻转精灵的坐标"""
    # 429是图集的宽度
    return (429 - sprite[0] - sprite[2], sprite[1], sprite[2], sprite[3])