from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from myadmin.models import Users, Types, Goods, Address, Order, OrderInfo
import time
from django.db.models import Q
from myadmin.views.views import upload
import os
from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.


def typetext():
    typedata = Types.objects.filter(pid=0)
    return typedata


def getshoppernum(request):
    num = 0
    ushopper = request.session.get('ushopper', {})
    if len(ushopper) == 0:
        num = 0
    else:
        for i in ushopper.values():
            num += i['num']
    return num


# 首页
def index(request):
    data = typetext()
    for i in data:
        i.sub = Types.objects.filter(pid=i.id)[:4]
        for j in i.sub:
            j.sub = Types.objects.filter(pid=j.id)[:6]

    typedata = typetext()
    num = getshoppernum(request)

    return render(request, 'home/index.html', {'data': data, 'typedata': typedata, 'num': num})


# 列表页
def list(request, id):
    sign = 0
    # 取数据
    ob = Types.objects.get(id=id)
    # 找到一级分类
    data = Types.objects.get(id=id)
    while data.pid != 0:
        sign += 1
        data = Types.objects.get(id=data.pid)
    # 找到二级分类
    data.sub = Types.objects.filter(pid=data.id)
    # 找到三级分类和所有商品
    data.goods = []
    for i in data.sub:
        if sign == 1:  # 1 代表按的二级分类
            if i == ob:
                i.sub = Types.objects.filter(pid=i.id)
                for j in i.sub:
                    for z in Goods.objects.filter(typeid=j):
                        data.goods.append(z)
        elif sign == 2:  # 2 代表按的三级分类
            if i == Types.objects.get(id=ob.pid):
                i.sub = Types.objects.filter(pid=i.id)
                for j in i.sub:
                    if j == ob:
                        for z in Goods.objects.filter(typeid=j):
                            data.goods.append(z)
        else:  # 0 代表按的一级分类
            i.sub = Types.objects.filter(pid=i.id)
            for j in i.sub:
                for z in Goods.objects.filter(typeid=j):
                    data.goods.append(z)
    # 把标记数据存入data
    data.ob = ob
    # 数量
    data.num = len(data.goods)

    # 查找销量最高的两件商品
    toplist = Goods.objects.all().order_by('num').reverse()[:2]

    typedata = typetext()
    num = getshoppernum(request)
    return render(request, 'home/list.html', {'typedata': typedata, 'data': data, 'num': num, 'toplist': toplist})


# # 列表页数据查询方法二，递归
# def list(request, id):
#     # 取数据
#     ob = Types.objects.get(id=id)

#     # 找到一级分类
#     data = Types.objects.get(id=id)
#     while data.pid != 0:
#         data = Types.objects.get(id=data.pid)

#     # 找到二级、三级分类和所有商品
#     def getdata(data):
#         if not Types.objects.filter(pid=data.id):
#             if Goods.objects.filter(typeid=data) and data==ob:
#                 for i in Goods.objects.filter(typeid=data):
#                     mylist.append(i)
#             return data
#         else:
#             data.sub = Types.objects.filter(pid=data.id)
#             for i in data.sub:
#                 getdata(i)

#     mylist = []
#     getdata(data)
#     data.goods = mylist
    
#     # 把标记数据存入data
#     data.ob = ob
    
#     # 数量
#     data.num = len(data.goods)
    
#     # 查找销量最高的两件商品

#     typedata = typetext()
#     num = getshoppernum(request)
#     return render(request, 'home/list.html', {'typedata': typedata, 'data': data, 'num': num})


# 详情页
def info(request, id):
    ob = Goods.objects.get(id=id)
    # 每搜索一下搜索量加一
    ob.num += 1
    ob.save()
    ob2 = ob.typeid
    ob3 = Types.objects.get(id=ob2.pid)

    # 面包屑用列表
    mylist = [ob3, ob2, ob]

    typedata = typetext()
    num = getshoppernum(request)
    return render(request, 'home/info.html', {'typedata': typedata, 'ob': ob, 'mylist': mylist, 'num': num})


