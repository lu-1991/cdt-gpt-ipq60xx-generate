#===========================================================================

#  helper script for emergency programmer for blank emmc devices

# REFERENCES

#  $Header: //components/rel/boot.bf/3.1.1/tools/genimage/misc/cdt_mod.py#2 $
#  $DateTime: 2015/07/22 10:35:57 $ 
#  $Author: pwbldsvc $

# when          who     what, where, why 
# --------      ---     ------------------------------------------------------- 
# 2015-01-27    an      Copied from cdt_generator.py 

# Copyright (c) 2007-2015 Qualcomm Technologies, Inc.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
# ===========================================================================*/
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

#from common import *
#import common
from time import sleep, time
import time
from inspect import getargspec
from os.path import getsize
import struct, sys
import logging

CDT_VERSION = '2'

crc32_table = [
  0x00000000,  0x04c11db7,  0x09823b6e,  0x0d4326d9,
  0x130476dc,  0x17c56b6b,  0x1a864db2,  0x1e475005,
  0x2608edb8,  0x22c9f00f,  0x2f8ad6d6,  0x2b4bcb61,
  0x350c9b64,  0x31cd86d3,  0x3c8ea00a,  0x384fbdbd,
  0x4c11db70,  0x48d0c6c7,  0x4593e01e,  0x4152fda9,
  0x5f15adac,  0x5bd4b01b,  0x569796c2,  0x52568b75,
  0x6a1936c8,  0x6ed82b7f,  0x639b0da6,  0x675a1011,
  0x791d4014,  0x7ddc5da3,  0x709f7b7a,  0x745e66cd,
  0x9823b6e0,  0x9ce2ab57,  0x91a18d8e,  0x95609039,
  0x8b27c03c,  0x8fe6dd8b,  0x82a5fb52,  0x8664e6e5,
  0xbe2b5b58,  0xbaea46ef,  0xb7a96036,  0xb3687d81,
  0xad2f2d84,  0xa9ee3033,  0xa4ad16ea,  0xa06c0b5d,
  0xd4326d90,  0xd0f37027,  0xddb056fe,  0xd9714b49,
  0xc7361b4c,  0xc3f706fb,  0xceb42022,  0xca753d95,
  0xf23a8028,  0xf6fb9d9f,  0xfbb8bb46,  0xff79a6f1,
  0xe13ef6f4,  0xe5ffeb43,  0xe8bccd9a,  0xec7dd02d,
  0x34867077,  0x30476dc0,  0x3d044b19,  0x39c556ae,
  0x278206ab,  0x23431b1c,  0x2e003dc5,  0x2ac12072,
  0x128e9dcf,  0x164f8078,  0x1b0ca6a1,  0x1fcdbb16,
  0x018aeb13,  0x054bf6a4,  0x0808d07d,  0x0cc9cdca,
  0x7897ab07,  0x7c56b6b0,  0x71159069,  0x75d48dde,
  0x6b93dddb,  0x6f52c06c,  0x6211e6b5,  0x66d0fb02,
  0x5e9f46bf,  0x5a5e5b08,  0x571d7dd1,  0x53dc6066,
  0x4d9b3063,  0x495a2dd4,  0x44190b0d,  0x40d816ba,
  0xaca5c697,  0xa864db20,  0xa527fdf9,  0xa1e6e04e,
  0xbfa1b04b,  0xbb60adfc,  0xb6238b25,  0xb2e29692,
  0x8aad2b2f,  0x8e6c3698,  0x832f1041,  0x87ee0df6,
  0x99a95df3,  0x9d684044,  0x902b669d,  0x94ea7b2a,
  0xe0b41de7,  0xe4750050,  0xe9362689,  0xedf73b3e,
  0xf3b06b3b,  0xf771768c,  0xfa325055,  0xfef34de2,
  0xc6bcf05f,  0xc27dede8,  0xcf3ecb31,  0xcbffd686,
  0xd5b88683,  0xd1799b34,  0xdc3abded,  0xd8fba05a,
  0x690ce0ee,  0x6dcdfd59,  0x608edb80,  0x644fc637,
  0x7a089632,  0x7ec98b85,  0x738aad5c,  0x774bb0eb,
  0x4f040d56,  0x4bc510e1,  0x46863638,  0x42472b8f,
  0x5c007b8a,  0x58c1663d,  0x558240e4,  0x51435d53,
  0x251d3b9e,  0x21dc2629,  0x2c9f00f0,  0x285e1d47,
  0x36194d42,  0x32d850f5,  0x3f9b762c,  0x3b5a6b9b,
  0x0315d626,  0x07d4cb91,  0x0a97ed48,  0x0e56f0ff,
  0x1011a0fa,  0x14d0bd4d,  0x19939b94,  0x1d528623,
  0xf12f560e,  0xf5ee4bb9,  0xf8ad6d60,  0xfc6c70d7,
  0xe22b20d2,  0xe6ea3d65,  0xeba91bbc,  0xef68060b,
  0xd727bbb6,  0xd3e6a601,  0xdea580d8,  0xda649d6f,
  0xc423cd6a,  0xc0e2d0dd,  0xcda1f604,  0xc960ebb3,
  0xbd3e8d7e,  0xb9ff90c9,  0xb4bcb610,  0xb07daba7,
  0xae3afba2,  0xaafbe615,  0xa7b8c0cc,  0xa379dd7b,
  0x9b3660c6,  0x9ff77d71,  0x92b45ba8,  0x9675461f,
  0x8832161a,  0x8cf30bad,  0x81b02d74,  0x857130c3,
  0x5d8a9099,  0x594b8d2e,  0x5408abf7,  0x50c9b640,
  0x4e8ee645,  0x4a4ffbf2,  0x470cdd2b,  0x43cdc09c,
  0x7b827d21,  0x7f436096,  0x7200464f,  0x76c15bf8,
  0x68860bfd,  0x6c47164a,  0x61043093,  0x65c52d24,
  0x119b4be9,  0x155a565e,  0x18197087,  0x1cd86d30,
  0x029f3d35,  0x065e2082,  0x0b1d065b,  0x0fdc1bec,
  0x3793a651,  0x3352bbe6,  0x3e119d3f,  0x3ad08088,
  0x2497d08d,  0x2056cd3a,  0x2d15ebe3,  0x29d4f654,
  0xc5a92679,  0xc1683bce,  0xcc2b1d17,  0xc8ea00a0,
  0xd6ad50a5,  0xd26c4d12,  0xdf2f6bcb,  0xdbee767c,
  0xe3a1cbc1,  0xe760d676,  0xea23f0af,  0xeee2ed18,
  0xf0a5bd1d,  0xf464a0aa,  0xf9278673,  0xfde69bc4,
  0x89b8fd09,  0x8d79e0be,  0x803ac667,  0x84fbdbd0,
  0x9abc8bd5,  0x9e7d9662,  0x933eb0bb,  0x97ffad0c,
  0xafb010b1,  0xab710d06,  0xa6322bdf,  0xa2f33668,
  0xbcb4666d,  0xb8757bda,  0xb5365d03,  0xb1f740b4
]

