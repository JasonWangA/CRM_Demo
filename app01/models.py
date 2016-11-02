from django.db import models

# Create your models here.


class Permission(models.Model):
    ##菜单的的权限,主要是为后台界面菜单部分单独拆分出来的字段,跟下面定义的code,method,kwargs等字段进行区分
    caption = models.CharField(max_length=32,blank=True)
    ##用于构造树形结构的权限表,可以自己关联自己
    parent_id = models.ForeignKey('Permission', related_name='k', to_field='id', null=True, blank=True)
    ##具体的某个访问的url
    code = models.CharField(max_length=64, null=True,blank=True)
    ##具体的请求方法
    method = models.CharField(max_length=16, null=True,blank=True)
    ##请求方法所带的参数
    kwargs = models.CharField(max_length=128, null=True,blank=True)
    ##是否是菜单栏
    is_menu = models.BooleanField(default=False)

    def __str__(self):
        return self.caption

class Role(models.Model):
    #定义角色名称
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class RoleToPermission(models.Model):
    ##定义角色和权限的对应关系
    menu_id = models.ForeignKey(Permission, to_field='id')
    role_id = models.ForeignKey(Role, to_field='id')

    def __str__(self):
        return "%s-%s" %(self.menu_id.caption, self.role_id.name)
# 目标，根据角色列表获取权限 li
# 获取当前用户的所有标题权限
# RoleToPermission.objects.filter(role_id__in=li,menu_id__is_menu=True).\
#     values('menu_id__caption','menu_id__parent_id','menu_id__parent_id','menu_id__code')

# 获取当前用户的所有权限
# RoleToPermission.objects.filter(role_id__in=li).\
#     values('menu_id__caption','menu_id__parent_id','menu_id__parent_id','menu_id__code')

class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.username


class UserInfoToRole(models.Model):
    user_id = models.ForeignKey(UserInfo, to_field='id')
    role_id = models.ForeignKey(Role, to_field='id')
    def __str__(self):
        return '%s-%s' %(self.user_id.username, self.role_id.name)

# userinfo: id = 3 username=alex
# result_list = UserInfoToRole.objects.filter(user_id_id=3).values('role_id_id')
# UserInfoToRole.objects.filter(user_id_id=1).values_list('role_id_id')
# [{'role_id_id': 1}.{'role_id_id': 2}.{'role_id_id': 3}]
# 当前用户的角色列表
# li = list(map(lambda x: x['role_id_id'], result_list))
# [1,2,3]
# [(1,)]
# [1,2,3]