#!/usr/bin/env python3

import platform
import getpass

USERNAME=getpass.getuser()
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

def _is_prime(gpu1, gpu2):
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

def get_correct_drivers(hw_l):
    current_driver_config = {
        'distro': get_distro(),
        'driver': None
    }
    if len(hw_l) > 1:
        if _is_optimus(hw_l[0][0], hw_l[1][0]):
            current_driver_config['driver']='bumblebee'
        elif _is_prime(hw_l[0][0], hw_l[1][0]):
            pass
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

def get_packages(hw_l):
    c_dri=get_correct_drivers(hw_l)
    return drivers_dict[c_dri['driver']][c_dri['distro']]

drivers_dict={
    'nvidia': {
        'arch': [
            'nvidia',
            'nvidia-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
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
        ]
    },
    'nvidia304xx': {
        'arch': [
            'nvidia-304xx',
            'nvidia-304xx-libgl',
            'nvidia-utils',
            'libva-vdpau-driver',
            'nvidia-settings'
        ]
    },
    'bumblebee': { # inherits nvidia(or nvidia legacy) and intel
        'arch': [
            'bumblebee',
            'mesa',
            'nvidia',
            'nvidia-libgl',
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
        ]
    },
    'amdgpu': {
        'arch': [
            'xf86-video-amdgpu',
            'mesa-libgl',
            'libva-mesa-driver',
            'mesa-vdpau'
        ]
    },
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
            'gpasswd -a '+USERNAME+' bumblebee',
            'systemctl enable bumblebeed.service'
        ]
    }
}

