"""

# Project:
# Author: justforstar
# CreateTime: 2021/5/4 下午1:34
# Function:

"""
import os

import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class LDAClustering():
    def load_stopwords(self, stopwords_path):
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]

    def pre_process_corpus(self, corpus):
        """
        数据预处理，将语料转换成以词频表示的向量。
        :param corpus_path: 语料路径，每条语料一行进行存放
        :param stopwords_path: 停用词路径
        :return:
        """

        self.cntVector = CountVectorizer()
        cntTf = self.cntVector.fit_transform(corpus)

        return cntTf

    def fmt_lda_result(self, lda_result):
        ret = {}
        for doc_index, res in enumerate(lda_result):
            # print("----",doc_index,res,"----")
            li_res = list(res)
            # print("li_res",li_res)
            doc_label = li_res.index(max(li_res))
            # print("doc_label",doc_label)
            if doc_label not in ret:
                ret[doc_label] = [doc_index]
            else:
                ret[doc_label].append(doc_index)
        # for doc_label in ret:
        #   print("Topic #%d:"%doc_label,ret[doc_label])
        return ret

    def print_top_words(self, model, feature_names, n_top_words):
        module_dir4 = os.path.dirname(__file__)
        file_path4 = os.path.join(module_dir4, 'LDA_stopwords.txt')  # full path to text.
        stopwords = self.load_stopwords(file_path4)
        final_interest = []
        for topic_idx, topic in enumerate(model.components_):
            message = "Topic #%d: " % topic_idx
            message += " ".join([feature_names[i]
                                 for i in topic.argsort()[:-n_top_words - 1:-1]])
            for i in topic.argsort()[:-n_top_words - 1:-1]:
                if feature_names[i] not in stopwords:
                    final_interest.append(feature_names[i])
        final_interest = set(final_interest)
        print(final_interest)
        return ' '.join(item for item in final_interest)

    def lda(self, corpus, n_components=10, learning_method='batch', max_iter=100):
        """
        LDA主题模型
        :param corpus_path: 语料路径
        :param n_topics: 主题数目
        :param learning_method: 学习方法: "batch|online"
        :param max_iter: EM算法迭代次数
        :param stopwords_path: 停用词路径
        :return:
        """
        cntTf = self.pre_process_corpus(corpus)
        tf_feature_names = self.cntVector.get_feature_names()
        lda = LatentDirichletAllocation(n_components=n_components, max_iter=max_iter, learning_method=learning_method)
        lda.fit_transform(cntTf)
        interest = self.print_top_words(lda, tf_feature_names, n_top_words=5)
        return interest


if __name__ == "__main__":
    pass
