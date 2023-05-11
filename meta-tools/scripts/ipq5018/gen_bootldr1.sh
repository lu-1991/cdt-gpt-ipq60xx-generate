#!/bin/bash
#===========================================================================
#Copyright (c) 2020 Qualcomm Technologies, Inc.
#All Rights Reserved.
#Confidential and Proprietary - Qualcomm Technologies, Inc.
#===========================================================================

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ]
then
   echo "Usage gen_bootldr.sh <script path> <image path> <cdt_name>";
   exit 1
fi

python $1/scripts/createxbl.py -f $2/SBL1_tiny_nor.elf -a 32 -c 32 -i $2/cdt-$3.bin -j 0x07030000  -o $2/bootldr1_nor.elf -n
python $1/scripts/elftombn.py -f $2/bootldr1_nor.elf -o $2/bootldr1_$3.mbn