NVIDIA_LEGACY_340XX_CARDS = [
    'GeForce 8800 GTX',
    'GeForce 8800 GTS',
    'GeForce 8800 Ultra',
    'Tesla C870',
    'Quadro FX 5600',
    'Quadro FX 4600',
    'GeForce 8600 GTS',
    'GeForce 8600 GT',
    'GeForce 8600 GT',
    'GeForce 8600 GS',
    'GeForce 8400 GS',
    'GeForce 9500M GS',
    'GeForce 8300 GS',
    'GeForce 8600M GT',
    'GeForce 9650M GS',
    'GeForce 8700M GT',
    'Quadro FX 370',
    'Quadro NVS 320M',
    'Quadro FX 570M',
    'Quadro FX 1600M',
    'Quadro FX 570',
    'Quadro FX 1700',
    'GeForce GT 330',
    'GeForce 8400 SE',
    'GeForce 8500 GT',
    'GeForce 8400 GS',
    'GeForce 8300 GS',
    'GeForce 8400 GS',
    'GeForce 8600M GS',
    'GeForce 8400M GT',
    'GeForce 8400M GS',
    'GeForce 8400M G',
    'Quadro NVS 140M',
    'Quadro NVS 130M',
    'Quadro NVS 135M',
    'GeForce 9400 GT',
    'Quadro FX 360M',
    'GeForce 9300M G',
    'Quadro NVS 290',
    'GeForce GTX 295',
    'GeForce GTX 280',
    'GeForce GTX 260',
    'GeForce GTX 285',
    'GeForce GTX 275',
    'Tesla C1060',
    'Tesla T10 Processor',
    'Tesla T10 Processor',
    'Tesla M1060',
    'Tesla M1060',
    'Tesla M1060',
    'GeForce GTX 260',
    'GeForce GTX 295',
    'Quadroplex 2200 D2',
    'Quadroplex 2200 S4',
    'Quadro CX',
    'Quadro FX 5800',
    'Quadro FX 4800',
    'Quadro FX 3800',
    'GeForce 8800 GTS 512',
    'GeForce 9800 GT',
    'GeForce 8800 GT',
    'GeForce GT 230',
    'GeForce 9800 GX2',
    'GeForce 9800 GT',
    'GeForce 8800 GS',
    'GeForce GTS 240',
    'GeForce 9800M GTX',
    'GeForce 8800M GTS',
    'GeForce 8800 GS',
    'GeForce GTX 280M',
    'GeForce 9800M GT',
    'GeForce 8800M GTX',
    'GeForce 8800 GS',
    'GeForce GTX 285M',
    'GeForce 9600 GSO',
    'GeForce 8800 GT',
    'GeForce 9800 GTX/9800 GTX+',
    'GeForce 9800 GTX+',
    'GeForce 9800 GT',
    'GeForce GTS 250',
    'GeForce 9800M GTX',
    'GeForce GTX 260M',
    'Quadro FX 4700 X2',
    'Quadro FX 3700',
    'Quadro VX 200',
    'Quadro FX 3600M',
    'Quadro FX 2800M',
    'Quadro FX 3700M',
    'Quadro FX 3800M',
    'GeForce GT 230',
    'GeForce 9600 GT',
    'GeForce 9600 GS',
    'GeForce 9600 GSO 512',
    'GeForce GT 130',
    'GeForce GT 140',
    'GeForce 9800M GTS',
    'GeForce 9700M GTS',
    'GeForce 9800M GS',
    'GeForce 9800M GTS',
    'GeForce 9600 GT',
    'GeForce 9600 GT',
    'GeForce GT 130',
    'GeForce 9700 S',
    'GeForce GTS 160M',
    'GeForce GTS 150M',
    'GeForce 9600 GSO',
    'GeForce 9600 GT',
    'Quadro FX 1800',
    'Quadro FX 2700M',
    'GeForce 9500 GT',
    'GeForce 9400 GT',
    'GeForce 9500 GT',
    'GeForce 9500 GS',
    'GeForce 9500 GS',
    'GeForce GT 120',
    'GeForce 9600M GT',
    'GeForce 9600M GS',
    'GeForce 9600M GT',
    'GeForce GT 220M',
    'GeForce 9700M GT',
    'GeForce 9500M G',
    'GeForce 9650M GT',
    'GeForce G 110M',
    'GeForce GT 130M',
    'GeForce GT 240M LE',
    'GeForce GT 120M',
    'GeForce GT 220M',
    'GeForce GT 320M',
    'GeForce GT 320M',
    'GeForce GT 120',
    'GeForce GT 120',
    'Quadro FX 380',
    'Quadro FX 580',
    'Quadro FX 1700M',
    'GeForce 9400 GT',
    'Quadro FX 770M',
    'GeForce 9300 GE',
    'GeForce 9300 GS',
    'GeForce 8400',
    'GeForce 8400 SE',
    'GeForce 8400 GS',
    'GeForce 9300M GS',
    'GeForce G100',
    'GeForce 9300 SE',
    'GeForce 9200M GS',
    'GeForce 9200M GE',
    'GeForce 9300M GS',
    'Quadro NVS 150M',
    'Quadro NVS 160M',
    'GeForce G 105M',
    'GeForce G 103M',
    'GeForce G105M',
    'Quadro NVS 420',
    'Quadro FX 370 LP',
    'Quadro FX 370 Low Profile',
    'Quadro NVS 450',
    'Quadro FX 370M',
    'Quadro NVS 295',
    'HICx16 + Graphics',
    'HICx8 + Graphics',
    'GeForce 8200M',
    'GeForce 9100M G',
    'GeForce 8200M G',
    'GeForce 9200',
    'GeForce 9100',
    'GeForce 8300',
    'GeForce 8200',
    'nForce 730a',
    'GeForce 9200',
    'nForce 980a/780a SLI',
    'nForce 750a SLI',
    'GeForce 8100 / nForce 720a',
    'GeForce 9400',
    'GeForce 9400',
    'GeForce 9400M G',
    'GeForce 9400M',
    'GeForce 9300',
    'ION',
    'GeForce 9400M G',
    'GeForce 9400M',
    'GeForce 9400',
    'nForce 760i SLI',
    'GeForce 9400',
    'GeForce 9400',
    'GeForce 9300 / nForce 730i',
    'GeForce 9200',
    'GeForce 9100M G',
    'GeForce 8200M G',
    'GeForce 9400M',
    'GeForce 9200',
    'GeForce G102M',
    'GeForce G205M',
    'GeForce G102M',
    'GeForce G205M',
    'ION',
    'ION',
    'GeForce 9400',
    'ION',
    'ION LE',
    'ION LE',
    'GeForce 320M',
    'GeForce 320M',
    'GeForce 320M',
    'GeForce 320M',
    'GeForce 320M',
    'GeForce GT 220',
    'GeForce 315',
    'GeForce 210',
    'GeForce 405',
    'GeForce 405',
    'GeForce GT 230M',
    'GeForce GT 330M',
    'GeForce GT 230M',
    'GeForce GT 330M',
    'NVS 5100M',
    'GeForce GT 320M',
    'GeForce GT 415',
    'GeForce GT 240M',
    'GeForce GT 325M',
    'Quadro 400',
    'Quadro FX 880M',
    'GeForce G210',
    'GeForce 205',
    'GeForce 310',
    'Second Generation ION',
    'GeForce 210',
    'GeForce 310',
    'GeForce 315',
    'GeForce G105M',
    'GeForce G105M',
    'NVS 2100M',
    'NVS 3100M',
    'GeForce 305M',
    'Second Generation ION',
    'Second Generation ION',
    'GeForce 310M',
    'Second Generation ION',
    'Second Generation ION',
    'GeForce 305M',
    'GeForce 310M',
    'GeForce 305M',
    'Second Generation ION',
    'Second Generation ION',
    'GeForce G210M',
    'GeForce G210',
    'GeForce 310M',
    'Second Generation ION',
    'Second Generation ION',
    'Quadro FX 380 LP',
    'GeForce 315M',
    'GeForce 405',
    'GeForce 405M',
    'GeForce 405M',
    'GeForce 405',
    'GeForce 405',
    'GeForce 405',
    'GeForce 405',
    'GeForce 405',
    'GeForce 405',
    'GeForce 405',
    'Quadro FX 380M',
    'GeForce GT 330',
    'GeForce GT 320',
    'GeForce GT 240',
    'GeForce GT 340',
    'GeForce GT 220',
    'GeForce GT 330',
    'GeForce GTS 260M',
    'GeForce GTS 250M',
    'GeForce GT 220',
    'GeForce GT 335M',
    'GeForce GTS 350M',
    'GeForce GTS 360M',
    'Quadro FX 1800M',
    'GeForce 9300 GS',
    'GeForce 8400GS',
    'GeForce 405',
    'NVS 300'
]