# 注册页面
def register(request):
    try:
        if request.method == 'POST':
            # 注册页面
            # 判断验证码
            if request.POST.get('vcode').lower() != request.session['verifycode'].lower():
                return HttpResponse('<script>alert("请输入正确的验证码");location.href="/register/"</script>')

            # 判断邮箱是否重复
            if not Users.objects.filter(email=request.POST.get('email')) and request.POST.get('retype') == 1:
                ob = Users()
                ob.email = request.POST.get('email')
                ob.password = make_password(request.POST.get('password'), None, 'pbkdf2_sha256')
                ob.save()
                showname(ob, request)
                return HttpResponse('<script>alert("注册成功！");location.href="/"</script>')
            if not Users.objects.filter(phone=request.POST.get('phone')) and request.POST.get('retype') == 2:
                ob = Users()
                ob.phone = request.POST.get('phone')
                ob.password = make_password(request.POST.get('password'), None, 'pbkdf2_sha256')
                ob.save()
                showname(ob, request)
                return HttpResponse('<script>alert("注册成功！");location.href="/"</script>')
            else:
                return HttpResponse('<script>alert("您的邮箱或手机号已被注册，请直接登录！");location.href="/login/"</script>')
        else:
            return render(request, 'home/register.html')
    except:
        return HttpResponse('<script>alert("请正确填写信息！");location.href="/register/"</script>')


# 登录页面
def login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        # 判断验证码
        if request.POST.get('vcode').lower() != request.session['verifycode'].lower():
            return HttpResponse('<script>alert("请输入正确的验证码");location.href="/login/"</script>')

        mylilist = [{'username': name}, {'email': name}, {'phone': name}]

        if Users.objects.filter(**mylilist[0]):
            return mylogin(mylilist[0], request)
        elif Users.objects.filter(**mylilist[1]):
            return mylogin(mylilist[1], request)
        elif Users.objects.filter(**mylilist[2]):
            return mylogin(mylilist[2], request)

        return HttpResponse('<script>alert("请先注册后再登录！");location.href="/login/"</script>')
    else:
        return render(request, 'home/login.html')


# 退出登录
def logout(request):
    del request.session['VipUser']
    return HttpResponse('<script>location.href="/"</script>')


# 添加购物车
def shopperadd(request):
    try:
        gid = request.GET['gid']
        num = int(request.GET['num'])
        ob = Goods.objects.get(id=gid)

        ushopper = request.session.get('ushopper', {})

        if gid in ushopper:
            ushopper[gid]['num'] += num
        else:
            ushopper[gid] = {'id': ob.id, 'title': ob.title, 'price': str(ob.price), 'pic': ob.picurl, 'num': num}
        
        request.session['ushopper'] = ushopper

        mynum = getshoppernum(request)

        return JsonResponse({'code': 1, 'msg': '添加购物车成功！', 'mynum': mynum})
    except:
        return JsonResponse({'code': 0, 'msg': '添加购物车失败！'})

    return HttpResponse('ok')


# 购物车列表
def shopperlist(request):
    num = getshoppernum(request)
    typedata = typetext()
    return render(request, 'home/shopperlist.html', {'typedata': typedata, 'num': num})


# 购物车商品删除
def shopperdel(request):
    request.session['ushopper'] = {}
    return HttpResponse('<script>location="/shopper/list/"</script>')


# 增加购物车中商品数量ajax
def shopperaddgoods(request):
    try:
        gdnum = request.GET['gdnum']
        gid = request.GET['gid']

        ushopper = request.session['ushopper']
        ushopper[gid]['num'] = int(gdnum)

        request.session['ushopper'] = ushopper
        return HttpResponse('1')
    except:
        return HttpResponse('0')


# 删除一条购物车中的数据
def delonedata(request):
    try:
        gid = request.GET['gid']

        ushopper = request.session['ushopper']
        ushopper.pop(gid)

        request.session['ushopper'] = ushopper

        return HttpResponse('1')
    except:
        return HttpResponse('0')

    return HttpResponse('ok')


