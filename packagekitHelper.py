#!/usr/bin/env python3
import gi
gi.require_version("PackageKitGlib", "1.0")
from gi.repository import PackageKitGlib as Pkit
import threading

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

def do_async(func, args):
    t=threading.Thread(
        group=None,
        target=func,
        name=None,
        args=args
    )
    t.start()
    return t

def install_pkg(name):
    try:
        pkg_id = _get_pkg_id(name)
        if pkg_id[-9:] == 'installed':
            print('Package already installed (%s)' % name)
            return 1
        cl = Pkit.Client()
        cl.install_packages(False, [pkg_id,], None, _do_nothing, None)
        return 0
    except:
        print('Error installing', name)
        return 2

def remove_pkg(name):
    try:
        pkg_id = _get_pkg_id(name)
        cl = Pkit.Client()
        cl.remove_packages(False, [pkg_id,], True, False, None, _do_nothing, None)
        return True
    except:
        print('Error removing %s. Aborting' % name)
        return False

def install_multi_pkgs(name_list, thread_return=None):
    try:
        pkg_list=[]
        for n in name_list:
            pkg_id=_get_pkg_id(n)
            if pkg_id[-9:] == 'installed':
                print('Package already installed (%s). Skipping' % n)
            else:
                pkg_list.append(pkg_id)
        if len(pkg_list) > 0:
            cl = Pkit.Client()
            cl.install_packages(False, pkg_list, None, _do_nothing, None)
            if thread_return:
                thread_return[0]=True
            return True
        else:
            print('All packages already installed')
            if thread_return:
                thread_return[0]=True
            return True
    except:
        print('Error installing packages. Aborting')
        if thread_return:
            thread_return[0]=False
        return False
