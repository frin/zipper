from binascii import unhexlify, crc32
from datetime import datetime
import os.path, time

def rot4b(num):
	# flips 4 bytes
	datamod = '%08x' % num # David Schwaderer, look up the algorithm
	datamod = datamod[6]+datamod[7]+datamod[4]+datamod[5]+datamod[2]+datamod[3]+datamod[0]+datamod[1]
	return datamod
def rot2b(num):
	# flips two bytes
	datamod = '%04x' % num # David Schwaderer, look up the algorithm
	datamod = datamod[2]+datamod[3]+datamod[0]+datamod[1]
	return datamod
def formatTimestamp(dt):
	# converts datetime object to 4-byte packed datetime MS-DOS format, returns tuple with date and time separately
	sec = "{0:08b}".format(int(dt.second/2))[3:]
	min = "{0:08b}".format(dt.minute)[2:]
	hrs = "{0:08b}".format(dt.hour)[3:]
	res_time = rot2b(int(hrs+min+sec, 2))
	day = "{0:08b}".format(dt.day)[3:]
	mon = "{0:08b}".format(dt.month)[4:]
	yrs = "{0:08b}".format(dt.year-1980)[1:]
	res_date = rot2b(int(yrs+mon+day, 2))

	return (res_date, res_time)

f = open("test.txt", 'rb')
content = f.read()
f.close()

filename = b'test.txt'
file_comment = b'bew'
file_comment = b''
zip_comment = b'frin was here!'
zip_comment = b''
num_files = 1

out = open('output.zip', 'wb')
file_sig = '504b0304'
version_extract = '0a00' # 1.0
general_purpose_flag = '0000'
comp_method = '0000' # no compression
date_bytes = formatTimestamp(datetime.fromtimestamp(os.path.getmtime(filename)))
last_mod_file_time = date_bytes[1] # as a9a3: 1010 1(21 hr).001 101(13 min).0 0011(3*2=6 sec)           21:13:06
last_mod_file_date = date_bytes[0] # as 470d: 0100 011(35+1980=2015 year).1 000(8 month).0 1101(13 day) 13.08.2015
crc32 = rot4b(crc32(content)) # David Schwaderer, look up the algorithm
comp_size = rot4b(len(content)) # '0e000000' # 14 bytes
uncomp_size = comp_size # 14 bytes
filename_length = rot2b(len(filename)) # '0800'
disk_number_start = ''
int_attribs = ''
ext_attribs = ''
rel_offset_local_header = '0000'

out.write(unhexlify(file_sig))
out.write(unhexlify(version_extract))
out.write(unhexlify(general_purpose_flag))
out.write(unhexlify(comp_method))
out.write(unhexlify(last_mod_file_time))
out.write(unhexlify(last_mod_file_date))
out.write(unhexlify(crc32))
out.write(unhexlify(comp_size))
out.write(unhexlify(uncomp_size))
out.write(unhexlify(filename_length))
out.write(unhexlify(disk_number_start))
out.write(unhexlify(int_attribs))
out.write(unhexlify(ext_attribs))
out.write(unhexlify(rel_offset_local_header))
out.write(filename)
out.write(content)




file_sig = '504b0102'
version_made_by = '1e03' # 1e03 means UNIX (03), 1e means zipper version 3.0
extra_field_length = '0000'
file_comment_length = rot2b(len(file_comment))
disk_number_start = '0000'
int_attribs = '0000'
ext_attribs = '00008081'
rel_offset_local_header = '00000000'
extra_field = b''

# end of central directory

dir_sig = '504b0506'
number_of_this_disk = '0000'
num_disk_start = '0000'
start_central_dir = '0100'
total_entries = rot2b(num_files)
size_central_dir = rot4b(46+len(filename)+len(extra_field)+len(file_comment)) # '36000000'
dir_disk_number = rot4b(30+len(filename)+len(content)) # '34000000'
comment_length = rot2b(len(zip_comment))
comment = zip_comment

out.write(unhexlify(file_sig))
out.write(unhexlify(version_made_by))
out.write(unhexlify(version_extract))
out.write(unhexlify(general_purpose_flag))
out.write(unhexlify(comp_method))
out.write(unhexlify(last_mod_file_time))
out.write(unhexlify(last_mod_file_date))
out.write(unhexlify(crc32))
out.write(unhexlify(comp_size))
out.write(unhexlify(uncomp_size))
out.write(unhexlify(filename_length))
out.write(unhexlify(extra_field_length))
out.write(unhexlify(file_comment_length))
out.write(unhexlify(disk_number_start))
out.write(unhexlify(int_attribs))
out.write(unhexlify(ext_attribs))
out.write(unhexlify(rel_offset_local_header))
out.write(filename)
out.write(extra_field)
out.write(file_comment)
out.write(unhexlify(dir_sig))
out.write(unhexlify(number_of_this_disk))
out.write(unhexlify(num_disk_start))
out.write(unhexlify(start_central_dir))
out.write(unhexlify(total_entries))
out.write(unhexlify(size_central_dir))
out.write(unhexlify(dir_disk_number))
out.write(unhexlify(comment_length))
out.write(comment)

out.close()
