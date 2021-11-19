import os

os.environ["CUDA_VISIBLE_DEVICES"] = '1'
from datetime import date, datetime, timedelta
import pandas as pd
from django.forms import model_to_dict
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from userPortrait.models import UserPortrait
from weiboCrawler.models import WeiboText, WeiboUser
from userPortrait.text_process import Clean_Cut_Stop
from userPortrait.cut_stop import Cut_Stop
import gensim
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import numpy as np
from userPortrait.LDA_interest import LDAClustering

print("Load word2vec.model")
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'word2vec.model')  # full path to text.
word_model = gensim.models.Word2Vec.load(file_path)

print("Load age_textcnn.h5")
module_dir2 = os.path.dirname(__file__)
file_path2 = os.path.join(module_dir2, 'age_class_weights_textcnn.h5')  # full path to text.
age_model = load_model(file_path2)

print("Load gender_textcnn.h5")
module_dir3 = os.path.dirname(__file__)
file_path3 = os.path.join(module_dir3, 'gender_class_weights_textcnn.h5')  # full path to text.
gender_model = load_model(file_path3)


# Create your views here.
@csrf_exempt
@api_view(['POST'])
def create_user_portrait(request):
    weibo_user_id = request.POST['weibo_user_id']
    weibotext = WeiboText.objects.filter(weibo_user_id=weibo_user_id, text__isnull=False).values('text')

    vocab_list = [word for word, Vocab in word_model.wv.vocab.items()]
    # 初始化[word:token]
    word_index = {" ": 0}

    # 填充字典和矩阵
    for i in range(len(vocab_list)):
        word = vocab_list[i]  # 每个词语
        word_index[word] = i + 1  # 词对应的序号，序号：词

    weibo_matrix = []
    for_LDA = []
    for item in weibotext:
        weibo = str(item['text'])
        weibo = Clean_Cut_Stop().clean_zh_text(weibo)
        weibo_cut_list = Cut_Stop().pre_process_corpus(weibo)
        sentence = ' '.join(item for item in weibo_cut_list)
        for_LDA.append(sentence)
        if len(weibo_cut_list) != 0:
            new_text = []
            for word in weibo_cut_list:
                try:
                    new_text.append(word_index[word])  # 把句子中的词语转化为index
                except:
                    new_text.append(0)
            weibo_matrix.append(new_text)

    print('开始LDA')
    LDA = LDAClustering()
    n_components = 0
    if len(for_LDA) <= 5:
        n_components = 1
    elif len(for_LDA) <= 15:
        n_components = 3
    elif len(for_LDA) <= 20:
        n_components = 5
    elif len(for_LDA) <= 50:
        n_components = 10
    else:
        n_components = 15
    interset = LDA.lda(for_LDA, max_iter=100, n_components=n_components)

    predict_data = pad_sequences(weibo_matrix, 140)

    print("Start predict gender")
    gender_predict_label = np.argmax(gender_model.predict(predict_data), 1)

    p_count = np.sum(gender_predict_label == 1)
    n_count = np.sum(gender_predict_label == 0)
    male_posibility = float(p_count) / float(p_count + n_count)
    female_posibility = float(n_count) / float(p_count + n_count)
    print(male_posibility, female_posibility)
    print("Start predict age")
    age_predict_label = np.argmax(age_model.predict(predict_data), 1)

    s_count = np.sum(age_predict_label == 0)
    e_count = np.sum(age_predict_label == 1)
    i_count = np.sum(age_predict_label == 2)
    s_posibility = float(s_count) / float(s_count + e_count + i_count)
    e_posibility = float(e_count) / float(s_count + e_count + i_count)
    i_posibility = float(i_count) / float(s_count + e_count + i_count)
    print(s_posibility, e_posibility, i_posibility)
    portrait_date = pd.to_datetime(date.today())

    user_portrait = UserPortrait(weibo_user_id=weibo_user_id, male_probability=male_posibility,
                                 female_probability=female_posibility,
                                 seven_probability=s_posibility, eight_probability=e_posibility,
                                 nine_probability=i_posibility, interest=interset, portrait_date=portrait_date)

    try:
        portrait = UserPortrait.objects.filter(weibo_user_id=weibo_user_id)
        if portrait:
            print("更新")
            UserPortrait.objects.filter(weibo_user_id=weibo_user_id).update(male_probability=male_posibility,
                                                                            female_probability=female_posibility,
                                                                            seven_probability=s_posibility,
                                                                            eight_probability=e_posibility,
                                                                            nine_probability=i_posibility,
                                                                            interest=interset,
                                                                            portrait_date=portrait_date)
        else:
            user_portrait.save(force_insert=True)
        WeiboUser.objects.filter(weibo_user_id=weibo_user_id).update(portrait_status=True)
        return JsonResponse({"status": 200})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