port_trace_level        = logging.INFO

c_data_fields = 8

def init_device_log():
    global port_logger

    LOGGINGFORMAT = '%(asctime)s %(filename)s %(lineno)s %(levelname)s: %(message)s'
    logging.basicConfig(filename='port_trace.txt', filemode='w' ,format=LOGGINGFORMAT,level=port_trace_level)   # filemode='w', level=logging.INFO

    #define a 2nd Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter( logging.Formatter( LOGGINGFORMAT ) )

    #add the handler to the root logger
    #logging.getLogger('').addHandler(console)
    port_logger = logging.getLogger('zeno')
    port_logger.addHandler(console)


def print_c_formatted(data_list, title, fp):
    fp.write("\t/* %s */\n" % title)
    for i in range(0, len(data_list), 2):
        data_item = data_list[i:i+2]
        if i % c_data_fields == 0:
            fp.write("\n\t")
        #import pdb; pdb.set_trace()
        fp.write("0x%.2X," % int(data_item,16))
        if i+2 % c_data_fields == 0:
            fp.write("\n")
        else:
            fp.write(" ")
    fp.write("\n")
    fp.write("\n")


def write_c_file(filename, header,metadata,blockdata):
    fp = open(filename, 'w')
    fp.write("""
/*==========================================================================	
                        NOTE: This is a generated file!
===========================================================================*/	
/*==========================================================================

                   INCLUDE FILES

===========================================================================*/
#include "boot_comdef.h"
#include "boot_config_data.h"

/*=============================================================================

        LOCAL DEFINITIONS AND DECLARATIONS FOR MODULE

This section contains local definitions for constants, macros, types,
variables and other items needed by this module.

=============================================================================*/
/**
* fixed size array that holds the cdt table in memory, it's intialized to 
* CDT v1 with only one data block which is platform id. The platform id type 
* is UNKNOWN as default.
*/
uint8 config_data_table[CONFIG_DATA_TABLE_MAX_SIZE] = 
{
""")

    print_c_formatted(header, "Header", fp)
    print_c_formatted(metadata, "Meta data", fp)
    print_c_formatted(blockdata, "Block data", fp)

    fp.write("""};
""")
    fp.write("""
/**
    cdt table size
*/
""")
    fp.write("uint32 config_data_table_size = %d;\n" % (len("".join(header+metadata+blockdata))/2))
    fp.close()


