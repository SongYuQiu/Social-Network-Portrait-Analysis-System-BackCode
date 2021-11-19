'''

# Project:
# Author: justforstar
# CreateTime: 2021/4/13 下午5:07
# Function:

'''
import codecs
import copy
import json
import logging
import math
import os
import sys
from collections import OrderedDict
from time import sleep
from datetime import date, datetime, timedelta
import random
from lxml import etree
import pandas as pd

import requests
from tqdm import tqdm

logger = logging.getLogger('weibo')


class Weibo(object):
    def __init__(self, config):
        """Weibo类初始化"""
        self.validate_config(config)
        self.filter = config[
            'filter']  # 取值范围为0、1,程序默认值为0,代表要爬取用户的全部微博,1代表只爬取用户的原创微博
        since_date = config['since_date']
        if isinstance(since_date, int):
            since_date = date.today() - timedelta(since_date)
        since_date = str(since_date)
        self.since_date = since_date  # 起始时间，即爬取发布日期从该值到现在的微博，形式为yyyy-mm-dd
        self.start_page = config.get('start_page',
                                     1)  # 开始爬的页，如果中途被限制而结束可以用此定义开始页码
        self.write_mode = config[
            'write_mode']  # 结果信息保存类型，为list形式，可包含csv、mongo和mysql三种类型
        self.original_pic_download = config[
            'original_pic_download']  # 取值范围为0、1, 0代表不下载原创微博图片,1代表下载
        self.retweet_pic_download = config[
            'retweet_pic_download']  # 取值范围为0、1, 0代表不下载转发微博图片,1代表下载
        self.original_video_download = config[
            'original_video_download']  # 取值范围为0、1, 0代表不下载原创微博视频,1代表下载
        self.retweet_video_download = config[
            'retweet_video_download']  # 取值范围为0、1, 0代表不下载转发微博视频,1代表下载
        self.result_dir_name = config.get(
            'result_dir_name', 0)  # 结果目录名，取值为0或1，决定结果文件存储在用户昵称文件夹里还是用户id文件夹里
        cookie = config.get('cookie')  # 微博cookie，可填可不填
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        self.headers = {'User_Agent': user_agent, 'Cookie': cookie}
        self.mysql_config = config.get('mysql_config')  # MySQL数据库连接配置，可以不填
        user_id_list = config['user_id_list']
        query_list = config.get('query_list') or []
        if isinstance(query_list, str):
            query_list = query_list.split(',')
        self.query_list = query_list
        if not isinstance(user_id_list, list):
            if not os.path.isabs(user_id_list):
                user_id_list = os.path.split(
                    os.path.realpath(__file__))[0] + os.sep + user_id_list
            self.user_config_file_path = user_id_list  # 用户配置文件路径
            user_config_list = self.get_user_config_list(user_id_list)
        else:
            self.user_config_file_path = ''
            user_config_list = [{
                'weibo_user_id': user_id,
                'since_date': self.since_date,
                'query_list': query_list
            } for user_id in user_id_list]
        self.user_config_list = user_config_list  # 要爬取的微博用户的user_config列表
        self.user_config = {}  # 用户配置,包含用户id和since_date
        self.start_date = ''  # 获取用户第一条微博时的日期
        self.query = ''
        self.user = {}  # 存储目标微博用户信息
        self.got_count = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id

    def get_user_config_list(self, file_path):
        """获取文件中的微博id信息"""
        with open(file_path, 'rb') as f:
            try:
                lines = f.read().splitlines()
                lines = [line.decode('utf-8-sig') for line in lines]
            except UnicodeDecodeError:
                logger.error(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序', file_path)
                sys.exit()
            user_config_list = []
            for line in lines:
                info = line.split(' ')
                if len(info) > 0 and info[0].isdigit():
                    user_config = {}
                    user_config['weibo_user_id'] = info[0]
                    if len(info) > 2:
                        if self.is_date(info[2]):
                            user_config['since_date'] = info[2]
                        elif info[2].isdigit():
                            since_date = date.today() - timedelta(int(info[2]))
                            user_config['since_date'] = str(since_date)
                    else:
                        user_config['since_date'] = self.since_date
                    if len(info) > 3:
                        user_config['query_list'] = info[3].split(',')
                    else:
                        user_config['query_list'] = self.query_list
                    if user_config not in user_config_list:
                        user_config_list.append(user_config)
        return user_config_list

    def validate_config(self, config):
        """验证配置是否正确"""

        # 验证filter、original_pic_download、retweet_pic_download、original_video_download、retweet_video_download
        argument_list = [
            'filter', 'original_pic_download', 'retweet_pic_download',
            'original_video_download', 'retweet_video_download'
        ]
        for argument in argument_list:
            if config[argument] != 0 and config[argument] != 1:
                logger.warning(u'%s值应为0或1,请重新输入', config[argument])
                sys.exit()

        # 验证since_date
        since_date = config['since_date']
        if (not self.is_date(str(since_date))) and (not isinstance(
                since_date, int)):
            logger.warning(u'since_date值应为yyyy-mm-dd形式或整数,请重新输入')
            sys.exit()

        # 验证query_list
        query_list = config.get('query_list') or []
        if (not isinstance(query_list, list)) and (not isinstance(
                query_list, str)):
            logger.warning(u'query_list值应为list类型或字符串,请重新输入')
            sys.exit()

        # 验证write_mode
        write_mode = ['csv', 'json', 'mongo', 'mysql']
        if not isinstance(config['write_mode'], list):
            sys.exit(u'write_mode值应为list类型')
        for mode in config['write_mode']:
            if mode not in write_mode:
                logger.warning(
                    u'%s为无效模式，请从csv、json、mongo和mysql中挑选一个或多个作为write_mode',
                    mode)
                sys.exit()

        # 验证user_id_list
        user_id_list = config['user_id_list']
        if (not isinstance(user_id_list,
                           list)) and (not user_id_list.endswith('.txt')):
            logger.warning(u'user_id_list值应为list类型或txt文件路径')
            sys.exit()
        if not isinstance(user_id_list, list):
            if not os.path.isabs(user_id_list):
                user_id_list = os.path.split(
                    os.path.realpath(__file__))[0] + os.sep + user_id_list
            if not os.path.isfile(user_id_list):
                logger.warning(u'不存在%s文件', user_id_list)
                sys.exit()

    def is_date(self, since_date):
        """判断日期格式是否正确"""
        try:
            datetime.strptime(since_date, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def update_user_config_file(self, user_config_file_path):
        """更新用户配置文件"""
        with open(user_config_file_path, 'rb') as f:
            try:
                lines = f.read().splitlines()
                lines = [line.decode('utf-8-sig') for line in lines]
            except UnicodeDecodeError:
                logger.error(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序',
                             user_config_file_path)
                sys.exit()
            for i, line in enumerate(lines):
                info = line.split(' ')
                if len(info) > 0 and info[0].isdigit():
                    if self.user_config['weibo_user_id'] == info[0]:
                        if len(info) == 1:
                            info.append(self.user['screen_name'])
                            info.append(self.start_date)
                        if len(info) == 2:
                            info.append(self.start_date)
                        if len(info) > 2:
                            info[2] = self.start_date
                        lines[i] = ' '.join(info)
                        break
        with codecs.open(user_config_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def get_json(self, params):
        """获取网页中json数据"""
        url = 'https://m.weibo.cn/api/container/getIndex?'
        r = requests.get(url,
                         params=params,
                         headers=self.headers,
                         verify=False)
        return r.json()

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u'\u200b', '').encode(
                    sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
        return weibo

    def get_page_count(self):
        """获取微博页数"""
        try:
            weibo_count = self.user['statuses_count']
            page_count = int(math.ceil(weibo_count / 10.0))
            return page_count
        except KeyError:
            logger.exception(
                u'程序出错，错误原因可能为以下两者：\n'
                u'1.user_id不正确；\n'
                u'2.此用户微博可能需要设置cookie才能爬取。\n'
                u'解决方案：\n'
                u'请参考\n'
                u'https://github.com/dataabc/weibo-crawler#如何获取user_id\n'
                u'获取正确的user_id；\n'
                u'或者参考\n'
                u'https://github.com/dataabc/weibo-crawler#3程序设置\n'
                u'中的“设置cookie”部分设置cookie信息')

    def get_weibo_json(self, page):
        """获取网页中微博json数据"""
        params = {
            'container_ext': 'profile_uid:' + str(self.user_config['weibo_user_id']),
            'containerid': '100103type=401&q=' + self.query,
            'page_type': 'searchall'
        } if self.query else {
            'containerid': '107603' + str(self.user_config['weibo_user_id'])
        }
        params['page'] = page
        js = self.get_json(params)
        return js

    def weibo_to_mysql(self, wrote_count):
        """将爬取的微博信息写入MySQL数据库"""
        mysql_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4'
        }

        weibo_list = []
        retweet_list = []
        if len(self.write_mode) > 1:
            info_list = copy.deepcopy(self.weibo[wrote_count:])
        else:
            info_list = self.weibo[wrote_count:]
        for w in info_list:
            # if 'retweet' in w:
            #     w['retweet']['retweet_id'] = ''
            #     retweet_list.append(w['retweet'])
            #     w['retweet_id'] = w['retweet']['weibo_text_id']
            #     del w['retweet']
            # else:
            #     w['retweet_id'] = ''
            weibo_list.append(w)
        # 在'weibo'表中插入或更新微博数据
        # self.mysql_insert(mysql_config, 'WeiboText', retweet_list)
        # print(weibo_list)
        self.mysql_insert(mysql_config, 'WeiboText', weibo_list)
        # print("0000000000000")
        logger.info(u'%d条微博写入MySQL数据库完毕', self.got_count)

    def write_data(self, wrote_count):
        """将爬到的信息写入文件或数据库"""
        if self.got_count > wrote_count:
            if 'mysql' in self.write_mode:
                self.weibo_to_mysql(wrote_count)

    def mysql_insert(self, mysql_config, table, data_list):
        """向MySQL表插入或更新数据"""
        import pymysql

        if len(data_list) > 0:
            keys = ', '.join(data_list[0].keys())
            values = ', '.join(['%s'] * len(data_list[0]))
            if self.mysql_config:
                mysql_config = self.mysql_config
            mysql_config['db'] = 'user_portrait'
            connection = pymysql.connect(**mysql_config)
            cursor = connection.cursor()
            sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
                     DUPLICATE KEY UPDATE""".format(table=table,
                                                    keys=keys,
                                                    values=values)
            update = ','.join([
                ' {key} = values({key})'.format(key=key)
                for key in data_list[0]
            ])
            sql += update
            try:
                # print("22222222")
                # print(data_list)
                cursor.executemany(
                    sql, [tuple(data.values()) for data in data_list])
                connection.commit()
                # print("3333333")
            except Exception as e:
                connection.rollback()
                logger.exception(e)
                # print("444444444")
            finally:
                connection.close()

    def user_to_mysql(self):
        """将爬取的用户信息写入MySQL数据库"""
        mysql_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4'
        }
        self.user['since_date'] = pd.to_datetime((self.user_config['since_date']))
        self.user['last_date'] = pd.to_datetime(date.today())
        self.user['portrait_status'] = False
        self.mysql_insert(mysql_config, 'WeiboUser', [self.user])
        logger.info(u'%s信息写入MySQL数据库完毕', self.user['screen_name'])

    def user_to_database(self):
        """将用户信息写入文件/数据库"""
        if 'mysql' in self.write_mode:
            self.user_to_mysql()

    def get_user_info(self):
        """获取用户信息"""
        params = {'containerid': '100505' + str(self.user_config['weibo_user_id'])}
        print(self.user_config)
        js = self.get_json(params)
        if js['ok']:
            info = js['data']['userInfo']
            user_info = OrderedDict()
            user_info['weibo_user_id'] = self.user_config['weibo_user_id']
            user_info['screen_name'] = info.get('screen_name', '')
            user_info['gender'] = info.get('gender', '')
            params = {
                'containerid':
                    '230283' + str(self.user_config['weibo_user_id']) + '_-_INFO'
            }
            zh_list = [
                u'所在地'
            ]
            en_list = [
                'location'
            ]
            for i in en_list:
                user_info[i] = ''
            js = self.get_json(params)
            if js['ok']:
                cards = js['data']['cards']
                if isinstance(cards, list) and len(cards) > 1:
                    card_list = cards[0]['card_group'] + cards[1]['card_group']
                    for card in card_list:
                        if card.get('item_name') in zh_list:
                            user_info[en_list[zh_list.index(
                                card.get('item_name'))]] = card.get(
                                'item_content', '')
            user_info['statuses_count'] = info.get('statuses_count', 0)
            user_info['followers_count'] = info.get('followers_count', 0)
            user_info['follow_count'] = info.get('follow_count', 0)
            user_info['description'] = info.get('description', '')
            user_info['avatar_hd'] = info.get('avatar_hd', '')
            user_info['weibo_rank'] = info.get('urank', 0)
            user_info['member_rank'] = info.get('mbrank', 0)
            user_info['verified'] = info.get('verified', False)
            user_info['verified_reason'] = info.get('verified_reason', '')
            user_info['profile_url'] = info.get('profile_url', '')
            user = self.standardize_info(user_info)
            self.user = user
            self.user_to_database()
            return user

    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u'刚刚' in created_at:
            created_at = datetime.now().strftime('%Y-%m-%d')
        elif u'分钟' in created_at:
            minute = created_at[:created_at.find(u'分钟')]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime('%Y-%m-%d')
        elif u'小时' in created_at:
            hour = created_at[:created_at.find(u'小时')]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime('%Y-%m-%d')
        elif u'昨天' in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime('%Y-%m-%d')
        else:
            created_at = created_at.replace('+0800 ', '')
            temp = datetime.strptime(created_at, '%c')
            created_at = datetime.strftime(temp, '%Y-%m-%d')
        return created_at

    def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(5):
            url = 'https://m.weibo.cn/detail/%s' % id
            html = requests.get(url, headers=self.headers, verify=False).text
            html = html[html.find('"status":'):]
            html = html[:html.rfind('"hotScheme"')]
            html = html[:html.rfind(',')]
            html = '{' + html + '}'
            js = json.loads(html, strict=False)
            weibo_info = js.get('status')
            if weibo_info:
                weibo = self.parse_weibo(weibo_info)
                return weibo
            sleep(random.randint(6, 10))

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = True if weibo_info.get(
                'pic_num') > 9 else weibo_info.get('isLongText')
            # if retweeted_status and retweeted_status.get('id'):  # 转发
            #     retweet_id = retweeted_status.get('id')
            #     is_long_retweet = retweeted_status.get('isLongText')
            #     if is_long:
            #         weibo = self.get_long_weibo(weibo_id)
            #         if not weibo:
            #             weibo = self.parse_weibo(weibo_info)
            #     else:
            #         weibo = self.parse_weibo(weibo_info)
            #     if is_long_retweet:
            #         retweet = self.get_long_weibo(retweet_id)
            #         if not retweet:
            #             retweet = self.parse_weibo(retweeted_status)
            #     else:
            #         retweet = self.parse_weibo(retweeted_status)
            #     retweet['created_at'] = self.standardize_date(
            #         retweeted_status['created_at'])
            #     # weibo['retweet_id'] = retweet
            # else:  # 原创
            if is_long:
                weibo = self.get_long_weibo(weibo_id)
                if not weibo:
                    weibo = self.parse_weibo(weibo_info)
            else:
                weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(
                weibo_info['created_at'])
            return weibo
        except Exception as e:
            logger.exception(e)

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['weibo_user_id'] = weibo_info['user']['id']
            # weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['weibo_user_id'] = ''
            # weibo['screen_name'] = ''
        weibo['weibo_text_id'] = weibo_info['id']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = etree.HTML(text_body).xpath('string(.)')
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['tool'] = weibo_info['source']
        weibo['like_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comment_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['repost_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topic'] = self.get_topics(selector)
        return self.standardize_info(weibo)

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ','.join(topic_list)
        return topics

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_one_page(self, page):
        """获取一页的全部微博"""
        try:
            js = self.get_weibo_json(page)
            if js['ok']:
                weibos = js['data']['cards']
                if self.query:
                    weibos = weibos[0]['card_group']
                for w in weibos:
                    if w['card_type'] == 9:
                        wb = self.get_one_weibo(w)
                        if wb:
                            if wb['weibo_text_id'] in self.weibo_id_list:
                                continue
                            created_at = datetime.strptime(
                                wb['created_at'], '%Y-%m-%d')
                            since_date = datetime.strptime(
                                self.user_config['since_date'], '%Y-%m-%d')
                            if created_at < since_date:
                                if self.is_pinned_weibo(w):
                                    continue
                                else:
                                    logger.info(
                                        u'{}已获取{}({})的第{}页{}微博{}'.format(
                                            '-' * 30, self.user['screen_name'],
                                            self.user['weibo_user_id'], page,
                                            '包含"' + self.query +
                                            '"的' if self.query else '',
                                            '-' * 30))
                                    return True
                            if (not self.filter) or (
                                    'retweet' not in wb.keys()):
                                self.weibo.append(wb)
                                self.weibo_id_list.append(wb['weibo_text_id'])
                                self.got_count += 1
                            else:
                                logger.info(u'正在过滤转发微博')
            else:
                return True
            logger.info(u'{}已获取{}({})的第{}页微博{}'.format(
                '-' * 30, self.user['screen_name'], self.user['weibo_user_id'], page,
                '-' * 30))
        except Exception as e:
            logger.exception(e)

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        weibo_info = info['mblog']
        title = weibo_info.get('title')
        if title and title.get('text') == u'置顶':
            return True
        else:
            return False

    def get_pages(self):
        """获取全部微博"""
        try:
            self.get_user_info()
            # self.print_user_info()
            since_date = datetime.strptime(self.user_config['since_date'],
                                           '%Y-%m-%d')
            today = datetime.strptime(str(date.today()), '%Y-%m-%d')
            if since_date <= today:
                page_count = self.get_page_count()
                wrote_count = 0
                page1 = 0
                random_pages = random.randint(1, 5)
                self.start_date = datetime.now().strftime('%Y-%m-%d')
                pages = range(self.start_page, page_count + 1)
                for page in tqdm(pages, desc='Progress'):
                    is_end = self.get_one_page(page)
                    if is_end:
                        break

                    if page % 20 == 0:  # 每爬20页写入一次文件
                        self.write_data(wrote_count)
                        wrote_count = self.got_count

                    # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
                    # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
                    # 认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
                    if (page -
                        page1) % random_pages == 0 and page < page_count:
                        sleep(random.randint(6, 10))
                        page1 = page
                        random_pages = random.randint(1, 5)

                self.write_data(wrote_count)  # 将剩余不足20页的微博写入文件
            logger.info(u'微博爬取完成，共爬取%d条微博', self.got_count)
        except Exception as e:
            logger.exception(e)

    def initialize_info(self, user_config):
        """初始化爬虫信息"""
        self.weibo = []
        self.user = {}
        self.user_config = user_config
        self.got_count = 0
        self.weibo_id_list = []

    def start(self):
        """运行爬虫"""
        try:
            for user_config in self.user_config_list:
                if len(user_config['query_list']):
                    for query in user_config['query_list']:
                        self.query = query
                        self.initialize_info(user_config)
                        self.get_pages()
                else:
                    self.initialize_info(user_config)
                    self.get_pages()
                logger.info(u'信息抓取完毕')
                logger.info('*' * 100)
                if self.user_config_file_path and self.user:
                    self.update_user_config_file(self.user_config_file_path)
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    pass
