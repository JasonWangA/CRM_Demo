from django.shortcuts import render, redirect, HttpResponse
from app01 import models
import json

def validate(func):
    def inner(request,*args,**kwargs):
        session_perm_l = list(map(lambda  x : x['menu_id__code'], request.session['permission_list']))
        session_kwargs_l = list(map(lambda  x : x['menu_id__kwargs'], request.session['permission_list']))
        print(request.session['permission_list'])
        if request.path_info.split('/')[1] in session_perm_l:
            print('pathfloor')
            if request.method =='POST' and request.POST.get('kwargs') :
                r_kwargs = request.POST.get('kwargs')
                if r_kwargs in session_kwargs_l:
                    print(request.POST)
                    ret = func(request,*args,**kwargs)
                    return ret
                else:
                    print('here')
                    data = {'error':'unauthored'}
                    return HttpResponse(json.dumps(data))
            else:
                ret = func(request,*args,**kwargs)
                return ret
        else:
            print('error')
            return HttpResponse('unauhoted')
    return inner

# Create your views here.
def login(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        obj = models.UserInfo.objects.filter(username=user, password=pwd).first()
        if obj:
            # 当前用户信息保存至Session
            request.session['user_info'] = {'id': obj.id, 'name': obj.username}

            # 当前用户角色列表保存至Session
            result_list = models.UserInfoToRole.objects.filter(user_id_id=obj.id).values('role_id_id')
            role_list = list(map(lambda x: x['role_id_id'], result_list))
            request.session['role_list'] = role_list

            # 当前用户所有权限加入Session
            from django.db.models import Count, Min, Max, Sum
            permission_list = models.RoleToPermission.objects.filter(role_id__in=role_list).values(
                'menu_id_id').annotate(c=Count('menu_id_id')).values('menu_id__caption',
                                                                     'menu_id__parent_id',
                                                                     'menu_id__code',
                                                                     'menu_id__method',
                                                                     'menu_id__kwargs',
                                                                     'menu_id__id')
            # 根据permission_id去重
            permission_list = list(permission_list)
            request.session['permission_list'] = permission_list

            menu_list = models.RoleToPermission.objects.filter(role_id__in=role_list,menu_id__is_menu=True).values(
                'menu_id_id').annotate(c=Count('menu_id_id')).values('menu_id__caption',
                                                                     'menu_id__parent_id',
                                                                     'menu_id__code',
                                                                     'menu_id__method',
                                                                     'menu_id__kwargs',
                                                                     'menu_id__id',)
            # 根据permission_id去重
            menu_list = list(menu_list)
            request.session['menu_list'] = menu_list

            return redirect('/index/')
    return render(request, 'login.html')

def build_node(menu_list, dic):
    #
    for menu in menu_list:
        if menu['id'] == dic['menu_id__parent_id']:
            temp = {'id': dic['menu_id__id'],'text': dic['menu_id__caption'], 'url': dic['menu_id__code'],'children': []}
            menu['children'].append(temp)
            break
        else:
            build_node(menu['children'], dic)

def build_tree(session_menu_list):
    # [ {menu_id__parent_id: None, 'menu_id__caption': '权限管理', 'menu_id__code': 'permission'},{},{} ]
    menu_list = []
    # menu_list = [{...}]
    for dic in session_menu_list:
        if dic['menu_id__parent_id'] == None:
            temp = {'id': dic['menu_id__id'],'text': dic['menu_id__caption'], 'url': dic['menu_id__code'],'children': []}
            menu_list.append(temp)
        else:
            # 当前
            build_node(menu_list, dic)
    return menu_list



def my_render(request, template_name, context=None, *args, **kwargs):
    session_menu_list = request.session['menu_list']
    print(request.session['permission_list'])
    menu_list = build_tree(session_menu_list)
    print(request.path_info.split('/')[1])
    if context:
        context['menu_list'] = menu_list
    else:
        context = {'menu_list': menu_list}
    return render(request, template_name, context, *args, **kwargs)



def index(request):
    # 根据session中保存的menu_list生成动态菜单
    # session_menu_list = request.session['menu_list']
    # menu_list = build_tree(session_menu_list)
    #
    # menu_list = [
    #     {
    #         'id': 1,
    #         'text': '权限管理',
    #         'url': None,
    #         'children': [
    #             {
    #                 'id': 4,
    #                 'text': '权限',
    #                 'url': 'permission'
    #             },
    #             {
    #                 'id': 5,
    #                 'text': '用户',
    #                 'url': 'user'
    #             }
    #         ]
    #      },
    #     {
    #         'id': 2,
    #         'text': '用户管理',
    #         'url': None
    #      },
    #     {
    #         'id': 3,
    #         'text': '帮助',
    #         'url': None
    #      }
    #
    #
    # ]

    return my_render(request, 'index.html')

@validate
def permission(request):
    # 当前用户所有的权限

    return my_render(request, 'permission.html')

def get_permission_tree(request):
    session_permission_list = request.session['permission_list']
    permission_list = build_tree(session_permission_list)
    return HttpResponse(json.dumps(permission_list))

def get_child_permission(request):
    node_parent_id = request.GET.get('node_parent_id')
    page = request.GET.get('page')
    rows = request.GET.get('rows')
    page = int(page)
    rows = int(rows)
    start = (page - 1) * rows
    end = page * rows

    result_queryset = models.Permission.objects.filter(parent_id = node_parent_id).values('caption','code')[start:end]
    result_list = list(result_queryset)
    # [ {'caption': 'x', 'code': xxx} ]
    return HttpResponse(json.dumps(result_list))

def user(request):
    return my_render(request, 'user.html')


def  delete_p(request):
    current_user_dic =  request.session['user_info']
    current_user_id = current_user_dic['id']
    current_user_name = current_user_dic['name']
    from django.db.models import Count, Min, Max, Sum
    related_role = models.UserInfoToRole.objects.filter(user_id_id = current_user_id).values('role_id_id')
# @validate
# def save_p(request):
#     r_args = request.POST.get('kwargs')
#     return HttpResponse('ok')