"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/14 下午8:06
# Function:

"""

from django.urls import path

from systemAdmin.views import login, insert_system_user, delete_system_user, modify_password, modify_system_user_info, \
    forget_passand_change, get_system_user_list

urlpatterns = [
    path('', login),
    path('api/insert_system_user', insert_system_user),
    path('api/delete_system_user/<pk>', delete_system_user),
    path('api/modify_password', modify_password),
    path('api/modify_system_user_info', modify_system_user_info),
    path('api/forget_passand_change', forget_passand_change),
    path('api/get_system_user_list', get_system_user_list),
]
