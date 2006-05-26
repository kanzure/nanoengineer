# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NanotubeGeneratorDialog.ui'
#
# Created: Fri May 26 17:14:03 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\x95\x49\x44\x41\x54\x38\x8d\xed\x94\x3d\x12\x82" \
    "\x30\x10\x85\xbf\x28\x45\x8c\x57\x08\x87\xc4\x52" \
    "\x2c\x74\xb4\xe5\x24\x5c\x80\xa1\xa5\xf1\x3a\xb6" \
    "\x5a\x3c\xab\x30\x68\x47\x58\x0a\x67\x7c\xe5\xb7" \
    "\x99\x97\xbf\xb7\xeb\x24\x61\xa9\x8d\xa9\xdb\x4f" \
    "\x18\xba\x18\xbc\xe9\x23\x6e\x1f\xcf\xd7\x05\x38" \
    "\xb7\x5d\x0f\xc0\x7d\x18\x00\xa8\x8e\x35\x73\x59" \
    "\xdb\xf5\x0e\x49\xc4\xe0\xd5\xdc\xae\x8a\xc1\x2b" \
    "\x29\x93\xc1\xb4\x98\x16\x2c\x61\xe3\x09\x13\x98" \
    "\x16\x33\x18\x48\x9f\xa6\xdf\x3b\xce\x60\x48\xb2" \
    "\x8f\x8d\xfd\x95\x57\xfb\x14\xab\xd8\x14\x29\x9c" \
    "\x87\xfa\x04\x40\xb9\xdf\x91\xcb\x60\x85\xd6\x73" \
    "\xfa\xcf\xc3\xa5\x7a\x03\xaf\xec\xb2\x69\x7f\xf9" \
    "\x68\x24\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\x83\x49\x44\x41\x54\x38\x8d\xed\x94\x31\x0e\x80" \
    "\x20\x0c\x45\x7f\x8d\x03\xc2\x15\xe0\xae\x78\x56" \
    "\xcf\x60\x1c\xbf\x8b\x98\x86\xb8\x60\xda\xc1\xc4" \
    "\x2e\x25\x8f\xe6\x43\xe8\x2f\x42\x12\x1e\x31\xb9" \
    "\xa8\xfe\xc2\x3a\x66\x00\x28\x69\x31\xed\xe0\xb6" \
    "\x1f\x32\xb5\x05\x80\xb5\x65\x55\x33\xcc\xae\x0c" \
    "\x90\x04\x49\xe4\x18\x98\x63\xa8\x39\x06\x5a\xb0" \
    "\x7b\xa3\x01\x55\xf8\x9a\xdd\xc2\x1a\xf4\x37\x79" \
    "\xcb\xf0\x74\x9a\x05\x73\xb3\x9b\xef\x53\xb8\x37" \
    "\xcf\xd2\x6e\x73\x67\xf2\x5a\xd2\xa2\x27\x71\x98" \
    "\xb5\x10\x92\x2e\x23\x2d\xfc\x3f\xfa\xcf\x0a\x9f" \
    "\x4d\xff\x95\x1c\x3d\x0e\xf0\x87\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"
image2_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x03" \
    "\x01\x49\x44\x41\x54\x38\x8d\x9d\xd3\x5d\x88\x94" \
    "\x65\x14\xc0\xf1\xff\xf3\xf5\xce\xb3\x33\xeb\x8c" \
    "\xc9\xe4\xae\x88\xad\x29\xa5\x2d\xbb\x21\x06\x6d" \
    "\x42\xb5\x64\x48\x10\x0b\x45\x97\xc2\x5e\x77\x15" \
    "\x45\x44\x20\x28\x94\x50\xdd\x46\x41\x17\x86\x7d" \
    "\x50\x1b\x65\x26\x45\x1f\x5a\xe8\x45\xb5\xa9\x5d" \
    "\x04\x11\xb1\x6a\x94\xb2\xe9\xae\xe3\xc8\xec\xec" \
    "\x7c\xef\xbc\xef\xbc\x73\xba\xd0\x8d\xb4\x75\x77" \
    "\x76\x1f\x78\x6e\x0e\xe7\xfc\x38\xe7\xf0\x3c\x4a" \
    "\x44\x58\xe9\x51\x2f\x2b\x4f\x17\x0e\x80\x9f\x48" \
    "\xd2\x44\xf3\x2d\x35\xa0\xa2\x57\x8c\xde\xa9\x86" \
    "\x4d\xce\xfc\x6e\x67\xed\xa4\x9d\xb5\x93\x76\xab" \
    "\x3d\x6f\x56\x99\xdf\x48\xf1\x3a\xd0\x6d\x57\x84" \
    "\x2a\x75\x9b\x7e\x58\xbf\xe1\xee\x72\x9b\x31\xd7" \
    "\x62\x72\x59\x08\xc7\xc3\x59\x6a\xbc\x2f\x22\x95" \
    "\x65\xc3\x4a\x29\xa5\xfb\xf4\x0b\xc1\x83\xc1\xa0" \
    "\xf6\xd7\x06\x96\xba\x10\x7d\x1d\x35\x25\x27\x7b" \
    "\x45\xe4\x7b\x80\xe5\x77\x6c\xd9\x61\xef\xb5\xcf" \
    "\xb8\x8d\x4e\xa1\x80\x36\x84\xa7\x42\xe2\x33\xf1" \
    "\xdb\xc0\xd8\x7c\xda\xb2\x76\xac\x94\x0a\xec\x26" \
    "\xbb\xcf\xef\xf4\xab\x4c\x60\x30\xce\xd0\x3e\xd7" \
    "\x26\x3c\x1e\x8e\x13\xf3\x8a\x88\x84\x2b\x82\x4d" \
    "\xda\xec\xf2\xc3\x7e\xa7\x5b\xeb\x30\xce\x20\x93" \
    "\xc2\xdc\x47\x73\x57\xa5\x2c\x2f\x8a\x48\xee\xbf" \
    "\xb9\x1d\xc3\x4a\xa9\xb4\x1d\xb4\xaf\xfa\x87\x7c" \
    "\xa0\x03\x0d\x75\xa8\x7f\x5a\x6f\xc5\xb9\x78\x3f" \
    "\x70\xfa\xe6\xfc\x8e\x61\xb3\xde\x3c\x95\x7a\x3c" \
    "\x35\x60\xd3\x16\xad\x34\x8d\xcf\x1b\x44\x13\xd1" \
    "\x11\xe0\x1d\x59\xe0\x33\x74\x04\x2b\xa5\x92\x7e" \
    "\x9b\x7f\xde\x0f\x7a\x6d\x02\x43\xf4\x4b\x44\xe3" \
    "\x44\xe3\x2c\x6d\xf6\x89\x48\x7d\xa1\x9a\x8e\x60" \
    "\xdf\xef\xef\xeb\x7e\xb4\xfb\x1e\xdb\x65\xa1\x04" \
    "\xd5\x43\x55\x91\x39\x39\x20\x22\x7f\xdc\xaa\xa6" \
    "\x23\xd8\xf5\xbb\x51\xdf\xef\xad\x76\x9a\xc6\x78" \
    "\x83\xf0\x7c\x38\x01\x1c\x5a\xac\xc6\x2a\xa7\x1e" \
    "\x4b\xdd\x9f\xda\xa6\x32\x2a\x31\x1f\x94\xaa\x44" \
    "\xb5\x93\xb5\x73\xc4\x7c\x45\x0f\xae\xf7\xd9\xde" \
    "\x11\x9b\xb6\x44\xd3\x11\xd5\x6f\xaa\x82\x70\x50" \
    "\x44\xa6\x16\x85\x11\xd6\xbb\x3b\xdc\xfe\xec\xd3" \
    "\xd9\x60\xfe\x7b\xc6\x85\x98\xe9\xcb\xd3\xd5\xe6" \
    "\x9f\xcd\x91\x35\x4f\xac\x59\x9b\xdc\x9e\xec\x31" \
    "\xce\x30\x73\x64\x86\xf0\x42\x78\x09\xf8\x72\xa9" \
    "\x29\x35\x31\x1f\x56\xbe\xab\xbc\x5b\xfb\xa1\x86" \
    "\xcb\x38\x5c\xc6\xe1\x37\x79\x56\x3f\xb9\xba\x1b" \
    "\xcd\x68\xf2\xee\xe4\xee\xc4\xba\x84\x6e\x5d\x6c" \
    "\x51\x39\x5e\x01\x38\x0c\xfc\xb5\x24\x2c\x22\x61" \
    "\x3c\x13\xbf\x54\x78\xaf\x70\x3a\x3c\x1b\x62\x02" \
    "\x83\x09\x0c\x99\x5d\x19\x12\x1b\x13\x23\x89\x0d" \
    "\x89\x47\x8c\x33\x94\xbe\x28\xd1\xca\xb7\xa6\x80" \
    "\x83\x0b\x3d\xaf\xff\x77\x0c\x88\x48\x2e\xbc\x10" \
    "\x3e\x97\x7f\x33\x7f\x25\xbe\x1a\x63\x02\x43\xd7" \
    "\xe6\x2e\xb2\xa3\xd9\x9e\xc4\x86\x44\x26\xfa\x3b" \
    "\xa2\x7c\xac\x0c\x70\x0c\x98\x58\x0a\xfd\x17\xbe" \
    "\x8e\xff\x5c\x19\xaf\xec\xc9\xbf\x95\x0f\x69\x82" \
    "\x0e\x34\xd9\xdd\x59\x82\x75\x01\xc5\xc3\x45\xa2" \
    "\x2b\x51\x19\xf8\xa0\x93\x6e\x6f\x80\xaf\x9f\xb1" \
    "\xe2\x67\xc5\x03\x85\xb1\x02\xda\x68\x5c\xc6\xd1" \
    "\x2e\xb6\x29\x9d\x28\x01\x1c\x05\x4e\x75\x82\xce" \
    "\x77\x7a\xc3\x05\x7a\xdd\xed\xee\xc7\x2d\x9f\x6c" \
    "\x91\xa1\x99\x21\xe9\x7b\xad\x4f\x50\x94\x80\xe1" \
    "\x9b\x73\x17\xbb\x0b\x07\x61\x28\xb9\x35\x39\x35" \
    "\x70\x74\x40\xd2\x3b\xd2\x02\x7c\x0c\x04\xcb\x81" \
    "\xd5\xad\x56\xa6\x94\x1a\x4e\x3f\x90\xde\x5e\xfb" \
    "\xb5\x56\x8e\xe7\xe2\x93\x22\x72\xa6\xe3\x35\x00" \
    "\xff\x00\x03\x11\x91\x02\xf5\x72\xea\x39\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
