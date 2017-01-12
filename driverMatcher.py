#!/usr/bin/env python3

import platform
import getpass
from cardsList import *
import os

DISTROS = [
    'arch',
    'ubuntu',
    'fedora',
    'gentoo'
]

VENDORS = [
    'NVIDIA Corporation',
    'Intel Corporation',
    'Advanced Micro Devices, Inc. [AMD/ATI]'
]

USERNAME = getpass.getuser()
# AMD vendor: 'Advanced Micro Devices, Inc. [AMD/ATI]'

def get_distro():
    return platform.linux_distribution()[0]

def _is_optimus(gpu1, gpu2): # returns true if gpu1 is intel and gpu2 is nvidia or vice versa
    if gpu1 == 'Intel Corporation':
        if gpu2 == 'NVIDIA Corporation':
            return True
        else:
            return False
    elif gpu1 == "NVIDIA Corporation":
        if gpu2 == "Intel Corporation":
            return True
        else:
            return False
    else:
        return False

def _is_intelamd(gpu1, gpu2):
    #return False # DONE: get output of lspci with amd cards to actually implement this
    if gpu1 == 'Intel Corporation':
        if gpu2 == 'Advanced Micro Devices, Inc. [AMD/ATI]':
            return True
        else:
            return False
    elif gpu1 == 'Advanced Micro Devices, Inc. [AMD/ATI]':
        if gpu2 == "Intel Corporation":
            return True
        else:
            return False
    else:
        return False

def get_correct_drivers(hw_l, distro): # TODO: add cases for bumblebee with legacy NVIDIA drivers
    current_driver_config = {
        'distro': distro,
        'driver': None
    }
    if len(hw_l) > 1:
        if _is_optimus(hw_l[0][0], hw_l[1][0]):
            current_driver_config['driver']='bumblebee'
        elif _is_intelamd(hw_l[0][0], hw_l[1][0]): # TODO: implement prime
            current_driver_config['driver']='intelamd'
    else:
        if hw_l[0][0] == 'NVIDIA Corporation':
            if hw_l[0][1] in NVIDIA_LEGACY_340XX_CARDS:
                current_driver_config['driver']='nvidia340xx'
            elif hw_l[0][1] in NVIDIA_LEGACY_304XX_CARDS:
                current_driver_config['driver']='nvidia304xx'
            else:
                current_driver_config['driver']='nvidia'
        elif hw_l[0][0] == 'Intel Corporation':
            current_driver_config['driver']='intel'
        elif hw_l[0][0] == 'Advanced Micro Devices, Inc. [AMD/ATI]':
            current_driver_config['driver']='amdgpu'
    return current_driver_config

def get_packages(config_dict):

    hw_l = [
        [
            config_dict['gpu1_vendor'],
            config_dict['gpu1_model']
        ]
    ]
    if config_dict['gpu2_model']:
        hw_l.append([
            config_dict['gpu2_vendor'],
            config_dict['gpu2_model']
        ])

    c_dri=get_correct_drivers(hw_l, config_dict['distro'])
    return {
        'packages': drivers_dict[c_dri['driver']][c_dri['distro']],
        'driver': c_dri['driver']
    }

def run_post_install_actions(actions):
    for i in actions:
        os.system(i)

drivers_dict={
    'nvidia': {
        'arch': [
            'nvidia',
            'nvidia-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
            'nvidia-settings'
        ],
        'ubuntu1604': [
            'nvidia-367',
            'vdpau-driver-all',
            'libvdpau1',
            'libxnvctrl0',
            'libcuda1',
            'nvidia-settings'
        ]
        # distro specific package names
    },
    'nvidia340xx': {
        'arch': [
            'nvidia-340xx',
            'nvidia-340xx-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
            'nvidia-settings'
        ],
        'ubuntu1604': [
            'nvidia-340-updates',
            'vdpau-driver-all',
            'libvdpau1',
            'libxnvctrl0',
            'libcuda1-340-updates',
            'nvidia-settings'
        ]
    },
    'nvidia304xx': {
        'arch': [
            'nvidia-304xx',
            'nvidia-304xx-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
            'nvidia-settings'
        ],
        'ubuntu1604': [
            'nvidia-304-updates',
            'vdpau-driver-all',
            'libvdpau1',
            'libxnvctrl0',
            'libcuda1-304-updates',
            'nvidia-settings'
        ]
    },
    'nvidiaprime': {
        'ubuntu1604': [
            'nvidia-340-updates',
            'vdpau-driver-all',
            'libvdpau1',
            'libxnvctrl0',
            'libcuda1-340-updates',
            'nvidia-settings',

        ]
    },
    'bumblebee': { # inherits nvidia(or nvidia legacy) and intel
        'arch': [
            'bumblebee',
            'mesa',
            'nvidia',
            #'nvidia-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
            'nvidia-settings',
            'xf86-video-intel',
            'mesa-libgl',
            'libva-intel-driver',
            'libvdpau-va-gl'
        ]
    },
    'nouveau': {
        'arch': [
            'xf86-video-nouveau',
            'mesa-libgl',
            'libva-vdpau-driver',
            'mesa-vdpau'
        ]
    },
    'intel': {
        'arch': [
            'xf86-video-intel',
            'mesa-libgl',
            'libva-intel-driver',
            'libvdpau-va-gl'
        ],
        'ubuntu1604': [
            'xserver-xorg-video-intel',
        ],
    },
    'amdgpu': {
        'arch': [
            'xf86-video-amdgpu',
            'mesa-libgl',
            'libva-mesa-driver',
            'mesa-vdpau'
        ],
    },
    'intelamd': {
        'arch': [
            'xf86-video-amdgpu',
            'xf86-video-intel',
            'mesa-libgl',
            'libva-mesa-driver',
            'mesa-vdpau'
        ],
    }
    #'amdgpupro': {
    #
    #}
    'ati': {
        'arch': [
            'xf86-video-ati',
            'mesa-libgl',
            'libva-mesa-driver',
            'mesa-vdpau'
        ]
    }
}

post_install_actions = {
    'bumblebee': {
        'arch': [
            'if groups '+ USERNAME +' | grep &>/dev/null \"\\bbumblebee\\b\"; then true; else pkexec gpasswd -a '+ USERNAME +' bumblebee; fi',
            'pkexec systemctl enable bumblebeed.service'
        ]
    },
    # 'intelamd' # Not necessary
    ## xrandr --setprovideroffloadsink radeon Intel
    # From the Arch Wiki
    # This setting is no longer necessary when using the default intel/modesetting driver from the official repos, as they have DRI3 enabled by default and will therefore automatically make these assignments. Explicitly setting them again does no harm, though.
}
