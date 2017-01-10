#!/usr/bin/env python3
import gi
gi.require_version("PackageKitGlib", "1.0")
from gi.repository import PackageKitGlib as Pkit

def _do_nothing(*args):
    pass

def _get_pkg_id(name):
    t = Pkit.Task()
    result = t.resolve_sync(False, [name,], None, _do_nothing, None)
    pkg_arr = result.get_package_array()
    if len(pkg_arr) > 1:
        raise ValueError('Package array contains more than 1 package')
        return False
    elif len(pkg_arr) < 1:
        raise ValueError('Package array is empty: no matches found')
        return False
    else:
        return pkg_arr[0].get_id()

def install_pkg(name):
    try:
        pkg_id = _get_pkg_id(name)
        cl = Pkit.Client()
        cl.install_packages(False, [pkg_id,], None, _do_nothing, None)
        return True
    except:
        print('Error installing', name)
        return False

def remove_pkg(name):
    try:
        pkg_id = _get_pkg_id(name)
        cl = Pkit.Client()
        cl.remove_packages(False, [pkg_id,], True, False, None, _do_nothing, None)
        return True
    except:
        print('Error removing', name)
        return False
