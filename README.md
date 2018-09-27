# Yanshee online upgrading
Yanshee online upgrading tool can upgrade the NOOBS image without format the SD card. When this tool upgraded the image, please reboot the system. The new system will install automatically.
## Steps
1. Get the DEB package.

```bash
pi@raspberrypi:~ $ ls
Desktop    Downloads  Music     Public        release    Videos           
Documents  MagPi      Pictures  python_games  Templates   yanshee-update-1.0.1_1-1_all.deb
pi@raspberrypi:~ $ sudo dpkg -i yanshee-update-1.0.1_1-1_all.deb
```

2. Check if the upgrade tool is installed.

```bash
pi@raspberrypi:~ $ dpkg -l | grep yanshee-update
ii  yanshee-update-1.0.1                      1-1                               all          <insert up to 60 chars description>
```

3. Get the md5sum of the new NOOBS image for the valid check.

```bash
pi@raspberrypi:~ $ cat md5sum
fa55f6bf2f3cc7a410bc1ec833b29881
```
4. Download the NOOBS image, the file should be a tar.gz package. And execute upgrade tool as below. Please remember to use root or sudo to get the priviage

```bash
pi@raspberrypi:~ $ sudo bash upgrade noobs.tar.gz fa55f6bf2f3cc7a410bc1ec833b29881
+ NOOBS_NEWIMAGES=noobs.tar.gz
+ NOOBS_NEWIMAGES_MD5SUM=fa55f6bf2f3cc7a410bc1ec833b29881
+ NOOBS_NEWIMAGES_TMPDIR=/tmp/noobsfs
+ MOUNT_NOOBSFS=/mnt/noobsfs
+ MOUNT_NOOBSFS_IMAGES=/mnt/noobsfs/os
+ '[' 2 -ne 2 ']'
+ main
+ local md5_valid=0
+ check_md5sum
+ local rc=0
++ md5sum noobs.tar.gz
...
Start to copy files to sd card.
+ cp -r /tmp/noobsfs/bcm2708-rpi-0-w.dtb /tmp/noobsfs/bcm2708-rpi-b.dtb /tmp/noobsfs/bcm2708-rpi-b-plus.dtb /tmp/noobsfs/bcm2708-rpi-cm.dtb /tmp/noobsfs/bcm2709-rpi-2-b.dtb /tmp/noobsfs/bcm2710-rpi-3-b.dtb /tmp/noobsfs/bcm2710-rpi-cm3.dtb /tmp/noobsfs/bootcode.bin /tmp/noobsfs/BUILD-DATA /tmp/noobsfs/defaults /tmp/noobsfs/flavours.json /tmp/noobsfs/INSTRUCTIONS-README.txt /tmp/noobsfs/os /tmp/noobsfs/overlays /tmp/noobsfs/recovery7.img /tmp/noobsfs/recovery.cmdline /tmp/noobsfs/recovery.elf /tmp/noobsfs/RECOVERY_FILES_DO_NOT_EDIT /tmp/noobsfs/recovery.img /tmp/noobsfs/recovery.rfs /tmp/noobsfs/riscos-boot.bin /mnt/noobsfs/
+ unmount_noobsfs
+ umount /mnt/noobsfs
+ rm -r /mnt/noobsfs
+ rm -rf /tmp/noobsfs
+ echo 'Upgrade to new version success. Please reboot the system, and try to install new NOOBS images.'
Upgrade to new version success. Please reboot the system, and try to install new NOOBS images.

```

5. Reboot the system

```bash
pi@raspberrypi:~ $ sudo reboot
```
