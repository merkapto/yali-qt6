#!/usr/bin/env python
#
# Copyright (C) 2005-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys
import glob
import shutil
# import sipconfig    #py2
# import sipbuild   #py3
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
from distutils.cmd import Command
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install import install
from distutils.spawn import find_executable  # , spawn

I18N_DOMAIN = "yali"
I18N_LANGUAGES = ["tr", "en", "nl", "it", "fr", "de", "pt_BR", "es",
                  "pl", "ca", "sv", "hu", "ru", "hr"]


# WARNING: update_messages and release_messages run with python3
def update_messages():
    files = glob.glob("build/lib.linux-x86_64-2.7/yali/**/*.py",
                      recursive=True)
    # print(files)

    for lng in I18N_LANGUAGES:
        print(lng)
        # os.system("pylupdate5 -translate-function _ {files} -ts lang/{lang}.ts\
        os.system("pylupdate6 -translate-function _ {files} -ts lang/{lang}.ts\
            ".format(files=" ".join(files), lang=lng))


def release_messages():
    ts_files = glob.glob1("lang", "*.ts")
    ts_files = "lang/" + " lang/".join(ts_files)

    # os.system("lrelease {}".format(ts_files))
    os.system("lrelease-qt6 {}".format(ts_files))


def qt_ui_files():
    ui_files = "yali/gui/Ui/*.ui"
    return glob.glob(ui_files)


def py_file_name(ui_file):
    return os.path.splitext(ui_file)[0] + '.py'


class YaliBuild(build):
    def changeQRCPath(self, ui_file):
        py_file = py_file_name(ui_file)
        lines = open(py_file, "r").readlines()
        replaced = open(py_file, "w")
        for line in lines:
            if line.find("data_rc") != -1:
                continue
            replaced.write(line)

    def compileUI(self, ui_file):
        # pyqt_configuration = sipconfig.Configuration()  #py2
        # pyqt_configuration = sipbuild.configurable.Configurable.configure()   #py3
        # pyuic_exe = find_executable(
        #     'py2uic5', pyqt_configuration.default_bin_dir)
        # if not pyuic_exe:
        #     pyuic_exe = find_executable('py2uic5')

        pyuic_exe = find_executable('pyuic6')
        cmd = [pyuic_exe, ui_file, '-o']
        cmd.append(py_file_name(ui_file))
        # cmd.append("-g \"yali\"")
        os.system(' '.join(cmd))

    def run(self):
        release_messages()
        for ui_file in qt_ui_files():
            print(ui_file)
            self.compileUI(ui_file)
            self.changeQRCPath(ui_file)
        build.run(self)


class YaliClean(clean):

    def run(self):
        clean.run(self)

        for ui_file in qt_ui_files():
            ui_file = py_file_name(ui_file)
            if os.path.exists(ui_file):
                os.unlink(ui_file)

        if os.path.exists("build"):
            shutil.rmtree("build")


class YaliUninstall(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        yali_dir = os.path.join(get_python_lib(), "yali")
        if os.path.exists(yali_dir):
            print("removing: ", yali_dir)
            shutil.rmtree(yali_dir)

        conf_dir = "/etc/yali"
        if os.path.exists(conf_dir):
            print("removing: ", conf_dir)
            shutil.rmtree(conf_dir)

        if os.path.exists("/usr/share/applications/yali.desktop"):
            print("removing: rest of installation")
            os.unlink("/usr/share/applications/yali.desktop")
        os.unlink("/usr/bin/yali-bin")
        os.unlink("/usr/bin/start-yali")
        os.unlink("/usr/bin/bindYali")
        os.unlink("/lib/udev/rules.d/70-yali.rules")


class I18nInstall(install):
    def run(self):
        install.run(self)

        for lang in I18N_LANGUAGES:
            print("Installing '%s' translations..." % lang)
            os.popen("msgfmt po/%s.po -o po/%s.mo" % (lang, lang))
            if not self.root:
                self.root = "/"
            destpath = os.path.join(
                self.root, "usr/share/locale/%s/LC_MESSAGES" % lang)
            try:
                os.makedirs(destpath)
            except Exception:
                pass
            shutil.copy("po/%s.mo" % lang,
                        os.path.join(destpath, "%s.mo" % I18N_DOMAIN))


if "update_messages" in sys.argv:
    update_messages()
    sys.exit(0)
elif "release_messages" in sys.argv:
    release_messages()
    sys.exit(0)

setup(
    name="yali",
    version="3.0.2",
    description="YALI (Yet Another Linux Installer)",
    long_description="Pisi Linux System Installer.",
    license="Latest GNU GPL version",
    author="Pisi Linux Developers",
    author_email="admins@pisilinux.org",
    url="https://github.com/pisilinux/project",
    packages=['yali', 'yali.gui', 'yali.gui.Ui', 'yali.storage',
              'yali.storage.devices', 'yali.storage.formats',
              'yali.storage.library'],
    data_files=[('/etc/yali', glob.glob("conf/*")),
                ('/lib/udev/rules.d', ["70-yali.rules"]),
                ('/usr/share/applications', ["yali.desktop"]),
                ('/usr/share/yali/lang', glob.glob("lang/*.qm"))],
    scripts=['yali-bin', 'start-yali', 'bindYali'],
    ext_modules=[Extension('yali._sysutils',
                           sources=['yali/_sysutils.c'],
                           libraries=["ext2fs"],
                           extra_compile_args=['-Wall'])],
    cmdclass={
        'build': YaliBuild,
        'clean': YaliClean,
        'install': I18nInstall,
        'uninstall': YaliUninstall
    }
)
