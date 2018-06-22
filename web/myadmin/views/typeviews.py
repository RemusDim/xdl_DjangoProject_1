from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .. models import Types
from django.contrib.auth.decorators import permission_required


# 增加
@permission_required('myadmin.insert_types',raise_exception = True)
def tadd(request):
    ob = Types.objects.extra(select={'paths': 'concat(path,id)'}).order_by('paths')
    ob = ordertypename(ob)
    return render(request, 'admin/type/add.html', {'ob': ob})


# 写入
@permission_required('myadmin.insert_types',raise_exception = True)
def tinsert(request):
    try:
        ob = Types()
        ob.pid = int(request.POST.get('tid'))
        ob.typename = request.POST.get('typename')
        if ob.pid == 0:
            ob.path = '0,'
        else:
            ob.path = Types.objects.get(id=ob.pid).path + str(ob.pid) + ','
        ob.save()
        return HttpResponse('<script>alert("添加成功！");location.href="/admin/type/list/"</script>')
    except:
        return HttpResponse('<script>alert("添加失败！");location.href="/admin/type/add/"</script>')


# 展示
@permission_required('myadmin.show_types',raise_exception = True)
def tlist(request):
    ob = Types.objects.extra(select = {'paths':'concat(path,id)'}).order_by('paths')
    # ob = ordertypename(ob)
    # 搜索类型
    sousel = request.GET.get('sousel')
    # 关键字
    souinp = request.GET.get('souinp')

    # 找出所有种类的名字
    ob_names1 = []
    ob_names2 = []
    ob_name = Types.objects.all()
    for i in ob_name:
        ob_names1.append(i.typename)
        ob_names2.extend(list(i.typename))

    ob_names2.extend(ob_names1)

    if souinp in ob_names2:
        sou_pid = []
        for i in ob_names1:
            if souinp in i:
                sou_pid.append(Types.objects.get(typename=i).id)
    else:
        sou_pid = []

    # 顶级分类的情况
    if souinp == '顶级分类':
        sou_pid = 0
    # 全部分类
    if sousel == 'all':
        q = Q()
        for i in sou_pid:
            q.add(Q(**{'pid__exact':int(i)}), Q.OR)
        q.add(Q(**{'typename__contains':souinp}), Q.OR)
        ob = Types.objects.filter(q).extra(select = {'paths':'concat(path,id)'}).order_by('paths')
    # 分类名称
    elif sousel == 'tname':
        ob = Types.objects.filter(typename__contains=souinp).extra(select = {'paths':'concat(path,id)'}).order_by('paths')
    # 父级分类
    elif sousel == 'ptname':
        q = Q()
        if len(sou_pid) != 0:
            for i in sou_pid:
                q.add(Q(**{'pid__exact':int(i)}), Q.OR)
         
        ob = Types.objects.filter(q).extra(select = {'paths':'concat(path,id)'}).order_by('paths')

    ob = ordertypename(ob)

    # 创建分页对象
    page_ina = Paginator(ob, 8)
    # 从list页面传过来的页数参数，如果没有传则说明是第一页，故默认值是1
    p = int(request.GET.get('p',1))
    typelist = page_ina.page(p)
    # print(typelist)
    # num = len(page_ina.page_range)
    num = page_ina.num_pages

    return render(request, 'admin/type/list.html', {'ob': typelist, 'num': num, 'p': p})

# 编辑
@permission_required('myadmin.edit_types',raise_exception = True)
def tedit(request, id):
    ob = Types.objects.extra(select = {'paths':'concat(path,id)'}).order_by('paths')
    allob = ordertypename(ob)
    ob = Types.objects.get(id=id)
    return render(request, 'admin/type/edit.html', {'ob': ob, 'allob': allob})


# 写入
@permission_required('myadmin.edit_types',raise_exception = True)
def tupdate(request):
    try:
        tname = request.POST.get('typename')
        ob = Types.objects.get(id=request.POST.get('id'))
        ob.typename = tname
        ob.save()
        return HttpResponse('<script>alert("修改成功！");location.href="/admin/type/list/"</script>')
    except:
        return HttpResponse('<script>alert("修改失败！");location.href="/admin/type/add/"</script>')


# 删除
@permission_required('myadmin.del_types',raise_exception = True)
def tdel(request):
    tid = request.GET.get('tid')
    obnum = Types.objects.filter(pid=tid).count()

    if obnum == 0:
        ob = Types.objects.get(id=tid)
        print(ob.typename)
        ob.delete()
        return JsonResponse({'status': 1, 'msg': '已经删除！'})
    else:
        return JsonResponse({'status': 0, 'msg': '此分类还有子类，不能进行删除操作！'})


# # 选择商品分类ajax  # test
# def tajax(request):
#     ob = Types.objects.filter(pid=int(request.GET.get('tid'))).values()
#     return JsonResponse(list(ob), safe=False)


# 处理一下取出的数据
def ordertypename(ob):
    for i in ob:
        if i.pid == 0:
            # 父级分类
            i.pname = '顶级分类'

            # 路径
            i.ppath = '顶级分类/'

            pathlist = ['0']

            i.lv = 1  # test
        else:
            # 父级分类
            i.pname = Types.objects.get(id=i.pid).typename

            # 路径
            pathlist = i.path.split(',')[:-1]
            i.ppath = ''
            for j in pathlist:
                if j == '0':
                    i.ppath += '顶级分类/'
                else:
                    i.ppath += Types.objects.get(id=int(j)).typename + '/'

            i.lv = len(pathlist)  # test

        i.typename = (len(pathlist)-1) * '|--' + i.typename
    return ob
