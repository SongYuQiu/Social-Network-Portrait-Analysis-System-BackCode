import datetime
from django.shortcuts import render
import jwt
# Create your views here.
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils import timezone
from systemAdmin.models import User
from systemAdmin.common import genhashpassword, verificationcodegenerator
from django.forms import model_to_dict
from rest_framework.response import Response
from rest_framework import status
from systemAdmin.serializers import UserSerializer


# 登录
@csrf_exempt
@api_view(['POST'])
def login(request):
    user_id, password = request.POST['user_id'], request.POST['password']
    JWTKEY = 'secret'
    try:
        user = User.objects.filter(user_id=user_id).first()
        passwordsalt = genhashpassword(password, user.salt)
        if user.last_login is None:
            isfirstlogin = True
        else:
            isfirstlogin = False
        if user is not None and passwordsalt == user.password:
            user.last_login = timezone.now()
            user.save(force_update=True)
            userdict = model_to_dict(user)
            payload = {
                'user_id': userdict['user_id'],
                'user_name': userdict['user_name'],
                'is_admin': userdict['is_admin'],
                'exp': datetime.datetime.now() + datetime.timedelta(days=1)
            }
            token = jwt.encode(payload=payload, key=JWTKEY, algorithm='HS256')
            return Response({
                "token": token,
                "isfirstlogin": isfirstlogin,
                'user': UserSerializer(user).data,
                "JWT": JWTKEY,
            }, status=200)
        else:
            return Response({'status': '404'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'status': '404'}, status=status.HTTP_400_BAD_REQUEST)


# 管理员创建一个新的用户
@csrf_exempt
@api_view(['POST'])
def insert_system_user(request):
    user_id, user_name, is_admin = request.POST['user_id'], request.POST['user_name'], request.POST['is_admin']
    if is_admin == 'true':
        is_admin = True
    else:
        is_admin = False
    salt = verificationcodegenerator()
    passwordsalt = genhashpassword(user_id, salt)
    systemU = User(user_id=user_id, user_name=user_name, password=passwordsalt, is_admin=is_admin, salt=salt)
    try:
        systemU.save(force_insert=True)
        return JsonResponse({"status": 200})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


# 管理员得删除某一个系统用户账号
@csrf_exempt
@api_view(['DELETE'])
def delete_system_user(request, pk):
    try:
        user = User.objects.filter(user_id=pk)
        user.delete()
        return JsonResponse({"status": 200})
    except:
        return JsonResponse({"status": 400})


# 修改密码
@csrf_exempt
@api_view(['POST'])
def modify_password(request):
    user_id, oldpassword, newpassword = request.POST['user_id'], request.POST['oldpassword'], \
                                        request.POST['newpassword']
    user = User.objects.filter(user_id=user_id).first()
    passwordsalt = genhashpassword(oldpassword, user.salt)
    if user.password == passwordsalt:
        try:
            salt = verificationcodegenerator()
            passwordsalt = genhashpassword(newpassword, salt)
            user.password = passwordsalt
            user.salt = salt
            user.save(force_update=True)
            return JsonResponse({'status': '200'}, safe=False)
        except Exception as e:
            return Response({'status': '400'}, status=200)
    else:
        return Response({'status': '400'}, status=200)


# 管理员修改用户信息和权限
@csrf_exempt
@api_view(['POST'])
def modify_system_user_info(request):
    user_id, user_name, is_admin = request.POST['user_id'], request.POST['user_name'], request.POST['is_admin']
    user = User.objects.filter(user_id=user_id).first()
    if is_admin == 'true':
        is_admin = True
    else:
        is_admin = False
    user.user_name = user_name
    user.is_admin = is_admin
    try:
        user.save(force_update=True)
        return JsonResponse({'status': '200'}, safe=False)
    except Exception as e:
        return Response({'status': '400'}, status=200)


# 忘记密码重新设置密码
@csrf_exempt
@api_view(['POST'])
def forget_passand_change(request):
    user_id, user_name, is_admin, password = request.POST['user_id'], request.POST['user_name'], request.POST[
        'is_admin'], request.POST['password']
    user = User.objects.filter(user_id=user_id).first()
    try:
        salt = verificationcodegenerator()
        passwordsalt = genhashpassword(password, salt)
        user.password = passwordsalt
        user.salt = salt
        user.save(force_update=True)
        return Response({"data": "修改成功，请重新登录！"}, status=200)
    except Exception as e:
        return Response({"data": "系统异常，请稍后再试！"}, status=400)


# 获取系统所有用户的信息
@csrf_exempt
@api_view(['GET'])
def get_system_user_list(request):
    systemuserlist = User.objects.all()
    serializer = UserSerializer(systemuserlist, many=True)
    return Response(serializer.data)
