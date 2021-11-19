'''

# Project:
# Author: justforstar
# CreateTime: 2021/4/14 下午4:06
# Function:

'''

from rest_framework import serializers
from systemAdmin.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'is_admin', 'last_login']
