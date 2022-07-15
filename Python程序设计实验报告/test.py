# 构建要求的蛇形三角矩阵
def build_array(N):
    # 初始化一个值为0的下三角矩阵
    array = []
    for i in range(N, 0, -1):                   # i的取值从N到0，步进为-1的循环。等同于for(int i = N; i > 0; i--)
                                                # range()函数有三个参数，依次为起始值（默认为0），结束值（必须输入），步进（默认为1）
                                                # range()覆盖范围范围左闭右开，跟C语言一致
        array.append([0 for x in range(i)])     # [0 for x in range(i)] 初始化一个长度为i的全0列表

    i = 0                                       # 行数
    j = 0                                       # 列数
    num = 1                                     # 填入的数字
    times = N                                   # 每一行、列、斜需要重复的次数

    while num <= int((N*(N+1))/2):
        # 横向排列
        for x in range(times):
            array[i][j] = num
            num += 1
            j += 1

        # 重定位至下一行末尾
        times -= 1
        i += 1
        j -= 2

        # 斜向排列
        for x in range(times):
            array[i][j] = num
            num += 1
            i += 1
            j -= 1

        # 重定位至上一行开头
        times -= 1
        i -= 2
        j += 1

        # 竖向排列
        for x in range(times):
            array[i][j] = num
            num += 1
            i -= 1

        # 重定位至右下
        times -= 1
        i += 1
        j += 1

    return array


# 输出矩阵
def output_array(array):
    for line in array:                          # python的循环不止能以range()的形式进行循环，
                                                # 可以直接对某个列表进行循环，此时的循环体 for x in list 中的x为list中的每个元素
        for x in line[:-1]:                     # line[:-1]表示除了line末尾元素外的所有元素
            print(x, end='\t')                  # end是print的一个可选参数，表示输出此行后结尾的符号。默认为'\n'换行。
        print(line[-1])


if __name__ == '__main__':                      # 一个python程序从此处开始运行。
    array = build_array(int(input('N = ')))
    output_array(array)