NVIDIA_LEGACY_304XX_CARDS = [
    'GeForce 6800 Ultra',
    'GeForce 6800',
    'GeForce 6800 LE',
    'GeForce 6800 XE',
    'GeForce 6800 XT',
    'GeForce 6800 GT',
    'GeForce 6800 GT',
    'GeForce 6800 GS',
    'GeForce 6800 XT',
    'Quadro FX 4000',
    'GeForce 7800 GTX',
    'GeForce 7800 GTX',
    'GeForce 7800 GT',
    'GeForce 7800 GS',
    'GeForce 7800 SLI',
    'GeForce Go 7800',
    'GeForce Go 7800 GTX',
    'Quadro FX 4500',
    'GeForce 6800 GS',
    'GeForce 6800',
    'GeForce 6800 LE',
    'GeForce 6800 XT',
    'GeForce Go 6800',
    'GeForce Go 6800 Ultra',
    'Quadro FX Go1400',
    'Quadro FX 3450/4000 SDI',
    'Quadro FX 1400',
    'GeForce 6600 GT',
    'GeForce 6600',
    'GeForce 6200',
    'GeForce 6600 LE',
    'GeForce 7800 GS',
    'GeForce 6800 GS',
    'Quadro FX 3400/Quadro FX 4000',
    'GeForce 6800 Ultra',
    'GeForce 6600 GT',
    'GeForce 6600',
    'GeForce 6600 LE',
    'GeForce 6600 VE',
    'GeForce Go 6600',
    'GeForce 6610 XL',
    'GeForce Go 6600 TE/6200 TE',
    'GeForce 6700 XL',
    'GeForce Go 6600',
    'GeForce Go 6600 GT',
    'Quadro NVS 440',
    'Quadro FX 540M',
    'Quadro FX 550',
    'Quadro FX 540',
    'GeForce 6200',
    'GeForce 6500',
    'GeForce 6200 TurboCache(TM)',
    'GeForce 6200SE TurboCache(TM)',
    'GeForce 6200 LE',
    'GeForce Go 6200',
    'Quadro NVS 285',
    'GeForce Go 6400',
    'GeForce Go 6200',
    'GeForce Go 6400',
    'GeForce 6250',
    'GeForce 7100 GS',
    'GeForce 7350 LE',
    'GeForce 7300 LE',
    'GeForce 7550 LE',
    'GeForce 7300 SE/7200 GS',
    'GeForce Go 7200',
    'GeForce Go 7300',
    'GeForce Go 7400',
    'Quadro NVS 110M',
    'Quadro NVS 120M',
    'Quadro FX 350M',
    'GeForce 7500 LE',
    'Quadro FX 350',
    'GeForce 7300 GS',
    'GeForce 6800',
    'GeForce 6800 LE',
    'GeForce 6800 GT',
    'GeForce 6800 XT',
    'GeForce 6200',
    'GeForce 6200 A-LE',
    'GeForce 6150',
    'GeForce 6150 LE',
    'GeForce 6100',
    'GeForce Go 6150',
    'Quadro NVS 210S / GeForce 6150LE',
    'GeForce Go 6100',
    'GeForce 7900 GTX',
    'GeForce 7900 GT/GTO',
    'GeForce 7900 GS',
    'GeForce 7950 GX2',
    'GeForce 7950 GX2',
    'GeForce 7950 GT',
    'GeForce Go 7950 GTX',
    'GeForce Go 7900 GS',
    'Quadro NVS 510M',
    'Quadro FX 2500M',
    'Quadro FX 1500M',
    'Quadro FX 5500',
    'Quadro FX 3500',
    'Quadro FX 1500',
    'Quadro FX 4500 X2',
    'GeForce 7600 GT',
    'GeForce 7600 GS',
    'GeForce 7300 GT',
    'GeForce 7900 GS',
    'GeForce 7950 GT',
    'GeForce 7650 GS',
    'GeForce 7650 GS',
    'GeForce 7600 GT',
    'GeForce 7600 GS',
    'GeForce 7300 GT',
    'GeForce 7600 LE',
    'GeForce 7300 GT',
    'GeForce Go 7700',
    'GeForce Go 7600',
    'GeForce Go 7600 GT',
    'Quadro FX 560M',
    'Quadro FX 560',
    'GeForce 6150SE nForce 430',
    'GeForce 6100 nForce 405',
    'GeForce 6100 nForce 400',
    'GeForce 6100 nForce 420',
    'GeForce 7025 / nForce 630a',
    'GeForce 7150M / nForce 630M',
    'GeForce 7000M / nForce 610M',
    'GeForce 7050 PV / nForce 630a',
    'GeForce 7050 PV / nForce 630a',
    'GeForce 7025 / nForce 630a',
    'GeForce 7150 / nForce 630i',
    'GeForce 7100 / nForce 630i',
    'GeForce 7050 / nForce 630i',
    'GeForce 7050 / nForce 610i',
    'GeForce 7050 / nForce 620i'
]
