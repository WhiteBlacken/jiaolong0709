from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from teng.models import Business

def getCommonCate():
    # 每页都查分类
    context = {}
    # 获取分类及所有二级分类进行填充
    allSub = []
    allBusiness = Business.objects.all()
    for business in allBusiness:
        business.listSub = business.subbusiness_set
        for sub in business.listSub.all():
            allSub.append(sub)
    context['allBusiness'] = allBusiness
    context['allSub'] = allSub
    return context

def login(request):
    # 获取登录页面的路径
    next = request.GET.get('next','/index/')
    # 和数据库中对象比对
    # 用户名是否存在
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = authenticate(request,username=username,password=password)

    if user:
        request.session['username'] = username
        groups = Group.objects.filter(user=user)
        if not any(groups):
            return HttpResponse('没有权限，请联系管理员')
        groupname = groups.first().name
        if groupname == "DataEntryClerk":
            return redirect('/myAdmin/index/')
    else:
        return HttpResponse("用户名或密码错误")
    return redirect(next)


def logout(request):
    request.session.flush()
    return redirect("/index/")

def goCreateAcc(request):
    # 每页都查分类
    context = getCommonCate()
    return render(request, 'rbac/create_account.html', {'context':context})


# 注册逻辑
def register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    hasUser = User.objects.filter(username=username)
    if any(hasUser):
        return HttpResponse("该账户已被注册")
    user = User()
    user.username = username
    user.set_password(password)
    user.save()
    group = Group.objects.get(name="nonmember")
    user.groups.add(group)
    user.save()
    request.session['username'] = username
    return redirect("/index/")

def info_of_myaccount(request):

    context = getCommonCate()
    # 读取个人信息 有bug待修复
    username = request.session.get('username', '')
    if not username:
        return HttpResponse('请先登录')
    context['username'] = username
    user = User.objects.get(username=username)
    group = Group.objects.filter(user=user)
    if any(group):
        groupname = group.first().name
        if groupname == 'DataEntryClerk':
            context['groupname'] = '管理员'
            context['limits'] = '可访问所有数据和后台'
        if groupname == 'member':
            context['groupname'] = '会员'
            context['limits'] = '可访问所有数据'
        if groupname == 'nonmember':
            context['groupname'] = '非会员'
            context['limits'] = '每类数据只可访问2条'
    else:
        context['groupname'] = '无等级'
        context['limits'] = '每类数据只可访问2条'
    return render(request,'rbac/my_account.html',{'context':context})

# 目前是点击直接升级，测试用
# 点击后应该是升级页面
# 后续升级不变，但是要接收充值成功的信号
def upgrade_by_spend(request):
    # bug：没有账号能否到达这个页面？
    username = request.session.get('username')
    if not username:
        return HttpResponse('请先登录')
    user = User.objects.get(username=username)
    # 判断一个当前User的会员
    groups = Group.objects.filter(user=user)
    if any(groups):
        groupname = groups.first().name
        if groupname == 'DataEntryClerk':
            return redirect('info_of_myaccount')
        if groupname == 'member':
            return redirect('info_of_myaccount')
        if groupname == 'nonmember':
            group = Group.objects.get(name="member")
            user.groups.clear()
            user.groups.add(group)
    else:
        group = Group.objects.get(name="member")
        user.groups.clear()
        user.groups.add(group)
    return redirect('info_of_myaccount')