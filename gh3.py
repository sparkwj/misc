# 配置
####################################
DEBUG = False
ACCOUNT = '王志学'
DOCTOR = '陈龙奇胸外科'
SCHEDULEDATE = '2022-03-23'
SCHEDULE_STATUS = 1
MAX_WORKERS = 20
TIME_DELAY = 0.05
TIME_WAIT_FINISH = 20
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

from requests_futures.sessions import FuturesSession

ACCOUNTS = {
    '王志学': ['18980083204', '218772921844371456', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '谭汉丽': ['18980083204', '218770840706224128', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '王军': ['18980083204', '218775160491216896', 'fgVuoa53qLSeIa6wo6pVVkmbfvTRb4LkzoA2EIGbNWLbXRyQE/5IxcJJtRXOqMxZvGB5wr4G+O0ldn6Vcm2KyInIlp3IKdKINvcTIhlcPNOCoXD94T3gUWfZl7dudNBx/r1RO4xR0VAhbrp9JGhSirDEJAC3tSkajsOyyeySZC0='],
    '熊艳': ['18980061204', '218819975878676481', 'kYj7HcQgtgjL7oqUXpMt32mieNPZjwWpYYLwIiU8IbFCJeIA51xGm+DxDYdYv43gj9ixYYjTEBrii9oWfTGrW5mBbZJOymzBvND06J+Wpct/hX4o/QOt2VPb5TfGHV3GZaHu64qWnt1sLq5z8jJjheJ1/sX6OMwvmbKYw1rDHyA='],
}
ACCOUNTNO, CARDID, PASSWORD = ACCOUNTS[ACCOUNT]

DOCTORS = {
    '车国卫胸外科': ['4028b881657fe07702657fe067490204', '294', '4201-XWK'],
    '车国卫特需': ['4028b881657fe07702657fe067490204', '918', '7829-TXMZ'],
    '陈龙奇胸外科': ['2c928082698199c8016a9ba8abd5320d', '294', '4201-XWK'],
    '陈龙奇特需': ['2c928082698199c8016a9ba8abd5320d', '918', '7829-TXMZ'],
    '朱敏': ['2c9580826f7f785b016ff183a3602816', '241', '3500-HXNK'],
    '朱丽娜': ['1499216756071116800', '250', '4140-KF'],
    '杨玉赏': ['1304366088137609216', '294', '4201-XWK'],
    '谢薇': ['4028b082715335fa01715d74308a276b', '722', '4140-KF'],
}
DOCTORID, DEPTCODE, DEPTCATEGORYCODE = DOCTORS[DOCTOR]

PROXIES = {'http': '192.168.50.3:9090'} if USE_PROXY else None
TOKEN = ''
SUCCEED = False

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
future_hxgyapiv2 = FuturesSession(session=hytapiv2, max_workers=MAX_WORKERS)
future_hytapiv2 = FuturesSession(session=hytapiv2, max_workers=MAX_WORKERS)

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

sysScheduleId = ''


def log(*msg):
    print(datetime.datetime.now(), '    ', *msg)


def login():
    global TOKEN
    path = '/cloud/hosplatcustomer/usercenter/account/login'
    data = {
        "password": PASSWORD,
        "accountNo": ACCOUNTNO,
        "channelCode": "PATIENT_IOS",
        "loginDeviceNum": "71b7f0fda0715ea031e3d7dc086f71c722458779db1b9226f809b5c87f6a4ba3",
        "loginDeviceType": "APP",
        "loginDeviceUUID": "179F83B9-44DD-43C6-81A7-8088EEDEE193",
        "appCode": "HXGYAPP"}
    try:
        res = hxgyapiv2.post(HXGYAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
        TOKEN = res['data']['token']
        headers = {'TOKEN': TOKEN, 'accessTOKEN': TOKEN}
        hxgyapiv2.headers.update(headers)
        hytapiv2.headers.update(headers)
        if int(res['code']) == 1 and len(TOKEN) > 0:
            return True
        else:
            return False
    except:
        return False


def selDoctorDetailsTwo(doctorId, deptCode, deptCategoryCode, scheduleDate):
    global sysScheduleId
    path = '/cloud/hosplatcustomer/call/appointment/selDoctorDetailsTwo'
    data = {"appointmentType":"1","channelCode":"PATIENT_IOS","hospitalAreaCode":"HID0101","deptCode":deptCode,"doctorId":doctorId,"appCode":"HXGYAPP","hospitalCode":"HID0101","tabAreaCode":"ALL","deptCategoryCode":deptCategoryCode}   # noqa
    res = hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
    items = res['data']['sourceItemsRespVos']
    sysScheduleId = ''
    for item in items:
        log('{}   {}  {}  Status: {}'.format(item['sysScheduleId'], item['docName'], item['scheduleDate'], item['status']))
        if item['status'] == SCHEDULE_STATUS:
            if item['scheduleDate'] == scheduleDate:
                sysScheduleId = item['sysScheduleId']
                break

    return sysScheduleId


def selDoctorListByMoreTerm(keyWord):
    path = '/cloud/hosplatcustomer/call/appointment/doctorListModel/selDoctorListByMoreTerm'
    data = {"scheduleDate":"","hospitalCode":"HID0101","deptCode":"","keyWord":keyWord,"regTitelCode":"","keyWordEnumType":"0","channelCode":"PATIENT_IOS","appCode":"HXGYAPP","haveNo":"0","timeRange":"2","hospitalAreaCode":"","deptCategoryCode":"","appointmentType":"1"}   # noqa
    res = hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES).json()
    for doctor in res['data']:
        print('{}   {}  {}  {}  {}  {}\n'.format(doctor['doctorId'], doctor['docName'], doctor['deptCode'], doctor['deptCategoryCode'], doctor['deptCategoryName'], doctor['status']))
        print(doctor, '\n')


def getimagecode_hook(resp, *args, **kwargs):
    try:
        res = resp.json()
        imageId = res['data']['bizSeq']
        imageData = res['data']['imageData']
        verifyCode = ocr.classification(img_base64=imageData)
        if verifyCode.isnumeric() and len(verifyCode) == 4 and not SUCCEED:
            if DEBUG:
                verifyCode = '000O'
            sureAppointment(verifyCode, imageId)
            log((verifyCode, imageId))
    except:
        traceback.print_exc()


def getimagecode():
    path = '/cloud/hosplatcustomer/customer/image/getimagecode'
    data = {"appCode":"HXGYAPP","organCode":"HID0101","channelCode":"PATIENT_IOS","type":"APP"}   # noqa

    try:
        future_hxgyapiv2.post(HXGYAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES, hooks={'response': getimagecode_hook})
    except:
        traceback.print_exc()


def sureAppointment_hook(resp, *args, **kwargs):
    global SUCCEED
    try:
        res = resp.json()
        log(res)
        if res['errCode'] == 0 or res['errCode'] == '0':
            SUCCEED = True
            log('挂号成功!!!')
            future_hytapiv2.close()
            exit()
    except:
        traceback.print_exc()


def sureAppointment(verifyCode, imageId):
    global sysScheduleId
    if len(sysScheduleId) <= 0:
        log('sureAppointment: sysScheduleId为空')
        return

    path = '/cloud/hosplatcustomer/call/appointment/appointmentModel/sureAppointment'
    data = {"appCode":"HXGYAPP","channelCode":"PATIENT_IOS","sysTimeArrangeId":"","appointmentType":1,"cardId":CARDID,"hospitalCode":"HID0101","hospitalAreaCode":"HID0101","sysScheduleId":sysScheduleId,"type":"APP","verifyCode":verifyCode,"imageId":imageId}   # noqa

    if DEBUG:
        verifyCode = '000O'

    try:
        future_hytapiv2.post(HYTAPIV2_BASE + path, json=data, verify=False, proxies=PROXIES, hooks={'response': sureAppointment_hook})
    except:
        # traceback.print_exc()
        pass


if __name__ == '__main__':
    log('启动', 'DEBUG is True' if DEBUG else '')

    while not login():
        log('登录失败，继续尝试')
        time.sleep(1)

    # 搜索
    # selDoctorListByMoreTerm('陈龙奇')
    # exit()

    # 挂号
    log('{}:{}  医生:{}  {}\n'.format(ACCOUNT, ACCOUNTNO, DOCTOR, SCHEDULEDATE))

    log('获取 {} 医生排班信息 ... '.format(DOCTOR))
    while len(sysScheduleId) <= 0:
        try:
            sysScheduleId = selDoctorDetailsTwo(DOCTORID, DEPTCODE, DEPTCATEGORYCODE, SCHEDULEDATE)
            break
        except:
            traceback.print_exc()
            log('获取 {} 医生排班信息失败，重试 ... '.format(DOCTOR))

    if len(sysScheduleId) <= 0:
        log('sysScheduleId为空, 没有获取到 {} 可用的排班, 退出 ...'.format(SCHEDULEDATE))
        exit()
    else:
        log('成功获取到 {} {} 的排班!\n'.format(DOCTOR, SCHEDULEDATE))

    openTime = datetime.datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    if DEBUG:
        beginTime = datetime.datetime.now()
        endTime = beginTime + datetime.timedelta(seconds=10)
    else:
        beginTime = openTime - datetime.timedelta(seconds=4)
        endTime = openTime + datetime.timedelta(seconds=4)

    log('开始获取验证码 ...', '截止时间', endTime)
    while datetime.datetime.now() < endTime and not SUCCEED:
        if datetime.datetime.now() > beginTime:
            getimagecode()
        time.sleep(TIME_DELAY)

    time.sleep(TIME_WAIT_FINISH)
    log('完成！')
