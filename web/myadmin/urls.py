"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . views import views, typeviews, goodsviews, orderviews, authviews

urlpatterns = [
    # 首页
    url(r'^$', views.index, name='adminindex'),
    # url(r'^login/$', views.adminlogin, name='adminlogin'),
    # url(r'^logout/$', views.adminlogout, name='adminlogout'),
    url(r'^vcode/$', views.vcode, name='adminvcode'),

    # 增删改查users
    url(r'^user/add/$', views.uadd, name='admin_user_add'),
    url(r'^user/insert/$', views.uinsert, name='admin_user_insert'),
    url(r'^user/list/$', views.ulist, name='admin_user_list'),
    url(r'^user/del/(?P<id>[0-9]+)/$', views.udel, name='admin_user_del'),
    url(r'^user/edit/(?P<id>[0-9]+)/$', views.uedit, name='admin_user_edit'),
    url(r'^user/update/$', views.uupdate, name='admin_user_update'),
    url(r'^user/state/$', views.ustate, name='admin_user_state'),

    # 新增users删除相关
    url(r'^user/listed/$', views.ulisted, name='admin_user_listed'),
    url(r'^user/deled/$', views.udeled, name='admin_user_deled'),
    url(r'^user/edited/(?P<id>[0-9]+)/$', views.uedited, name='admin_user_edited'),

    # 增删改查types
    url(r'^type/add/$', typeviews.tadd, name='admin_type_add'),
    url(r'^type/insert/$', typeviews.tinsert, name='admin_type_insert'),
    url(r'^type/list/$', typeviews.tlist, name='admin_type_list'),
    url(r'^type/edit/(?P<id>[0-9]+)/$', typeviews.tedit, name='admin_type_edit'),
    url(r'^type/update/$', typeviews.tupdate, name='admin_type_update'),
    url(r'^type/del/$', typeviews.tdel, name='admin_type_del'),

    # # 选择商品分类ajax  # test
    # url(r'^type/ajax/$', typeviews.tajax, name='admin_type_ajax'),

    # 增删改查goods
    url(r'^goods/add/$', goodsviews.gadd, name='admin_goods_add'),
    url(r'^goods/insert/$', goodsviews.ginsert, name='admin_goods_insert'),
    url(r'^goods/list/$', goodsviews.glist, name='admin_goods_list'),
    url(r'^goods/edit/(?P<id>[0-9]+)/$', goodsviews.gedit, name='admin_goods_edit'),
    url(r'^goods/update/$', goodsviews.gupdate, name='admin_goods_update'),
    url(r'^goods/del/$', goodsviews.gdel, name='admin_goods_del'),
    url(r'^goods/state/$', goodsviews.gstate, name='admin_goods_state'),

    # 订单管理
    # 列表显示订单：订单号，订单时间，用户，总价，总数，状态
    #     订单详情：订单号，订单时间，用户，总价，总数，状态，购买的商品和商品数量及商品的价格，收货信息
    #     状态更新，发货，取消订单
    url(r'^order/list/$', orderviews.olist, name='admin_order_list'),
    url(r'^order/state/$', orderviews.ostate, name='admin_order_state'),
    url(r'^order/listdetail/(?P<id>[0-9]+)$', orderviews.olistdetail, name='admin_order_listdetail'),

    # 管理员相关
    # 后台用户相关
    url(r'^auth/user/add/$', authviews.useradd, name='auth_user_add'),
    url(r'^auth/user/list/$', authviews.userlist, name='auth_user_list'),
    url(r'^auth/user/del/$', authviews.userdel, name='auth_user_del'),
    # 后台组相关
    url(r'^auth/group/add/$', authviews.groupadd, name='auth_group_add'),
    url(r'^auth/group/list/$', authviews.grouplist, name='auth_group_list'),
    url(r'^auth/group/del/$', authviews.groupdel, name='auth_group_del'),
    # 后台登录
    url(r'^login/$', authviews.adminlogin, name='adminlogin'),
    url(r'^logout/$', authviews.adminlogout, name='adminlogout'),
]
