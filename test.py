import atomac
from atomac.AXKeyCodeConstants import *


bundle_id = 'com.tdx.tdxiMac'
atomac.launchAppByBundleId(bundle_id)
_tdx = atomac.getAppRefByBundleId(bundle_id)

print(_tdx)