from django.shortcuts import render,reverse
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.core.paginator import Paginator
from .. models import Users, Goods
import time,random,os
from django.contrib.auth.decorators import permission_required

# Create your views here.


# 首页
def index(request):
    usernum = Users.objects.all().count()
    goodsnum = Goods.objects.all().count()

    return render(request, 'admin/index.html', {'usernum': usernum, 'goodsnum': goodsnum})


# 旧版的登入
def adminlogin(request):
    if request.method == 'POST':
        # 判断验证码是否正确
        if request.POST['vcode'].lower() != request.session['verifycode'].lower():
            return HttpResponse('<script>alert("请输入正确的验证码");location.href="/admin/login/"</script>')

        # 查找用户是否在库中
        un = Users.objects.filter(username=request.POST['username'])
        if un:
            # 如果有多个用户同名循环判断
            for i in un:
                # 检查密码对不对
                if check_password(request.POST['password'], i.password):
                    # 看看用户有没有权限
                    if i.status == 0:
                        # 记住用户
                        request.session['AdminUsers'] = {'name': i.username, 'pic': i.picurl}
                        if request.POST.get('rem', '') == '1':
                            request.session.set_expiry(3600*24*15)
                            return HttpResponse('<script>alert("登录成功");location.href="/admin/"</script>')
                        else:
                            request.session.set_expiry(0)
                            return HttpResponse('<script>alert("登录成功");location.href="/admin/"</script>')
        
        return HttpResponse('<script>alert("请输入正确的用户名或密码");location.href="/admin/login/"</script>')
    else:
        return render(request, 'admin/login.html')


# 旧版的登出
def adminlogout(request):
    del request.session['AdminUsers']
    return HttpResponse('<script>alert("退出成功");location.href="/admin/login/"</script>')
        

# 验证码生成函数
def vcode(request):
    #引入绘图模块
    from PIL import Image, ImageDraw, ImageFont
    #引入随机函数模块
    import random
    #定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    #创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    #创建画笔对象
    draw = ImageDraw.Draw(im)
    #调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    #定义验证码的备选值
    str1 = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    #构造字体对象
    font = ImageFont.truetype('FreeMono.ttf', 23)
    #构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    #绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    #释放画笔
    del draw
    #存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    #内存文件操作
    import io
    buf = io.BytesIO()
    #将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    #将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


# 显示用户添加页面
@permission_required('myadmin.insert_users',raise_exception = True)
def uadd(request):

    return render(request, 'admin/user/add.html')


# 执行用户添加
@permission_required('myadmin.insert_users',raise_exception = True)
def uinsert(request):
    try:
        us = Users()
        us.username = request.POST.get('username')
        us.age = request.POST.get('age')
        us.sex = request.POST.get('sex')
        us.phone = request.POST.get('phone')
        us.email = request.POST.get('email')

        # 密码
        upass = make_password(request.POST.get('password'), None, 'pbkdf2_sha256')
        us.password = upass

        # 图片
        pic = upload(request)
        if pic is False:
            return HttpResponse('<script>alert("请输入正确格式的图片");location.href="/admin/user/add/"</script>')
        us.picurl = pic

        us.save()

        return HttpResponse('<script>alert("添加成功！");location.href="/admin/user/list/"</script>')
    except:
        return HttpResponse('<script>alert("添加失败！");location.href="/admin/user/add/"</script>')


# 用户列表页
@permission_required('myadmin.show_users',raise_exception = True)
def ulist(request):
    data = request.GET
    datasel = data.get('sousel')
    datainp = data.get('souinp')

    if datainp:
        status_sel = {'管理员': 0, '管': 0, '理': 0, '员': 0, '正常': 1, '正': 1, '常': 1, '禁用': 2, '禁': 2, '用': 2}
        status_res = status_sel.get(datainp, 'None')

        if datasel == 'all':
            uinfo = Users.objects.filter(
                Q(username__contains=datainp)|Q(age__contains=datainp)|
                Q(sex__contains=datainp)|Q(phone__contains=datainp)|
                Q(email__contains=datainp)|Q(addtime__contains=datainp)|
                Q(status__contains=status_res)
            ).exclude(status=3)

        elif datasel == 'username':
            uinfo = Users.objects.filter(Q(username__contains=datainp)).exclude(status=3)
        elif datasel == 'age':
            uinfo = Users.objects.filter(Q(age__contains=datainp)).exclude(status=3)
        elif datasel == 'sex':
            uinfo = Users.objects.filter(Q(sex__contains=datainp)).exclude(status=3)
        elif datasel == 'phone':
            uinfo = Users.objects.filter(Q(phone__contains=datainp)).exclude(status=3)
        elif datasel == 'email':
            uinfo = Users.objects.filter(Q(email__contains=datainp)).exclude(status=3)
        elif datasel == 'addtime':
            uinfo = Users.objects.filter(Q(addtime__contains=datainp)).exclude(status=3)
        elif datasel == 'status':
            uinfo = Users.objects.filter(Q(status__contains=status_res)).exclude(status=3)
    else:
        uinfo = Users.objects.exclude(status=3)

    # 创建分页对象
    page_ina = Paginator(uinfo, 8)
    p = int(request.GET.get('p',1))
    userlist = page_ina.page(p)
    # num = len(page_ina.page_range)
    num = page_ina.num_pages

    return render(request, 'admin/user/list.html', {'uinfo': userlist, 'num': num, 'p': p})