image3_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x03" \
    "\x15\x49\x44\x41\x54\x38\x8d\xb5\xd4\x5f\x68\x95" \
    "\x75\x1c\xc7\xf1\xf7\xf7\xf9\x3d\xe7\x39\xcf\x4e" \
    "\x4c\x0b\xc2\x46\x61\x8a\xb9\x10\xaf\xc2\x2e\x86" \
    "\xa8\xb0\x41\x37\x25\x48\x85\xd9\x45\x5e\xb4\x90" \
    "\x86\x4d\x02\xa1\x70\x14\x52\xbb\x10\x46\x66\xb4" \
    "\xfe\xc0\x06\x6b\x20\x2a\x4d\x27\x91\x15\x5e\x44" \
    "\xa5\x56\x28\xbb\x08\x02\x65\xe2\x22\x87\x0a\x9b" \
    "\x86\xb8\xa1\xb9\x7f\x3d\xe7\xf7\xe9\xe2\x9c\x33" \
    "\x9f\x73\x76\x0e\xcd\x8b\x7e\xf0\x85\xe7\x79\x7e" \
    "\xbf\xdf\xeb\xfb\x7b\xbe\xf0\xfd\x99\x24\xfe\x8f" \
    "\x11\xa4\x5f\x76\x45\x51\x53\x7b\x14\x7d\xb8\x2b" \
    "\x8e\x9f\x5c\xcc\xe6\x4e\xb3\xd0\xcc\xac\xda\x9c" \
    "\x95\x4e\xfc\x76\x14\x35\x79\xef\x8f\x60\xf6\x04" \
    "\xf0\xf1\xb5\x24\x79\xeb\x98\x94\xaf\x85\xee\x31" \
    "\xab\xcf\x87\xe1\x7b\x82\x39\x20\x8b\x73\xbd\x07" \
    "\x66\x66\x46\x4a\xf3\x61\xe9\xc1\x49\x9b\x32\x66" \
    "\xab\x00\x3c\xbc\xb6\x3a\x0c\xbf\x06\xce\xd4\x42" \
    "\x43\xe7\xba\x1c\xb4\x01\x0e\xf8\x21\x99\x9d\xbd" \
    "\x9d\x5e\x33\x5f\x8a\x81\x24\x99\xb8\x29\xf9\x18" \
    "\xc8\xc1\x92\x2c\xbc\xd3\x65\xf6\x50\x25\xfa\x81" \
    "\x59\x7d\xce\xb9\xae\xac\x59\x5b\x0c\xee\x96\x74" \
    "\xeb\xa0\xf7\x7f\xed\x87\xfa\xaa\xf0\x15\x48\x7e" \
    "\xf2\x5e\xff\x48\xc4\x85\x78\x26\x08\xc3\xf7\x3b" \
    "\xcd\xa2\x34\x8a\x73\x5d\x75\xd0\x16\x4b\x6e\xcc" \
    "\x7b\x06\xf3\xf9\xa5\x63\xde\x4f\x02\xd7\xab\xd6" \
    "\xd8\xcc\x96\x18\x9c\xd8\x68\xd6\xfc\x7c\x10\xe0" \
    "\x00\xc1\xb4\x49\x1d\x75\xde\xf7\x8d\x43\xf2\x60" \
    "\x18\xee\x47\x6a\x07\xdc\x4d\xe0\x90\xf7\xfe\x8a" \
    "\xd4\x03\x74\x48\xba\x53\x15\x2e\xe2\xcd\x59\x18" \
    "\x78\x31\x08\x1e\xd9\x64\x56\xfa\x9d\x39\xe0\x08" \
    "\xd2\x1f\x32\xdb\x6b\x50\x37\x05\xf4\x7b\xcf\x05" \
    "\xe9\x24\xb0\x5d\xd2\x44\x65\xc9\x2a\x61\x03\xda" \
    "\x63\x38\xf0\x92\x59\xd4\x72\x0f\x07\xc8\x03\x2e" \
    "\x01\x8e\x4a\xfc\x28\x8d\x78\xd8\x2a\xe9\x7c\x25" \
    "\x5a\x56\x63\x00\x15\xb2\xf4\xcf\x40\xdf\x71\x29" \
    "\xff\xab\x44\x06\xc8\x16\xc2\x65\x81\x3b\xc0\x88" \
    "\x74\xdb\xc3\xee\x5a\xe8\x02\xb8\x88\x4f\x01\x1d" \
    "\xd3\xf0\xf9\x6f\x30\x0b\x10\xa7\x62\x25\xd0\x19" \
    "\x04\x7f\x0f\x3a\x17\x0c\x9a\xb9\x5a\xb0\xd5\x6a" \
    "\xe9\x2f\xcc\x56\x67\x82\xe0\xe4\x32\x68\x84\x42" \
    "\xa1\x33\x40\xaa\xcd\x26\x0c\x0e\x26\xde\x7f\xba" \
    "\x59\xba\xbc\x28\xf8\x3b\xb3\xdc\x03\x41\xf0\x99" \
    "\x49\xad\x00\x53\x40\x8f\xc4\xa3\x66\x6c\x01\x72" \
    "\x69\x00\x86\xbd\xd4\x3d\x03\x03\xcf\x4a\xf3\x4d" \
    "\xb2\x10\x36\xb3\x73\xd0\x8e\xd9\x47\x06\x19\x0f" \
    "\x1c\x06\x7a\xa5\x49\x60\x69\x0b\xd8\xeb\x66\x3c" \
    "\x5e\xbe\x6b\x0e\x38\x8b\xd4\x93\x81\x6f\x9f\x96" \
    "\xa6\x16\xc0\xbf\x9b\x35\x7b\xb3\xa3\x01\x2c\x03" \
    "\x38\x0b\xbc\x2b\x5d\x9b\x84\x37\x80\x0d\xc0\xab" \
    "\x8d\xd0\xb0\xc3\x8c\x96\x62\x79\xca\x12\x48\xdb" \
    "\x9f\x92\x06\x91\x34\x1f\xc3\xb0\x62\xd8\x6c\xe8" \
    "\xa2\x99\x2e\x9a\xe9\x17\x33\xad\x83\x69\xa0\xb5" \
    "\x78\x00\x03\xd6\x03\xa7\x62\xf0\xdb\x40\xdf\x17" \
    "\xd7\x96\x62\x08\x76\x48\x62\x1e\x1d\x83\xdc\x28" \
    "\xf4\x8f\x82\x46\x41\x97\x41\x3b\x41\x01\xf4\x02" \
    "\x51\xfa\x00\x40\x03\xf0\x09\x70\xb7\x11\xb4\x0f" \
    "\xf4\x15\x68\x0f\x24\xeb\xa1\xad\x0c\xbe\x0e\x2f" \
    "\x8f\xc1\xdc\x38\x68\x1c\x74\x1a\xb4\x1c\x2e\x01" \
    "\xab\xd2\x68\x0a\x8f\x80\x56\xe0\xcf\x10\x94\x03" \
    "\x01\x9e\x42\x27\xde\x83\x4f\xc0\xe6\x2f\x61\xfc" \
    "\x06\xe8\x67\xd0\x0b\x85\x45\xbb\xab\xa1\x15\x09" \
    "\xd6\x02\x3d\xc0\x37\xc0\x2b\xc0\xc3\x65\x30\xf0" \
    "\x66\x0e\xfc\x73\xa0\x35\x85\xec\x17\x80\xc7\xfe" \
    "\x0b\x2e\xee\x0d\x81\xb8\xec\x5b\x6a\x72\x23\xd0" \
    "\x0d\x5c\x05\x4e\x01\xdb\x16\x83\xd6\x8a\x6a\x97" \
    "\xd0\x4a\x60\xb2\xda\x8d\x75\x3f\xe3\x5f\xbf\xdc" \
    "\x0a\xd6\x12\xa9\x67\xde\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"
