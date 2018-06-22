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
from . import views

urlpatterns = [
    # 首页-----
    url(r'^$', views.index, name='index'),
    # 列表页
    url(r'^list/(?P<id>[0-9]+)/$', views.list, name='list'),
    # 详情页
    url(r'^info/(?P<id>[0-9]+)/$', views.info, name='info'),
    # 注册
    url(r'^register/$', views.register, name='register'),
    # 登录
    url(r'^login/$', views.login, name='login'),
    # 退出登录
    url(r'^logout/$', views.logout, name='logout'),

    # 购物车-----
    # 增商品
    url(r'^shopper/add/$', views.shopperadd, name='shopperadd'),
    # 清空购物车
    url(r'^shopper/del/$', views.shopperdel, name='shopperdel'),
    # 显示购物车
    url(r'^shopper/list/$', views.shopperlist, name='shopperlist'),
    # 购物车增加商品ajax
    url(r'^shopper/addgoods/$', views.shopperaddgoods, name='shopperaddgoods'),
    # 删除购物车中一条商品数据ajax
    url(r'^shopper/delonedata/$', views.delonedata, name='delonedata'),

    # 我的订单-----
    # 订单确认
    url(r'order/confirm/$', views.orderconfirm, name='orderconfirm'),
    # 生成订单
    url(r'order/create/$', views.ordercreate, name='ordercreate'),
    # 付款
    url(r'order/buy/$', views.orderbuy, name='orderbuy'),

    # 个人中心-----(收货地址 增删改查、个人基本信息查看和更新)
    #首页
    url(r'^person/$', views.personindex, name='personindex'),
    # 我的订单
    url(r'person/myorder/$', views.myorder, name='myorder'),
    # 删除订单
    url(r'person/delmyorder/$', views.delmyorder, name='delmyorder'),
    # 收货地址管理
    url(r'^person/address/$', views.personaddress, name='personaddress'),
    # 收货地址编辑
    url(r'^person/addressedit/(?P<aid>[0-9]+)/$', views.personaddressedit, name='personaddressedit'),
    # 个人中心地址删除
    url(r'^person/addressdel/$', views.personaddressdel, name='personaddressdel'),
    # 个人中心默认地址更换
    url(r'^person/defaultaddress/$', views.persondaddress, name='persondaddress'),
    # 个人信息
    url(r'^person/information/$', views.personinformation, name='personinformation'),
    # 安全设置
    url(r'^person/safety/$', views.personsafety, name='personsafety'),
    # 个人中心修改密码
    url(r'^person/password/$', views.personpassword, name='personpassword'),
    # 个人中心修改密码ajax
    url(r'^person/checkpassword/$', views.checkpersonpassword, name='checkpersonpassword'),
    # 个人中心修改邮箱
    url(r'^person/email/$', views.personemail, name='personemail'),
    url(r'^person/checkemail/$', views.personcheckemail, name='personcheckemail'),
]
