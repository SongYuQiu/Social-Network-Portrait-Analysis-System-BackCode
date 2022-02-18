<h1 align="center">
社交媒体人物画像分析系统后端项目代码
</h1>

## 背景简介
构建人物画像是描绘目标用户形象、把握需求与确定设计方向的有效途径，可以使产品实现精准服务。

其次，贴近实际人物形象的人物画像结果非常有助于确定产品前期的设计，设计师能够通过画像获取到用户的切实需求以辅助产品进行正确的定位。

人物画像是当前大数据领域的一种典型应用，是精细化和数据化运营的需求产物，普遍应用在互联网产品中。

## 本科毕设简单介绍
毕设主要研究基于微博博文等文本数据推断微博用户性别、年龄标签属性以及挖掘微博用户兴趣爱好的算法。

搭建社交媒体人物画像分析系统，支持数据爬取、画像分析以及结果管理等功能，以可视化的方式呈现本文选用的算法模型推断出来的微博用户的性别、年龄标签概率值以及兴趣挖掘的关键词。

## 所使用的数据集
所使用的数据集是SMP CUP 在2016年发布的公开微博数据集，该数据集分了四个文件，分别是微博用户基本信息文件、微博用户标签文件、微博用户关系文件和微博文本文件。

考虑到微博用户的个人简介、认证信息等文本内容对于微博用户的性别、年龄标签属性值的推断可能存在一定的价值，利用爬虫技术爬取了该数据集中所有微博用户更详细的基本信息以对数据集进行特征补充。

同时，该数据集的发布时间为2016年，距离毕设研究的时间相对有些久远，绝大多数的微博用户的微博状态以及发布的博文肯定都有所更新，遂使用爬虫技术一并补充爬取数据集中微博用户从2016年至毕设开始时的微博文本数据。

## 系统开发框架
### 后端框架
- [Django](https://www.djangoproject.com/)


### 前端框架
<p align="center">
  <a href="https://github.com/vuejs/vue">
    <img src="https://img.shields.io/badge/vue-2.6.10-brightgreen.svg" alt="vue">
  </a>
  <a href="https://github.com/ElemeFE/element">
    <img src="https://img.shields.io/badge/element--ui-2.7.0-brightgreen.svg" alt="element-ui">
  </a>
  <a href="https://travis-ci.org/PanJiaChen/vue-element-admin" rel="nofollow">
    <img src="https://travis-ci.org/PanJiaChen/vue-element-admin.svg?branch=master" alt="Build Status">
  </a>
  <a href="https://github.com/PanJiaChen/vue-element-admin/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="license">
  </a>
  <a href="https://github.com/PanJiaChen/vue-element-admin/releases">
    <img src="https://img.shields.io/github/release/PanJiaChen/vue-element-admin.svg" alt="GitHub release">
  </a>
  <a href="https://gitter.im/vue-element-admin/discuss">
    <img src="https://badges.gitter.im/Join%20Chat.svg" alt="gitter">
  </a>
  <a href="https://panjiachen.github.io/vue-element-admin-site/donate">
    <img src="https://img.shields.io/badge/%24-donate-ff69b4.svg" alt="donate">
  </a>
</p>

- [vue-element-admin](https://panjiachen.github.io/vue-element-admin) 是一个后台前端解决方案，它基于 [vue](https://github.com/vuejs/vue) 和 [element-ui](https://element.eleme.io/#/zh-CN/component/installation) 实现。它使用了最新的前端技术栈，内置了 i18n 国际化解决方案，动态路由，权限验证，提炼了典型的业务模型，提供了丰富的功能组件，它可以帮助你快速搭建企业级中后台产品原型。

- License： [MIT](https://github.com/PanJiaChen/vue-element-admin/blob/master/LICENSE)
Copyright (c) 2017-present PanJiaChen

- [前端代码地址](https://github.com/SongYuQiu/Social-Network-Portrait-Analysis-System)


## 系统功能

```

- 微博数据爬取
  - 爬取指定微博用户的微博文本
  - 设置爬取开始时间

- 微博用户管理
  - 已爬取微博用户总数
  - 已爬取所有微博文本总数
  - 已生成人物画像数
  - 删除已爬取微博用户数据

- 画像分析
  - 推断性别概率
  - 推断年龄概率
  - 推断兴趣关键词
  - 结果可视化展示
  - 所爬取的微博文本的定位地图展示
  - 所爬取的微博文本时间轴展示

```

## 备注
- 由于训练的分类模型太大，没有上传
- [爬虫代码借鉴](https://github.com/dataabc/weibo-crawler)


## License
[MIT](https://github.com/SongYuQiu/Social-Network-Portrait-Analysis-System-BackCode/blob/master/LICENSE)

Copyright (c) 2021 Just for Star (yqSong)
