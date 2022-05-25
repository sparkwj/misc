import atomac
from atomac.AXKeyCodeConstants import *


_tdx = None

DEBUG = True

TRADE_ACCOUNT = ''
TRADE_PASSWORD = ''


def login(account=None, password=None):
    logger.debug('enter login')
    if password is None:
        raise Exception('Trade api needs account and password!')

    global _tdx
    bundle_id = 'com.tdx.tdxiMac'
    atomac.launchAppByBundleId(bundle_id)
    _tdx = atomac.getAppRefByBundleId(bundle_id)
    logger.debug('wait front')
    while True:
        time.sleep(0.1)
        first = _tdx.findFirst()
        try:
            if '国泰君安证券锐智版' in first.AXTitle:
                time.sleep(1)
                break
        except:
            pass
    _login(account, password)
    logger.debug('finish login')


def _login(account, password):
    _activate()
    _ensureLogin(account, password)


def _ensureLogin(account, password):
    logger.debug('enter _ensureLogin')
    global _tdx
    while not _checkIfAlreadyLogin():
        _loginFirstIfUnlogin(account, password)
        _loginFirstIfLocked(password)
        _confirmIfMessage()
        time.sleep(0.1)
    time.sleep(0.2)


def _checkIfAlreadyLogin():
    logger.debug('check if already login')
    global _tdx
    try:
        buttons = _tdx.windows()[0].AXChildren[2]._convenienceMatchR('AXTextField', 'AXValue', '       历史成交')
        if len(buttons) > 0:
            logger.debug('check login success')
            return True
        else:
            logger.debug('not login at else')
            return False
    except:
        logger.debug('not login at except')
        return False


def query_portfolio(portfolio=True):
    global _tdx
    _activate()
    time.sleep(0.1)
    flag = False
    try:
        s = _tdx.windows()[0].staticTextsR('人民币: 余额:*')[0].AXValue
        if len(s) > 0:
            flag = True
    except:
        pass
    if not flag:
        _tdx.windows()[0]._convenienceMatch('AXCheckBox', 'AXTitle', '持仓')[0].Press()
        time.sleep(0.1)
        flag = False
        while not flag:
            try:
                s = _tdx.windows()[0].staticTextsR('人民币: 余额:*')[0].AXValue
                if len(s) > 0:
                    flag = True
                    break
            except:
                pass
            time.sleep(0.1)

    s = _tdx.windows()[0].staticTextsR('人民币: 余额:*')[0].AXValue
    cash_balance, cash_available, _, stocks_total, assets_total = re.match(
        r'人民币:余额:([\d\.]*)可用:([\d\.]*)可取:([\d\.]*)股票市值:([\d\.]*)资产:([\d\.]*)', s.replace(' ', '')).groups()

    if portfolio:
        portfolio = _table_to_dataframe('累计浮动盈亏').iloc[:, :-1]
        portfolio.set_index('证券代码', inplace=True)

    return (float(cash_balance), float(cash_available), float(stocks_total), float(assets_total)), portfolio


def query_orders():
    global _tdx
    _activate()
    time.sleep(0.1)
    _tdx.windows()[0]._convenienceMatch('AXCheckBox', 'AXTitle', '成交')[0].Press()
    time.sleep(1.8)
    today_orders = _table_to_dataframe('成交日期').iloc[:, :-2]
    print(today_orders)

    _click(_tdx.windows()[0].AXChildren[2]._convenienceMatchR('AXTextField', 'AXValue', '       历史成交')[0])
    time.sleep(1.8)
    history_orders = _table_to_dataframe('成交日期').iloc[:, :-1]
    print(history_orders)

    import pandas as pd
    orders = pd.concat([today_orders, history_orders])

    return orders


def _table_to_dataframe(header_key):
    global _tdx
    table = _tdx.windows()[0].buttonsR(header_key)[0].AXParent.AXParent
    rows = table._convenienceMatch('AXRow', 'AXRoleDescription', 'table row')

    data = [[column.AXValue for column in row.AXChildren] for row in rows]
    columns = [button.AXTitle for button in table.buttonsR()]

    import pandas as pd
    return pd.DataFrame(data, columns=columns)


