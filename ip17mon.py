# -*- coding: utf-8 -*-

import os
import socket
import struct
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
try:
    import mmap
except ImportError:
    mmap = None

__all__ = ['IPv4Database', 'find']

_unpack_V = lambda b: struct.unpack("<L", b)[0]
_unpack_N = lambda b: struct.unpack(">L", b)[0]

def _unpack_C(b):
    if isinstance(b, int):
        return b
    return struct.unpack("B", b)[0]


datfile = os.path.join(os.path.dirname(__file__), "mydata4vipday2.datx")


class IPv4Database(object):
    def __init__(self, filename=None, use_mmap=True):
        if filename is None:
            filename = datfile
        with open(filename, 'rb') as f:
            if use_mmap and mmap is not None:
                buf = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            else:
                buf = f.read()
                use_mmap = False

        self._use_mmap = use_mmap
        self._buf = buf

        self._offset = _unpack_N(buf[:4])
        self._is_closed = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self._use_mmap:
            self._buf.close()
        self._is_closed = True

    def _lookup_ipv4(self, ip):
        index_offset = None
        index_length = None
        nip = socket.inet_aton(ip)
        # first IP number
        fip = bytearray(nip)[0]
        # second IP number
        sip = bytearray(nip)[1]
        # 4 + (fip - 1) * 4
        tmp_offset = (fip * 256 + sip) * 4
        # position in the index block
        start = _unpack_V(self._buf[tmp_offset:tmp_offset + 4])
        start = start * 9 + 262148
        max_comp_len = self._offset - 262148

        while start < max_comp_len:
            if self._buf[start:start + 4] >= nip:
                index_offset = _unpack_V(self._buf[start + 4:start + 7] + b'\0')
                index_length = _unpack_C(self._buf[start + 8])
                break
            start += 9

        if index_offset == self._offset:
            return None

        offset = self._offset + index_offset - 262144

        value = self._buf[offset:offset + index_length]
        return value.decode('utf-8').strip()

    def find(self, ip):
        if self._is_closed:
            raise ValueError('I/O operation on closed dat file')

        return self._lookup_ipv4(ip)


def find(ip):
    # keep find for compatibility
    result = {'stat': 'fail',
              'area': [],
              'location': {'latitude': None, 'longitude': None}}
    try:
        ip = socket.gethostbyname(ip)
    except socket.gaierror:
        return result

    with IPv4Database() as db:
        data = db.find(ip)

    if data:
        result['stat'] = 'ok'
        ipinfo = data.split('\t')
        if len(ipinfo) >= 5:
            result['area'] = ipinfo[:5]
        else:
            result['area'] = ['','','',ipinfo[0],'']
        if len(ipinfo) >= 6:
                try:
                    result['location']['latitude'] = float(ipinfo[5])
                    result['location']['longitude'] = float(ipinfo[6])
                except:
                    pass
    return result
