from django.db import models

# Create your models here.


# 会员模型
class Users(models.Model):
    username = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=77)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)
    sex = models.CharField(max_length=1, null=True)
    age = models.IntegerField(null=True)
    picurl = models.CharField(max_length=100, default='/static/pics/default/default.png')
    # 0后台管理员 1为启用 2为禁用 3为逻辑删除
    status = models.IntegerField(default=1)
    addtime = models.DateTimeField(auto_now_add=True)

    # 指定生成权限：
    class Meta:
        permissions = (
            ("show_users", "查看会员"), 
            ("insert_users", "添加会员"), 
            ("edit_users", "修改会员"), 
            ("del_users", "删除会员")
        )


# 商品分类模型
class Types(models.Model):
    typename = models.CharField(max_length=50)
    pid = models.IntegerField()
    path = models.CharField(max_length=50)

    # def __str__(self):
    #     return self.typename

    # 指定生成权限：
    class Meta:
        permissions = (
            ("show_types", "查看商品分类"), 
            ("insert_types", "添加商品分类"), 
            ("edit_types", "修改商品分类"), 
            ("del_types", "删除商品分类")
        )


# 商品模型
class Goods(models.Model):
    typeid = models.ForeignKey(to="Types", to_field="id")
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    storage = models.IntegerField()
    picurl = models.CharField(max_length=100)
    info = models.TextField()
    # 购买数量
    num = models.IntegerField(default=0)
    clicknum = models.IntegerField(default=0)
    # 商品状态：1.新品、2.热销、3.下架
    status = models.IntegerField(default=1)
    addtime = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title


    # 指定生成权限：
    class Meta:
        permissions = (
            ("show_goods", "查看商品"), 
            ("insert_goods", "添加商品"), 
            ("edit_goods", "修改商品"), 
            ("del_goods", "删除商品")
        )


# 会员收货地址
class Address(models.Model):
    # 用户id
    uid = models.ForeignKey(to="Users", to_field="id")
    aname = models.CharField(max_length=50)
    aaddress = models.CharField(max_length=255)
    aphone = models.CharField(max_length=20)
    # 是否为默认，1为默认
    status = models.IntegerField(default=0)


    # 指定生成权限：
    class Meta:
        permissions = (
            ("show_address", "查看地址"), 
            ("insert_address", "添加地址"), 
            ("edit_address", "修改地址"), 
            ("del_address", "删除地址")
        )


# 订单表
class Order(models.Model):
    uid = models.ForeignKey(to="Users", to_field="id")
    address = models.ForeignKey(to="Address", to_field="id")
    totalprice = models.FloatField()
    totalnum = models.IntegerField()
    # 1.未付款 2.已付款、待发货 3.已发货、待收货 4.已完成 5.已取消
    status = models.IntegerField(default=1)
    addtime = models.DateTimeField(auto_now_add=True)


    # 指定生成权限：
    class Meta:
        permissions = (
            ("show_order", "查看订单"), 
            ("insert_order", "添加订单"), 
            ("edit_order", "修改订单"), 
            ("del_order", "删除订单")
        )


# 订单详情表
class OrderInfo(models.Model):
    orderid = models.ForeignKey('Order',to_field="id")
    gid =  models.ForeignKey('Goods',to_field="id")
    num = models.IntegerField()
    price = models.FloatField()
