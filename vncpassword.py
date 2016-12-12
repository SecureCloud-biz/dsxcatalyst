#!/usr/bin/python
# https://gist.github.com/pudquick/1bff29ea56a93089dcfc
# A python implementation of https://communities.vmware.com/docs/DOC-7535
# "Compute hashed password for use with RemoteDisplay.vnc.key"

# d3des from here: https://vnc2flv.googlecode.com/svn-history/r2/trunk/vnc2flv/vnc2flv/d3des.py
# (Available all over the place, but apparently originally from here)

from __future__ import print_function
from d3des import deskey
import sys
import base64
import struct


def generate_vmware_vncpassword(password):
    # Passwords are 8 characters max, unused bytes are filled with null
    c_password = (password + '\x00'*8)[:8]
    encrypted = deskey(c_password, False)
    # The result is an array of 32 32-bit numbers, aka 1024 bits
    # Using struct.pack, we convert each 32-bit integer into 4 bytes (for a total of 128 bytes/characters)
    encrypted_bytes = struct.pack('i'*32, *encrypted)
    # Convert to base64 encoding
    encrypted_string = base64.b64encode(encrypted_bytes)
    return 'RemoteDisplay.vnc.key = "' + encrypted_string


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: vmware-vncpasswd.py <passphrase>")
    else:
        print(generate_vmware_vncpassword(sys.argv[1]))
