# ===========================================================================
#Copyright (c) 2017 Qualcomm Technologies, Inc.
#All Rights Reserved.
#Confidential and Proprietary - Qualcomm Technologies, Inc.
# ===========================================================================

from collections import namedtuple

import xml.etree.ElementTree as ET
import os
import subprocess
import sys
from getopt import getopt
from getopt import GetoptError

cdir = os.path.dirname("")
cdir = os.path.abspath(cdir)
Nor_Params = namedtuple("Nor_Params", "pagesize pages_per_block total_blocks")
Nand_Params = namedtuple("nand_Params", "pagesize pages_per_block total_blocks")
outputdir = ""

def process_nand_device(pagesize, pages_per_block, total_blocks, entry, nand_type):

        global mbn_gen
        global nandsyspartition
        global partition_tool
        global cdir
        global ARCH_NAME
        global outputdir
        global QCN9000

	nand_pagesize = pagesize
	nand_pages_per_block = pages_per_block
	nand_total_blocks = total_blocks

	if nand_type == "audio-4k":
		nand_partition = "$$/" + ARCH_NAME + "/flash_partition/nand-audio-4k-partition.xml"
	elif nand_type == "audio-2k":
		nand_partition = "$$/" + ARCH_NAME + "/flash_partition/nand-audio-partition.xml"
	elif nand_type == "4k":
		nand_partition = "$$/" + ARCH_NAME + "/flash_partition/nand-4k-partition.xml"
	elif nand_type == "2k":
		if QCN9000:
			nand_partition = "$$/" + ARCH_NAME + "/flash_partition/nand-partition-qcn9000.xml"
		else:
			nand_partition = "$$/" + ARCH_NAME + "/flash_partition/nand-partition.xml"

	nand_partition = nand_partition.replace('$$', cdir)

	nand_parts = Nand_Params(nand_pagesize, nand_pages_per_block, nand_total_blocks)

	mbn_gen = '$$/scripts/nand_mbn_generator.py'
	mbn_gen = mbn_gen.replace('$$', cdir)

	if ARCH_NAME == "ipq806x":
		partition_tool = outputdir + '/nor_tool'
	else:
		partition_tool = outputdir + '/partition_tool'
	os.chmod(partition_tool, 0744)

	if entry == False or (entry == True and nand_pagesize == 2048 and nand_type == '2k'):
		if QCN9000:
			nandsyspartition = outputdir + '/nand-system-partition-' + ARCH_NAME + '-qcn9000.bin'
			nanduserpartition = 'nand-user-partition-qcn9000.bin'
		else:
			nandsyspartition = outputdir + '/nand-system-partition-' + ARCH_NAME + '.bin'
			nanduserpartition = 'nand-user-partition.bin'
	else:
		nand_blocksize = (nand_pagesize * nand_pages_per_block) / 1024
		if nand_type == "audio-2k" or nand_type == "audio-4k":
			nand_type = "audio-"
		elif nand_type == "4k":
			nand_type = ""
		nandsyspartition = outputdir + '/nand-' + nand_type + 'system-partition-' + ARCH_NAME + '-m' + str(nand_pagesize) + '-p' + str(nand_blocksize) + 'KiB.bin'
		nanduserpartition = 'nand-' + nand_type + 'user-partition-m' + str(nand_pagesize) + '-p' + str(nand_blocksize) + 'KiB.bin'

	nanduserbin= os.path.splitext(nanduserpartition)[0] + ".bin"

	print '\tNand page size: ' + str(nand_parts.pagesize) + ', pages/block: ' \
		+ str(nand_parts.pages_per_block) + ', total blocks: ' \
		+ str(nand_parts.total_blocks)
	print '\tPartition info: ' + nand_partition

	print '\tCreating user partition',
	prc = subprocess.Popen(['python', mbn_gen, nand_partition,
			nanduserbin], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create user partition'
		return prc.returncode
	else:
		print '...User partition created'
	userpart_path = os.path.join(outputdir, nanduserbin)

	print '\tCreating system partition'
	prc = subprocess.Popen([
			partition_tool,
			'-s',
			str(nand_parts.pagesize),
			'-p',
			str(nand_parts.pages_per_block),
			'-b',
			str(nand_parts.total_blocks),
			'-u',
			userpart_path,
			'-o',
			nandsyspartition,
			], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'
	return 0


def process_nand(config_path, flash_type):
	global mbn_gen
	global nandsyspartition
	global partition_tool
	global cdir
	global ARCH_NAME
	global outputdir
	global QCN9000

	tree = ET.parse(config_path)
	root = tree.getroot()

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)
	entry = False
	QCN9000 = False

	if ARCH_NAME == "ipq807x":
		QCN9000 = True

	if root.find(".//data[@type='NAND_PARAMETER']/entry") != None:

		entry = True
		entries = root.findall("./data[@type='NAND_PARAMETER']/entry")
		for nand_param in entries:
			nand_pagesize = int(nand_param.find(".//page_size").text)
			nand_pages_per_block = int(nand_param.find(".//pages_per_block").text)
			nand_total_blocks = int(nand_param.find(".//total_block").text)
			nand_type = nand_param.get('type')

			if QCN9000:
				if process_nand_device(nand_pagesize, nand_pages_per_block, nand_total_blocks, entry, nand_type) != 0:
					return -1
				QCN9000 = False

			if process_nand_device(nand_pagesize, nand_pages_per_block, nand_total_blocks, entry, nand_type) != 0:
				return -1
	else:
		nand_param = root.find(".//data[@type='NAND_PARAMETER']")
		nand_pagesize = int(nand_param.find('page_size').text)
		nand_pages_per_block = int(nand_param.find('pages_per_block').text)
		nand_total_blocks = int(nand_param.find('total_block').text)

		if QCN9000:
			if process_nand_device(nand_pagesize, nand_pages_per_block, nand_total_blocks, entry, "2k") != 0:
				return -1
			QCN9000 = False

		if process_nand_device(nand_pagesize, nand_pages_per_block, nand_total_blocks, entry, "2k") != 0:
			return -1

	return 0


def process_nor(config_path, flash_type):
	global mbn_gen
	global syspart
	global partition_tool
	global cdir
	global ARCH_NAME
	global outputdir

	tree = ET.parse(config_path)
	root = tree.getroot()

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)

	nor_param = root.find(".//data[@type='NOR_PARAMETER']")
	nor_pagesize = int(nor_param.find('page_size').text)
	nor_pages_per_block = int(nor_param.find('pages_per_block').text)
	nor_total_blocks = int(nor_param.find('total_block').text)
	block_size = (nor_pagesize * nor_pages_per_block) / 1024
	density = (block_size * nor_total_blocks) / 1024

	nor_partition = "$$/" + ARCH_NAME + "/flash_partition/" + flash_type + "-partition.xml"
	nor_partition = nor_partition.replace('$$', cdir)

	if ARCH_NAME != "ipq806x":
		root_part = ET.parse(nor_partition)
		part = root_part.find(".//partitions/partition[2]")
		part[5].text = str(block_size)
		part[6].text = str(density)
		root_part.write(nor_partition)

	nor_parts = Nor_Params(nor_pagesize, nor_pages_per_block, nor_total_blocks)

        mbn_gen = '$$/scripts/nand_mbn_generator.py'
        mbn_gen = mbn_gen.replace('$$', cdir)

	if ARCH_NAME == "ipq806x":
		partition_tool = outputdir + '/nor_tool'
	else:
		partition_tool = outputdir + '/partition_tool'
	os.chmod(partition_tool, 0744)

	syspart = outputdir + '/' + flash_type + '-system-partition-' + ARCH_NAME + '.bin'
	userpart = flash_type + '-user-partition.bin'
	noruserbin= os.path.splitext(userpart)[0] + ".bin"

	print '\tNor page size: ' + str(nor_parts.pagesize) + ', pages/block: ' \
		+ str(nor_parts.pages_per_block) + ', total blocks: ' \
		+ str(nor_parts.total_blocks) + ', partition info: ' + nor_partition

	print '\tCreating user partition',
	prc = subprocess.Popen(['python', mbn_gen, nor_partition,
                            noruserbin], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create user partition'
		return prc.returncode
	else:
		print '...User partition created'

	userpart_path = os.path.join(outputdir, noruserbin)

	print '\tCreating system partition'
	prc = subprocess.Popen([
			partition_tool,
			'-s',
			str(nor_parts.pagesize),
			'-p',
			str(nor_parts.pages_per_block),
			'-b',
			str(nor_parts.total_blocks),
			'-c',
			str(1),
			'-u',
			userpart_path,
			'-o',
			syspart,
			], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'

	return 0


def process_norplusnand_device(nor_pagesize, nor_pages_per_block, nor_total_blocks,
		nand_pagesize, nand_pages_per_block, nand_total_blocks, entry):
	global mbn_gen
	global norplusnandsyspartition
	global partition_tool
	global cdir
	global ARCH_NAME
	global outputdir
        global QCN9000

	if nand_pagesize == 2048:
		if QCN9000:
			norplusnand_partition = "$$/" + ARCH_NAME + "/flash_partition/norplusnand-partition-qcn9000.xml"
		else:
			norplusnand_partition = "$$/" + ARCH_NAME + "/flash_partition/norplusnand-partition.xml"
	else:
		norplusnand_partition = "$$/" + ARCH_NAME + "/flash_partition/norplusnand-4k-partition.xml"

	norplusnand_partition = norplusnand_partition.replace('$$', cdir)
	nand_parts = Nand_Params(nand_pagesize, nand_pages_per_block, nand_total_blocks)
	nor_parts = Nor_Params(nor_pagesize, nor_pages_per_block, nor_total_blocks)

	mbn_gen = '$$/scripts/nand_mbn_generator.py'
	mbn_gen = mbn_gen.replace('$$', cdir)

	if ARCH_NAME == "ipq806x":
		partition_tool = outputdir + '/nor_tool'
	else:
		partition_tool = outputdir + '/partition_tool'
	os.chmod(partition_tool, 0744)

	if entry == False or (entry == True and nand_pagesize == 2048):
		if QCN9000:
			norplusnandsyspartition = outputdir + '/norplusnand-system-partition-' + ARCH_NAME + '-qcn9000.bin'
			userpart = 'norplusnand-user-partition-qcn9000.bin'
		else:
			norplusnandsyspartition = outputdir + '/norplusnand-system-partition-' + ARCH_NAME + '.bin'
			userpart = 'norplusnand-user-partition.bin'
	else:
		nand_blocksize = (nand_pagesize * nand_pages_per_block) / 1024
		norplusnandsyspartition = outputdir + '/norplusnand-system-partition-' + ARCH_NAME + '-m' + str(nand_pagesize) + '-p' + str(nand_blocksize) + 'KiB.bin'
		userpart = 'norplusnand-user-partition-m' + str(nand_pagesize) + '-p' + str(nand_blocksize) + 'KiB.bin'

	norplusnanduserbin= os.path.splitext(userpart)[0] +".bin"

	print '\tNor page size: ' + str(nor_parts.pagesize) + ', pages/block: ' \
		+ str(nor_parts.pages_per_block) + ', total blocks: ' \
		+ str(nor_parts.total_blocks)
	print '\tPartition info: ' + norplusnand_partition

	print '\tCreating user partition',
	prc = subprocess.Popen(['python', mbn_gen, norplusnand_partition,
				norplusnanduserbin], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create user partition'
		return prc.returncode
	else:
		print '...User partition created'

	userpart_path = os.path.join(outputdir, norplusnanduserbin)

	print '\tCreating system partition'
	prc = subprocess.Popen([
			partition_tool,
			'-s',
			str(nor_parts.pagesize),
			'-p',
			str(nor_parts.pages_per_block),
			'-b',
			str(nor_parts.total_blocks),
			'-x',
			str(nand_parts.pagesize),
			'-y',
			str(nand_parts.pages_per_block),
			'-z',
			str(nand_parts.total_blocks),
			'-c',
			str(1),
			'-u',
			userpart_path,
			'-o',
			norplusnandsyspartition,
			], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'
		return 0


def process_norplusnand(config_path, flash_type):
	global mbn_gen
	global norplusnandsyspartition
	global partition_tool
	global cdir
	global ARCH_NAME
	global outputdir
	global QCN9000

	tree = ET.parse(config_path)
	root = tree.getroot()

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)

	nor_param = root.find(".//data[@type='NOR_PARAMETER']")
	nor_pagesize = int(nor_param.find('page_size').text)
	nor_pages_per_block = int(nor_param.find('pages_per_block').text)
	nor_total_blocks = int(nor_param.find('total_block').text)

	norplusnand_partition = "$$/" + ARCH_NAME + "/flash_partition/norplusnand-partition.xml"
	norplusnand_partition = norplusnand_partition.replace('$$', cdir)

	if ARCH_NAME != "ipq806x":
		root_part = ET.parse(norplusnand_partition)
		part = root_part.find(".//partitions/partition[2]")
		block_size = (nor_pagesize * nor_pages_per_block) / 1024
		density = (block_size * nor_total_blocks) / 1024
		part[5].text = str(block_size)
		part[6].text = str(density)
		root_part.write(norplusnand_partition)

	entry = False
	QCN9000 = False

	if ARCH_NAME == "ipq807x":
		QCN9000 = True

	if root.find(".//data[@type='NAND_PARAMETER']/entry") != None:

		entry = True
		entries = root.findall("./data[@type='NAND_PARAMETER']/entry")
		for nand_param in entries:
			nand_pagesize = int(nand_param.find(".//page_size").text)
			nand_pages_per_block = int(nand_param.find(".//pages_per_block").text)
			nand_total_blocks = int(nand_param.find(".//total_block").text)

			if QCN9000:
				if process_norplusnand_device(nor_pagesize,
						nor_pages_per_block, nor_total_blocks, nand_pagesize,
						nand_pages_per_block, nand_total_blocks, entry) != 0:
					return -1
				QCN9000 = False

			if process_norplusnand_device(nor_pagesize,
				nor_pages_per_block, nor_total_blocks, nand_pagesize,
				nand_pages_per_block, nand_total_blocks, entry) != 0:
				return -1

	else:
		nand_param = root.find(".//data[@type='NAND_PARAMETER']")
		nand_pagesize = int(nand_param.find('page_size').text)
		nand_pages_per_block = int(nand_param.find('pages_per_block').text)
		nand_total_blocks = int(nand_param.find('total_block').text)

		if QCN9000:
			if process_norplusnand_device(nor_pagesize,
					nor_pages_per_block, nor_total_blocks, nand_pagesize,
					nand_pages_per_block, nand_total_blocks, entry) != 0:
				return -1
			QCN9000 = False

		if process_norplusnand_device(nor_pagesize,
			nor_pages_per_block, nor_total_blocks, nand_pagesize,
			nand_pages_per_block, nand_total_blocks, entry) != 0:
			return -1
	return 0


def process_emmc(config_path, flash_type):
	global ptool
	global msp
	global ARCH_NAME
	global outputdir

	tree = ET.parse(config_path)
	root = tree.getroot()

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)
	emmc_partition = "$$/" + ARCH_NAME + "/flash_partition/emmc-partition.xml"
	emmc_partition = emmc_partition.replace('$$', cdir)

	emmc_total_blocks = None

	emmc_entry = root.find(".//data[@type='EMMC_PARAMETER']/total_block")
	total_blocks = int(emmc_entry.text)

	ptool = '$$/scripts/ptool.py'
	ptool = ptool.replace('$$', cdir)
	msp = '$$/scripts/msp.py'
	msp = msp.replace('$$', cdir)

	emmc_total_blocks = total_blocks

	print '\tTotal blocks: ' + str(emmc_total_blocks)
	print '\tPartition info: ' + emmc_partition
	print '\temmc path: ' + outputdir

	print '\tCreating rawprogram0.xml and patch0.xml',
	prc = subprocess.Popen(['python', ptool, '-x', emmc_partition], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create rawprogram0.xml and patch0.xml'
		return prc.returncode
	else:
		print '...rawprogram0.xml and patch0.xml created'

	rawprogram_path = os.path.join(outputdir, 'rawprogram0.xml')
	patch_path = os.path.join(outputdir, 'patch0.xml')

	print '\t rawprogram' + rawprogram_path
	print '\t patch' + patch_path

	print '\tRunning msp.py to update gpt_main0.bin partition'
	prc = subprocess.Popen([
		'python',
		msp,
		'-r',
		rawprogram_path,
		'-p',
		patch_path,
		'-d',
		str(emmc_total_blocks),
		'-n',
		], cwd=outputdir)
	prc.wait()

	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'
	return 0


def process_norplusemmc(config_path, flash_type):
	global mbn_gen
	global syspart
	global partition_tool
	global cdir
	global ptool
	global msp
	global ARCH_NAME
	global outputdir

	tree = ET.parse(config_path)
	root = tree.getroot()

	arch = root.find(".//data[@type='ARCH']/SOC")
	ARCH_NAME = str(arch.text)

	blocks = root.find(".//data[@type='EMMC_PARAMETER']")
	emmc_total_blocks = int(blocks.find('total_block').text)

	nor_param = root.find(".//data[@type='NORPLUSEMMC_PARAMETER']")
	nor_pagesize = int(nor_param.find('page_size').text)
	nor_pages_per_block = int(nor_param.find('pages_per_block').text)
	nor_total_blocks = int(nor_param.find('total_block').text)
	norplusemmc_partition = "$$/" + ARCH_NAME + "/flash_partition/norplusemmc-partition.xml"
	emmc_partition = "$$/" + ARCH_NAME + "/flash_partition/emmc-partition.xml"
	norplusemmc_partition = norplusemmc_partition.replace('$$', cdir)
	emmc_partition = emmc_partition.replace('$$', cdir)

	if ARCH_NAME != "ipq806x":
		root_part = ET.parse(norplusemmc_partition)
		part = root_part.find(".//partitions/partition[2]")
		block_size = (nor_pagesize * nor_pages_per_block) / 1024
		density = (block_size * nor_total_blocks) / 1024
		part[5].text = str(block_size)
		part[6].text = str(density)
		root_part.write(norplusemmc_partition)

	nor_parts = Nor_Params(nor_pagesize, nor_pages_per_block, nor_total_blocks)

	mbn_gen = '$$/scripts/nand_mbn_generator.py'
	mbn_gen = mbn_gen.replace('$$', cdir)

	ptool = '$$/scripts/ptool.py'
	ptool = ptool.replace('$$', cdir)
	msp = '$$/scripts/msp.py'
	msp = msp.replace('$$', cdir)

	if ARCH_NAME == "ipq806x":
		partition_tool = outputdir + '/nor_tool'
	else:
		partition_tool = outputdir + '/partition_tool'
	os.chmod(partition_tool, 0744)

	syspart = outputdir + '/norplusemmc-system-partition-' + ARCH_NAME + '.bin'
	userpart = 'norplusemmc-user-partition.bin'
	norplusemmcuserbin= os.path.splitext(userpart)[0] + ".bin"

	print '\tNor page size: ' + str(nor_parts.pagesize) + ', pages/block: ' \
		+ str(nor_parts.pages_per_block) + ', total blocks: ' \
		+ str(nor_parts.total_blocks) + ', partition info: ' + norplusemmc_partition

	print '\tCreating user partition',
	prc = subprocess.Popen(['python', mbn_gen, norplusemmc_partition,
				norplusemmcuserbin], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create user partition'
		return prc.returncode
	else:
		print '...User partition created'

	userpart_path = os.path.join(outputdir, norplusemmcuserbin)

	print '\tCreating system partition'
	prc = subprocess.Popen([
			partition_tool,
			'-s',
			str(nor_parts.pagesize),
			'-p',
			str(nor_parts.pages_per_block),
			'-b',
			str(nor_parts.total_blocks),
			'-c',
			str(1),
			'-u',
			userpart_path,
			'-o',
			syspart,
			], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'

	print '\tCreating rawprogram1.xml and patch1.xml',
	prc = subprocess.Popen(['python', ptool, '-x', emmc_partition, '-p', '1'], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create rawprogram1.xml and patch1.xml'
		return prc.returncode
	else:
		print '...rawprogram1.xml and patch1.xml created'

	rawprogram_path = os.path.join(outputdir, 'rawprogram1.xml')
	patch_path = os.path.join(outputdir, 'patch1.xml')

	print '\t rawprogram' + rawprogram_path
	print '\t patch' + patch_path

	print '\tRunning msp.py to update gpt_main0.bin partition',
	prc = subprocess.Popen([
			'python',
			msp,
			'-r',
			rawprogram_path,
			'-p',
			patch_path,
			'-d',
			str(emmc_total_blocks),
			'-n',
			], cwd=outputdir)
	prc.wait()
	if prc.returncode != 0:
		print 'ERROR: unable to create system partition'
		return prc.returncode
	else:
		print '...System partition created'
		return 0

def main():

	global cdir
	global ARCH_NAME
	global outputdir

	funcdict = {
		'nor': process_nor,
		'tiny-nor': process_nor,
		'nand': process_nand,
		'norplusnand': process_norplusnand,
		'emmc': process_emmc,
		'norplusemmc': process_norplusemmc,
		'tiny-nor-debug': process_nor
	}

	if len(sys.argv) > 1:
		try:
			opts, args = getopt(sys.argv[1:], "c:f:o:")
		except GetoptError, e:
			print "Configuration xml, flash type and output path are needed to generate cdt files"
			raise

		for option, value in opts:
			if option == "-c":
				config_path = value
			if option == "-o":
				outputdir = value
			if option == "-f":
				flash_type = value
				print flash_type
	else:
		print "Configuration xml, flash type and output path are needed to generate cdt files"

        if funcdict[flash_type](config_path, flash_type) < 0:
		return -1

if __name__ == '__main__':
    main()
