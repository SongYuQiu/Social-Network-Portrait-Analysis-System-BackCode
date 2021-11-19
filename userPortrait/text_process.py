"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/29 下午12:59
# Function:

"""

import re
from html.parser import HTMLParser

import jieba
from tqdm import tqdm


class Clean_Cut_Stop():
    # 去除html标签
    def dealHtmlTags(self, html):
        '''
        去掉html标签
        '''
        # from HTMLParser import HTMLParser
        html = html.strip()
        html = html.strip("\n")
        result = []
        parse = HTMLParser()
        parse.handle_data = result.append
        parse.feed(html)
        parse.close()
        return "".join(result)

    # 去除多余的空格 保留英文之间的空格
    def clean_space(self, text):
        match_regex = re.compile(u'[\u4e00-\u9fa5。\.,，:：《》、\(\)（）]{1} +(?<![a-zA-Z])|\d+ +| +\d+|[a-z A-Z]+')
        should_replace_list = match_regex.findall(text)
        order_replace_list = sorted(should_replace_list, key=lambda i: len(i), reverse=True)
        for i in order_replace_list:
            if i == u' ':
                continue
            new_i = i.strip()
            text = text.replace(i, new_i)
        return text

    def clean_zh_text(self, weibo):
        if "抱歉，作者已设置仅展示半年内微博，此微博已不可见。 " in weibo:
            weibo = weibo.replace("转发微博抱歉，作者已设置仅展示半年内微博，此微博已不可见。 ", '')
        if "抱歉，由于作者设置，你暂时没有这条微博的查看权限哦。查看帮助： 网页链接 " in weibo:
            weibo = weibo.replace("转发微博抱歉，由于作者设置，你暂时没有这条微博的查看权限哦。查看帮助： 网页链接 ", '')
        if "NoneNone" in weibo:
            weibo = weibo.replace("NoneNone", '')
        if "网页链接 NoneNone" in weibo:
            weibo = weibo.replace("网页链接 NoneNone", '')
        if "该账号行为异常，存在安全风险，用户验证之前暂时不能查看。查看帮助  网页链接" in weibo:
            weibo = weibo.replace("该账号行为异常，存在安全风险，用户验证之前暂时不能查看。查看帮助  网页链接", '')
        if "该账号因被投诉违反《微博社区公约》的相关规定，现已无法查看。查看帮助  网页链接" in weibo:
            weibo = weibo.replace("转发微博该账号因被投诉违反《微博社区公约》的相关规定，现已无法查看。查看帮助  网页链接", '')
        if "转发微博" in weibo:
            weibo = weibo.replace("转发微博", '')
        if "来自 网页链接" in weibo:
            weibo = weibo.replace("来自 网页链接", '')
        if "网页链接" in weibo:
            weibo = weibo.replace("网页链接", '')
        if "分享图片" in weibo:
            weibo = weibo.replace("分享图片", '')
        # 去除掉 （分享自 ） 这种格式的内容
        text = re.sub("（分享自.*?）", '', weibo)

        # 去除正文中的@和回复/转发中的用户名  本质上是可以用的
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", "", text)

        # 去除网址
        text = self.dealHtmlTags(text)
        re.sub('''http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+''', '',text)
        URL_REGEX = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\(['
            r'^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", text)

        # 去除表情符号
        myre = re.compile(u'['
                          u'\U0001F300-\U0001F64F'
                          u'\U0001F680-\U0001F6FF'
                          u'\u2600-\u2B55'
                          u'\u23cf'
                          u'\u23e9'
                          u'\u231a'
                          u'\u3030'
                          u'\ufe0f'
                          u"\U0001F600-\U0001F64F"  # emoticons
                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                          u'\U00010000-\U0010ffff'
                          u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                          u'\U00002702-\U000027B0]+',
                          re.UNICODE)
        text = myre.sub('', text)

        # 只保留中文 英文 数字
        string_code = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ", text)
        text = self.clean_space(string_code)
        # 保留英文之间的空格
        text = ' '.join(text.split())

        # 再次去除系统无用语句（之前的步骤似乎没有完全清掉）
        if "抱歉作者已设置仅展示半年内微博此微博已不可见" in text:
            text = text.replace("抱歉作者已设置仅展示半年内微博此微博已不可见", '')
        if "该账号因被投诉违反微博社区公约的相关规定现已无法查看查看帮助" in text:
            text = text.replace("该账号因被投诉违反微博社区公约的相关规定现已无法查看查看帮助", '')
        if "抱歉由于作者设置你暂时没有这条微博的查看权限哦查看帮助" in text:
            text = text.replace("抱歉由于作者设置你暂时没有这条微博的查看权限哦查看帮助", '')
        if "该账号行为异常存在安全风险用户验证之前暂时不能查看查看帮助" in text:
            text = text.replace("该账号行为异常存在安全风险用户验证之前暂时不能查看查看帮助", '')
        return text
