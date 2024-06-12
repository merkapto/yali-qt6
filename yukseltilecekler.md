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
- yali/storage/bootloader.py    --> from pardus import grubutils


parted --> import parted
------
- yali/storage/storageBackendHelpers.py     --> (Çözüm için py3parted paketi yüklenmelidir.)
- yali/storage/partitioning.py              --> (Çözüm için py3parted paketi yüklenmelidir.)


cmp()
-----
--> py2'de olup py3'te kaldırılan cmp() fonksiyonunu kendim yazdım.
- yali/storage/partitioning.py
- yali/storage/devicetree.py


block --> import block
-----
- yali/storage/devicetree.py    --> ne olduğunu anlamadım


!!!
maxLogicals (hataya sebep olabilecek değişken)
-----------
- yali/storage/partitioning.py --> satır 520'de maxLogicals değişkeni tanımlaması yorum satırı yapılmış ama dosya içinde aktif maxLogicals kıyaslamaları mevcut.