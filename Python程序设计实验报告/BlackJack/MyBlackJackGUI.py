

import sys
import pygame
from settings import Settings
from button import Button
from game import Game

#import tkinter.messagebox
class Main:
    def LoadImage(self):
        self.imgRobot=[]
        self.imgPlayer=[]
        for card in self.game.Robot.cards:

            strCard=str(card).lower()
            if strCard=="**":
                strCard='back'
            img=pygame.image.load('image/'+strCard+'.gif').convert()
            self.imgRobot.append(img)
        for card in self.game.Player.cards:
            strCard=str(card).lower()
            img=pygame.image.load('image/'+strCard+'.gif').convert()
            self.imgPlayer.append(img)

    def check_play(self,button,mouse_x,mouse_y):  #点击按钮开始游戏
        if button.rect.collidepoint(mouse_x,mouse_y):#该方法检测鼠标点击的位置是否在按钮的rect内
            if button.msg=='Hits':
                if self.game.bGameStart:
                    if self.game.PlayerPts<=21:
                        self.game.Hit()
                        self.LoadImage()

            if button.msg=='Stand':
                if self.game.bGameStart:
                    self.game.bGameEnd=True
                    self.game.Win=self.game.Stand()
                    self.LoadImage()

            if button.msg=='New Game':
                self.game.bGameStart=True
                if self.game.bGameStart:
                    self.game.NewGame()
                    self.LoadImage()
                    #display cards
                    i=0
                    '''
                    for img in self.imgRobot:
                        self.screen.blit(img,(10,100*(i+1)))
                        i+=1
                    '''
                    #self.screen.blit(self.imgRobot[0],(0,0))

            print('Clicked:'+button.msg)
    def Paint(self):
        if self.game.bGameStart:
            #显示Robot cards
            i=0
            for img in self.imgRobot:
                #imgpic=pygame.image.load(pic).convert()
                self.screen.blit(img,(10+75*i,30))
                i+=1
            #显示Player cards
            i=0
            for img in self.imgPlayer:
                #imgpic=pygame.image.load(pic).convert()
                self.screen.blit(img,(10+75*i,220))
                i+=1

    def DisplayText(self,msg,x,y):
        text=pygame.font.Font('freesansbold.ttf',20)
        text_fmt=text.render(msg,1,(255,255,255))
        self.screen.blit(text_fmt,(x,y))
    def __init__(self):
        self.game=Game()
        # 初始化游戏并创建一个屏幕对象
        pygame.init()
        ai_settings = Settings()
        self.screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
        pygame.display.set_caption("MyBlackJack")
        button_Hit=Button(ai_settings,self.screen,"Hits",0)
        button_Stand=Button(ai_settings,self.screen,"Stand",1)
        button_NewGame=Button(ai_settings,self.screen,"New Game",2)
        #self.game=Game();
        # 开始游戏的主循环
        while True:
            # 监视键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type==pygame.MOUSEBUTTONDOWN:#检测鼠标点击事件
                    mouse_x,mouse_y=pygame.mouse.get_pos() #get_pos()返回一个单击时鼠标的xy坐标
                    self.check_play(button_Hit,mouse_x,mouse_y)
                    self.check_play(button_Stand,mouse_x,mouse_y)
                    self.check_play(button_NewGame,mouse_x,mouse_y)

            # 让最近绘制的屏幕可见
            #pygame.display.flip()
            # 每次循环时都重绘屏幕
            self.screen.fill(ai_settings.bg_color)

            button_Hit.draw_button()
            button_Stand.draw_button()
            button_NewGame.draw_button()
            '''
            if self.game.bGameStart:
                imgpic=pygame.image.load(pic).convert()
                self.screen.blit(imgpic,(0,0))
            '''
            if self.game.bGameEnd:
                self.DisplayText("Robot Cards:"+str(self.game.RobotPts)+"pts",5,5)
            else:
                self.DisplayText("Robot Cards:**"+"pts",5,5)
            self.DisplayText("Player Cards:"+str(self.game.PlayerPts)+"pts",5,195)
            self.Paint()
            if self.game.bGameEnd:
                #self.game.bGameStart=False
                #1，Robot win,0,Deuce;-1 Player win
                if self.game.Win>0:
                    self.DisplayText("Result:Robot Win!",5,400)
                elif self.game.Win==0:
                    self.DisplayText("Result:Deuce!",5,400)
                elif self.game.Win<0:
                    self.DisplayText("Result:You Win!",5,400)

            #pygame.display.update()
            pygame.display.flip()

main=Main()