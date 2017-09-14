# coding=utf-8
__author__ = "yaoo"
__version__ = "1.0.1"
__email__ = "1711602280@qq.com"

import requests
import time
import yundama
import json
import copy
# from captcha import retrive_img,process_img,recognize

'''用来模拟登陆知乎 保存cookies,并且返回cookie字典对象'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
sess = requests.Session()
def getCookies(account, passwd):
    '''
    :param account: 用户名
    :param passwd: 密码
    :return:
    '''
    try:
        with open('cookies.txt', 'r') as f:
            all_cookies = f.readlines()
        cookies_dict = json.loads(all_cookies[0])
        requests.utils.add_dict_to_cookiejar(sess.cookies,cookies_dict)
        if checkLogin():
            # 成功登陆
            return cookies_dict
        else:
            login(account, passwd)
    except Exception as e:
        cookies_dict = login(account, passwd)
        return cookies_dict

def login(account, passwd):
    '''
    登陆流程
    :param account:
    :param passwd:
    :return:
    '''
    response = sess.get('https://www.zhihu.com/', headers=headers)
    cookies_dict = response.cookies.get_dict()
    _xsrf = cookies_dict['_xsrf']
    # 调用云打码
    captcha = getChapcha(sess)
    if '@' in account:
        #邮箱登陆
        url = 'https://www.zhihu.com/login/email'
        form_data = {
            '_xsrf': _xsrf,
            'password': passwd,
            'captcha': captcha,
            'captcha_type': 'en',
            'email': account
        }
    else:
        #手机号登陆
        url = 'https://www.zhihu.com/login/phone_num'
        form_data = {
            '_xsrf': _xsrf,
            'password': passwd,
            'captcha': captcha,
            'captcha_type': 'en',
            'phone_num': account
        }
    response = sess.post(url=url, data=form_data, headers=headers)
    json_obj = json.loads(response.text)
    print json_obj['msg']
    if u'登录成功'==json_obj['msg']:
        cookies_dict = copy.deepcopy(response.cookies.get_dict())
        json_cookies = json.dumps(response.cookies.get_dict(), ensure_ascii=False)
        with open('cookies.txt', 'w') as f:
            f.write(json_cookies.encode('utf-8'))
        return cookies_dict
    else:
        login(account, passwd)

def getChapcha(sess):
    '''
    获取登陆验证码
    :param sess:
    :return:
    '''
    captcha_time = str(time.time()).split('.')[0]+str(time.clock()).split('.')[1][:3]
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(captcha_time)
    response = sess.get(url=captcha_url, headers=headers)
    # captcha = recognize(process_img(retrive_img(response)))
    # print captcha
    with open('captcha.gif', 'wb') as f:
        f.write(response.content)
    captcha = yundama.result_captcha('captcha.gif')
    return captcha

def checkLogin():
    '''
    检查是否登陆成功
    :return:
    '''
    response = sess.get('https://www.zhihu.com/settings/profile', headers=headers, allow_redirects=False)
    if 200 == response.status_code:
        return True
    else:
        return False

if __name__ == '__main__':
    cookies = getCookies('13652331556', '49ba59abbe56e057')
    index_api = 'https://www.zhihu.com/api/v3/feed/topstory?action_feed=True&limit=10&action=down&after_id=0&desktop=true'
    url = 'https://www.zhihu.com/api/v4/questions/48350201/answers?sort_by=default&include=data[*].is_normal%2Ccomment_count%2Ccontent%2Cvoteup_count%2Ccreated_time%2Cupdated_time%2Cbadge[%3F(type%3Dbest_answerer)].topics&limit=20&offset=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Authorization': 'Bearer ' + cookies['z_c0'],
    }
    response = requests.get(index_api,headers=headers)
    print response.text