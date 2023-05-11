# ===========================================================================
#Copyright (c) 2017 Qualcomm Technologies, Inc.
#All Rights Reserved.
#Confidential and Proprietary - Qualcomm Technologies, Inc.
# ===========================================================================

import re
import sys

c_file_name = "boot_cdt_array.c"
debug = True

if len(sys.argv) < 3:
    print "Usage: cdt_generator.py filename.xml binfile.bin"
    sys.exit(1);

filename = sys.argv[1]
bin_file_name = sys.argv[2]
token_stack = []
ignore_tags = ['comment', 'img_name', 'layout']
xml_comment_tag = '!--'
partitions_parent_tag_name = "partition"
partition_table_header_size = 16
partition_entry_size = 28
num_partition_entries = 32
full_file_length = (partition_table_header_size + (partition_entry_size * num_partition_entries))
header = []
metadata = []
blockdata = []
footer = []
all_data = []

def clean_string(some_string):
    from string import printable
    some_string = "".join([ ch for ch in some_string if ch in printable ])
    some_string = some_string.replace("\n", "")
    some_string = some_string.replace("\r", "")
    return some_string

def strip_hex(hex_string):
    if len(hex_string) < 3 or not (hex_string[:2] == "0x" or hex_string[:2] == "0X"):
        return hex_string	
    return hex_string[2:]

def little_endian(hex_string):
    if len(hex_string) % 2 != 0:
        print "%s is an invalid value to convert to little endian!" % (hex_string)
        return
    swap_list = []
    for i in range(0, len(hex_string), 2):
        swap_list.insert(0, hex_string[i:i+2])
    return ''.join(swap_list)

def get_attribute(token, att_name):
    tag = get_tag_name(token)
    tag_att_list = re.split('\s+', strip_tags(token))
    tag_att_list.remove(tag)
    for att in tag_att_list:
        att_val = att.split("=")
        if len(att_val) == 2 and att_val[0] == att_name:
            return att_val[1].strip('"').strip("'")
    return None

def pad_string(token, length, rightjust=True):
    if len(token) >= length:
        return token
    else:
        return (rightjust and token.rjust(length, '0') or token.ljust(length, '0'))

def is_tag(token):
    return (len(token) > 2 and token[0] == '<' and token[-1] == '>')

def strip_tags(token):
    if is_tag(token):
        return token[1:-1]

def is_closing_tag(token):
    return (is_tag(token) and token[1] == '/')

def get_tag_name(tag):
    if is_closing_tag(tag):
        return tag[2:-1]
    else:
        tag_split = re.split('\s+', tag[1:-1])
        return tag_split[0]

def process_tag(tag):
    tag_name = get_tag_name(tag)	
    parent_tag_name = len(token_stack) >= 2 and get_tag_name(token_stack[-2]) or ""
        
    if is_closing_tag(tag):
        if tag_name == partitions_parent_tag_name:
            if len(metadata) == 0:
                metadata.append(1)
            else:
                metadata[0] = metadata[0] + 1

def process_data(data, token_stack):
    tag = token_stack[-1]
    tag_name = get_tag_name(tag)
    parent_tag_name = len(token_stack) >= 2 and get_tag_name(token_stack[-2]) or ""
    
    if tag_name in ignore_tags:
        return

    clean_data = data
    data_length = get_attribute(tag, "length")
    data_type = get_attribute(tag, "type")
    if not data_type == "string":
        clean_data = "%02X" % eval(clean_data)
    else:
        clean_data = "".join(["%02x" % ord(x) for x in clean_data])
    if not data_length is None:
        data_length = int(data_length)
        clean_data = pad_string(clean_data, data_length * 2, data_type != "string")
    
    data_endianness = get_attribute(tag, "endian")
    # assuming big-endian by default
    # assuming 'string's need to be converted to little endian
    if not data_type == "string" or ((not data_endianness is None) and data_endianness.lower() == "little"):
        clean_data = little_endian(clean_data)
    
    if not parent_tag_name == partitions_parent_tag_name:
        header.append(clean_data)
    else:
        blockdata.append(clean_data)

def generate_metadata():
    if len(metadata) > 0:
        metadata[0] = little_endian(pad_string("%02X" % metadata[0], 4*2))

def generate_footer():
    current_file_len = 0
    for x in all_data:
        current_file_len  = current_file_len + len(x)/2
    footer.append("0" * 2 * (full_file_length - current_file_len))

def write_bin_file(filename, data):
    fp = open(filename, 'wb')
    for i in range(0, len(data), 2):
        data_item = data[i:i+2]
        fp.write(chr(int(data_item, 16)))
    fp.close()

file_string = open(filename, 'r').read()
file_string = re.sub(r'>\s+', ">", file_string)
file_string = re.sub(r'\s+<', "<", file_string)
file_string = clean_string(file_string)

# A token is either a tag i.e. <[^>\s]*> or it is a (non-tag) value i.e. [^<>]+
#splitter = re.compile('(<\/?\S+[^>]*>|[^<>]+)')
splitter = re.compile('(<[^>]*>|[^<>]+)')
token_list = splitter.findall(file_string)

for token in token_list:
    #print "Processing", token
    if is_tag(token):
        if get_tag_name(token) == xml_comment_tag or get_tag_name(token) == "?xml":
            continue
        if is_closing_tag(token):
            token_stack.pop()
        else:
            token_stack.append(token)
        process_tag(token)
    else:
        process_data(token, token_stack)

generate_metadata()

all_data.extend(header)
all_data.extend(metadata)
all_data.extend(blockdata)

generate_footer()

all_data.extend(footer)
all_data = "".join(all_data)
write_bin_file(bin_file_name, all_data)
