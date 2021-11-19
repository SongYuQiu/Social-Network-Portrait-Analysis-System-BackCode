'''

# Project:
# Author: justforstar
# CreateTime: 2021/4/13 下午10:55
# Function:

'''

from django.urls import path
from weiboCrawler.views import weibo_crawler, get_weibo_user_info, get_all_user_data, delete_weibo_user


urlpatterns = [
    path('api/weibo_crawler', weibo_crawler),
    path('api/get_weibo_user_info', get_weibo_user_info),
    path('api/get_all_user_data', get_all_user_data),
    path('api/delete_weibo_user/<pk>', delete_weibo_user),
]
