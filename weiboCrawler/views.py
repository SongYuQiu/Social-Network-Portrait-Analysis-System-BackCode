# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view

from userPortrait.models import UserPortrait
from weiboCrawler.serializers import WeiboserSerializer
from weiboCrawler.models import WeiboUser, WeiboText
from weiboCrawler.weibo import Weibo


@csrf_exempt
@api_view(['POST'])
def weibo_crawler(request):
    weibo_user_id, since_date = request.POST['weibo_user_id'], request.POST['since_date']
    user_id_list = []
    user_id_list.append(weibo_user_id)
    try:
        config = {
            "user_id_list": user_id_list,
            "filter": 1,
            "since_date": since_date,
            "start_page": 1,
            "write_mode": ["mysql"],
            "original_pic_download": 0,
            "retweet_pic_download": 0,
            "original_video_download": 0,
            "retweet_video_download": 0,
            "result_dir_name": 0,
            "cookie": "your cookie",
            "mysql_config": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "20140008syq2017",
                "charset": "utf8mb4"
            }
        }
        wb = Weibo(config)
        wb.start()
        print("11111")
        return JsonResponse({"status": 200})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


# 获取系统所有微博用户的信息，用于那个表格展示
@csrf_exempt
@api_view(['GET'])
def get_weibo_user_info(request):
    weibouserlist = WeiboUser.objects.values('weibo_user_id', 'screen_name', 'statuses_count', 'description',
                                             'verified_reason', 'since_date', 'last_date', 'portrait_status')
    for item in weibouserlist:
        weibo_user_id = item['weibo_user_id']
        weiboList = WeiboText.objects.filter(weibo_user_id=weibo_user_id)
        item['crawler_num'] = len(weiboList)
    return Response(weibouserlist)


# 获取系统所有微博用户统计信息
@csrf_exempt
@api_view(['GET'])
def get_all_user_data(request):
    weibouserlist = WeiboUser.objects.all()
    weibolist = WeiboText.objects.all()
    portrait = UserPortrait.objects.all()
    # 到时候再补一个画像的总数
    weibo_user_num = len(weibouserlist)
    weibo_num = len(weibolist)
    portrait_num = len(portrait)
    data = {'all_user_count': weibo_user_num, 'all_weibo_count': weibo_num, 'all_portrait_count':portrait_num}
    return Response(data)


# 删除某一个微博用户账号
@csrf_exempt
@api_view(['DELETE'])
def delete_weibo_user(request, pk):
    try:
        weibouser = WeiboUser.objects.filter(weibo_user_id=pk).first()
        weibotext = WeiboText.objects.filter(weibo_user_id=pk)
        weibotext.delete()
        if weibouser.portrait_status is True:
            userportrait = UserPortrait.objects.filter(weibo_user_id=pk)
            userportrait.delete()
        weibouser.delete()
        return JsonResponse({"status": 200})
    except:
        return JsonResponse({"status": 400})