image4_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\xcf\x49\x44\x41\x54\x38\x8d\xed\x94\x4d\x68\x13" \
    "\x51\x10\xc7\xe7\xbd\x7d\xd9\xec\x26\xeb\x26\x6d" \
    "\x92\x4d\x25\xa5\xb5\x55\x14\x2b\xf6\x54\xb4\x45" \
    "\xbc\x68\x05\xa9\x1f\x07\xc5\x83\x20\xa2\x20\xa5" \
    "\x07\x45\x0f\x1e\x44\x54\xd0\x83\x52\x4f\x82\x9e" \
    "\xc4\x0f\x54\x5a\x44\x2a\xa2\x22\x0a\x85\x88\x8a" \
    "\x1f\x68\x6c\x6b\xd1\xaa\x68\x1b\x5b\x35\x31\xb5" \
    "\x36\x5d\x9b\xd8\xdd\xcd\xdb\x37\x9e\x52\xab\xf6" \
    "\xda\x83\xe0\x9c\xe6\xf0\x9f\x1f\x33\xf0\x9f\x3f" \
    "\x41\x44\x98\x89\xa2\x33\x42\xfd\x0f\xfe\xb7\xc1" \
    "\xac\xd8\x6c\xdf\x7e\x58\x09\xea\x64\xbf\x99\x1d" \
    "\x6b\xe8\x7f\x9f\x2c\x7b\xd1\xfd\xb2\xd7\x2e\x90" \
    "\x4e\xcb\xd5\xdb\x10\x13\x85\xa9\x43\xfb\xf6\x9d" \
    "\xae\xd0\x54\x7a\x24\xd9\x3f\x58\x73\x37\xfe\x08" \
    "\x32\x5f\x46\x13\x0e\x61\xd7\x0a\x85\x67\x9d\x45" \
    "\x0d\x41\x44\x68\x6c\xdc\x13\x35\x42\x70\x6d\x5e" \
    "\x55\xb4\x6a\x51\x59\x30\x13\x09\x07\xa5\xec\xc8" \
    "\xc8\xc4\x95\xdb\x0f\xd4\xf8\xc3\x44\xdf\x48\xde" \
    "\x6d\x41\x1c\xcc\x02\x00\xac\x5b\xb7\x73\xe5\xfc" \
    "\xea\xc8\x89\x9a\xaa\x98\x1a\x55\xa9\xe9\xf1\xc8" \
    "\xac\xa7\xe7\x0d\xbf\x70\x33\x1e\x18\x18\x4a\xdf" \
    "\xb0\xc5\x87\xbd\x88\x28\x18\x00\x80\x65\x7d\x3d" \
    "\xee\x73\xf5\xc0\xfa\x85\x91\x97\xaa\x4f\x25\x00" \
    "\x02\xa2\xb1\x52\x38\xb0\x6d\xad\x69\x04\xfc\x95" \
    "\x67\xaf\xde\x39\x02\x00\xbb\x9a\x9a\xb6\xe8\x32" \
    "\xa1\x47\x17\xe9\x86\xb9\x34\xa6\x66\x8a\xdb\x95" \
    "\x2f\x5f\x08\x75\xf3\x42\xa3\x2d\xad\xe7\x57\x27" \
    "\x53\xe5\x09\x00\x68\x67\x73\x6a\x36\xce\x2e\x95" \
    "\xed\xfa\x5a\xb4\x13\xe9\x87\xf7\x27\xac\xef\x63" \
    "\xce\x8f\xcc\xb0\xad\x06\x82\x1e\x35\x1c\xf2\xd6" \
    "\x32\x57\x53\x55\xba\x86\x90\xc8\xa9\x05\xd5\x95" \
    "\x2b\x4a\x34\xc5\x08\xc7\x20\xfe\xee\x56\x1f\xcf" \
    "\x0f\x0f\xdb\xdc\xca\x73\x9f\x11\x55\x14\x3d\x28" \
    "\xaf\xac\x28\xb5\xce\xa5\x3f\xed\x00\x80\x76\x96" \
    "\x4e\xa6\x9a\x1d\xef\x84\xfc\xe3\xf3\xdb\xfe\x57" \
    "\xdc\x11\xc0\xc5\xaf\x1f\x67\x94\x00\x63\xd4\xb5" \
    "\xb4\x7a\x46\xe5\xe6\x54\xfa\x63\x1d\x61\xfc\x6b" \
    "\xdf\xd0\xe3\x8f\xbf\xe9\x00\x4c\x60\x94\xc8\xd4" \
    "\x97\x67\x44\xde\x40\x48\xc9\x56\xc6\x1d\x1b\x73" \
    "\x85\x71\x74\xfd\x0e\x4a\x42\xfc\x1e\x1c\x5c\xa0" \
    "\x2d\x38\x14\x84\xe4\x11\x88\x31\xcb\x12\x8a\x4d" \
    "\x39\x82\x2a\xfe\x0e\x18\x2e\x70\x5c\xb8\x12\xa2" \
    "\x47\x00\x50\x97\x0a\xc1\x4f\xda\x08\xd9\x17\x4e" \
    "\xa0\x6c\x3a\xdb\xf4\x73\x2d\x02\xc4\x6b\x0a\xf0" \
    "\xed\xa6\x92\x76\xe8\x1b\x2a\x5a\x1e\xa8\x67\x3a" \
    "\x6d\x37\xd7\x2a\x04\x28\x5d\x88\xa9\x36\x8a\xd8" \
    "\x9b\x45\x80\x8b\x9d\x8e\x56\xff\x5a\xe8\xc6\x54" \
    "\x61\x06\xbd\x5a\xdc\x31\xe6\x23\x94\x9c\x41\x1c" \
    "\xc8\xd8\xfc\x43\x27\x87\xe0\xd3\xeb\x56\x6c\x71" \
    "\x9e\xb2\x49\xb8\x4b\x29\xbd\xe7\x86\xe7\xbe\x13" \
    "\x7a\xb5\xc3\x42\xad\x93\x76\x23\xa4\xce\xa3\xb0" \
    "\xb1\x83\x80\x7c\xb3\x42\x88\x08\x12\xf8\x34\x4e" \
    "\xa4\x88\x0d\x04\x38\xa8\x1d\x96\x23\x1f\x2b\x7a" \
    "\x99\xcc\x5a\x66\xf8\x84\xd9\x2a\xa1\xd3\xe0\xa7" \
    "\xae\xa9\x10\x91\xcb\xa2\x54\x6e\x51\xc9\x46\xe6" \
    "\x3f\x6a\x8f\x76\x5d\x9e\x04\x17\xcb\xeb\xad\x5d" \
    "\x2c\xc0\xd9\x04\x84\x6a\x40\x58\x8e\x4a\x9e\x0e" \
    "\x3b\xf7\xbc\xf7\xcf\x93\x09\x21\x94\x19\x4b\x56" \
    "\x81\xe0\x8d\x40\x5d\x09\x80\xa4\xb8\xdf\x7b\x09" \
    "\x07\x9e\x4c\x5a\x90\xfc\x0f\xfa\x7f\x17\xfc\x13" \
    "\xc9\x2f\x4f\xb7\x05\xee\x2c\xf0\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"
