"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/21 下午5:12
# Function:

"""
from rest_framework import serializers
from weiboCrawler.models import WeiboUser


class WeiboserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeiboUser
        fields = ['weibo_user_id', 'screen_name', 'gender', 'location', 'statuses_count', 'followers_count',
                  'follow_count', 'description', 'avatar_hd', 'weibo_rank', 'member_rank', 'verified',
                  'verified_reason', 'since_date', 'last_date']
