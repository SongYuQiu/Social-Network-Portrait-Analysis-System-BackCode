"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/29 上午11:13
# Function:

"""

from django.urls import path

from userPortrait.views import create_user_portrait, get_user_portrait, delete_user_portrait, get_user_weibo, \
    get_user_interest, get_user_probability, get_user_all_location, modify_interest

urlpatterns = [
    path('api/create_user_portrait', create_user_portrait),
    path('api/get_user_portrait/<pk>', get_user_portrait),
    path('api/delete_user_portrait/<pk>', delete_user_portrait),
    path('api/get_user_weibo/<pk>', get_user_weibo),
    path('api/get_user_interest/<pk>', get_user_interest),
    path('api/get_user_probability/<pk>', get_user_probability),
    path('api/get_user_all_location/<pk>', get_user_all_location),
    path('api/modify_interest', modify_interest)
]
