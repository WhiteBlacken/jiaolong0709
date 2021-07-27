from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.models import User, Group
from teng.models import Business, Subbusiness, Supplier, Keyword, Keyword_en, Keyword_cn


def show_index(request):
    return render(request, 'teng/index.html')


# 身份认证
def userVisitContro(request):
    pass


# 每页都查分类
def getCommomCate():
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

# 判断用户的登录状态
def judgeUserLevel(request):
    username = request.session.get('username', '')
    if not username:
        return 0
    user = User.objects.get(username=username)
    group_name = Group.objects.filter(user=user).first().name
    if group_name == 'member':
        return 2
    else:
        return 1
# 提取获取结果列表的公共部分(结果显示)
def getCommomPageData(request, suppliers):
    context = getCommomCate()
    # 分页
    page = request.GET.get('page', 1)
    # 会员非会员能看到的数据不一样 test：会员：全部  非会员：2条
    userLevel = judgeUserLevel(request)
    if userLevel == 2:
        paginator = Paginator(suppliers, 4)
        page_data = paginator.page(page)
    else:
        paginator = Paginator(suppliers[:2], 4)
        page_data = paginator.page(page)
    context['paginator'] = paginator
    context['page_data'] = page_data
    return context


# 首页
def index(request):
    context = getCommomCate()
    # 取前三个大分类(此处不合理，后续要修改)
    business = Business.objects.all()
    showBusiness = business[0:3]

    showBus0 = showBusiness[0]
    supplier0 = []
    count0 = 0
    for subbus in showBus0.subbusiness_set.all():
        for j in Supplier.objects.filter(categories=subbus):
            supplier0.append(j)
            count0 = count0 + 1
            if count0 == 10:
                break
    context['showBus0'] = showBus0
    context['supplier0'] = supplier0

    showBus1 = showBusiness[1]
    supplier1 = []
    count1 = 0
    for subbus in showBus1.subbusiness_set.all():
        for j in Supplier.objects.filter(categories=subbus):
            supplier1.append(j)
            count1 = count1 + 1
            if count1 == 10:
                break
    context['showBus1'] = showBus1
    context['supplier1'] = supplier1

    showBus2 = showBusiness[2]
    supplier2 = []
    count2 = 0
    for subbus in showBus2.subbusiness_set.all():
        for j in Supplier.objects.filter(categories=subbus):
            supplier2.append(j)
            count2 = count2 + 1
            if count2 == 10:
                break
    context['showBus2'] = showBus2
    context['supplier2'] = supplier2

    return render(request, 'teng/index.html', {'context': context})


# 点击一级分类返回结果
def suppliers_with_business(request, id):
    # 查询出当前business分类下所有的supplier
    nowBusiness = Business.objects.get(id=id)
    suppliers = []
    for subbusiness in nowBusiness.subbusiness_set.all():
        supplier_list = Supplier.objects.filter(categories=subbusiness).order_by('id')
        if supplier_list:
            for list in supplier_list:
                suppliers.append(list)
    context = getCommomPageData(request, suppliers)
    context['nowBusiness'] = nowBusiness
    return render(request, 'teng/cateOneSearchResult.html', {'context': context})

# 点击二级分类返回结果
def suppliers_with_subbusiness(request,id):
    # 查询出当前subbusiness分类下所有的supplier
    nowSubbusiness = Subbusiness.objects.get(id=id)
    nowBusiness = Business.objects.get(id=nowSubbusiness.parent_id)
    suppliers = Supplier.objects.filter(categories=nowSubbusiness)

    context = getCommomPageData(request, suppliers)
    context['nowBusiness'] = nowBusiness
    context['nowSubbusiness'] = nowSubbusiness
    return render(request, 'teng/cateTwoSearchResult.html', {'context': context})

