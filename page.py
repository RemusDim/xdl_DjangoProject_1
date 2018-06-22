def page(count, p):

    if p<3:
        begin=1
        end=8
    elif p<count-4:
        begin=p-3
        end=p+4
    else:
        begin=count-8
        end=count

    for i in range(begin, end+1):
        print(i)

page(100, 1)
print('--------------')
page(100, 5)
print('--------------')
page(100, 29)
print('--------------')
page(100, 99)