image5_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\x9d\x49\x44\x41\x54\x38\x8d\xb5\x94\xcf\x4b\x54" \
    "\x51\x14\xc7\x3f\xf7\xcd\xd3\x37\xe9\xcc\xbc\x71" \
    "\x1c\x67\x74\x98\x07\x86\xab\xd2\x7d\x86\xa1\x08" \
    "\x11\x45\x85\x4a\xb4\x70\x27\x4a\x8b\x76\x2d\xfc" \
    "\x0b\x5a\x89\xc8\x20\x48\xb4\x10\x8c\x36\xc2\xa0" \
    "\x50\x38\x20\x04\xa1\x6d\x45\xa8\xb4\x8d\x2e\x02" \
    "\x09\xc2\x18\xc9\x19\xc7\x19\x66\x70\x7c\x9e\x16" \
    "\xf9\x63\x74\x9c\x1f\x15\x1d\x38\x8b\x7b\xdf\xf9" \
    "\x7e\x38\xef\x9e\xef\xbd\x4a\x44\xf8\x1f\xa1\x97" \
    "\xfb\xa8\x94\x52\x40\x2b\xe0\x2e\xd8\xde\x01\x12" \
    "\x22\x92\x2b\xab\x2d\xd5\xb1\x52\xea\xba\x89\xf9" \
    "\x2c\x4f\x7e\xc0\x8b\x57\x74\x74\x01\x70\xe0\x38" \
    "\xc8\x90\xd9\x03\xa2\x71\xe2\x33\x22\xf2\xbd\x6a" \
    "\xb0\x4f\xf9\xee\x1d\x71\xf4\xca\x8f\xdf\x33\xc0" \
    "\x80\xb3\x8b\x2e\x65\x60\x00\x90\x26\xcd\x0a\x2b" \
    "\x32\xc7\x5c\x6e\x97\xdd\x6f\x69\xd2\x8f\x45\xe4" \
    "\x4b\x45\xb0\xa1\x8c\x76\x27\xce\xf7\xbd\xf4\x06" \
    "\x86\x19\xd6\x3c\x78\xd8\x67\x9f\xa7\x3c\x45\x47" \
    "\x67\x8c\x31\x1a\x69\x24\x45\x8a\x69\xa6\x53\x2b" \
    "\xac\xac\x27\x49\xde\x17\x91\xd4\x39\x90\x88\x9c" \
    "\x26\xa0\x9a\x69\x7e\xdd\x41\x47\x2e\x46\x4c\xa2" \
    "\x44\xa5\x8f\xbe\xbd\x20\xc1\x9d\x93\x1a\x13\x33" \
    "\xd9\x49\x67\x36\x4a\x54\xe6\x99\x17\x0b\x6b\x3f" \
    "\x4c\xf8\x49\x21\x47\x44\x8a\xc0\x2d\x6e\xdc\xdb" \
    "\x43\x0c\xc9\x34\xd3\xd2\x45\x57\x36\x48\xf0\x03" \
    "\xf0\x10\xb8\x0a\xb4\xe8\xe8\x77\x5c\xb8\x36\xfb" \
    "\xe9\x4f\x2f\xb3\x2c\x23\x8c\xd8\x7e\xfc\x1f\x01" \
    "\x67\x21\xeb\xa2\x2b\x04\x68\x3c\x5b\x48\x6d\x92" \
    "\xe4\x88\x88\x7c\x2d\xa8\xd9\x76\x28\xc7\x8b\x55" \
    "\x56\x9f\x67\xc9\x62\x61\x69\x1a\x5a\x0b\x50\x03" \
    "\x9c\x3a\xe5\x1c\x58\x44\x7e\x78\x95\xf7\xd3\x02" \
    "\x0b\xfe\x18\x31\x01\xf6\x72\x92\x2b\x84\xa2\x94" \
    "\x6a\x08\x10\xb8\xdb\x46\x5b\xad\x81\xc1\x06\x1b" \
    "\x08\x92\x00\xf2\x85\x75\x45\x3e\x4e\x4a\xf2\xc6" \
    "\xc5\xbd\x93\xa8\x53\x75\x37\x03\x04\x5e\xd6\x50" \
    "\x73\x6d\x90\xc1\xda\x35\xd6\x58\x62\xe9\x40\x47" \
    "\x9f\x2d\xf2\xf5\xc5\x43\x2f\x95\x41\x82\x0f\x4c" \
    "\xcc\x9d\x1e\x7a\xf2\x33\xcc\x48\x84\x88\x84\x08" \
    "\x1d\x58\x58\x6f\x01\x77\xd9\xe1\x95\x4a\x13\xf3" \
    "\xb6\x0f\x5f\xa2\x8f\xbe\xa3\x45\x16\x25\x42\x44" \
    "\x82\x04\xb3\x16\xd6\x9b\xcb\xa0\x55\x81\x01\x67" \
    "\x13\x4d\x9f\xfb\xe9\xcf\x1f\x43\xed\x30\xe1\xbd" \
    "\x10\xa1\xf1\x52\xd0\xcb\x5c\x51\x14\x06\x86\x75" \
    "\xc8\x61\x5b\x37\xdd\x7a\x8e\x1c\x93\x4c\xa6\x33" \
    "\x64\xc6\x12\x24\xc6\x45\xc4\x2e\xa5\xab\x08\x76" \
    "\xe1\xea\xb4\xb1\x6b\x6d\x6c\xd6\x59\x67\x97\x5d" \
    "\x3d\x4d\x3a\x56\x0e\x0a\x65\x1e\xa1\xd3\x8e\x95" \
    "\xd1\x5e\x4f\xfd\xac\x86\x76\x05\x50\x0e\x1c\x5b" \
    "\x71\xe2\x8f\x8a\xae\xf0\x9f\x82\x01\x94\x52\xed" \
    "\x80\xf7\x78\xf9\x53\x44\x36\x2a\x69\x2a\x1e\x85" \
    "\x52\xaa\xd5\xc4\x7c\x67\x63\x37\x00\x38\x70\x24" \
    "\x94\x52\xb7\x44\x64\xeb\x9f\xc0\x80\xc7\xc6\x6e" \
    "\x18\x65\xb4\x0e\x60\x82\x09\x00\x4f\x25\x91\x56" \
    "\x05\xf8\xaf\xa2\x9a\x8e\x53\x1a\xda\xe6\x14\x53" \
    "\xee\xdf\x9d\x68\xfb\x40\xd9\xc1\x41\xf5\xc3\xab" \
    "\xe7\xec\xef\x8e\x44\x24\x53\x49\xf3\x0b\xdf\x5b" \
    "\xae\x1e\x18\x8b\x7a\x54\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"