# 搜索关键词返回结果
def search_by_keyword(request):
    context = getCommomCate()
    # 拿到post中提交的分类值和关键词
    businessId = request.POST.get('search_category', 1)
    searchText = request.POST.get('search_text', '')
    page = request.GET.get('page', 1)
    print('option value is ' + businessId + ' searchText is ' + searchText)
    # 通过关键词去查找内容（通过分类值进行限制） 要修改，仅作为test
    # get返回值的数量只能为1，为空或者>=2都会报错
    keyword = Keyword.objects.filter(chinese_keyword=searchText)
    # pro:怎么判断keyword（集合）是否为空
    paginator = []
    page_data = []
    # 这边要再改掉，能和前面进行复合
    if keyword:
        suppliers = Supplier.objects.filter(categories=keyword[0].subbusiness).order_by('id')
        # 分页
        # 会员非会员能看到的数据不一样 test：会员：全部  非会员：2条

        userLevel = judgeUserLevel(request)
        if userLevel == 0:
            return HttpResponse('请先登录')
        if userLevel == 2:
            paginator = Paginator(suppliers, 4)
            page_data = paginator.page(page)
        else:
            paginator = Paginator(suppliers[:2], 4)
            page_data = paginator.page(page)
    # 前三条测试后看是否要删掉
    # context['keyword'] = keyword
    # context['searchText'] = searchText
    # context['businessId'] = businessId
    context['paginator'] = paginator
    context['page_data'] = page_data
    return render(request, 'teng/keywordSearchResult.html',
                  {'context': context})

def quick_view(request,id):
    supply = Supplier.objects.get(id=id)

    return render(request, "teng/example.html", {'supply': supply})


def start(request):
    return HttpResponse("this is start")





def test(request):
    allBuniess = Business.objects.all()
    allSubbuniess = []
    for bus in allBuniess:
        for subbus in bus.subbusiness_set.all():
            allSubbuniess.append(subbus)
    return render(request, "testForm.html", {'allSubbuniess': allSubbuniess})


def testFinished(request):
    chinese_word = request.POST.get('chinese_keyword', '')
    english_word = request.POST.get('english_keyword', '')
    status = request.POST.get('status', 0)
    similarSet = request.POST.get('similar set', 0)
    comment = request.POST.get('comment', '')
    subbuiness = request.POST.get('subbusiness', '')
    keyword = Keyword()
    keyword.chinese_keyword = chinese_word
    keyword.english_keyword = english_word
    keyword.status = status
    keyword.similar_set = similarSet
    keyword.comment = comment
    keyword.subbusiness_id = subbuiness

    cWord = Keyword.objects.filter(chinese_keyword=chinese_word)
    eWord = Keyword.objects.filter(english_keyword=english_word)

    if not any(cWord) and not any(eWord):
        keyword.save()
        return HttpResponse("chinese_word:" + chinese_word + " status:" + status + " subbuiness:" + subbuiness)
    if any(cWord) and any(eWord):
        if cWord.first().english_keyword == eWord.first().english_keyword:
            return HttpResponse("chinese_word:" + chinese_word + " status:" + status + " subbuiness:" + subbuiness)
    if any(cWord):
        keyword_en = Keyword_en()
        keyword_en.english_keyword = english_word
        keyword_en.subbusiness = Subbusiness.objects.get(id=subbuiness)
        keyword_en.keyword = cWord.first()
        # keyword_en.keyword = keywords.first()
        keyword_en.comment = "测试数据"
        keyword_en.save()
        return HttpResponse("chinese_word:" + chinese_word + " status:" + status + " subbuiness:" + subbuiness)
    if any(eWord):
        keyword_cn = Keyword_cn()
        keyword_cn.chinese_keyword = chinese_word
        keyword_cn.subbusiness = Subbusiness.objects.get(id=subbuiness)
        keyword_cn.keyword = eWord.first()
        # keyword_cn.keyword =keywords.first()
        keyword_cn.comment = "测试数据"
        keyword_cn.save()
        return HttpResponse("chinese_word:" + chinese_word + " status:" + status + " subbuiness:" + subbuiness)

    # return HttpResponse("chinese_word:"+chinese_word+" status:"+status+" subbuiness:"+subbuiness)
