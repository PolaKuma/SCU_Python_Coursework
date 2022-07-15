'''
Write as followed:
1   2  3  4    5
12 13 14  6
11 15  7
10  8
9
'''
def main():
    SIZE=int(input('Input Size of Array:'))
    data = [[0] * SIZE for _ in range(SIZE)]
    row=col=0
    i=1
    data[row][col]=i
    max=getMaxNum(SIZE)
    while i<max:
        while CanGoRight(data,row,col,i,SIZE-1):
            i+=1
            col+=1
            data[row][col]=i
        while CanGoSlope(data,row,col,i,SIZE-1):
            i+=1
            col-=1
            row+=1
            data[row][col]=i
        while CanGoUp(data,row,col,i):
            i+=1
            row-=1
            data[row][col]=i
    display(data)

def getMaxNum(x):
    return (1+x)*x/2
def display(data):
    for i in range(len(data)):
        for j in range(len(data)):
            print(format(data[i][j],'4d'),end='')
        print('')

def CanGoRight(data,row,col,i,maxcol):
    flag=False
    if col==maxcol:
        flag=False
    elif data[row][col+1]!=0:
        flag=False
    else:
        flag=True
    return flag
def CanGoSlope(data,row,col,i,maxrow):
    flag=False
    if col==0 or row==maxrow:
	    flag=False
    elif data[row+1][col-1]!=0:
        flag=False
    else:
        flag=True
    return flag

def CanGoUp(data,row,col,i):
    flag=False
    if row==0:
        flag=False
    elif data[row-1][col]!=0:
        flag=False
    else:
        flag=True
    return flag
main()

