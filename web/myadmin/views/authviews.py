from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User,Permission,Group
from django.contrib.auth import authenticate, login,logout


def useradd(request):
    if request.method == 'GET':
        # 获取所有组
        glist = Group.objects.all()
        return render(request, 'auth/user/add.html', {'glist': glist})

    elif request.method == 'POST':
        try:
            # 执行管理员添加
            # 判断是否创建超级管理员
            if request.POST['is_superuser'] == '1':
                ob = User.objects.create_superuser(request.POST['username'], request.POST['email'], request.POST['password'])
            else:
                ob = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            # 进行添加
            ob.save()

            # 判断是否需要为用户分配组
            gs = request.POST.getlist('gs', None)
            print(gs)
            if gs:
                # 给当前用户分组
                ob.groups.set(gs)
                ob.save()

            return HttpResponse('<script>alert("添加成功！");location.href="/admin/auth/user/list/"</script>')
        except:
            return HttpResponse('<script>alert("添加失败！请确认您填写的信息是否符合要求！");location.href="/admin/auth/user/list/"</script>')


def userlist(request):
    # 获取所有管理员
    data = User.objects.all()
    return render(request, 'auth/user/list.html', {'ulist': data})


def userdel(request):
    try:
        id = request.GET['id']
        ob = User.objects.get(id=id)
        ob.delete()
        return JsonResponse({'code': '1', 'msg': '删除成功！'})
    except:
        return JsonResponse({'code': '0', 'msg': '删除失败！'})


def groupadd(request):
    if request.method  == 'GET':
        # 读取所有权限信息，排除以Can开头的系统默认权限
        perms = Permission.objects.exclude(name__istartswith='Can')
        return render(request, 'auth/group/add.html', {'perms': perms})
    elif request.method == 'POST':
        # 创建组
        g = Group(name=request.POST['name'])
        g.save()

        # 获取选择的所有权限
        prms = request.POST.getlist('prms', None)
        # 判断是否需要给组添加权限
        if prms:
            # 给组分配权限
            g.permissions.set(prms)
            g.save()
        return HttpResponse('<script>alert("添加成功！");location.href="/admin/auth/group/list/"</script>')


def grouplist(request):
    # 获取所有组
    data = Group.objects.all()
    return render(request, 'auth/group/list.html', {'glist': data})


def groupdel(request):
    try:
        id = request.GET['id']
        ob = Group.objects.get(id=id)
        ob.delete()
        return JsonResponse({'code': '1', 'msg': '删除成功！'})
    except:
        return JsonResponse({'code': '0', 'msg': '删除失败！'})


def adminlogin(request):
    if request.method == 'POST':
        # 判断验证码是否正确
        if request.POST['vcode'].lower() != request.session['verifycode'].lower():
            return HttpResponse('<script>alert("请输入正确的验证码");location.href="/admin/login/"</script>')

        # 记住密码
        if request.POST.get('rem', ''):
            request.session['rem'] = '1'
            request.session.set_expiry(3600*24*15)
        else:
            request.session.set_expiry(0)

        # 使用django提供的后台用户验证方法
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            #登录
            login(request,user)
            return HttpResponse('<script>location.href="/admin/"</script>')

        return HttpResponse('<script>alert("用户名或密码不存在");location.href="/admin/login/"</script>')        
    else:
        return render(request, 'admin/login.html')


def adminlogout(request):
    logout(request)

    # 重置记住密码命令
    request.session['rem'] = '0'
    return HttpResponse('<script>alert("退出登录成功!");location.href="/admin/login/"</script>')
