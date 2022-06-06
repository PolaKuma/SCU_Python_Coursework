from .basetypes import Vector2
import pygame as pg

# 不同基类型之间共享的变量
screen = None
clock = None
camera = None
keys = None
delta_time = None
mario = None
final_count_down = False

# 关卡加载的颜色
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
GRAY = (100, 100, 100, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (100, 255, 100, 255)
BROWN = (124, 66, 0, 255)
PURPLE = (124, 0, 255, 255)

# 关卡的背景颜色
BACKGROUND_COLOR = (107, 140, 255)

# 窗口设置
SCREEN_SIZE = Vector2(744, 672)
CAPTION = 'Mario Bros'

# 起始位置
MARIO_START_POSITION = Vector2(138, 552)
FOREGROUND_POS = Vector2(9840, 505)

TILE_SIZE = 48

# 实体变量
ACCELERATION = 0
MARIO_ACCELERATION = 0.0005
MAX_VEL = 0.35
GRAVITY = 0.002
MAX_JUMP_HEIGHT = 140
FRICTION = 1
DECEL_FRICTION = 0.95
BRAKE_FRICTION = 0.85

# 不同事件的速度
BOUNCE_VEL = 0.1
JUMP_VELOCITY = -0.5
MUSHROOM_START_VEL_X = 0.2
ENEMY_START_VEL_X = -0.1
STOMP_VEL = -0.4
DEATH_VEL_Y = -0.8
GOOMBA_KNOCKED_VEL_Y = -0.8

# 关卡设置结束
MAXIMUM_CAMERA_SCROLL = 9300
LEVEL_END_X = 9840

# 相机开始跟随时与屏幕左侧的距离
CAMERA_FOLLOW_X = 300

# 设置计时器值，以便动画立即开始，而不是先计数
INITIAL_TIMER_VALUE = 1000

# 分数变量
collected_coins = 0
total_score = 0
COIN_SCORE = 200
MUSHROOM_SCORE = 1000
GOOMBA_SCORE = 100
TIME_SCORE = 1000

# 歌曲结束时的事件
WIN_SONG_END = pg.USEREVENT + 1
DEATH_SONG_END = pg.USEREVENT + 2
OUT_OF_TIME_END = pg.USEREVENT + 3









