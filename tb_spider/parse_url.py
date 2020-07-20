# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/13 12:21"
__doc__ = """ 解析url得到data"""

import re


def get_data_from_url(s):
    p0 = re.compile('^(.*?\?)')
    p = re.compile('&')

    url_head = re.findall(p0, s)[0]
    url_data = s.replace(url_head, '')
    res = re.split(p, url_data)

    data = {}
    url_tail = ''
    for ele in res:
        tmp = ele.split('=')
        if tmp[1]:
            data[tmp[0]] = tmp[1]
            url_tail += tmp[0] + '=' + tmp[1] + '&'
    url = url_head + url_tail
    return url[:-1], data


if __name__ == '__main__':
    s = 'http://detail.tmall.com/item.htm?id=616377396214&ad_id=&am_id=&cm_id=140105335569ed55e27b&pm_id=&abbucket=13'
    url, data = get_data_from_url(s)
    print(url, data)
