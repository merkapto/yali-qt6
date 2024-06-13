piksemel --> import piksemel
--------
- yali/util.py
- yali/yalireadpiks.py
- yali/pisiiface.py
- tools/release-xml


comar --> import comar
-----
- yali/util.py

pisi --> import pisi.ui
----
- yali/gui/ScrCheckCD.py                    --> import pisi.ui
- yali/gui/ScrInstall_packageInstaller.py   --> import pisi.ui
- yali/gui/ScrInstall.py                    --> import pisi.ui
- yali/gui/ScrRescuePisi.py                 --> import pisi
- yali/gui/YaliDialog.py                    --> import pisi

pardus
------
- yali/util.py                          --> from pardus import diskutils, grubutils
- yali/flags.py                         --> from pardus.sysutils import get_kernel_option
- yali/storage/storageset.py            --> from pardus import fstabutils
- yali/storage/bootloader.py            --> from pardus import grubutils
- yali/storage/formats/filesystem.py    --> import pardus.sysutils
- yali/gui/ScrAdmin.py                  --> import pardus.xorg
- yali/gui/ScrRescuePassword.py         --> import pardus.xorg


parted --> import parted
------
- yali/storage/storageBackendHelpers.py     --> (Çözüm için py3parted paketi yüklenmelidir.)
- yali/storage/partitioning.py              --> (Çözüm için py3parted paketi yüklenmelidir.)


cmp()
-----
--> py2'de olup py3'te kaldırılan cmp() fonksiyonunu kendim yazdım.
- yali/storage/partitioning.py
- yali/storage/devicetree.py


block --> import block (python-pyblock var py2 için)
-----
- yali/storage/devicetree.py            --> ne olduğunu anlamadım
- yali/storage/devices/devicemapper.py
- yali/storage/devices/partition.py


pyaspects --> (python-pyaspects var py2 için)
---------
- yali/gui/aspects.py --> from pyaspects.meta import MetaAspect


pds --> ?
---
- yali/gui/ScrAdmin.py                      --> from pds.thread import PThread
- yali/gui/ScrDateTime.py                   --> from pds.gui import PMessageBox, MIDCENTER, CURRENT, OUT
- yali/gui/ScrInstall_packageInstaller.py   --> from pds.gui import PAbstractBox, BOTCENTER
- yali/gui/ScrInstall.py                    --> from pds.gui import PAbstractBox, BOTCENTER
- yali/gui/ScrNetwork.py                    --> import pds.container


Queue - Empty
-------------
- yali/gui/ScrInstall_packageInstaller.py   --> from Queue import Empty


!!!
maxLogicals (hataya sebep olabilecek değişken)
-----------
- yali/storage/partitioning.py --> satır 520'de maxLogicals değişkeni tanımlaması yorum satırı yapılmış ama dosya içinde aktif maxLogicals kıyaslamaları mevcut.