def buy(codes, positions):
    logger.debug('enter buy')
    global _tdx
    _activate()
    time.sleep(0.1)
    logger.debug('will press buy button')
    _tdx.windows()[0]._convenienceMatch('AXCheckBox', 'AXTitle', '买入')[0].Press()
    time.sleep(0.2)

    codes = [codes] if isinstance(codes, str) else codes

    logger.debug('loop codes for buy')
    for code, money in zip(codes, positions):
        logger.debug('target code is: {}'.format(code))

        try:
            time.sleep(0.2)
            logger.debug('will press order type 1')
            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            types = _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[1].AXChildren[
                0].AXChildren
            type_index = 0
            logger.debug('will click type option')
            _click(types[type_index])
            time.sleep(0.1)

            logger.debug('set code focus')
            _tdx.windows()[0].textFields()[0].AXFocused = True
            _tdx.windows()[0].textFields()[0].setString('AXValue', code)
            # _tdx.windows()[0].textFields()[0].Confirm()
            time.sleep(1.5)

            price = _tdx.windows()[0].textFields()[2].AXValue
            price = float(price)
            logger.debug('price is: {}'.format(price))

            amount = int(money / price / 100) * 100
            if amount < 100:
                logger.error('money: {} can not buy {} 100 shares, stock price: {}'.format(money, code, price))
                # amount = 100
            logger.debug('amount is: {}'.format(amount))

            _tdx.windows()[0].textFields()[1].setString('AXValue', amount)
            _tdx.windows()[0].textFields()[1].Confirm()
            time.sleep(0.5)

            logger.debug('select order type option')
            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            # time.sleep(0.1)
            types = _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[1].AXChildren[
                0].AXChildren
            type_index = 4 if len(types) > 3 else 1
            logger.debug('click order option: {}'.format(types[type_index]))
            _click(types[type_index])
            time.sleep(0.1)

            if not DEBUG:
                _click(_tdx.windows()[0].buttonsR('买入下单')[0])
            time.sleep(0.2)
            _confirmIfMessage()
            time.sleep(0.5)
            _confirmIfMessage()
            time.sleep(0.2)

        except:
            logger.exception('Exception while tdx.buy')


def sell(codes):
    logger.debug('enter sell')
    global _tdx
    _activate()
    time.sleep(0.1)
    logger.debug('press the sell button')
    _tdx.windows()[0]._convenienceMatch('AXCheckBox', 'AXTitle', '卖出')[0].Press()
    time.sleep(0.1)

    codes = [codes] if isinstance(codes, str) else codes

    logger.debug('loop codes for sell')
    for code in codes:
        logger.debug('target code: {}'.format(code))
        try:
            _tdx.windows()[0].textFields()[0].AXFocused = True
            _tdx.windows()[0].textFields()[0].setString('AXValue', code)
            # _tdx.windows()[0].textFields()[0].Confirm()
            time.sleep(1.5)

            _click(_tdx.windows()[0].buttonsR('全部')[0])
            time.sleep(0.1)

            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[0].Press()
            # time.sleep(0.1)
            types = _tdx.windows()[0]._convenienceMatch('AXComboBox', 'AXTitle', None)[1].AXChildren[1].AXChildren[
                0].AXChildren
            type_index = 4 if len(types) > 3 else 1
            logger.debug('click order option: {}'.format(types[type_index]))
            _click(types[type_index])
            time.sleep(0.1)


            # stop_price = _tdx.windows()[0]._convenienceMatch('AXScrollArea', 'AXTitle', None)[1].AXChildren[0]._convenienceMatch('AXRow', 'AXTitle', None)[-3].AXChildren[1].AXValue


            if not DEBUG:
                _click(_tdx.windows()[0].buttonsR('卖出下单')[0])
            time.sleep(0.2)
            _confirmIfMessage()
            time.sleep(0.2)
            _confirmIfMessage()
            time.sleep(0.2)

        except:
            logger.exception('Exception while tdx.sell')


# def query_order(codes, flag=None):
#     global _tdx
#     _activate()
#     time.sleep(0.1)
#     _tdx.windows()[0]._convenienceMatchR('AXCheckBox', 'AXTitle', '成交')[0].Press()
#     time.sleep(0.2)
#
#     codes = [codes] if isinstance(codes, str) else codes

def exit():
    global _tdx
    _activate()
    time.sleep(0.1)
    _tdx.sendKeyWithModifiers('q', [COMMAND_L])
    time.sleep(1)


