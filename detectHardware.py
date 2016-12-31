#!/usr/bin/env python3

import subprocess
import re

def lspci():
	p=subprocess.Popen(['lspci', '-mm'], stdout=subprocess.PIPE)
	o=p.communicate()[0].decode()
	return o

def filter_gpus(out):
	out_l=out.split('\n')
	filtered_l=[]
	for i in out_l:
		if 'VGA' in i or '3D' in i or 'Display' in i:
			filtered_l.append(i)
	return filtered_l

def lspci_filter():
	return filter_gpus(lspci())

def get_relevant_info(info_unf_l=None):
	if info_unf_l is None:
		info_unf_l=lspci_filter()
	info_l=[]
	for i in info_unf_l:
		info_l.append(re.findall(r'"([^"]*)"', i))
	relevant_info=[]
	for i in info_l:
		if i[1] == 'NVIDIA Corporation':
			i[2] = re.findall(r'\[([^"]*)\]', i[2])[0]
		relevant_info.append([i[1], i[2]])
	return relevant_info

def get_relevant_info_str(info_unf_l=None):
	out=get_relevant_info(info_unf_l)
	s=''
	for i in out:
		for j in i:
			s+=(j+' ')
		s+='\n'
	return s.strip()
