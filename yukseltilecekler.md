piksemel --> import piksemel
--------
- yali/util.py
- yali/yalireadpiks.py
- yali/pisiiface.py


comar --> import comar
-----
- yali/util.py


pardus
------
- yali/util.py                  --> from pardus import diskutils, grubutils
- yali/flags.py                 --> from pardus.sysutils import get_kernel_option
- yali/storage/storageset.py    --> from pardus import fstabutils


parted --> import parted
------
- yali/storage/storageBackendHelpers.py (Çözüm için py3parted paketi yüklenmelidir.)