image6_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x08" \
    "\x08\x06\x00\x00\x00\xf0\x76\x7f\x97\x00\x00\x00" \
    "\x42\x49\x44\x41\x54\x28\x91\x8d\xd0\xb1\x15\x00" \
    "\x20\x08\x03\xd1\xd3\xc9\x18\x9d\xcd\xb4\x55\x5f" \
    "\x08\xa6\xd5\xfb\x05\xd0\x6f\xb9\xc7\xd9\xc5\x99" \
    "\x69\x91\xf1\x11\x03\x10\x11\xf2\x7f\x05\x5c\xb1" \
    "\x43\x14\x20\xe3\x0a\x79\x01\x1b\x2b\xe4\x04\xec" \
    "\xb5\x8b\xb9\x1b\xfe\x6d\x03\xe1\x83\x16\x45\xa6" \
    "\xee\x58\x99\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"

class nanotube_dialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image2 = QPixmap()
        self.image2.loadFromData(image2_data,"PNG")
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        self.image4 = QPixmap()
        self.image4.loadFromData(image4_data,"PNG")
        self.image5 = QPixmap()
        self.image5.loadFromData(image5_data,"PNG")
        self.image6 = QPixmap()
        self.image6.loadFromData(image6_data,"PNG")
        if not name:
            self.setName("nanotube_dialog")

        self.setIcon(self.image0)

        nanotube_dialogLayout = QVBoxLayout(self,0,0,"nanotube_dialogLayout")

        self.heading_frame = QFrame(self,"heading_frame")
        self.heading_frame.setPaletteBackgroundColor(QColor(122,122,122))
        self.heading_frame.setFrameShape(QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QFrame.Plain)
        heading_frameLayout = QHBoxLayout(self.heading_frame,0,3,"heading_frameLayout")

        self.heading_pixmap = QLabel(self.heading_frame,"heading_pixmap")
        self.heading_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.heading_pixmap.sizePolicy().hasHeightForWidth()))
        self.heading_pixmap.setPixmap(self.image1)
        self.heading_pixmap.setScaledContents(1)
        heading_frameLayout.addWidget(self.heading_pixmap)

        self.heading_label = QLabel(self.heading_frame,"heading_label")
        self.heading_label.setPaletteForegroundColor(QColor(255,255,255))
        heading_label_font = QFont(self.heading_label.font())
        heading_label_font.setPointSize(12)
        heading_label_font.setBold(1)
        self.heading_label.setFont(heading_label_font)
        heading_frameLayout.addWidget(self.heading_label)
        nanotube_dialogLayout.addWidget(self.heading_frame)

        self.sponsor_frame = QFrame(self,"sponsor_frame")
        self.sponsor_frame.setPaletteBackgroundColor(QColor(230,230,230))
        self.sponsor_frame.setFrameShape(QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QFrame.Plain)
        sponsor_frameLayout = QGridLayout(self.sponsor_frame,1,1,0,0,"sponsor_frameLayout")

        self.sponsor_btn = QPushButton(self.sponsor_frame,"sponsor_btn")
        self.sponsor_btn.setMaximumSize(QSize(32767,32767))
        self.sponsor_btn.setPaletteBackgroundColor(QColor(255,255,255))
        self.sponsor_btn.setAutoDefault(0)
        self.sponsor_btn.setFlat(1)

        sponsor_frameLayout.addWidget(self.sponsor_btn,0,0)
        nanotube_dialogLayout.addWidget(self.sponsor_frame)

        self.body_frame = QFrame(self,"body_frame")
        self.body_frame.setFrameShape(QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QFrame.Raised)
        body_frameLayout = QVBoxLayout(self.body_frame,3,3,"body_frameLayout")

        layout59 = QHBoxLayout(None,0,6,"layout59")
        left_spacer = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(left_spacer)

        self.done_btn = QToolButton(self.body_frame,"done_btn")
        self.done_btn.setIconSet(QIconSet(self.image2))
        layout59.addWidget(self.done_btn)

        self.abort_btn = QToolButton(self.body_frame,"abort_btn")
        self.abort_btn.setIconSet(QIconSet(self.image3))
        layout59.addWidget(self.abort_btn)

        self.preview_btn = QToolButton(self.body_frame,"preview_btn")
        self.preview_btn.setIconSet(QIconSet(self.image4))
        layout59.addWidget(self.preview_btn)

        self.whatsthis_btn = QToolButton(self.body_frame,"whatsthis_btn")
        self.whatsthis_btn.setIconSet(QIconSet(self.image5))
        layout59.addWidget(self.whatsthis_btn)
        right_spacer = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(right_spacer)
        body_frameLayout.addLayout(layout59)

        self.parameters_grpbox = QGroupBox(self.body_frame,"parameters_grpbox")
        self.parameters_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.parameters_grpbox.setFrameShadow(QGroupBox.Sunken)
        self.parameters_grpbox.setMargin(0)
        self.parameters_grpbox.setColumnLayout(0,Qt.Vertical)
        self.parameters_grpbox.layout().setSpacing(1)
        self.parameters_grpbox.layout().setMargin(4)
        parameters_grpboxLayout = QVBoxLayout(self.parameters_grpbox.layout())
        parameters_grpboxLayout.setAlignment(Qt.AlignTop)

        layout42 = QHBoxLayout(None,0,6,"layout42")

        self.parameters_grpbox_label = QLabel(self.parameters_grpbox,"parameters_grpbox_label")
        self.parameters_grpbox_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.parameters_grpbox_label.sizePolicy().hasHeightForWidth()))
        self.parameters_grpbox_label.setPaletteForegroundColor(QColor(0,0,255))
        self.parameters_grpbox_label.setAlignment(QLabel.AlignVCenter)
        layout42.addWidget(self.parameters_grpbox_label)
        spacer21 = QSpacerItem(67,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout42.addItem(spacer21)

        self.nt_parameters_grpbtn = QPushButton(self.parameters_grpbox,"nt_parameters_grpbtn")
        self.nt_parameters_grpbtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.nt_parameters_grpbtn.sizePolicy().hasHeightForWidth()))
        self.nt_parameters_grpbtn.setMaximumSize(QSize(16,16))
        self.nt_parameters_grpbtn.setIconSet(QIconSet(self.image6))
        self.nt_parameters_grpbtn.setFlat(1)
        layout42.addWidget(self.nt_parameters_grpbtn)
        parameters_grpboxLayout.addLayout(layout42)

        self.line2 = QFrame(self.parameters_grpbox,"line2")
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setMidLineWidth(0)
        self.line2.setFrameShape(QFrame.HLine)
        parameters_grpboxLayout.addWidget(self.line2)

        nt_parameters_body_layout = QGridLayout(None,1,1,0,6,"nt_parameters_body_layout")

        self.chirality_n_label = QLabel(self.parameters_grpbox,"chirality_n_label")
        self.chirality_n_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.chirality_n_label,2,0)

        self.chirality_m_spinbox = QSpinBox(self.parameters_grpbox,"chirality_m_spinbox")
        self.chirality_m_spinbox.setMinValue(0)
        self.chirality_m_spinbox.setValue(5)

        nt_parameters_body_layout.addWidget(self.chirality_m_spinbox,3,1)

        self.chirality_m_label = QLabel(self.parameters_grpbox,"chirality_m_label")
        self.chirality_m_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.chirality_m_label,3,0)

        self.length_label = QLabel(self.parameters_grpbox,"length_label")
        self.length_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.length_label,1,0)

        self.chirality_n_spinbox = QSpinBox(self.parameters_grpbox,"chirality_n_spinbox")
        self.chirality_n_spinbox.setMinValue(0)
        self.chirality_n_spinbox.setValue(5)

        nt_parameters_body_layout.addWidget(self.chirality_n_spinbox,2,1)

        self.members_combox = QComboBox(0,self.parameters_grpbox,"members_combox")

        nt_parameters_body_layout.addWidget(self.members_combox,0,1)

        self.endings_label = QLabel(self.parameters_grpbox,"endings_label")
        self.endings_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.endings_label,5,0)

        self.bond_length_label = QLabel(self.parameters_grpbox,"bond_length_label")
        self.bond_length_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.bond_length_label,4,0)

        self.endings_combox = QComboBox(0,self.parameters_grpbox,"endings_combox")

        nt_parameters_body_layout.addWidget(self.endings_combox,5,1)

        self.length_linedit = QLineEdit(self.parameters_grpbox,"length_linedit")

        nt_parameters_body_layout.addWidget(self.length_linedit,1,1)

        self.members_label = QLabel(self.parameters_grpbox,"members_label")
        self.members_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_parameters_body_layout.addWidget(self.members_label,0,0)

        self.bond_length_linedit = QLineEdit(self.parameters_grpbox,"bond_length_linedit")

        nt_parameters_body_layout.addWidget(self.bond_length_linedit,4,1)
        parameters_grpboxLayout.addLayout(nt_parameters_body_layout)
        body_frameLayout.addWidget(self.parameters_grpbox)

        self.tube_distortions_grpbox = QGroupBox(self.body_frame,"tube_distortions_grpbox")
        self.tube_distortions_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.tube_distortions_grpbox.setFrameShadow(QGroupBox.Sunken)
        self.tube_distortions_grpbox.setCheckable(0)
        self.tube_distortions_grpbox.setChecked(0)
        self.tube_distortions_grpbox.setColumnLayout(0,Qt.Vertical)
        self.tube_distortions_grpbox.layout().setSpacing(1)
        self.tube_distortions_grpbox.layout().setMargin(4)
        tube_distortions_grpboxLayout = QVBoxLayout(self.tube_distortions_grpbox.layout())
        tube_distortions_grpboxLayout.setAlignment(Qt.AlignTop)

        layout43 = QHBoxLayout(None,0,6,"layout43")

        self.parameters_grpbox_label_2 = QLabel(self.tube_distortions_grpbox,"parameters_grpbox_label_2")
        self.parameters_grpbox_label_2.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding,0,0,self.parameters_grpbox_label_2.sizePolicy().hasHeightForWidth()))
        self.parameters_grpbox_label_2.setPaletteForegroundColor(QColor(0,0,255))
        self.parameters_grpbox_label_2.setAlignment(QLabel.AlignVCenter)
        layout43.addWidget(self.parameters_grpbox_label_2)
        spacer21_2 = QSpacerItem(50,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout43.addItem(spacer21_2)

        self.nt_distortion_grpbtn = QPushButton(self.tube_distortions_grpbox,"nt_distortion_grpbtn")
        self.nt_distortion_grpbtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.nt_distortion_grpbtn.sizePolicy().hasHeightForWidth()))
        self.nt_distortion_grpbtn.setMaximumSize(QSize(16,16))
        self.nt_distortion_grpbtn.setIconSet(QIconSet(self.image6))
        self.nt_distortion_grpbtn.setFlat(1)
        layout43.addWidget(self.nt_distortion_grpbtn)
        tube_distortions_grpboxLayout.addLayout(layout43)

        self.line2_2 = QFrame(self.tube_distortions_grpbox,"line2_2")
        self.line2_2.setFrameShape(QFrame.HLine)
        self.line2_2.setFrameShadow(QFrame.Sunken)
        self.line2_2.setMidLineWidth(0)
        self.line2_2.setFrameShape(QFrame.HLine)
        tube_distortions_grpboxLayout.addWidget(self.line2_2)

        nt_distortions_body_layout = QGridLayout(None,1,1,0,6,"nt_distortions_body_layout")

        self.z_distortion_label = QLabel(self.tube_distortions_grpbox,"z_distortion_label")
        self.z_distortion_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_distortions_body_layout.addWidget(self.z_distortion_label,0,0)

        self.xy_distortion_label = QLabel(self.tube_distortions_grpbox,"xy_distortion_label")
        self.xy_distortion_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_distortions_body_layout.addWidget(self.xy_distortion_label,1,0)

        self.twist_spinbox = QSpinBox(self.tube_distortions_grpbox,"twist_spinbox")
        self.twist_spinbox.setMinValue(0)
        self.twist_spinbox.setValue(0)

        nt_distortions_body_layout.addWidget(self.twist_spinbox,2,1)

        self.z_distortion_linedit = QLineEdit(self.tube_distortions_grpbox,"z_distortion_linedit")

        nt_distortions_body_layout.addWidget(self.z_distortion_linedit,0,1)

        self.bend_label = QLabel(self.tube_distortions_grpbox,"bend_label")
        self.bend_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_distortions_body_layout.addWidget(self.bend_label,3,0)

        self.bend_spinbox = QSpinBox(self.tube_distortions_grpbox,"bend_spinbox")
        self.bend_spinbox.setMinValue(0)
        self.bend_spinbox.setValue(0)

        nt_distortions_body_layout.addWidget(self.bend_spinbox,3,1)

        self.xy_distortion_linedit = QLineEdit(self.tube_distortions_grpbox,"xy_distortion_linedit")

        nt_distortions_body_layout.addWidget(self.xy_distortion_linedit,1,1)

        self.twist_label = QLabel(self.tube_distortions_grpbox,"twist_label")
        self.twist_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        nt_distortions_body_layout.addWidget(self.twist_label,2,0)
        tube_distortions_grpboxLayout.addLayout(nt_distortions_body_layout)
        body_frameLayout.addWidget(self.tube_distortions_grpbox)

        self.mwcnt_grpbox = QGroupBox(self.body_frame,"mwcnt_grpbox")
        self.mwcnt_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.mwcnt_grpbox.setFrameShadow(QGroupBox.Sunken)
        self.mwcnt_grpbox.setCheckable(0)
        self.mwcnt_grpbox.setChecked(0)
        self.mwcnt_grpbox.setColumnLayout(0,Qt.Vertical)
        self.mwcnt_grpbox.layout().setSpacing(1)
        self.mwcnt_grpbox.layout().setMargin(4)
        mwcnt_grpboxLayout = QVBoxLayout(self.mwcnt_grpbox.layout())
        mwcnt_grpboxLayout.setAlignment(Qt.AlignTop)

        layout44 = QHBoxLayout(None,0,6,"layout44")

        self.parameters_grpbox_label_3 = QLabel(self.mwcnt_grpbox,"parameters_grpbox_label_3")
        self.parameters_grpbox_label_3.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.parameters_grpbox_label_3.sizePolicy().hasHeightForWidth()))
        self.parameters_grpbox_label_3.setPaletteForegroundColor(QColor(0,0,255))
        self.parameters_grpbox_label_3.setAlignment(QLabel.AlignVCenter)
        layout44.addWidget(self.parameters_grpbox_label_3)
        spacer21_3 = QSpacerItem(40,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout44.addItem(spacer21_3)

        self.mwcnt_grpbtn = QPushButton(self.mwcnt_grpbox,"mwcnt_grpbtn")
        self.mwcnt_grpbtn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.mwcnt_grpbtn.sizePolicy().hasHeightForWidth()))
        self.mwcnt_grpbtn.setMaximumSize(QSize(16,16))
        self.mwcnt_grpbtn.setIconSet(QIconSet(self.image6))
        self.mwcnt_grpbtn.setFlat(1)
        layout44.addWidget(self.mwcnt_grpbtn)
        mwcnt_grpboxLayout.addLayout(layout44)

        self.line2_3 = QFrame(self.mwcnt_grpbox,"line2_3")
        self.line2_3.setFrameShape(QFrame.HLine)
        self.line2_3.setFrameShadow(QFrame.Sunken)
        self.line2_3.setMidLineWidth(0)
        self.line2_3.setFrameShape(QFrame.HLine)
        mwcnt_grpboxLayout.addWidget(self.line2_3)

        mwcnt_body_layout = QGridLayout(None,1,1,0,6,"mwcnt_body_layout")

        self.mwcnt_spacing_label = QLabel(self.mwcnt_grpbox,"mwcnt_spacing_label")
        self.mwcnt_spacing_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        mwcnt_body_layout.addWidget(self.mwcnt_spacing_label,1,0)

        self.mwcnt_count_label = QLabel(self.mwcnt_grpbox,"mwcnt_count_label")
        self.mwcnt_count_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        mwcnt_body_layout.addWidget(self.mwcnt_count_label,0,0)

        self.mwcnt_count_spinbox = QSpinBox(self.mwcnt_grpbox,"mwcnt_count_spinbox")
        self.mwcnt_count_spinbox.setMinValue(0)
        self.mwcnt_count_spinbox.setValue(1)

        mwcnt_body_layout.addWidget(self.mwcnt_count_spinbox,0,1)

        self.mwcnt_spacing_linedit = QLineEdit(self.mwcnt_grpbox,"mwcnt_spacing_linedit")

        mwcnt_body_layout.addWidget(self.mwcnt_spacing_linedit,1,1)
        mwcnt_grpboxLayout.addLayout(mwcnt_body_layout)
        body_frameLayout.addWidget(self.mwcnt_grpbox)
        nanotube_dialogLayout.addWidget(self.body_frame)
        spacer14 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        nanotube_dialogLayout.addItem(spacer14)

        layout42_2 = QHBoxLayout(None,4,6,"layout42_2")
        spacer20 = QSpacerItem(59,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout42_2.addItem(spacer20)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        layout42_2.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(self,"ok_btn")
        layout42_2.addWidget(self.ok_btn)
        nanotube_dialogLayout.addLayout(layout42_2)

        self.languageChange()

        self.resize(QSize(244,597).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.nt_distortion_grpbtn,SIGNAL("clicked()"),self.toggle_nt_distortion_grpbox)
        self.connect(self.nt_parameters_grpbtn,SIGNAL("clicked()"),self.toggle_nt_parameters_grpbox)
        self.connect(self.mwcnt_grpbtn,SIGNAL("clicked()"),self.toggle_mwcnt_grpbox)
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),self.enter_WhatsThisMode)
        self.connect(self.done_btn,SIGNAL("clicked()"),self.doneClicked)
        self.connect(self.abort_btn,SIGNAL("clicked()"),self.abortClicked)
        self.connect(self.preview_btn,SIGNAL("clicked()"),self.previewClicked)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.cancel_btn_clicked)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.ok_btn_clicked)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.sponsor_btn_clicked)
        self.connect(self.length_linedit,SIGNAL("textChanged(const QString&)"),self.length_fixup)


    def languageChange(self):
        self.setCaption(self.__tr("Nanotube"))
        self.heading_label.setText(self.__tr("Nanotube"))
        self.sponsor_btn.setText(QString.null)
        self.done_btn.setText(QString.null)
        QToolTip.add(self.done_btn,self.__tr("Done"))
        self.abort_btn.setText(QString.null)
        QToolTip.add(self.abort_btn,self.__tr("Cancel"))
        self.preview_btn.setText(QString.null)
        QToolTip.add(self.preview_btn,self.__tr("Preview"))
        self.whatsthis_btn.setText(QString.null)
        QToolTip.add(self.whatsthis_btn,self.__tr("What's This Help"))
        self.parameters_grpbox.setTitle(QString.null)
        self.parameters_grpbox_label.setText(self.__tr("Nanotube Parameters"))
        self.nt_parameters_grpbtn.setText(QString.null)
        self.chirality_n_label.setText(self.__tr("Chirality (n) :"))
        self.chirality_m_spinbox.setSuffix(QString.null)
        self.chirality_m_label.setText(self.__tr("Chirality (m) :"))
        self.length_label.setText(self.__tr("Length (A) :"))
        self.chirality_n_spinbox.setSuffix(QString.null)
        self.members_combox.clear()
        self.members_combox.insertItem(self.__tr("C - C"))
        self.members_combox.insertItem(self.__tr("B - N"))
        self.endings_label.setText(self.__tr("Endings :"))
        self.bond_length_label.setText(self.__tr("Bond Length :"))
        self.endings_combox.clear()
        self.endings_combox.insertItem(self.__tr("None"))
        self.endings_combox.insertItem(self.__tr("Capped"))
        self.endings_combox.insertItem(self.__tr("Hydrogen"))
        self.endings_combox.insertItem(self.__tr("Nitrogen"))
        self.length_linedit.setText(self.__tr("20.0"))
        self.members_label.setText(self.__tr("Members :"))
        self.bond_length_linedit.setText(self.__tr("1.41 A"))
        self.tube_distortions_grpbox.setTitle(QString.null)
        self.parameters_grpbox_label_2.setText(self.__tr("Nanotube Distortions"))
        self.nt_distortion_grpbtn.setText(QString.null)
        self.z_distortion_label.setText(self.__tr("Z-distortion :"))
        self.xy_distortion_label.setText(self.__tr("XY-distortion :"))
        self.twist_spinbox.setSuffix(self.__tr(" deg/A"))
        self.z_distortion_linedit.setText(self.__tr("1.0 A"))
        self.bend_label.setText(self.__tr("Bend :"))
        self.bend_spinbox.setSuffix(self.__tr(" deg"))
        self.xy_distortion_linedit.setText(self.__tr("1.0 A"))
        self.twist_label.setText(self.__tr("Twist :"))
        self.mwcnt_grpbox.setTitle(QString.null)
        self.parameters_grpbox_label_3.setText(self.__tr("Multi-Walled Nanotubes"))
        self.mwcnt_grpbtn.setText(QString.null)
        self.mwcnt_spacing_label.setText(self.__tr("Spacing :"))
        self.mwcnt_count_label.setText(self.__tr("Number of Nanotubes :"))
        self.mwcnt_count_spinbox.setSuffix(QString.null)
        self.mwcnt_spacing_linedit.setText(self.__tr("2.46 A"))
        self.cancel_btn.setText(self.__tr("Cancel"))
        self.ok_btn.setText(self.__tr("OK"))


    def toggle_nt_distortion_grpbox(self):
        print "nanotube_dialog.toggle_nt_distortion_grpbox(): Not implemented yet"

    def open_sponsor_homepage(self):
        print "nanotube_dialog.open_sponsor_homepage(): Not implemented yet"

    def toggle_nt_parameters_grpbox(self):
        print "nanotube_dialog.toggle_nt_parameters_grpbox(): Not implemented yet"

    def toggle_mwcnt_grpbox(self):
        print "nanotube_dialog.toggle_mwcnt_grpbox(): Not implemented yet"

    def enter_WhatsThisMode(self):
        print "nanotube_dialog.enter_WhatsThisMode(): Not implemented yet"

    def changeLength(self):
        print "nanotube_dialog.changeLength(): Not implemented yet"

    def nChanged(self,a0):
        print "nanotube_dialog.nChanged(const QString&): Not implemented yet"

    def mChanged(self,a0):
        print "nanotube_dialog.mChanged(const QString&): Not implemented yet"

    def bondLengthChanged(self):
        print "nanotube_dialog.bondLengthChanged(): Not implemented yet"

    def doneClicked(self):
        print "nanotube_dialog.doneClicked(): Not implemented yet"

    def abortClicked(self):
        print "nanotube_dialog.abortClicked(): Not implemented yet"

    def previewClicked(self):
        print "nanotube_dialog.previewClicked(): Not implemented yet"

    def zDistortChanged(self):
        print "nanotube_dialog.zDistortChanged(): Not implemented yet"

    def xyDistortChanged(self):
        print "nanotube_dialog.xyDistortChanged(): Not implemented yet"

    def cancel_btn_clicked(self):
        print "nanotube_dialog.cancel_btn_clicked(): Not implemented yet"

    def ok_btn_clicked(self):
        print "nanotube_dialog.ok_btn_clicked(): Not implemented yet"

    def sponsor_btn_clicked(self):
        print "nanotube_dialog.sponsor_btn_clicked(): Not implemented yet"

    def length_fixup(self):
        print "nanotube_dialog.length_fixup(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("nanotube_dialog",s,c)
