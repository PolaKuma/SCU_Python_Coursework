import sys
import pygame
from settings import Settings
from button import Button

def check_play(button,mouse_x,mouse_y):  #点击按钮开始游戏
    if button.rect.collidepoint(mouse_x,mouse_y):#该方法检测鼠标点击的位置是否在按钮的rect内

        print('Clicked:'+button.msg)
def run_game():
    # 初始化游戏并创建一个屏幕对象
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Test")
    button_Hit=Button(ai_settings,screen,"Hits",0)
    button_Stand=Button(ai_settings,screen,"Stand",1)
    button_NewGame=Button(ai_settings,screen,"New Game",2)
    # 开始游戏的主循环
    while True:
        # 监视键盘和鼠标事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type==pygame.MOUSEBUTTONDOWN:#检测鼠标点击事件
                mouse_x,mouse_y=pygame.mouse.get_pos() #get_pos()返回一个单击时鼠标的xy坐标
                check_play(button_Hit,mouse_x,mouse_y)
                check_play(button_Stand,mouse_x,mouse_y)
                check_play(button_NewGame,mouse_x,mouse_y)

        # 让最近绘制的屏幕可见
        #pygame.display.flip()
        # 每次循环时都重绘屏幕
        screen.fill(ai_settings.bg_color)
        button_Hit.draw_button()
        button_Stand.draw_button()
        button_NewGame.draw_button()
        #pygame.display.update()
        pygame.display.flip()
run_game()