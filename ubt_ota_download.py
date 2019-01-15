"""
Copyright (c) 2019 by UBTECH.
All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys
import os
import time
import json
import hashlib
import urllib
import socket
import logging
import urllib3
import getopt


UPGRADE_URL = "https://upgrade.ubtrobot.com/v1/upgrade-rest/"
# UPGRADE_URL = "http://10.10.20.71:8032/v1/upgrade-rest/"
APP_ID = '500010015'
APP_KEY = '185ce49be88544da81741a01b1f1ea2c'

PRODUCT_NAME = 'YANSHEE03'
MODULE_ROBOT_NAME = 'ubt-yanshee-ros-linux'
FILE_ROBOT_INFO = 'upgrade_robot_info.txt'
MODULE_BLOCKLY_NAME = 'ubtedu-yansheeblockly'
FILE_BLOCKLY_INFO = 'upgrade_blockly_info.txt'
STR_FROM_VERSION = 'fromversion'
STR_TO_VERSION = 'toversion'
NOOBS_FILE_NAME = 'noobs'


class DownloadNoobsImage(object):
    """Download noobs image from OTA server.

    Parameters
    ----------
    url : type
        Description of parameter `url`.

    Attributes
    ----------
    __url : type
        Description of attribute `__url`.
    __logger : type
        Description of attribute `__logger`.

    """

    def __init__(self, url, module, logger):
        """Init DownloadNoobsImage class.

        Parameters
        ----------
        url : type
            Description of parameter `url`.

        Returns
        -------
        type
            Description of returned object.

        """
        super(DownloadNoobsImage, self).__init__()
        self.__url = url
        self.__module = module
        self.__logger = logger

    def progress_rate(self, block_num, block_size, total_size):
        """Get the progress rate.

        Parameters
        ----------
        block_num : type
            Already downloaded data block.
        block_size : type
            The data block size.
        total_size : type
            The remote file total size.

        Returns
        -------
        NA

        """
        percent = 100.0 * block_num * block_size / total_size
        self.__logger.info("Downloading progress. %s%%", int(percent))

    def download(self, url, target_md5, file_name, path):
        """Download the file from OTA server.

        Parameters
        ----------
        url : type
            Description of parameter `url`.
        target_md5 : type
            Description of parameter `md5`.
        file_name : type
            Description of parameter `file_name`.
        path : type
            Description of parameter `path`.

        Returns
        -------
        type
            Description of returned object.

        """
        try:
            socket.setdefaulttimeout(30)
            local_noobs_index = url.rfind('/')
            local_noobs = url[local_noobs_index+1:]

            local_noobs = os.path.join(path, local_noobs)
            self.__logger.debug('Try to download noobs from OTA server. file: %s, url:%s', local_noobs, url)
            urllib.urlretrieve(url, local_noobs, self.progress_rate)
            md5sum_value = self.get_file_md5(local_noobs)
            self.__logger.info('File is downloaded, md5sum: %s', md5sum_value)

            if md5sum_value == target_md5:
                self.__logger.info('Download success')
                ret = True
            else:
                self.__logger.info('Download noobs failed. \n \
                Downloaded file md5sum: %s \n \
                MD5 value from server: %s', md5sum_value, target_md5)
                ret = False
            return ret
        except IOError as err:
            self.__logger.debug('Error occur in downloading. %s', err)
            return False

    @classmethod
    def do_shell_cmd(self, cmd):
        """Execute bash cmd.

        Parameters
        ----------
        cmd : type
            Description of parameter `cmd`.

        Returns
        -------
        string
            return the bash result.

        """
        result = os.popen(cmd)
        return result.read().rstrip('\n')

    def get_file_md5(self, file_name):
        """Calc the md5 for a file.

        Parameters
        ----------
        file_name : type
            Description of parameter `file_name`.

        Returns
        -------
        type
            return the hex md5 value.

        """
        self.__logger = logging.getLogger(__name__)
        if not os.path.isfile(file_name):
            self.__logger.debug("Cannot find file:%s", file_name)
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

    def generate_http_header(self, device_ID):
        """Generate the HTTP header.

        Parameters
        ----------
        device_ID : type
            Description of parameter `device_ID`.

        Returns
        -------
        type
            Description of returned object.

        """
        time_stamp = str(int(time.time()))
        m2 = hashlib.md5()
        m2.update(time_stamp + APP_KEY)
        ubtSign = m2.hexdigest() + ' ' + time_stamp
        HEADER_PARA = {}
        HEADER_PARA["X-UBT-Sign"] = ubtSign
        HEADER_PARA['X-UBT-AppId'] = APP_ID
        HEADER_PARA['X-UBT-DeviceId'] = device_ID
        HEADER_PARA['ContenType'] = 'application/json'
        self.__logger.debug('Header:%s', HEADER_PARA)
        return HEADER_PARA

    def detect_new_version(self, module_name, ver, device_ID):
        """Check if there is a new version.

        Parameters
        ----------
        module_name : type
            Description of parameter `module_name`.
        ver : type
            Description of parameter `ver`.
        deviceself.__logger = logging.getLogger(__name__)_ID : type
            Description of parameter `device_ID`.

        Returns
        -------
        type
            True, (url, md5, force, version)     means there is a new version
            False, (url, md5, force, version)    means check new version failed

        """
        url = self.__url
        url += ('version/upgradable?productName=YANSHEE'
                '&moduleNames=')
        url += module_name
        url += '&versionNames='
        url += ver
        api_url = (url)
        HEADER_PARA = self.generate_http_header(device_ID)

        self.__logger.debug('url:%s', api_url)
        try:
            http = urllib3.PoolManager(retries=urllib3.Retry(5, redirect=3))
            r = http.request('GET', api_url, headers=HEADER_PARA)
            self.__logger.debug('http ret:%s content:%s', r.status, r.data)
            if len(r.data) < 10:
                self.__logger.debug(
                    'You already upgraded to the '
                    'latest version. Module: %s, Version: %s',
                    module_name, ver)
                return False, ('error',)

            text = json.loads(r.data)
            name = text[0]['moduleName']
            if module_name != name:
                self.__logger.debug('Wrong module name.'
                                    'Please check the module name again.')
                return False, ('error',)

            url = text[0]['packageUrl']
            md5 = text[0]['packageMd5']
            force = text[0]['isForced']
            version = text[0]['versionName']
            self.__logger.debug('Get http response from OTA server. '
                                'url: %s'
                                'md5: %s'
                                'version: %s',
                                url,
                                md5,
                                version)
            if len(url) < 10:
                self.__logger.debug('Get wrong URL from OTA server.')
                return ('error',)
            return True, (url, md5, force, version)
        except IOError as err:
            self.__logger.error('Try to detect the new version failed. %s',
                                err)
            return False, ('error',)

    def get_devid(self):
        """Device id format YANSHEE02+MAC."""
        cmd = ('ifconfig | grep wlan0 | wc -l')
        ret = self.do_shell_cmd(cmd)
        if ret == 0:
            return "YANSHEE_TEST"
        cmd = ('''cat /etc/os-release | grep VERSION_ID| '''
               '''awk -F\\\" '{print $2}' ''')
        version = self.do_shell_cmd(cmd)
        self.__logger.debug('os version is %s', version)
        if cmp(version, '9') == 0:
            mac = self.do_shell_cmd(
                '''ifconfig  wlan0 | grep ether | awk '{print $2}' |'''
                '''awk -F: '{print $1$2$3$4$5$6}' | tr [a-z] [A-Z]''')
        else:
            mac = self.do_shell_cmd('''ifconfig  wlan0 | '''
                                    '''awk '/HWaddr/{print $NF}' | '''
                                    '''awk -F: '{print $1$2$3$4$5$6}' | '''
                                    '''tr [a-z] [A-Z]''')

        self.__logger.debug('Get MAC address: %s', mac)
        name = PRODUCT_NAME + mac
        return name

    def get_robot_version(self, module_name):
        """Get the robot version.

        Parameters
        ----------
        module_name : type
            Description of parameter `module_name`.

        Returns
        -------
        type
            Description of returned object.

        """
        version_file = "/etc/ubt_version.txt"
        if os.access(version_file, os.R_OK):
            cmd = "cat" + version_file + " |grep " + module_name + "cut -d\" \" -f2"
            version = self.do_shell_cmd(cmd)
            result = 'v' + version
            return result.replace('-', '.')
        else:
            return "v1.3.5"

    def run(self):
        """Start to detect the new noobs."""
        devid = self.get_devid()
        version = self.get_robot_version(self.__module)
        while True:
            ret, info = self.detect_new_version(self.__module, version, devid)
            if ret is True:
                ret = self.download(info[0], info[1], self.__module, '.')
                if ret is False:
                    self.__logger.info('Download new version failed!'
                                       'I am going to try it in 5 seconds '
                                       'later.')
                    time.sleep(5)
                else:
                    self.__logger.info('Download noobs success. ')
                    break

    __url = ""
    __logger = None


def usage():
    """Print the usage.

    Returns
    -------
    NA.

    """
    print (
        'python download_image.pyc -u <remote url> -m <module name>'
        '   -u, --url   Upgrade url.'
        '   -m, --module        The upgrade module.'
        'Please note, '
        'if the -u and -m is not provited, '
        'the default value should be as below:'
        '   python download_image.pyc '
        '-u http://10.10.20.71:8032/v1/upgrade-rest/ -m noobs'
    )


if __name__ == "__main__":

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = UPGRADE_URL
    module = NOOBS_FILE_NAME

    try:
        options, args = getopt.getopt(sys.argv[1:],
                                      "hu:m:", ["help", "url=", "module="])
    except getopt.GetoptError:
        sys.exit()
    for name, value in options:
        if name in ("-h", "--help"):
            usage()
        if name in ("-u", "--url"):
            url = value
        if name in ("-m", "--module"):
            module = value

    logger_name = "NOOBS Upgrade"
    logger = logging.getLogger(logger_name)
    logging.basicConfig(level=logging.INFO)

    download = DownloadNoobsImage(url, module, logger)
    download.run()
