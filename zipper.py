from binascii import unhexlify, crc32
from datetime import datetime
import os.path
import math
import sys


def rot4b(num):
	# flips 4 bytes
	datamod = '%08x' % num  # David Schwaderer, look up the algorithm
	datamod = datamod[6]+datamod[7]+datamod[4]+datamod[5]+datamod[2]+datamod[3]+datamod[0]+datamod[1]
	return datamod


def rot2b(num):
	# flips 2 bytes
	datamod = '%04x' % num  # David Schwaderer, look up the algorithm
	datamod = datamod[2] + datamod[3] + datamod[0] + datamod[1]
	return datamod


def format_timestamp(dt):
	# converts datetime object to 4-byte packed datetime MS-DOS format, returns tuple with date and time separately
	sec = "{0:08b}".format(math.ceil(dt.second/2))[3:]
	mns = "{0:08b}".format(dt.minute)[2:]
	hrs = "{0:08b}".format(dt.hour)[3:]
	res_time = rot2b(int(hrs+mns+sec, 2))
	day = "{0:08b}".format(dt.day)[3:]
	mon = "{0:08b}".format(dt.month)[4:]
	yrs = "{0:08b}".format(dt.year-1980)[1:]
	res_date = rot2b(int(yrs+mon+day, 2))

	return res_date, res_time

filelist = sys.argv
filelist.pop(0)
if len(filelist) < 2:
	print("Missing arguments, usage: zipper <output.zip> <file 1> [file 2] ...")
	exit(1)
output = filelist.pop(0)

num_files = 0
total_offset = 0
files = []
out = open(output, 'wb')

file_sig = '504b0304'
version_extract = '0a00'  # 1.0
general_purpose_flag = '0000'
comp_method = '0000'  # no compression
extra_field_length = '0000'

for inputfile in filelist:
	print("Processing file " + inputfile)
	num_files += 1
	filename = bytes(inputfile, 'UTF-8')
	f = open(filename, 'rb')
	content = f.read()
	f.close()

	file_comment = b''
	# file_comment = b'This is an example file comment'

	date_bytes = format_timestamp(datetime.fromtimestamp(os.path.getmtime(filename)))
	last_mod_file_time = date_bytes[1]  # as a9a3: 1010 1(21 hr).001 101(13 min).0 0011(3*2=6 sec)           21:13:06
	last_mod_file_date = date_bytes[0]  # as 470d: 0100 011(35+1980=2015 year).1 000(8 month).0 1101(13 day) 13.08.2015
	crc_32 = rot4b(crc32(content))
	comp_size = rot4b(len(content))
	uncomp_size = comp_size
	filename_length = rot2b(len(filename))

	local_header_length = (len(file_sig)+len(version_extract)+len(general_purpose_flag)+len(comp_method)+len(last_mod_file_time)+len(last_mod_file_date)+len(crc_32)+len(comp_size)+len(uncomp_size)+len(filename_length)+len(extra_field_length))/2+len(filename)+len(content)

	out.write(unhexlify(file_sig))
	out.write(unhexlify(version_extract))
	out.write(unhexlify(general_purpose_flag))
	out.write(unhexlify(comp_method))
	out.write(unhexlify(last_mod_file_time))
	out.write(unhexlify(last_mod_file_date))
	out.write(unhexlify(crc_32))
	out.write(unhexlify(comp_size))
	out.write(unhexlify(uncomp_size))
	out.write(unhexlify(filename_length))
	out.write(unhexlify(extra_field_length))
	out.write(filename)
	out.write(content)

	file_data = dict()
	file_data['comp_method'] = comp_method
	file_data['last_mod_file_time'] = last_mod_file_time
	file_data['last_mod_file_date'] = last_mod_file_date
	file_data['crc_32'] = crc_32
	file_data['comp_size'] = comp_size
	file_data['uncomp_size'] = uncomp_size
	file_data['filename_length'] = filename_length
	file_data['filename'] = filename
	file_data['file_comment'] = file_comment
	file_data['extra_field_length'] = extra_field_length
	file_data['total_offset'] = total_offset
	file_data['content_length'] = len(content)
	total_offset += local_header_length
	files.append(file_data)


# central directory fields

file_sig = '504b0102'
version_made_by = '1e03'  # 1e03 means UNIX (03), 1e means zipper version 3.0
extra_field_length = '0000'
disk_number_start = '0000'
int_attribs = '0000'
extra_field = b''

# end of central directory fields

dir_sig = '504b0506'
number_of_this_disk = '0000'
num_disk_start = '0000'
total_entries = rot2b(num_files)
total_entries_this_disk = rot2b(num_files)
zip_comment = b''
# zip_comment = b'This is an example global ZIP file comment'
comment_length = rot2b(len(zip_comment))

dir_disk_number = 0
total_size_cd = 0

for data in files:
	out.write(unhexlify(file_sig))
	out.write(unhexlify(version_made_by))
	out.write(unhexlify(version_extract))
	out.write(unhexlify(general_purpose_flag))
	out.write(unhexlify(data['comp_method']))
	out.write(unhexlify(data['last_mod_file_time']))
	out.write(unhexlify(data['last_mod_file_date']))
	out.write(unhexlify(data['crc_32']))
	out.write(unhexlify(data['comp_size']))
	out.write(unhexlify(data['uncomp_size']))
	out.write(unhexlify(data['filename_length']))
	out.write(unhexlify(extra_field_length))
	file_comment_length = rot2b(len(data['file_comment']))
	out.write(unhexlify(file_comment_length))
	out.write(unhexlify(disk_number_start))
	out.write(unhexlify(int_attribs))
	out.write(unhexlify('0000'+rot2b(os.stat(data['filename']).st_mode)))
	out.write(unhexlify(rot4b(data['total_offset'])))
	out.write(data['filename'])
	out.write(extra_field)
	out.write(data['file_comment'])
	total_size_cd += (len(file_sig+version_made_by+version_extract+general_purpose_flag)
		+ len(data['comp_method']+data['last_mod_file_time']+data['last_mod_file_date']+data['crc_32'])
		+ len(data['comp_size']+data['uncomp_size']+data['filename_length']+extra_field_length)
		+ len(file_comment_length+disk_number_start+int_attribs))/2+4+4+len(data['filename']+extra_field)
	+ len(data['file_comment'])
	dir_disk_number += 30 + len(data['filename']) + data['content_length']

out.write(unhexlify(dir_sig))
out.write(unhexlify(number_of_this_disk))
out.write(unhexlify(num_disk_start))
out.write(unhexlify(total_entries))
out.write(unhexlify(total_entries_this_disk))
out.write(unhexlify(rot4b(total_size_cd)))
out.write(unhexlify(rot4b(dir_disk_number)))
out.write(unhexlify(comment_length))
out.write(zip_comment)

out.close()