def lockHide():
    global _tdx
    _activate()
    time.sleep(0.1)
    _tdx.windows()[0].buttonsR('锁定')[0].Press()
    time.sleep(0.1)
    _tdx.windows()[0].buttons()[-1].Press()
    time.sleep(0.1)


def _confirmIfMessage():
    try:
        title = _tdx.windows()[0].AXChildren[1].AXValue
        message = _tdx.windows()[0].AXChildren[2].AXValue
        if title in ('提示', '交易确认', '连接确认'):
            logger.debug('confirm message {}: {}'.format(title, message))
            button = _tdx.windows()[0].AXChildren[3]
            if button.AXTitle in ('确定', '是'):
                button.Press()
                time.sleep(0.1)

            if 'KCBPCLI_CallProgramAndCommit' in message:
                minutes = 30
                logger.info('KCBPCLI_CallProgramAndCommit失败, system in maitain, wait {} minutes ...'.format(minutes))
                time.sleep(60 * minutes)
            elif '接收应答超时或网络已断开' in message:
                minutes = 10
                logger.info('接收应答超时或网络已断开, wait {} minutes...'.format(minutes))
                time.sleep(60 * minutes)
    except:
        pass


def _click(obj):
    position = obj.AXPosition
    size = list(obj.AXSize)
    size[0] = 60. if size[0] > 200 else size[0]
    coord = (position[0] + size[0] / 2, position[1] + size[1] / 2)
    obj.clickMouseButtonLeft(coord)
    time.sleep(0.1)


def _loginFirstIfUnlogin(account, password):
    global _tdx
    try:
        search_text = ''
        try:
            search_text = _tdx.windows()[0].AXChildren[1].AXChildren[1].AXTitle
        except:
            pass
        if len(search_text) > 0:
            if account is None or len(account) < 5 or password is None or len(password) < 6:
                raise Exception('You must assgin correct trade account and password for login!')
        else:
            return

        if _tdx.windows()[0].AXChildren[1].AXChildren[4].AXValue != 'c成都顺城大街(原人民中路)':
            _tdx.windows()[0].AXChildren[1].AXChildren[4].setString('AXValue', 'c成都顺城大街(原人民中路)')
            _tdx.windows()[0].AXChildren[1].AXChildren[4].AXChildren[0].Press()
            time.sleep(0.3)
            _click(_tdx.windows()[0].AXChildren[1].AXChildren[4].AXChildren[1].AXChildren[0].AXChildren[25])
            time.sleep(0.2)

        _tdx.windows()[0].AXChildren[1].AXChildren[6].setString('AXValue', account)
        _tdx.windows()[0].AXChildren[1].AXChildren[9].setString('AXValue', password)
        time.sleep(0.1)
        _tdx.windows()[0].AXChildren[1].AXChildren[13].Press()
        logger.debug('will waiting for login button enabled')
        try:
            while not _tdx.windows()[0].AXChildren[1].AXChildren[13].AXEnabled:
                time.sleep(1)
                _confirmIfMessage()
        except:
            pass
    except:
        logger.debug('exception at _loginFirstIfUnlogin', exc_info=True)


def _loginFirstIfLocked(password):
    global _tdx
    try:
        lock_text = []
        try:
            lock_text = _tdx.windows()[0].staticTextsR('交易界面已锁定*')
        except:
            pass
        if len(lock_text) > 0:
            if password is None or len(password) < 6:
                _loginFirstIfLocked.passwordFlag = True
                raise Exception('You must assgin correct trade password for login!')
        else:
            return
        text_password = _tdx.windows()[0].textFields()[0]
        if text_password.AXSubrole == 'AXSecureTextField':
            text_password.setString('AXValue', password)
            _tdx.windows()[0].buttonsR('确定')[0].Press()
            time.sleep(0.1)
    except Exception as ex:
        print(ex)


_loginFirstIfLocked.passwordFlag = False


def _activate():
    global _tdx
    while not _tdx.AXFrontmost:
        _confirmIfMessage()
        _tdx.activate()
        time.sleep(0.1)
    time.sleep(0.1)
    _confirmIfMessage()
    _confirmIfMessage()


def _sendKey(key):
    global _tdx
    _tdx.sendKey(key)


def _sendKeys(keys):
    global _tdx
    _tdx.sendKeys(keys)


if __name__ == '__main__':
    login(123456, 123456)

    account_info = query_portfolio()
    print(account_info)

    buy('600036', 20000)
    sell('601345')

    exit()
