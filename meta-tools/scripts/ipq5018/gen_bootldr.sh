#!/bin/bash
#===========================================================================
#Copyright (c) 2020 Qualcomm Technologies, Inc.
#All Rights Reserved.
#Confidential and Proprietary - Qualcomm Technologies, Inc.
#===========================================================================

if [ -z $1 ] || [ -z $2 ]
then
   echo "Usage gen_bootldr.sh <script path> <image path> [build type]";
   exit 1
fi

if [ -z $3 ]
then
   build="tiny-nor"
else
   build=$3
fi

if echo $build | grep -q "debug"
then
   img_variant="tiny_debug"
else
   img_variant="tiny"
fi

# BOOTLDR2 generation
python $1/scripts/createxbl.py -f $2/tiny_mon.elf -s $2/tiny_qsee.elf -a 64 -b 64 -n -o $2/mon_qsee.elf
python $1/scripts/createxbl.py -f $2/mon_qsee.elf -s $2/devcfg.elf -a 64 -b 64 -n -o $2/mon_qsee_devcfg.elf
python $1/scripts/createxbl.py -f $2/mon_qsee_devcfg.elf -s $2/openwrt-ipq5018_${img_variant}-u-boot.elf -a 64 -b 32 -o $2/tz_uboot.elf -e -n
python $1/scripts/elftombn.py -f $2/tz_uboot.elf -o $2/tz_uboot_compress.mbn -c com

dd if=$2/${build}-system-partition-ipq5018.bin of=$2/mibib bs=1024 count=4
cat $2/mibib > $2/bootldr2_nor.mbn
cat $2/tz_uboot_compress.mbn >> $2/bootldr2_nor.mbn

# BOOTLDR1 generation
python $1/scripts/createxbl.py -f $2/SBL1_tiny_nor.elf -a 32 -c 32 -i $2/cdt-AP-MP02.1_128M16_DDR3.bin -j 0x07030000  -o $2/bootldr1_nor.elf -n
python $1/scripts/elftombn.py -f $2/bootldr1_nor.elf -o $2/bootldr1_nor.mbn

# BOOTLDR2 ATF generation
python $1/scripts/createxbl.py -f $2/bl31.elf -s $2/openwrt-ipq5018_${img_variant}-u-boot.elf -a 64 -b 32 -o $2/atf_uboot.elf -e -n
python $1/scripts/elftombn.py -f $2/atf_uboot.elf -o $2/atf_uboot_compress.mbn -c com

dd if=$2/${build}-system-partition-ipq5018.bin of=$2/mibib bs=1024 count=4
cat $2/mibib > $2/bootldr2_atf_nor.mbn
cat $2/atf_uboot_compress.mbn >> $2/bootldr2_atf_nor.mbn

# BOOTLDR2_NOAC generation
python $1/scripts/createxbl.py -f $2/mon_qsee.elf -s $2/devcfg_noac.elf -a 64 -b 64 -n -o $2/mon_qsee_devcfg_noac.elf
python $1/scripts/createxbl.py -f $2/mon_qsee_devcfg_noac.elf -s $2/openwrt-ipq5018_${img_variant}-u-boot.elf -a 64 -b 32 -o $2/tz_noac_uboot.elf -e -n
python $1/scripts/elftombn.py -f $2/tz_noac_uboot.elf -o $2/tz_noac_uboot_compress.mbn -c com

dd if=$2/${build}-system-partition-ipq5018.bin of=$2/mibib bs=1024 count=4
cat $2/mibib > $2/bootldr2_noac_nor.mbn
cat $2/tz_noac_uboot_compress.mbn >> $2/bootldr2_noac_nor.mbn
