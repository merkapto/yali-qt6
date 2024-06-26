# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
import os
import codecs
try:
    from PyQt6.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import  QTextBrowser
from PyQt6.QtCore import pyqtSignal

import yali.context as ctx
from yali.gui import ScreenWidget, GUIError
from yali.gui.YaliDialog import Dialog
from yali.gui.Ui.license import Ui_LicenseWidget

class Widget(QWidget, ScreenWidget):
    name = "license"
    finished = pyqtSignal()
    def __init__(self):
        super(QWidget, self).__init__()
        self.ui = Ui_LicenseWidget()
        self.ui.setupUi(self)

        self.ui.accept.toggled[bool].connect(self.slotAcceptToggled)

        self.ui.disclamer.linkActivated[str].connect(self.showGPL)


    def slotAcceptToggled(self, state):
        if state:
            ctx.mainScreen.enableNext()
        else:
            ctx.mainScreen.disableNext()

    def showGPL(self):
        dialog = Dialog("GPL", LicenseBrowser(self), self)
        dialog.resize(500, 400)
        dialog.exec_()

    def shown(self):
        #ctx.mainScreen.disableBack()
        if self.ui.accept.isChecked():
            ctx.mainScreen.enableNext()
        else:
            ctx.mainScreen.disableNext()
        ctx.mainScreen.processEvents()
        
    def destroyed(self):
        self.finished.emit()

class LicenseBrowser(QTextBrowser):

    def __init__(self, *args):
        QTextBrowser.__init__(self, *args)

        self.setStyleSheet("background:white;color:black;")

        try:
            self.setText(codecs.open(self.loadFile(), "r", "UTF-8").read())
        # except Exception, msg:
        except Exception as msg:
            raise GUIError(msg)

    def loadFile(self):
        license = os.path.join(ctx.consts.source_dir, "license", "license-%s.txt" % ctx.lang)

        if not os.path.exists(license):
            license = os.path.join(ctx.consts.source_dir, "license/license-en.txt")

        if os.path.exists(license):
            return license
        raise GUIError(_("General", "License text could not be found."))


