from data import main
from data import menu
from data import config as c
import pygame as pg
import os
import sys

class App():
    def __init__(self):
        self.menu = None
        self.main = None

    def run(self):
        self.menu = menu.Menu() 
        self.menu.menu_loop()
        if self.menu.quit_state == 'play':      # 检查是否退出
            self.main = main.Main()
            self.main.main_loop()
            if self.main.quit_state == 'menu':
                os.execl(sys.executable, sys.executable, *sys.argv) # 重启游戏（没关闭之前一直重启）

if __name__ == '__main__':
    pg.init() # 初始化pygame模块
    c.screen = pg.display.set_mode((c.SCREEN_SIZE.x, c.SCREEN_SIZE.y))  # 初始化屏幕
    pg.display.set_caption(c.CAPTION)   # 显示
    c.clock = pg.time.Clock()   # 使用pygame中的计时器模块

    app = App()     # 初始化一个实例
    app.run()       # 运行app实例

    pg.quit()       # 退出