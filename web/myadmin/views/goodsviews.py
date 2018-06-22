import os
from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .. models import Types, Goods
from . typeviews import ordertypename
from . views import upload
from django.contrib.auth.decorators import permission_required


# 添加
@permission_required('myadmin.insert_goods',raise_exception = True)
def gadd(request):
    ob = Types.objects.extra(select={'paths': 'concat(path,id)'}).order_by('paths')
    ob = ordertypename(ob)
    return render(request, 'admin/goods/add.html', {'ob': ob})


# 存入输入库
@permission_required('myadmin.insert_goods',raise_exception = True)
def ginsert(request):
    try:
        data = Goods()
        data.typeid = Types.objects.get(id=request.POST.get('tid'))
        data.title = request.POST.get('title')
        data.price = request.POST.get('price')
        data.storage = request.POST.get('storage')
        data.info = request.POST.get('info')

        pic = request.FILES.get('picurl')
        if (pic is not None):
            pic = upload(request)
            if pic is False:
                return HttpResponse('<script>alert("请输入正确格式的图片");location.href="/admin/goods/add/"</script>')
            data.picurl = pic
        else:
            return HttpResponse('<script>alert("请传入商品图片");location.href="/admin/goods/add/"</script>')

        data.save()
        return HttpResponse('<script>alert("添加成功！");location.href="/admin/goods/list"</script>')
    except:
        return HttpResponse('<script>alert("添加失败！");location.href="/admin/goods/add"</script>')


# 展示数据
@permission_required('myadmin.show_goods',raise_exception = True)
def glist(request):

    data = Goods.objects.all()

    # 关键字搜索
    sousel = request.GET.get('sousel', None)
    souinp = request.GET.get('souinp', '')

    # 找出所有种类的名字
    ob_names2 = []
    ob_name = []
    for i in Goods.objects.all():
        ob_name.append(i.typeid.typename)  # 根据商品表查类型表

    # 把字母、字存入查询列表
    for i in ob_name:
        ob_names2.extend(list(i))

    # 把词存入查询列表
    ob_names2.extend(ob_name)

    # 通过字母、字，找到词，进而查到商品对应的类型id
    sou_pid = []
    if souinp in ob_names2:
        for i in ob_name:
            if souinp in i:
                sou_pid.append(Types.objects.get(typename=i).id)

    # 去重，sou_pid拿到的是模糊搜索中查到的字段在types表中的id值
    sou_pid = list(set(sou_pid))

    if sousel == 'title':
        data = Goods.objects.filter(title__contains=souinp)
    elif sousel == 'typename':
        q = Q()
        if len(sou_pid) != 0:
            for i in sou_pid:
                q.add(Q(**{'typeid__id__contains':int(i)}), Q.OR)
       
        data = Goods.objects.filter(q)

        # 通过外键直接模糊搜索，此为测试
        # data = Goods.objects.filter(Q(typeid__id__contains=souinp))
    else:
        q = Q()
        for i in sou_pid:
            q.add(Q(**{'typeid__id__contains':int(i)}), Q.OR)
        q.add(Q(**{'title__contains':souinp}), Q.OR)
        data = Goods.objects.filter(q)

    # 排序相关
    gdsort = request.GET.get('gdsort', 'up')
    gdsort_item = request.GET.get('gdsort_item', 'id')
    if gdsort == 'up':
        data = data.order_by(gdsort_item)
    else:
        data = data.order_by(gdsort_item).reverse()

    # 创建分页对象
    page_ina = Paginator(data, 8)
    # 从list页面传过来的页数参数，如果没有传则说明是第一页，故默认值是1
    p = int(request.GET.get('p',1))
    data = page_ina.page(p)
    num = page_ina.num_pages

    return render(request, 'admin/goods/list.html', {'ginfo': data, 'num': num, 'p': p})


# 编辑
@permission_required('myadmin.edit_goods',raise_exception = True)
def gedit(request, id):
    data = Goods.objects.get(id=id)
    ob = Types.objects.extra(select={'paths': 'concat(path,id)'}).order_by('paths')
    ob = ordertypename(ob)
    return render(request, 'admin/goods/edit.html', {'ginfo': data, 'ob': ob})


# 更新
@permission_required('myadmin.edit_goods',raise_exception = True)
def gupdate(request):
    try:
        ob = Goods.objects.get(id=request.POST.get('id'))
        ob.typeid = Types.objects.get(id=request.POST.get('tid'))
        ob.title = request.POST.get('title')
        ob.price = request.POST.get('price')
        ob.storage = request.POST.get('storage')
        ob.info = request.POST.get('info')

        pic = request.FILES.get('picurl', None)
        if pic is not None:
            pic = upload(request)
            if pic is False:
                return HttpResponse('<script>alert("请输入正确格式的图片");location.href="/admin/goods/edit/"</script>')
            os.remove('.' + ob.picurl)
            ob.picurl = pic

        ob.save()
        return HttpResponse('<script>alert("修改成功！");location.href="/admin/goods/list"</script>')
    except:
        return HttpResponse('<script>alert("修改失败！");location.href="/admin/goods/list"</script>')


# 删除
@permission_required('myadmin.del_goods',raise_exception = True)
def gdel(request):
    ob = Goods.objects.get(id=request.GET.get('gid'))
    os.remove('.' + ob.picurl)
    ob.delete()
    return HttpResponse('ok')


# 状态操作
def gstate(request):
    sid = request.GET.get('sid')
    ob = Goods.objects.get(id=int(sid))
    ob.status = int(request.GET.get('v'))
    ob.save()
    return HttpResponse('ok')
