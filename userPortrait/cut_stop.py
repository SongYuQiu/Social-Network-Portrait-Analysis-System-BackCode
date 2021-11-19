"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/29 下午2:00
# Function:

"""
import os

import jieba
from tqdm import tqdm


class Cut_Stop():

    # 加载停用词
    def load_stopwords(self, stopwords_path):
        with open(stopwords_path, 'r', encoding='utf-8') as s:
            return [line.strip('\n') for line in s]

    # 分词、去停用词等，最终存储数据
    def pre_process_corpus(self, weibo):
        '''

        :param sourcePath: 经过初步清洗后的微博文本路径
        :param targetPath: 分词、去停用词后的文本存放路径
        :param stopwords_path: 停用词路径
        :return:

        '''
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'stopwords.txt')  # full path to text.
        stop_words = self.load_stopwords(file_path)
        user_weibo_list = list(jieba.cut(weibo))
        new_list = []
        for item in user_weibo_list:
            if item not in stop_words and item != ' ':
                new_list.append(item)
        return new_list
