import struct

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def unpack(buffer):
    return unpack_buffer(list(chunks(buffer, 2)))

def unpack_buffer(buffer):
    return [struct.unpack('h', frame)[0] for frame in buffer]

def pack(buffer):
  return [struct.pack('h', i) for i in buffer]