def write_bin_file(filename, data): 
    fp = open(filename, 'wb')
    # Add padding to make data 4-byte aligned
    padding = (len(data)/2)%4
    if padding!=0:
        data = data + '00'*(4 - padding)
    for i in range(0, len(data), 2):
        data_item = data[i:i+2]
        fp.write(chr(int(data_item, 16)))
    fp.close()


def ReturnSizeString(size):
    if size>(1024*1024*1024):
        return "%.2f GB" % (size/(1024.0*1024.0*1024.0))
    elif size>(1024*1024):
        return "%.2f MB" % (size/(1024.0*1024.0))
    elif size>(1024):
        return "%.2f KB" % (size/(1024.0))
    else:
        return "%i B" % (size)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



if __name__ == "__main__":

    if len(sys.argv) < 3:
    	print "Usage: cdt_parse.py filename.xml binfile.bin"
    	sys.exit(1);

    init_device_log()

    filename = sys.argv[1]
    bin_file_name = sys.argv[2]
    c_file_name = "boot_cdt_array.c"

    port_logger.info("Filename: '%s'"% (filename))

    root = ET.parse( filename )
    NewXML = Element(root.getroot().tag)    ## elem = tree.getroot(), typically it's <data>

    RootTag = root.getroot().tag

    iter = root.getiterator()

    Array       = []
    TempArray   = []
    for element in iter:
        ##print "\n" + element.tag
        if element.tag == 'device':
            if len(TempArray)>0:
                Array.append(TempArray)
                TempArray   = []
                print Array
        if element.keys():
            TEXT = element.text
            for name, value in element.items():
                ##print "%s=%s" % (name,value)
                if name == 'type':
                    if value == 'DALPROP_ATTR_TYPE_UINT32':
                        ## means it looks like 0x0
                        sz = element.text.strip()   ## remove all whitespace,newlines etc
                        ## does it start with 0x ?
                        #import pdb; pdb.set_trace()
                        if sz[0:2].lower()=='0x':
                            ##print "%.8X" % int(sz,16)
                            ## need to keep as big endian if written in hex
                            TempArray.append("%.8X" % int(sz,16))
                        else:
                            ## need to convert to little endian if written as an integer
                            temp = int(sz)
                            TempArray.append("%.2X%.2X%.2X%.2X" % (temp&0xFF,(temp>>8)&0xFF,(temp>>16)&0xFF,(temp>>24)&0xFF))

                    elif value == 'DALPROP_ATTR_TYPE_BYTE_SEQ':
                        ## means it looks like 0x43, 0x44, 0x54, 0x0, end
                        sz = element.text.strip()   ## remove all whitespace,newlines etc
                        temp = sz.split(',')
                        sz = ''
                        for i in range(len(temp)-1):
                            ##print temp[i].strip()
                            sz += "%.2X" % int(temp[i].strip(),16)

                        TempArray.append(sz)
                    else:
                        ## unhandled
                        print "ERROR: Don't know how to handle that"
                        sys.exit(1)

                #import pdb; pdb.set_trace()

    if len(TempArray)>0:
        Array.append(TempArray)
        TempArray   = []
        print Array

metadata = []