# 个人中心首页
def personindex(request):
    # 热卖推荐
    ob = Goods.objects.all().order_by('num').reverse()[:3]

    # 订单相关信息
    us = Users.objects.get(id=request.session['VipUser']['uid'])
    usorder1 = us.order_set.filter(status=1).count()
    usorder2 = us.order_set.filter(status=2).count()
    usorder3 = us.order_set.filter(status=3).count()
    usorder4 = us.order_set.filter(status=4).count()
    usorder5 = us.order_set.filter(status=5).count()
    usorderlist = [usorder1, usorder2, usorder3, usorder4, usorder5]

    # 日历相关信息
    tm = time.localtime()
    if tm[6] == 0:
        tm1 = '一'
    elif tm[6] == 1:
        tm1 = '二'
    elif tm[6] == 2:
        tm1 = '三'
    elif tm[6] == 3:
        tm1 = '四'
    elif tm[6] == 4:
        tm1 = '五'
    elif tm[6] == 5:
        tm1 = '六'
    elif tm[6] == 6:
        tm1 = '日'
    else:
        tm1 = '无'

    # 我的物流相关信息
    myob = us.order_set.filter(Q(status=3)|Q(status=4))
    return render(request, 'home/person/index.html', {'topgoods': ob, 'usorderlist': usorderlist, 'tm': tm, 'tm1': tm1, 'logistics': myob})


# 订单确认
def orderconfirm(request):
    # 拿到购物车传过来的用户选择的数据
    if request.method == "GET":
        gid = request.GET['gid'].split(',')
        # 从session中取出购物车中的数据
        shopperdata = request.session['ushopper']
        orderdata = {}
        for i in shopperdata:
            if i in gid:
                orderdata[i] = shopperdata[i]

        # 把用户选择的商品存入session
        request.session['uorder'] = orderdata

        # 查用户的收货地址
        uaddress = Address.objects.filter(uid=request.session['VipUser']['uid'])

        num = getshoppernum(request)
        return render(request, 'home/orderconfirm.html', {'num': num, 'uaddress': uaddress})

    # 地址添加
    elif request.method == "POST":
        # 拿到用户添加的信息，存到数据库
        ob = Address()
        ob.uid = Users.objects.get(id=request.session['VipUser']['uid'])
        ob.aname = request.POST['aname']
        ob.aphone = request.POST['aphone']
        ob.aaddress = request.POST['aaddress']
        # 判断如果用户设置了默认收货地址，则把数据库中所有的地址都改为非默认地址
        s = request.POST.get('status', 0)
        if s == '1':
            for i in Address.objects.filter(uid=request.session['VipUser']['uid']):
                i.status = 0
                i.save()
        ob.status = s
        ob.save()
        return HttpResponse('<script>location.href="/order/confirm/?gid='+request.GET['gid']+'"</script>')


# 把订单、订单详情存入数据库，把购物车session中已购买的数据删除，增加商品销量
def ordercreate(request):
    # 订单数据存入数据库
    od = Order()
    od.uid = Users.objects.get(id=request.session['VipUser']['uid'])
    od.address = Address.objects.get(id=request.GET['aid'])
    totalprice = 0
    totalnum = 0
    # 算出总钱数和商品个数
    for i in request.session['uorder'].values():
        totalprice += float(i['price']) * i['num']
        totalnum += i['num']

    od.totalprice = totalprice
    od.totalnum = totalnum
    od.save()

    # 订单详情存入数据库
    ushopper = request.session['ushopper']
    data = request.session['uorder']
    for i in data:
        odif = OrderInfo()
        odif.orderid = od
        ob = Goods.objects.get(id=i)

        odif.gid = ob
        odif.price = data[i]['price']
        odif.num = data[i]['num']
        odif.save()

        # 把购物车session中已购买的数据删除
        ushopper.pop(i)

        # 增加商品销量
        ob.num += data[i]['num']
        ob.storage -= data[i]['num']
        ob.save()

    request.session['ushopper'] = ushopper
    request.session['uorder'] = {}

    # 跳转到付款页面
    return HttpResponse('<script>alert("订单创建成功,请立即支付");location.href="/order/buy/?orderid='+str(od.id)+'"</script>')


# 付款
def orderbuy(request):
    ob = Order.objects.get(id=request.GET['orderid'])
    num = getshoppernum(request)
    return render(request, 'home/orderbuy.html', {'ob': ob, 'num': num})


