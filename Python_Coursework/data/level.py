from .sprites import level_1
from .basetypes import Vector2, Rectangle
from . import config as c
from .components.tiles import Question, Brick, Collider_Rect, Flagpole
from .components.items import *
from .components.enemies import *

# 不具备速度的对撞机
static_colliders = []

# 具有速度的对撞机
dynamic_colliders = []

coins = []
super_mushrooms = []
enemies = []

# 当砖瓦被打破时出现碎片
brick_fragments = []

# 开始和结束瓦片，用于将大行瓦片组合成一个对撞机
start_tile = None
end_tile = None

# 从关卡地图中读取像素数据并实例化与像素颜色对应的对象
for y in range(0, level_1.size[1]):
    for x in range(0, level_1.size[0]):

        color = level_1.getpixel((x, y))
        pos = Vector2(x * c.TILE_SIZE, y * c.TILE_SIZE + 24)

        # 黑色 = 静态地面对撞机，它们组合在一起进行优化
        if color == c.BLACK:
            if start_tile == None:
                start_tile = pos
            if end_tile == None:
                if x + 1 > level_1.size[0]:
                    end_tile = pos
                if level_1.getpixel((x + 1, y)) != c.BLACK:
                    end_tile = pos
            if end_tile != None and start_tile != None:
                w = end_tile.x - start_tile.x + c.TILE_SIZE
                h = c.TILE_SIZE
                rect = Rectangle(start_tile, w, h)
                static_colliders.append(Collider_Rect(rect))
                end_tile = None
                start_tile = None
        
        # 红色 = 管道对撞机
        elif color == c.RED:
            h = c.SCREEN_SIZE.y - pos.y
            w = 2 * c.TILE_SIZE
            rect = Rectangle(pos, w, h)
            static_colliders.append(Collider_Rect(rect))

        # 黄色 = 以硬币为项目的问题图块
        elif color == c.YELLOW:
            coin_rect = Rectangle(Vector2(pos.x, pos.y), 48, 42)
            contents = Coin(coin_rect)
            coins.append(contents)
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Question(rect, contents))

        # 灰色 = 砖瓦
        elif color == c.GRAY:
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Brick(rect))

        # 绿色 = 以蘑菇为项目的问题图块
        elif color == c.GREEN:
            mushroom_rect = Rectangle(Vector2(pos.x, pos.y), c.TILE_SIZE, c.TILE_SIZE)
            contents = Super_Mushroom(mushroom_rect, Vector2(c.MUSHROOM_START_VEL_X, 0))
            super_mushrooms.append(contents)
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Question(rect, contents))

        # 棕色 = Goomba
        elif color == c.BROWN:
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            enemies.append(Goomba(rect, Vector2()))

        elif color == c.PURPLE:
            rect = Rectangle(Vector2(pos.x, pos.y - 24), 48, 72)
            enemies.append(Turtle(rect, Vector2()))

# 实例化旗杆
rect = Rectangle(Vector2(9504, 96), 48, 456)
flag_pos = Vector2(9480, 120)
c.flagpole = Flagpole(rect, flag_pos)

