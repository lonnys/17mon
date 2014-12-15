17mon
=====

支持新版的DATX

用法：

import ip17mon
result = ip17mon.find('1.2.3.4')

返回结构：
{'stat': 'ok',  #返回状态（ok/fail）
'location': {'latitude': 纬度, 'longitude': 经度}, 
'area': [u'国家', u'省份|直辖市', u'市区', u'地址详情', u'运营商']}