# 我的订单
def myorder(request):
    ob = Order.objects.filter(uid=request.session['VipUser']['uid']).order_by('addtime').reverse()
    return render(request, 'home/person/order.html', {'ob': ob})


# 删除一条订单 ajax
def delmyorder(request):
    try:
        oid = request.GET['oid']
        ob = Order.objects.get(id=oid)
        ob.delete()
        return JsonResponse({'msg': '删除成功！'})
    except:
        return JsonResponse({'msg': '删除失败！'})


# 个人中心地址管理
def personaddress(request):
    if request.method == 'POST':
        # 拿到用户添加的信息，存到数据库
        ob = Address()
        ob.uid = Users.objects.get(id=request.session['VipUser']['uid'])
        ob.aname = request.POST['aname']
        ob.aphone = request.POST['aphone']
        ob.aaddress = request.POST['aaddress']
        # 判断如果用户设置了默认收货地址，则把数据库中所有的地址都改为非默认地址
        s = request.POST.get('status', 0)
        if s == '1':
            for i in Address.objects.filter(uid=request.session['VipUser']['uid']):
                i.status = 0
                i.save()
        ob.status = s
        ob.save()
        return HttpResponse('<script>alert("添加成功！");location.href="/person/address/?"</script>')

    else:
        # 查用户的收货地址
        uaddress = Address.objects.filter(uid=request.session['VipUser']['uid'])
        return render(request, 'home/person/address.html', {'uaddress': uaddress})


# 个人中心默认地址更换ajax
def persondaddress(request):
    aid = request.GET['aid']
    a = Address.objects.filter(uid=request.session['VipUser']['uid'])
    for i in a:
        if i.id == int(aid):  # 注意id是数字
            i.status = 1
        else:
            i.status = 0
        i.save()
    return HttpResponse('ok')


# 个人中心地址修改
def personaddressedit(request, aid):
    if request.method == 'POST':
        ob = Address.objects.get(id=request.POST['id'])
        ob.aname = request.POST['aname']
        ob.aphone = request.POST['aphone']
        ob.aaddress = request.POST['aaddress']
        s = request.POST['status']
        if s == '1':
            for i in Address.objects.filter(uid=request.session['VipUser']['uid']):
                i.status = 0
                i.save()
        ob.status = s
        ob.save()
        return HttpResponse('<script>alert("修改成功！");location.href="/person/address/?"</script>')
    ob = Address.objects.get(id=aid)
    return render(request, 'home/person/personaddressedit.html', {'ob': ob})


# 个人中心地址删除 ajax
def personaddressdel(request):
    try:
        aid = request.GET['aid']
        ob = Address.objects.get(id=aid)
        ob.delete()
        return JsonResponse({'msg': '删除成功！', 'code': 1})
    except:
        return JsonResponse({'msg': '删除失败！', 'code': 0})


# 个人信息
def personinformation(request):
    if request.method == 'POST':
        # 接受一下数据
        username = request.POST.get('username')
        sex = request.POST.get('sex')
        age = request.POST.get('age', 0)
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        # 找到数据库中的数据
        ob = Users.objects.get(id=request.session['VipUser']['uid'])
        if username:
            if not Users.objects.filter(username=username):
                ob.username = username
                data = request.session['VipUser']
                data['name'] = username
                request.session['VipUser'] = data
            else:
                return HttpResponse('<script>alert("用户名已被注册！");location.href="/person/information/?"</script>')
        if sex:
            ob.sex = sex
        if age:
            ob.age = age
        if phone:
            if not Users.objects.filter(phone=phone):
                ob.phone = phone
            else:
                return HttpResponse('<script>alert("手机号已被使用！");location.href="/person/information/?"</script>')
        if email:
            if not Users.objects.filter(email=email):
                ob.email = email
            else:
                return HttpResponse('<script>alert("邮箱已被使用！");location.href="/person/information/?"</script>')

        pic = request.FILES.get('picurl')
        if pic is not None:
            pic = upload(request)
            if ob.picurl != '/static/pics/default/default.png':
                os.remove('.' + ob.picurl)
            print(pic)
            ob.picurl = pic

        ob.save()
        vu = request.session['VipUser']
        if username:
            vu['name'] = username
        if pic:
            vu['pic'] = pic
        request.session['VipUser'] = vu

        return HttpResponse('<script>alert("修改成功！");location.href="/person/information/?"</script>')

    ob = Users.objects.get(id=request.session["VipUser"]['uid'])
    return render(request, 'home/person/information.html', {'ob': ob})


