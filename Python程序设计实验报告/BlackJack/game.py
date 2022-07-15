#花色，大小
RANKS = ["A", "2", "3", "4", "5", "6", "7","8", "9", "10", "J", "Q", "K"]
SUITS = ["c", "d", "h", "s"]

class Card:
    def __init__(self, rank, suit,faceup=True):
        self.rank = rank
        self.suit = suit
        self.bFaceUp=faceup

    def __str__(self):
        if self.bFaceUp:
            rep = self.rank + self.suit
        else:
            rep = '**'
        return rep
    def __cmp__(self, other):
        if(self.rank==other.rank and self.suit==other.suit):
            return True
        else:
            return False


class Hand:
    def __init__(self):
        self.cards=[]
    def Clear(self):
        self.cards.clear()
    def Add(self,card):
        self.cards.append(card)
    def Give(self,card,hand):
        if (len(self.cards)):
            for x in self.cards:
                if(x==card):
                    del self.cards[self.cards.index(x)]
                    hand.cards.append(x)


    def __str__(self):
        str1=""
        for x in self.cards:
            str1=str1+" "+str(x)
        return str1
    @property
    def Value(self):
        #A可以作为11，也可作为1点，当它与<10点的牌配对时，=11点，否则，=1点
        iRet=0
        iCountA=0
        for card in self.cards:
            if card.rank not in["A","J","Q","K"]:
                iRet+=int(card.rank)
            else :
                if card.rank in ["J","Q","K"]:
                    iRet+=10
                else:
                    iRet+=11
                    iCountA=iCountA+1
        #查看A，必要时将A当成1点；

        while (iRet>21):
            if(iCountA>0):
                iRet-=10
                iCountA-=1
            elif (iCountA==0):
                break
        return iRet
class Deck(Hand):
    def __init__(self):
        Hand.__init__(self)
        for rank in RANKS:
            for suit in SUITS:
                card=Card(rank,suit)
                self.Add(card)
    def Clear(self):
        self.cards.clear()
    def Shuffle(self):
        import random
        random.shuffle(self.cards)
    def Deal(self,hand,num=1):
        pass
class Game:
    def __init__(self):
        self.deck=Deck()
        self.Robot=Hand()
        self.Player=Hand()
        self.bGameStart=False
        self.RobotPts=0
        self.PlayerPts=0
        self.bGameEnd=False
        self.Win=0
    def NewGame(self):
        self.bGameStart=True
        self.bGameEnd=False
        self.deck=Deck()
        self.deck.Shuffle()
        self.Robot=Hand()
        self.Player=Hand()
        acard=self.deck.cards[0]
        acard.bFaceUp=False
        self.deck.Give(acard,self.Robot)
        self.deck.Give(self.deck.cards[0],self.Robot)
        self.deck.Give(self.deck.cards[0],self.Player)
        self.deck.Give(self.deck.cards[0],self.Player)
        self.RobotPts=self.Robot.Value
        self.PlayerPts=self.Player.Value

        print('Robot Cards:'+str(self.RobotPts))
        print('Player Cards:'+str(self.PlayerPts))
    def Hit(self):
        if self.Player.Value<=21:
            self.deck.Give(self.deck.cards[0],self.Player)
            self.PlayerPts=self.Player.Value
            return True
        else:
            return False
    def Stand(self):
        #返回值为胜平负：1，Robot win,0,Deuce;-1 Player win
        while (self.Robot.Value<17):
            self.deck.Give(self.deck.cards[0],self.Robot)
            if self.Robot.Value>21:
                break
        self.Robot.cards[0].bFaceUp=True
        iWin=0
        self.bGameEnd=True
        self.RobotPts=self.Robot.Value
        self.PlayerPts=self.Player.Value
        if self.RobotPts>21 and self.PlayerPts>21:
            iWin=0
        elif self.RobotPts>21 and self.PlayerPts<=21:
            iWin=-1
        elif self.RobotPts<=21 and self.PlayerPts>21:
            iWin=1
        elif self.RobotPts<=21 and self.PlayerPts<=21:
            if self.RobotPts>self.PlayerPts:
                iWin=1
            elif self.RobotPts==self.PlayerPts:
                iWin=0;
            else:
                iWin=-1
        return iWin

deck=Deck()
deck.Shuffle()
print(deck)
me = Hand()
computer = Hand()
deck.Give(deck.cards[0],me)
deck.Give(deck.cards[0],computer)
print(deck)
print(me)
print(computer)