## length of Array[0] is the size of the header
##cdb0    = ''.join(Array[1])     ## len is 5 (actually it's 10, but its a string rep of 0xFF, which is 'FF', so it's half
##cdb1    = ''.join(Array[2])     ## len is 392

## metadata is distance from 0 to first cdb, then size of cdb
### so if 2 CDB, then metadata is going to be 2*4bytes = 8, 
## so  14+8=22
## and 14+8=22+size of last cdb, so +5 = 
blockdata = ''
NumCDBs = len(Array)-1  ## i.e. 2
header  = ''.join(Array[0])     ## len is 28, but it's in string form, so 1 byte is FF, so in string form its 2bytes, so len=14
NumHeaderBytes = len(header)/2

SizeOfMetaData = NumCDBs*4

SizeOfLastCDB = 0

MetaData = ''

DistanceInBytesToCDB = NumHeaderBytes + SizeOfMetaData

for i in range(NumCDBs):
    DistanceInBytesToCDB = DistanceInBytesToCDB + SizeOfLastCDB
    SizeOfLastCDB = len(''.join(Array[(i+1)]))/2
    print "DistanceInBytesToCDB=%d" % DistanceInBytesToCDB
    print "SizeOfLastCDB=%d" % SizeOfLastCDB
    MetaData = MetaData + ''.join( "%.2X%.2X" % ( (int(DistanceInBytesToCDB)>>0)&0xFF , (int(DistanceInBytesToCDB)>>8)&0xFF ) )
    MetaData = MetaData + ''.join( "%.2X%.2X" % ( (int(SizeOfLastCDB)>>0)&0xFF , (int(SizeOfLastCDB)>>8)&0xFF ))
    blockdata = blockdata + ''.join(Array[i+1])

    

##import pdb; pdb.set_trace() 

# "%.2X" % int(header[0:2])


#(Pdb) header
#['43445400', '0100', '00000000', '00000000']

#(Pdb) metadata
#['1600', '0500', '1B00', '8801']

#(Pdb) blockdata
#['0201010000', '01000000', '00524444', 'FFFF0000', '02000000', 'B8000000', '03000000', '01000000', '00000000', '05000000', '14050000', 'A4010000', '60AE0A00', '76020000', '40010000
#', '58980000', '78050000', '4B000000', '4B000000', '0E010000', '64000000', '96000000', '4B000000', 'F0000000', '02000000', '0E000000', '0A000000', '08000000', '0E000000', '0A000000
#', '08000000', '20000000', '08000000', '03000000', 'F0000000', 'F4010000', '4B000000', '08000000', '04000000', '05000000', '80841E00', '10270000', '04000000', '100E0000', '84030000
#', '10270000', '0A000000', '96000000', 'F4010000', '80A20000', '00200000', '19000000', '37000000', '00000000', '00000000', '05000000', '14050000', 'A4010000', '60AE0A00', '76020000
#', '40010000', '58980000', '78050000', '4B000000', '4B000000', '0E010000', '64000000', '96000000', '4B000000', 'F0000000', '02000000', '0E000000', '0A000000', '08000000', '0E000000
#', '0A000000', '08000000', '20000000', '08000000', '03000000', 'F0000000', 'F4010000', '4B000000', '08000000', '04000000', '05000000', '80841E00', '10270000', '04000000', '100E0000
#', '84030000', '10270000', '0A000000', '96000000', 'F4010000', '80A20000', '00200000', '19000000', '37000000']

#CRC computation for metadata and blockdata
data = MetaData+blockdata
crc = 0

for i in range(0, len(data), 2):
        data_item = data[i:i+2]
        x = chr(int(data_item, 16))
        crc = crc32_table[((crc >> 24) ^ (ord(x)))%256] ^ (crc << 8)


crc = hex(crc & 0xffffffff).strip('L')
crc = struct.pack('<I', int(crc, 16)).encode('hex')

#Updating CRC field in CDT Header
header_crc = header[0:12] + str(crc) + header[20:]

#Update CDT version
header_new = header_crc[0:9] + CDT_VERSION + header_crc[10:]

write_bin_file(bin_file_name, header_new+MetaData+blockdata)
write_c_file(c_file_name, header_new,MetaData,blockdata)

print "\n\nCreated '%s'" % bin_file_name
print "Created '%s'" % c_file_name

