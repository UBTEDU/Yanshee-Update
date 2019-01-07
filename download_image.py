#!/usr/bin/python
# coding=utf-8
"""
# Copyright (c) 2019 by UBTECH.
# All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
import os
import time
import json
import hashlib
import urllib
import socket
import urllib3

API_URL = "https://upgrade.ubtrobot.com/v1/upgrade-rest/"
APP_ID = '500010015'
APP_KEY = '185ce49be88544da81741a01b1f1ea2c'

PRODUCT_NAME = 'YANSHEE03'
MODULE_ROBOT_NAME = 'ubt-yanshee-ros-linux'
FILE_ROBOT_INFO = 'upgrade_robot_info.txt'
MODULE_BLOCKLY_NAME = 'ubtedu-yansheeblockly'
FILE_BLOCKLY_INFO = 'upgrade_blockly_info.txt'
STR_FROM_VERSION = 'fromversion'
STR_TO_VERSION = 'toversion'

NOOBS_FILE_NAME = 'noobs.tar.gz'


"Ret Value"
UBTEDU_RC_SUCCESS = 0  # /**< Success */
UBTEDU_RC_FAILED = 1  # /**< Failed */
UBTEDU_RC_NORESOURCE = 2  # /**< No resource */
UBTEDU_RC_NOT_FOUND = 3  # /**< Not found */
UBTEDU_RC_WRONG_PARAM = 4  # /**< Wrong parameter */
UBTEDU_RC_IGNORE = 5  # /**< Ignore this return value */

"Robot global variable"
language = 0  # 0:chinses 1:english
robot_status = 0
curr_path = '.'
download_info = 10


def progress_rate(a, b, c):
    """Get the progress rate."""
    percent = 100.0 * a * b / c
    print('downloading %.3f%%', percent)


def do_shell_cmd(cmd):
    """Execute bash cmd."""
    result = os.popen(cmd)
    return result.read().rstrip('\n')


def get_file_md5(file_name):
    """Calc the md5 for a file."""
    if not os.path.isfile(file_name):
        print("Cannot find file:%s", file_name)
        return ''
    myhash = hashlib.md5()
    f = file(file_name, 'rb')
    while True:
        buff = f.read(8096)
        if not buff:
            break
        myhash.update(buff)
    f.close()
    return myhash.hexdigest()


def create_header(device_ID):
    """Create the http headers."""
    time_stamp = str(int(time.time()))
    m2 = hashlib.md5()
    m2.update(time_stamp + APP_KEY)
    ubtSign = m2.hexdigest() + ' ' + time_stamp
    HEADER_PARA = {}
    HEADER_PARA["X-UBT-Sign"] = ubtSign
    HEADER_PARA['X-UBT-AppId'] = APP_ID
    HEADER_PARA['X-UBT-DeviceId'] = device_ID
    HEADER_PARA['ContenType'] = 'application/json'
    print('Header:%s', HEADER_PARA)
    return HEADER_PARA


def detect_new_version(module_name, ver, device_ID):
    """Detect the new version."""
    api_url = API_URL + 'version/upgradable?productName=YANSHEE' + '&moduleNames=' + module_name + '&versionNames=' + ver
    HEADER_PARA = create_header(device_ID)

    print('url:%s', api_url)
    try:
        http = urllib3.PoolManager(retries=urllib3.Retry(5, redirect=3))
        r = http.request('GET', api_url, headers=HEADER_PARA)
        print('http ret:%s content:%s', r.status, r.data)
        if len(r.data) < 10:
            print('You already upgraded to the latest version. Module: %s, Version: %s', module_name, ver)
            return ('error',)

        text = json.loads(r.data)
        name = text[0]['moduleName']
        if module_name != name:
            print 'Wrong module name. Please check the module name again'
            return ('error',)

        url = text[0]['packageUrl']
        md5 = text[0]['packageMd5']
        force = text[0]['isForced']
        version = text[0]['versionName']
        print('url:%s', url)
        print('md5:%s,version:%s', md5, version)
        if len(url) < 10:
            print 'Get wrong URL from OTA server.'
            return ('error',)
        return (url, md5, force, version)
    except Exception, err:
        print 'Try to detect the new version failed.', err
        return ('error',)


def download_file(url, md5, file_name, path):
    """Download the file from OTA server."""
    try:
        socket.setdefaulttimeout(30)
        local = os.path.join(path, file_name)
        print('local:%s,url:%s', local, url)
        urllib.urlretrieve(url, local, progress_rate)
        MD5_value = get_file_md5(path+'/'+file_name)
        print('MD5_value:%s', MD5_value)

        if MD5_value == md5:
            print 'Download Success'
            ret = True
        else:
            print('Download Failed(md5:%s:%s)', MD5_value, md5)
            ret = False
        return ret
    except Exception, err:
        print 'Error occur in downloading', err
        return False


def get_devid():
    """Device id format YANSHEE02+MAC."""
    cmd = "cat /etc/os-release | grep VERSION_ID| awk -F\\\" '{print $2}' "
    version = do_shell_cmd(cmd)
    print('os version is %s', version)
    if cmp(version, '9') == 0:
        mac = do_shell_cmd(
            "ifconfig  wlan0 | grep ether | awk '{print $2}' | awk -F: '{print $1$2$3$4$5$6}' | tr [a-z] [A-Z]")
        print('get_devid(os 9) mac:%s', mac)
    else:
        mac = do_shell_cmd("ifconfig  wlan0 | awk '/HWaddr/{print $NF}' | awk -F: '{print $1$2$3$4$5$6}' | tr [a-z] [A-Z]")
        print('get_devid mac:%s', mac)

    name = PRODUCT_NAME + mac
    return name


def get_robot_version(module_name):
    """Get the robot version."""
    version = do_shell_cmd("dpkg -l|grep " + module_name + "|awk '{print $3}'")
    result = 'v' + version
    return result.replace('-', '.')


def main():
    """Start to detect the new noobs."""
    devid = get_devid()
    version = get_robot_version(MODULE_ROBOT_NAME)
    while True:
        info = detect_new_version(MODULE_ROBOT_NAME, version, devid)
        if info[0] == 'error':
            time.sleep(30)
            continue
        elif info[2] is False:
            print "Detected a new version."
            time.sleep(6)
            break

        ret = download_file(info[0], info[1], NOOBS_FILE_NAME, curr_path)
        if ret is False:
            print "Download new version fail! Please check the network or\
            reboot the system."
            break
        time.sleep(30)
        # todo This continue can be deleted?
        continue


if __name__ == "__main__":
    main()
