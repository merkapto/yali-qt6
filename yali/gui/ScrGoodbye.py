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
import sys
import time
try:
    from PyQt6.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap

import yali.util
import yali.context as ctx
import yali.postinstall
from yali.gui import ScreenWidget
from yali.gui.YaliDialog import InfoDialog, QuestionDialog
from yali.gui.Ui.goodbyewidget import Ui_GoodByeWidget

class Widget(QWidget, ScreenWidget):
    name = "goodbye"

    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_GoodByeWidget()
        self.ui.setupUi(self)

    def shown(self):
        ctx.mainScreen.disableNext()
        ctx.mainScreen.disableBack()

        ctx.interface.informationWindow.update(_("General", "Running post-install operations..."))
        self.runOperations()
        ctx.mainScreen.pds_helper.toggleHelp()
        self.ui.label.setPixmap(QPixmap(":/gui/pics/goodbye.png"))
        ctx.interface.informationWindow.hide()
        ctx.mainScreen.enableNext()

    def execute(self):
        ctx.mainScreen.disableNext()

        if not ctx.flags.install_type == ctx.STEP_FIRST_BOOT:
            ctx.logger.debug("Show restart dialog.")
            restart = True
            if ctx.flags.live:
                result = QuestionDialog(_("General", "Restart"), _("General", "Press <b>Restart</b> to restart the computer."))
                if result == "no": restart = False
            else:
                InfoDialog(_("General", "Press <b>Restart</b> to restart the computer."), _("General", "Restart"))

            if restart:
                ctx.interface.informationWindow.update(_("General", "<b>Please wait while restarting...</b>"))
                ctx.logger.debug("Trying to eject the CD.")
                yali.util.eject()
                ctx.logger.debug("Yali, reboot calling..")
                ctx.mainScreen.processEvents()
                time.sleep(4)
                yali.util.reboot()
            else:
                sys.exit(0)
        else:
            sys.exit(0)

    def runOperations(self):
        postInstallOperations = []

        if not (ctx.flags.install_type == ctx.STEP_RESCUE or ctx.flags.install_type == ctx.STEP_FIRST_BOOT):
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Setting timezone..."), yali.postinstall.setupTimeZone))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Migrating Xorg configuration..."), yali.postinstall.setKeymapLayout))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Copying repository index..."), yali.postinstall.setupRepoIndex))

        if ctx.flags.install_type == ctx.STEP_DEFAULT or ctx.flags.install_type == ctx.STEP_BASE or ctx.flags.install_type == ctx.STEP_FIRST_BOOT:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Setting hostname..."), yali.postinstall.setHostName))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Setting root password..."), yali.postinstall.setAdminPassword))

        if ctx.flags.install_type == ctx.STEP_RESCUE and ctx.installData.rescueMode == ctx.RESCUE_PASSWORD:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Resetting user password..."), yali.postinstall.setUserPassword))

        if ctx.flags.install_type == ctx.STEP_BASE:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Setup First-Boot..."), yali.postinstall.setupFirstBoot))

        if ctx.flags.install_type == ctx.STEP_FIRST_BOOT:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Teardown First-Boot..."), yali.postinstall.teardownFirstBoot))


        if ctx.flags.install_type == ctx.STEP_FIRST_BOOT or ctx.flags.install_type == ctx.STEP_DEFAULT:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Adding users..."), yali.postinstall.setupUsers))

        if (ctx.flags.install_type == ctx.STEP_BASE or ctx.flags.install_type == ctx.STEP_DEFAULT or \
            (ctx.flags.install_type == ctx.STEP_RESCUE and ctx.installData.rescueMode == ctx.RESCUE_GRUB)) and \
            ctx.bootloader.stage1Device:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Installing bootloader..."), yali.postinstall.installBootloader))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Writing bootloader config..."), yali.postinstall.writeBootLooder))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Stopping to D-Bus..."), yali.util.stop_dbus))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Teardown storage subsystem..."), yali.postinstall.teardownStorage))
        elif ctx.flags.install_type == ctx.STEP_BASE or ctx.flags.install_type == ctx.STEP_DEFAULT:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Writing bootloader config..."), yali.postinstall.writeBootLooder))

        if ctx.flags.install_type == ctx.STEP_DEFAULT or ctx.flags.install_type == ctx.STEP_BASE or ctx.flags.install_type == ctx.STEP_RESCUE:
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Stopping to D-Bus..."), yali.util.stop_dbus))
            postInstallOperations.append(yali.postinstall.Operation(_("General", "Teardown storage subsystem..."), yali.postinstall.teardownStorage))

        for operation in postInstallOperations:
            if not operation.status:
                operation.run()