@csrf_exempt
@api_view(['GET'])
def get_user_portrait(request, pk):
    weibo_user_id = pk
    try:
        portrait = model_to_dict(UserPortrait.objects.filter(weibo_user_id=weibo_user_id).first())
        weibo_user_info = model_to_dict(WeiboUser.objects.filter(weibo_user_id=weibo_user_id).first())
        merge_data = dict(portrait, **weibo_user_info)
        return Response(merge_data)
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


@csrf_exempt
@api_view(['GET'])
def get_user_interest(request, pk):
    weibo_user_id = pk
    try:
        interest = UserPortrait.objects.values("interest").filter(weibo_user_id=weibo_user_id).first()
        return Response(interest)
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


@csrf_exempt
@api_view(['GET'])
def get_user_probability(request, pk):
    weibo_user_id = pk
    try:
        probability = UserPortrait.objects.values("male_probability", "female_probability", "seven_probability",
                                                  "eight_probability", "nine_probability").filter(
            weibo_user_id=weibo_user_id).first()
        return Response(probability)
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


# 删除一个用户画像
@csrf_exempt
@api_view(['DELETE'])
def delete_user_portrait(request, pk):
    try:
        userportrait = UserPortrait.objects.filter(weibo_user_id=pk)
        userportrait.delete()
        WeiboUser.objects.filter(weibo_user_id=pk).update(portrait_status=False)
        return JsonResponse({"status": 200})
    except:
        return JsonResponse({"status": 400})


# 获取用户微博
@csrf_exempt
@api_view(['GET'])
def get_user_weibo(request, pk):
    weibo_user_id = pk
    try:
        weibotext = WeiboText.objects.values("created_at", "text", "tool", "like_count", "comment_count",
                                             "repost_count", "location").filter(weibo_user_id=weibo_user_id)
        result = []
        for item in weibotext:
            item["created_at"] = str(item["created_at"]).split(" ")[0]
            if item["location"] in item["text"]:
                item["text"] = item["text"].replace(item["location"], "")
            result.append(item)
        return Response(result)
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


# 获取用户微博
@csrf_exempt
@api_view(['GET'])
def get_user_all_location(request, pk):
    weibo_user_id = pk
    try:
        r_location = WeiboUser.objects.values("location").filter(weibo_user_id=weibo_user_id).first()
        weibolocation = WeiboText.objects.values("location").filter(weibo_user_id=weibo_user_id)
        location_list = []
        if r_location["location"] != '':
            temp = r_location.split("·")
            # print(len(temp))
            for i in range(len(temp)):
                # print(temp[i])
                location_list.append(
                    r_location.split("·")[i].translate(str.maketrans({'省': None, '市': None, '区': None, '县': None})))
            # location_list.append(
            #     r_location.split("·")[0].translate(str.maketrans({'省': None, '市': None, '区': None, '县': None})))
        for item in weibolocation:
            if item["location"] != '':
                temp = item["location"].split("·")
                for i in range(len(temp)):
                    # print(temp[i])
                    location_list.append(
                        item["location"].split("·")[i].translate(
                            str.maketrans({'省': None, '市': None, '区': None, '县': None})))
                # location_list.append(
                #     item["location"].split("·")[0].translate(str.maketrans({'省': None, '市': None, '区': None, '县': None})))
        nodup_location = set(location_list)
        result = []
        for item in nodup_location:
            temp = {"name": item, "value": str(location_list).count(item)}
            result.append(temp)
        # print(result)
        return Response(result)
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400})


@csrf_exempt
@api_view(['POST'])
def modify_interest(request):
    weibo_user_id, interest = request.POST['weibo_user_id'], request.POST['interest']
    try:
        UserPortrait.objects.filter(weibo_user_id=weibo_user_id).update(interest=interest)
        return JsonResponse({'status': '200'}, safe=False)
    except Exception as e:
        return Response({'status': '400'}, status=200)
