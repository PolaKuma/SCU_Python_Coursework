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
deck=Deck()
deck.Shuffle()
print(deck)
me = Hand()
computer = Hand()
deck.Give(deck.cards[0],me)
deck.Give(deck.cards[0],me)
deck.cards[0].bFaceUp=False
deck.Give(deck.cards[0],computer)
deck.Give(deck.cards[0],computer)
#print(deck)
#print(me)
#print(computer)
print('电脑的牌：')
print(computer)
print('电脑的点数：')
print('**')
print('我的牌：')
print(me)
print('我的点数：')
print(me.Value())
#该我要牌了
while me.Value()<=21:
    choice=input('你还要牌吗？（y/n)')
    if choice=='n':
        break
    else:
        deck.Give(deck.cards[0],me)
        print('我的牌：')
        print(me)
        print('我的点数：')
        print(me.Value())
#如果电脑的点数<=17，必须要牌；
while computer.Value()<=17:
    deck.Give(deck.cards[0],computer)
    if computer.Value()>=21:
        break
#最后，摊牌
print('Game Over!')
print('电脑的牌：')
computer.cards[0].bFaceUp=True
print(computer)
print('电脑的点数：')
print(computer.Value())
print('我的牌：')
print(me)
print('我的点数：')
print(me.Value())
#判断输赢；
if computer.Value()>21 and me.Value()>21:
    print('平局！')
elif computer.Value()>21 and me.Value()<=21:
    print('我赢了！')
elif computer.Value()<=21 and me.Value()>21:
    print('电脑赢了！')
else:
    if computer.Value()>me.Value():
         print('电脑赢了！')
    elif computer.Value()<me.Value():
         print('我赢了！')
    else:
         print('平局！')