# 安全设置
def personsafety(request):
    ob = Users.objects.get(id=request.session["VipUser"]['uid'])
    return render(request, 'home/person/safety.html', {'ob': ob})


# 个人中心修改密码
def personpassword(request):
    if request.method == 'POST':
        try:
            pswd1 = request.POST['pswd1']
            pswd2 = request.POST['pswd2']

            ob = Users.objects.get(id=request.session['VipUser']['uid'])
            upass = check_password(pswd1, ob.password)
            if upass:
                ob.password = make_password(pswd2, None, 'pbkdf2_sha256')
                ob.save()
            return HttpResponse('<script>alert("修改成功！");location.href="/person/safety/"</script>')
        except:
            return HttpResponse('<script>alert("修改失败！");location.href="/person/password/?"</script>')

    return render(request, 'home/person/password.html')


# 个人中心修改密码ajax
def checkpersonpassword(request):
    if check_password(request.GET['tstext'], Users.objects.get(id=request.session['VipUser']['uid']).password):
        return JsonResponse({'code': '1'})
    else:
        return JsonResponse({'code': '0'})


# 个人中心修改邮箱
def personemail(request):
    if request.method == 'POST':
        # newemail = request.POST.getlist('email')
        newemail = request.POST['email']
        yzm_email = request.POST['yzm']

        if yzm_email != request.session['yzm_email']:
            return HttpResponse('<script>alert("验证码错误！");location.href="/person/email/"</script>')

        ob = Users.objects.get(id=request.session['VipUser']['uid'])
        ob.email = newemail
        ob.save()

        return HttpResponse('<script>alert("修改成功！");location.href="/person/safety/"</script>')
    return render(request, 'home/person/email.html')


# 验证个人邮箱
def personcheckemail(request):
    # 接受邮箱地址
    myemail = request.GET['vemail']

    # 生成验证码
    mylistpsw = [random.randrange(10) for i in range(4)]
    s = ''
    for i in mylistpsw:
        s += str(i)
    # 把验证码存入session
    request.session['yzm_email']=s
    # print(request.session['yzm_email'])

    # 发送邮件
    send_status = send_mail(
        '更改邮箱的验证码',
        '您的验证码为'+s,
        '1980919138@qq.com',  # 貌似这里必须写发送的邮箱地址
        [myemail],
    )

    # send_title = '123'
    # send_message = '123'
    # send_obj_list = ['madihegongda@126.com',]  # 收件人列表
    # # send_html_message = '<h1>包含 html 标签且不希望被转义的内容</h1>'
    # send_status = send_mail(send_title, send_message, settings.EMAIL_FROM, send_obj_list)
    return HttpResponse('ok')


# 在网页中显示名字使用
def showname(ob, request):
    if ob.username:
        request.session['VipUser'] = {'name': ob.username, 'pic': ob.picurl, 'uid': ob.id}
    elif ob.email:
        request.session['VipUser'] = {'name': ob.email, 'pic': ob.picurl, 'uid': ob.id}
    else:
        request.session['VipUser'] = {'name': ob.phone, 'pic': ob.picurl, 'uid': ob.id}

    if request.POST.get('check') == 'a':
        request.session.set_expiry(3600*24*15)
    else:
        request.session.set_expiry(0)


# 登录时检查用
def mylogin(arr, request):
    ob = Users.objects.get(**arr)
    # 检查密码对不对
    if check_password(request.POST['password'], Users.objects.filter(**arr)[0].password):
        showname(ob, request)
        return HttpResponse('<script>alert("登录成功！");location.href="/"</script>')
    else:
        return HttpResponse('<script>alert("请输入正确的密码！");location.href="/login/?name='+request.POST.get('name')+'"</script>')
