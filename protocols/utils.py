import struct
import bitarray

def unpackaddr(data:bytearray, offset=0):
    if isinstance(data, bytes):
        data = bytearray(data)
    ln = struct.unpack('=B', data[offset:offset+1])[0]
    addr = struct.unpack(f'{ln}H', data[offset+1:offset+2+ln*2])
    return addr

def packaddr(addr:list[int]):
    data = struct.pack(f'=B{len(addr)}H', len(addr), *addr)
    return data

def packflag(flags: list[bool]):
    data = bitarray.bitarray(flags)
    return bytearray(data.tobytes())

def unpackflags(data: bytearray):
    flags = bitarray.bitarray(data)
    return flags.tolist()