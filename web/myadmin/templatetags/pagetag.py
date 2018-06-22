from django import template
from django.utils.html import format_html

register = template.Library()

# 自定义过滤器
# @register.filter
# def kong_upper(val):
#     # print ('val from template:',val)
#     return val.upper()


@register.simple_tag
def score(ob):
    s = 0
    if ob.username:
        s += 30
    if ob.phone:
        s += 30
    if ob.email:
        s += 30
    if ob.sex:
        s += 5
    if ob.age:
        s += 5
    return s


@register.simple_tag
def multiplication(n1, n2):
    n1 = float(n1)
    n2 = int(n2)
    return n1 * n2

# 自定义标签
@register.simple_tag
def showpage(request, count):

    kv = ''
    for i in request.GET:
        if i != 'p':
            kv += '&' + i + '=' + request.GET[i]

    p = int(request.GET.get('p', 1))
    count = int(count)

    if p <= 3:
        begin = 1
        end = 8
    elif p < count-4:
        begin = p-3
        end = p+4
    else:
        begin = count-7
        end = count

    if count <= 8:
        begin = 1
        end = count

    res = '<li><a href="?p=1'+kv+'">'+'<<'+'</a></li>'

    # 上一页
    if p <= 1:
        res += '<li><a href="?p=1'+kv+'">上一页</a></li>'
    else:
        res += '<li><a href="?p='+str(p-1)+kv+'">上一页</a></li>'

    # 中间部分
    for i in range(begin, end+1):
        if i == p:
            res += '<li class="am-active"><a href="?p='+str(i)+kv+'">'+str(i)+'</a></li>'
        else:
            res += '<li><a href="?p='+str(i)+kv+'">'+str(i)+'</a></li>'

    # 下一页
    if p >= count:
        res += '<li><a href="?p='+str(count)+kv+'">下一页</a></li>'
    else:
        res += '<li><a href="?p='+str(p+1)+kv+'">下一页</a></li>'

    res += '<li><a href="?p='+str(count)+kv+'">'+'>>'+'</a></li>'

    return format_html(res)