# 用户删除页
@permission_required('myadmin.del_users',raise_exception = True)
def udel(request, id):
    try:
        ob = Users.objects.get(id=id)
        ob.status = 3
        ob.save()
        return HttpResponse('<script>alert("删除成功！");location.href="/admin/user/list/"</script>')
    except:
        return HttpResponse('<script>alert("删除失败！");location.href="/admin/user/list/"</script>')


# 用户修改
@permission_required('myadmin.edit_users',raise_exception = True)
def uedit(request, id):
    ob = Users.objects.get(id=id)
    return render(request, 'admin/user/edit.html', {'ob': ob, 'e': 0})


# 执行修改
@permission_required('myadmin.edit_users',raise_exception = True)
def uupdate(request):
    if request.POST.get('e', 1) == '0':
        loc = '/admin/user/list/'
    else:
        loc = '/admin/user/listed/'

    try:
        res = request.POST.get('id')

        ob = Users.objects.get(id=int(res))
        ob.username = request.POST.get('username')
        ob.age = request.POST.get('age')
        ob.sex = request.POST.get('sex')
        ob.phone = request.POST.get('phone')
        ob.email = request.POST.get('email')

        pic = request.FILES.get('picurl')
        if (pic is not None):
            if (ob.picurl != '/static/pics/default/default.png'):
                os.remove('.'+ob.picurl)
            pic = upload(request)
            if pic is False:
                return HttpResponse('<script>alert("请输入正确格式的图片");location.href="/admin/user/add/"</script>')
            ob.picurl = pic
        ob.save()
        return HttpResponse('<script>alert("修改成功！");location.href="'+loc+'"</script>')
    except:
        return HttpResponse('<script>alert("修改失败！");location.href="'+loc+'"</script>')


def ustate(request):
    sid = request.GET.get('sid')
    ob = Users.objects.get(id=int(sid))
    ob.status = int(request.GET.get('v'))
    ob.save()
    return HttpResponse('ok')


# 已删除成员列表的展示、删除、编辑
@permission_required('myadmin.show_users',raise_exception = True)
def ulisted(request):
    uinfo = Users.objects.filter(status=3)
    return render(request, 'admin/user/listed.html', {'uinfo': uinfo})


@permission_required('myadmin.del_users',raise_exception = True)
def udeled(request):
    sid = request.GET.get('sid')
    ob = Users.objects.get(id=int(sid))
    if ob.picurl != '/static/pics/default/default.png':
        os.remove('.'+ob.picurl)
    ob.delete()
    return HttpResponse('ok')


@permission_required('myadmin.edit_users',raise_exception = True)
def uedited(request, id):
    ob = Users.objects.get(id=id)
    return render(request, 'admin/user/edit.html', {'ob': ob, 'e': 1})


def upload(request):
    picob = request.FILES.get('picurl')
    if not picob:
        return '/static/pics/default/default.png'

    # 通过后缀名判断文件类型
    hzm = picob.name.split('.').pop()
    if hzm not in ['jpg', 'png', 'gif', 'icon', 'bmp', 'jpeg']:
        return False

    # 拼接名字
    tname = str(time.time())
    rname = str(random.randrange(10000, 99999))

    # 存储文件
    pfile = open('./static/pics/'+tname+rname+'.'+hzm, 'wb+')
    for i in picob.chunks():
        pfile.write(i)
    pfile.close()

    return '/static/pics/'+tname+rname+'.'+hzm
