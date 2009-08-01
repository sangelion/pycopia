#!/usr/bin/python2.4
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab


import sys
import os

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension 
from glob import glob

NAME = "pycopia-utils"
VERSION = "1.0"
REVISION="$Revision$"

DNAME = NAME.split("-", 1)[-1]
EGGNAME = "%s-%s.dev_r%s" % (NAME.replace("-", "_"), VERSION, REVISION[1:-1].split(":")[-1].strip())

SCRIPTS = []
EXTENSIONS = []

if sys.platform == "darwin":
    EXTENSIONS.append(Extension('pycopia.itimer', ['pycopia.itimer.pyx']))
elif sys.platform == "linux2":
    EXTENSIONS.append(Extension('pycopia.itimer', ['pycopia.itimer.pyx'], libraries=["rt"]))
    SCRIPTS = glob("bin/*")


if sys.version_info[:2] < (2, 5):
# The readline and mmap modules here are copies of the Python 2.5 modules.
# They can also be used with previous versions of Python (as far as I can
# tell).  They provide some new features and bug fixes that Pycopia needs
# to function properly.

    readline = Extension('readline', ['readline.c'],
                    define_macros=[("HAVE_RL_COMPLETION_MATCHES", None)],
                    library_dirs=['/usr/lib/termcap'],
                   libraries=["readline", "ncurses"])
    EXTENSIONS.append(readline)

    mmap = Extension('mmap', ['mmapmodule.c'],)
    EXTENSIONS.append(mmap)


setup (name=NAME, version=VERSION,
    namespace_packages = ["pycopia"],
    packages = ["pycopia"],
    scripts = SCRIPTS,
    ext_modules = EXTENSIONS,
    install_requires = ['pycopia-aid>=1.0.dev-r138,==dev'],
    dependency_links = [
            "http://www.pycopia.net/download/"
                ],
    test_suite = "test.UtilsTests",

    description = "Pycopia helper programs.",
    long_description = """Some functions of Pycopia require root
    privileges. This module contains some helper programs so that Pycopia
    scripts can run as non-root, but still perform some functions that
    require root (e.g. open ICMP socket, SNMP trap port, and syslog port). 
    It also includes the Python 2.5 readline module for older Pythons.
    """,
    license = "LGPL",
    author = "Keith Dart",
    author_email = "keith@dartworks.biz",
    keywords = "pycopia framework ping",
    url = "http://www.pycopia.net/",
    download_url = "http://pycopia.googlecode.com/svn/trunk/%s#egg=%s" % (DNAME, EGGNAME),
    #download_url = "ftp://ftp.pycopia.net/pub/python/%s.%s.tar.gz" % (NAME, VERSION),
    classifiers = ["Operating System :: POSIX", 
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Topic :: System :: Networking :: Monitoring",
                   "Intended Audience :: Developers"],
)

def build_tools():
    savedir = os.getcwd()
    os.chdir("src")
    try:
        os.system("sh configure")
        os.system("make")
        os.system("make install")
        os.system("make sinstall")
    finally:
        os.chdir(savedir)


# unlinks the orignal modules, since the new ones are installed into
# site-packages.
def unlink_old_modules():
    pythonver = "%s.%s" % tuple(sys.version_info[:2])
    for name in ("readline", "mmap"):
        try:
            os.unlink("%s/lib/python%s/lib-dynload/%s.so" % (sys.prefix, pythonver, name))
        except OSError:
            pass


if sys.platform == "linux2":
    if os.getuid() == 0 and sys.argv[1] == "install":
        print "Installing SUID helpers."
        try:
            build_tools()
        except:
            ex, val, tb = sys.exc_info()
            print >>sys.stderr, "Could not build helper programs:"
            print >>sys.stderr, "%s (%s)" % (ex, val)

        if sys.version_info[:2] < (2, 5):
            unlink_old_modules()
    else:
        print >>sys.stderr, "You must run 'setup.py install' as root to install helper programs."

