from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .. models import Types, Goods, Order, OrderInfo, Users
from django.db.models import Q
from django.contrib.auth.decorators import permission_required


# 列表显示订单
@permission_required('myadmin.show_order',raise_exception = True)
def olist(request):
    ob = Order.objects.all()

    sousel = request.GET.get('sousel')
    souinp = request.GET.get('souinp')
    unms = []
    
    if souinp:
        unms = Users.objects.filter(username__contains=souinp)

    if sousel == 'all':
        q = Q()
        for i in unms:
            q.add(Q(**{'uid__id__exact':int(i.id)}), Q.OR)

        for i in ['id__contains', 'totalprice__contains', 'totalnum__contains', 'addtime__contains']:
            q.add(Q(**{i: souinp}), Q.OR)

        ob = Order.objects.filter(q)
    elif sousel == 'username':
        q = Q()
        if unms:
            for i in unms:
                q.add(Q(**{'uid__id__exact':int(i.id)}), Q.OR)
        ob = Order.objects.filter(q)

    # 创建分页对象
    page_ina = Paginator(ob, 8)
    # 从list页面传过来的页数参数，如果没有传则说明是第一页，故默认值是1
    p = int(request.GET.get('p',1))
    ob = page_ina.page(p)
    num = page_ina.num_pages

    return render(request, 'admin/order/list.html', {'oinfo': ob, 'num': num, 'p': p})


# 订单状态修改 ajax
def ostate(request):
    oid = request.GET['oid']
    s = request.GET['s']
    ob = Order.objects.get(id=oid)
    ob.status = s
    ob.save()
    return HttpResponse('ok')


# 列表显示订单详情
@permission_required('myadmin.show_order',raise_exception = True)
def olistdetail(request, id):
    ob = Order.objects.get(id=id)
    ob = ob.orderinfo_set.all()
    return render(request, 'admin/order/listdetail.html', {'oinfo': ob})