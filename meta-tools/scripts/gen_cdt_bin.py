#!/usr/bin/python
# ===========================================================================
#Copyright (c) 2017 Qualcomm Technologies, Inc.
#All Rights Reserved.
#Confidential and Proprietary - Qualcomm Technologies, Inc.
# ===========================================================================

import xml.etree.ElementTree as ET
import itertools
import os
import subprocess
import sys
import math
from getopt import getopt
from getopt import GetoptError

ARCH_NAME = ''

cdir = os.path.dirname("")
cdir = os.path.abspath(cdir)

def process_cdtinfo(cdt_info):
	global cdir
	global configdir
	global cdt_gen
	global ARCH_NAME
	global outputdir

	configdir = '$$/' + ARCH_NAME + '/machid_xml'
	configdir = configdir.replace('$$', cdir)

	cdt_gen = '$$/scripts/cdt_generator.py'
	cdt_gen = cdt_gen.replace('$$', cdir)
	cdt_info_file = os.path.join(configdir, cdt_info)
	cdtname = cdt_info.replace(".xml", "")
	cdtbrdbin= "cdt" + "-" + cdtname +".bin"

	try:
		with open(cdt_info_file, 'r'):
			print '\tcdt_info_file location: ' + cdt_info_file
	except IOError:
		print 'cdt_info_file not found. Have you placed it in (' \
			+ cdt_info_file + ')?'
		return -1

	print '\tCreating CDT binary',
	new_cdtbin = os.path.splitext(cdt_info)[0] + os.path.extsep + "mbn"
	prc = subprocess.Popen(['python', cdt_gen, cdt_info_file, cdtbrdbin],
			cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create CDT binary'
		return prc.returncode
	else:
		print '...CDT binary created'
		os.remove(os.path.join(outputdir, "boot_cdt_array.c"))
		os.remove(os.path.join(outputdir, "port_trace.txt"))

	return 0

def main():

	global cdir
	global outputdir
	global ARCH_NAME
	global memory_profile

	memory_profile = "default"
	if len(sys.argv) > 1:
		try:
			opts, args = getopt(sys.argv[1:], "c:o:m:")
		except GetoptError, e:
			print "config file and output path are needed to generate cdt files"
			raise
		for option, value in opts:
			if option == "-c":
				file_path = value
			elif option == "-o":
				outputdir = value
			elif option == "-m":
				memory_profile = value
	else:
		print "config file and output path are needed to generate cdt files"
		return -1
	tree = ET.parse(file_path)
	root = tree.getroot()

	machid = None
	board = None
	memory = None
	discrete_smps = None
	spruce_on_pcie_x1 = None
	spruce_on_pcie_x2 = None
	memory_first = None
	device_size = None

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)

	srcDir = '$$/' + ARCH_NAME + '/machid_xml'
	srcDir = srcDir.replace('$$', cdir)
	if not os.path.exists(srcDir):
		os.makedirs(srcDir)
	cdt_path = '$$/' + ARCH_NAME + '/cdt/'
	cdt_path = cdt_path.replace('$$', cdir)


	if ARCH_NAME != "ipq806x":
		entries = root.findall("./data[@type='MACH_ID_BOARD_MAP']/entry")
		memory_first = entries[0].find(".//memory")

		for entry in entries:
			machid = entry.find(".//machid")
			board = entry.find(".//board")
			memory = entry.find(".//memory")
			discrete_smps = entry.find(".//discrete_smps")
			spruce_on_pcie_x2 = entry.find(".//spruce_on_pcie_x2")
			spruce_on_pcie_x1 = entry.find(".//spruce_on_pcie_x1")
			if memory == None:
				memory = memory_first
			set_props = None
			print("%s  %s  %s" % (machid.text, board.text, memory.text))
			set_props = "\n\t  0x02, 0x0" + machid.text[2] + ", 0x" + \
					machid.text[3] + machid.text[4] + ", 0x" + \
					machid.text[5] + machid.text[6] + ", 0x" + \
					machid.text[7] + machid.text[8] + ", end\n\t"
			tree_cdt_xml = ET.parse(os.path.join(cdt_path, memory.text + ".xml"))
			root_cdt = tree_cdt_xml.getroot()
			machID = root_cdt.find(".//device[@id='cdb0']/props[@name='platform_id']")
			machID.text = set_props

                        if discrete_smps != None:
                            if discrete_smps.text == "true":
                                boot_settings = root_cdt.find(".//device[@id='cdb2']/props[@name='boot_settings']")
                                # Overwritting Bit12 for discrete smps
                                boot_settings.text = str(int(boot_settings.text) | 4096)

			if ARCH_NAME == "ipq5018":
				if spruce_on_pcie_x2.text == "true":
					boot_settings = root_cdt.find(".//device[@id='cdb2']/props[@name='boot_settings']")
					# overwritting Bit 16 for spruce on pcie x2
					boot_settings.text = str(int(boot_settings.text) | 65536)

				if spruce_on_pcie_x1.text == "true":
					boot_settings = root_cdt.find(".//device[@id='cdb2']/props[@name='boot_settings']")
					# overwritting Bit 17 for spruce on pcie x1
					boot_settings.text = str(int(boot_settings.text) | 131072)

			if memory_profile != "default":
				if memory_profile == '256' or memory_profile == '512':
					config_memory_organization = memory.text.split('_', 1)[0]
					config_memory_type = memory.text.split('_', 1)[1]
					print "!!!!!!!!!!!############!!!!!!!!!!!"
					print config_memory_type
					config_memory_in_bits = config_memory_organization.split('M')
					config_memory_size_in_bits = 1
					for i in range(len(config_memory_in_bits)):
						config_memory_size_in_bits = config_memory_size_in_bits*int(config_memory_in_bits[i])

					config_memory_size = config_memory_size_in_bits/8
					diff_in_memory = (config_memory_size/int(memory_profile))
					if diff_in_memory >= 1:
						diff_rows_cs = int(math.log(diff_in_memory,2))
						sizes = root_cdt.findall(".//device[@id='cdb1']/props[@name='device_size_cs0']")
						for device_size in sizes:
							device_size.text = memory_profile

					if config_memory_type != "DDR4":
						# Set row cs for Low Memory profiles
						row_cs0 = root_cdt.findall(".//device[@id='cdb1']/props[@name='num_rows_cs0']")
						for width in row_cs0:
							width.text = str(int(width.text) - diff_rows_cs)
							print "!!!!num_rows_cs0!!!" + width.text

						row_cs1 = root_cdt.findall(".//device[@id='cdb1']/props[@name='num_rows_cs1']")
						for width in row_cs1:
							width.text = str(int(width.text) - diff_rows_cs)
							print "!!!!num_rows_cs1!!!" + width.text

					tree_cdt_xml.write(os.path.join(srcDir, board.text + "_" + \
							memory.text + "_LM" + memory_profile + ".xml"))
				else:
					print "memory_profile should be 256/512"
					return -1

			else:
				tree_cdt_xml.write(os.path.join(srcDir, board.text + "_" + \
									memory.text + ".xml"))
	else:
		os.system("cp " + cdt_path + "*"  + " " + srcDir + "/")

	for cdt_info in os.listdir(srcDir):
		if not os.path.isdir(cdt_info):
			if cdt_info.endswith(".xml"):
				if process_cdtinfo(cdt_info) < 0:
					return -1

if __name__ == '__main__':
    main()
