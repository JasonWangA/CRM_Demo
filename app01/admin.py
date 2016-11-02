from django.contrib import admin
from app01 import models
# Register your models here.
admin.site.register(models.Permission)
admin.site.register(models.Role)
admin.site.register(models.RoleToPermission)
admin.site.register(models.UserInfo)
admin.site.register(models.UserInfoToRole)
# python manage.py createsuperuser
# root,  root!23456
