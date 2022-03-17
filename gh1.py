# 配置
####################################
DEBUG = False
AUTOMAKE = True
ACCOUNT = '王军'
DOCTOR = '谢薇'
SCHEDULEDATE = '2022-03-21'
MAXTRYTIME = 10
USE_PROXY = False
####################################

import traceback
import time
import datetime
import ddddocr
ocr = ddddocr.DdddOcr(old=True, show_ad=False)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# from requests_futures.sessions import FuturesSession

ACCOUNTS = {
    '王志学': ['18980083204', '218772921844371456', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '谭汉丽': ['18980083204', '218770840706224128', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '王军': ['18980083204', '218775160491216896', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '熊艳': ['18980061204', '218819975878676481', 'kYj7HcQgtgjL7oqUXpMt32mieNPZjwWpYYLwIiU8IbFCJeIA51xGm+DxDYdYv43gj9ixYYjTEBrii9oWfTGrW5mBbZJOymzBvND06J+Wpct/hX4o/QOt2VPb5TfGHV3GZaHu64qWnt1sLq5z8jJjheJ1/sX6OMwvmbKYw1rDHyA='],
}
ACCOUNTNO, CARDID, PASSWORD = ACCOUNTS[ACCOUNT]

DOCTORS = {
    '车国卫特需': ['4028b881657fe07702657fe067490204', '918', '7829-TXMZ'],
    '车国卫胸外科': ['4028b881657fe07702657fe067490204', '294', '4201-XWK'],
    '朱敏': ['2c9580826f7f785b016ff183a3602816', '241', '3500-HXNK'],
    '朱丽娜': ['1499216756071116800', '250', '4140-KF'],
    '杨玉赏': ['1304366088137609216', '294', '4201-XWK'],
    '谢薇': ['4028b082715335fa01715d74308a276b', '722', '4140-KF'],
}
DOCTORID, DEPTCODE, DEPTCATEGORYCODE = DOCTORS[DOCTOR]

PROXIES = {'http': '192.168.50.3:9090'} if USE_PROXY else None
TOKEN = ''
SUCCEED = False

if DEBUG:
    print('DEBUG is True')

NSLOOKUP = {
    'hxgyapiv2.cd120.info': '47.102.226.113',
    'hytapiv2.cd120.com': '47.108.20.21',
    # 'hytapiv2.cd120.com': '59.36.229.20',
    '127.0.0.1': '127.0.0.1',
}


def patched_create_connection(address, *args, **kwargs):
    global NSLOOKUP
    host, port = address
    hostname = NSLOOKUP[host]
    return _orig_create_connection((hostname, port), *args, **kwargs)


from urllib3.util import connection
_orig_create_connection = connection.create_connection
connection.create_connection = patched_create_connection

HXGYAPIV2_BASE = 'https://hxgyapiv2.cd120.info'
HYTAPIV2_BASE = 'https://hytapiv2.cd120.com'
hxgyapiv2 = requests.Session()
hytapiv2 = requests.Session()
# future_session = FuturesSession(session=hytapiv2, max_workers=100)

HEADERS = {
    'UUID': '179F83B9-44DD-43C6-81A7-8088EEDEE193',
    'Mac': 'Not Found',
    'Accept': '*/*',
    'Client-Version': '6.4.2',
    'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, zh-Hant-CN;q=0.8',
    'User-Agent': 'hua yi tong/6.4.2 (iPhone; iOS 15.3.1; Scale/2.00)',
}
hxgyapiv2.headers.update(HEADERS)
hytapiv2.headers.update(HEADERS)


def api_request(path='', data='', base=HYTAPIV2_BASE):
    global TOKEN
    url = base + path
    headers = {
        'Host': base.replace('https://', ''),
        'UUID': '179F83B9-44DD-43C6-81A7-8088EEDEE193',
        'Mac': 'Not Found',
        'Accept': '*/*',
        'Client-Version': '6.4.2',
        'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, zh-Hant-CN;q=0.8',
        'TOKEN': TOKEN,
        'accessTOKEN': TOKEN,
        'User-Agent': 'hua yi tong/6.4.2 (iPhone; iOS 15.3.1; Scale/2.00)',

    }
    if USE_PROXY:
        req = requests.post(url, headers=headers, json=data, proxies=PROXIES, verify=False)
    else:
        req = requests.post(url, headers=headers, json=data)

    return req.json()


def login():
    global HXGYAPIV2_BASE
    global TOKEN
    global ACCOUNTNO
    global PASSWORD
    path = '/cloud/hosplatcustomer/usercenter/account/login'
    data = {
        "password": PASSWORD,
        "accountNo": ACCOUNTNO,
        "channelCode": "PATIENT_IOS",
        "loginDeviceNum": "71b7f0fda0715ea031e3d7dc086f71c722458779db1b9226f809b5c87f6a4ba3",
        "loginDeviceType": "APP",
        "loginDeviceUUID": "179F83B9-44DD-43C6-81A7-8088EEDEE193",
        "appCode": "HXGYAPP"}
    # res = api_request(path, data, base=HXGYAPIV2_BASE)
    res = hxgyapiv2.post(HXGYAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
    assert int(res['code']) == 1, res['msg']
    TOKEN = res['data']['token']
    headers = {'TOKEN': TOKEN, 'accessTOKEN': TOKEN}
    hxgyapiv2.headers.update(headers)
    hytapiv2.headers.update(headers)


def selDoctorDetailsTwo(doctorId, deptCode, deptCategoryCode, scheduleDate):
    print('获取医生排班信息 ... ')
    path = '/cloud/hosplatcustomer/call/appointment/selDoctorDetailsTwo'
    data = {"appointmentType":"1","channelCode":"PATIENT_IOS","hospitalAreaCode":"HID0101","deptCode":deptCode,"doctorId":doctorId,"appCode":"HXGYAPP","hospitalCode":"HID0101","tabAreaCode":"ALL","deptCategoryCode":deptCategoryCode}   # noqa
    # res = api_request(path, data)
    res = hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
    # print(res)
    items = res['data']['sourceItemsRespVos']
    sysScheduleId = ''
    for item in items:
        print('{}   {}  {}  Status: {}'.format(item['sysScheduleId'], item['docName'], item['scheduleDate'], item['status']))
        if item['status'] == 1:
            if item['scheduleDate'] == scheduleDate:
                sysScheduleId = item['sysScheduleId']
                break

    if len(sysScheduleId) <= 0:
        print('sysScheduleId为空, 没有获取到 {} 可用的排班'.format(scheduleDate))
    else:
        print('成功获取到 {} 的排班!'.format(scheduleDate))

    return sysScheduleId


def getimagecode():
    global ocr
    global HXGYAPIV2_BASE
    path = '/cloud/hosplatcustomer/customer/image/getimagecode'
    data = {"appCode":"HXGYAPP","organCode":"HID0101","channelCode":"PATIENT_IOS","type":"APP"}   # noqa

    verifyCode = ''
    imageId = ''
    try:
        while not verifyCode.isnumeric() or len(verifyCode) != 4:
            # res = api_request(path, data, base=HXGYAPIV2_BASE)
            res = hxgyapiv2.post(HXGYAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
            imageId = res['data']['bizSeq']
            imageData = res['data']['imageData']
            verifyCode = ocr.classification(img_base64=imageData)
    except (KeyboardInterrupt, SystemExit):
        exit()
    except:
        traceback.print_exc()

    return verifyCode, imageId


def sureAppointment(cardId, sysScheduleId, verifyCode, imageId):
    global DEBUG

    if len(sysScheduleId) <= 0:
        print('sureAppointment: sysScheduleId为空')
        return None

    path = '/cloud/hosplatcustomer/call/appointment/appointmentModel/sureAppointment'
    data = {"appCode":"HXGYAPP","channelCode":"PATIENT_IOS","sysTimeArrangeId":"","appointmentType":1,"cardId":cardId,"hospitalCode":"HID0101","hospitalAreaCode":"HID0101","sysScheduleId":sysScheduleId,"type":"APP","verifyCode":verifyCode,"imageId":imageId}   # noqa

    res = None
    if DEBUG:
        print('DEBUG is True, Cancel ...')
    else:
        # res = api_request(path, data)
        try:
            res = hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
            # future_session.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
        except:
            traceback.print_exc()

    return res


def makeAppointment(sysScheduleId):
    global CARDID
    global DOCTORID
    global DEPTCATEGORYCODE
    global SCHEDULEDATE
    global DEBUG
    global SUCCEED
    res = None

    if len(sysScheduleId) <= 0:
        print('makeAppointment: sysScheduleId为空')
        if not DEBUG:
            return

    start = time.time()
    while time.time() - start < MAXTRYTIME:
        try:
            verifyCode, imageId = getimagecode()
            if DEBUG:
                verifyCode = '000O'
            res = sureAppointment(CARDID, sysScheduleId, verifyCode, imageId)
            if res is not None and (res['errCode'] == 0 or res['errCode'] == '0'):
                SUCCEED = True
                print(datetime.datetime.now(), '挂号成功!!!')
                break
            # elif res is not None and res['errCode'] in ['303014', '30300001', '900001']:  # 900001无可用号源
            #     print(verify, res['errCode'], res['msg'])
            #     continue
            else:
                print(datetime.datetime.now(), res)
                continue
        except SystemExit:
            exit()
        except:
            traceback.print_exc()

    print('' if res is None else res)
    return res


def selDoctorListByMoreTerm(keyWord):
    path = '/cloud/hosplatcustomer/call/appointment/doctorListModel/selDoctorListByMoreTerm'
    data = {"scheduleDate":"","hospitalCode":"HID0101","deptCode":"","keyWord":keyWord,"regTitelCode":"","keyWordEnumType":"0","channelCode":"PATIENT_IOS","appCode":"HXGYAPP","haveNo":"0","timeRange":"2","hospitalAreaCode":"","deptCategoryCode":"","appointmentType":"1"}   # noqa
    # res = api_request(path, data)
    res = hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
    for doctor in res['data']:
        print('{}   {}  {}  {}  {}  {}\n'.format(doctor['doctorId'], doctor['docName'], doctor['deptCode'], doctor['deptCategoryCode'], doctor['deptCategoryName'], doctor['status']))
        print(doctor, '\n')


if __name__ == '__main__':
    login()

    # 搜索
    # selDoctorListByMoreTerm('谢薇')
    # exit()

    # 挂号
    print('{}:{}  医生:{}  {}\n'.format(ACCOUNT, ACCOUNTNO, DOCTOR, SCHEDULEDATE))
    sysScheduleId = selDoctorDetailsTwo(DOCTORID, DEPTCODE, DEPTCATEGORYCODE, SCHEDULEDATE)

    print('\n')
    AUTOMAKED = False
    while not SUCCEED:
        if AUTOMAKE and not AUTOMAKED:
            print('AUTOMAKE', datetime.datetime.now(), '\n')
            startuptime = datetime.datetime.today().replace(hour=7, minute=59, second=58, microsecond=0)
            while datetime.datetime.now() < startuptime and not DEBUG:
                time.sleep(0.2)
            AUTOMAKED = True
        elif AUTOMAKED and not DEBUG:
            exit()
        else:
            input('\nPress enter to continue ...')

        try:
            makeAppointment(sysScheduleId)
        except:
            traceback.print_exc()
