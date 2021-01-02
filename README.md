# 从深圳住建局爬取预售项目详细价格信息

深圳住建局官方网站 http://zjj.sz.gov.cn/ris/bol/szfdc/index.aspx 会公示新房预售价格信息。但是如果要找到套房的户型、面积、单价等信息，非常麻烦。因为每个套房的信息都放在了一个单独的页面，且要点进去4层：项目 > 楼栋 > 单元 > 套房。并且住建局只提供了建筑面积单价，需要自己计算总价。

微博上有个自媒体 @唐老师傅 https://weibo.com/10890189 经常会把价格信息汇总做成图片。我想做一个类似的。

现在生成的 `result.xlsx` 基本上符合 @唐老师傅 的格式，手工简单修改一下自动生成的`result.xlsx`，就可以得到 `result_manual_optimization.xlsx`，和 @唐老师傅 的表格差不多。

---

2021-1-1

优化了 RE patterns，现在除了个别写字楼，其他的住宅和公寓项目应该都没啥问题了。看上去不用XPath也行。

2020-1-2

修复了一些bug，现在可以抓取所有项目，包括办公、公寓、住宅、商铺，也适配地下层和区局锁定状态。


## 使用方法

首先访问 http://zjj.sz.gov.cn/ris/bol/szfdc/index.aspx 找到想要爬取价格的楼盘，然后将楼盘的URL复制下来，替换变量 `project_url` 的值。准备环境变量之后运行 `python szZjj_crawler.py`