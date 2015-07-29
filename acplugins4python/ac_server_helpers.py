import struct
import codecs

class GenericStructParser:
    def __init__(self, fmt, converter = lambda x: x):
        self.fmt = fmt
        self.converter = converter
        
    def get(self,b,k):
        r=struct.unpack_from(self.fmt,b,k)
        if len(r) == 1:
            r = r[0]
        return self.converter(r),k+struct.calcsize(self.fmt)
    
    def put(self,v):
        try:
            v[0]
        except:
            v = [v]
        return struct.pack(self.fmt,*v)
    
class GenericArrayParser:
    def __init__(self, lFmt, eSize, decode, encode):
        self.lFmt = lFmt
        self.eSize = eSize
        self.decode = decode
        self.encode = encode
        
    def get(self,b,k):
        l,=struct.unpack_from(self.lFmt,b,k)
        k += struct.calcsize(self.lFmt)
        nk = k+self.eSize*l
        raw = b[k:nk]
        return self.decode(raw),nk
        
    def put(self,v):
        raw = self.encode(v)
        l = len(raw)//self.eSize
        return struct.pack(self.lFmt,l) + raw
    
Uint8 = GenericStructParser('B')
Bool = GenericStructParser('B', lambda x: x != 0)
Uint16 = GenericStructParser('H')
Uint32 = GenericStructParser('I')
Float = GenericStructParser('f')
Vector3f = GenericStructParser('fff')
Ascii = GenericArrayParser(
    'B', 1, 
    lambda x: codecs.decode(x, 'ascii', 'replace'),
    lambda x: codecs.encode(x, 'ascii', 'strict'),
)
UTF32 = GenericArrayParser(
    'B', 4,
    lambda x: codecs.decode(x, 'utf-32', 'replace'),
    lambda x: codecs.encode(x, 'utf-32', 'strict'),
)

class GenericPacket:
    def __init__(self, **kw):
        if len(kw):
            for f,p in self._content:
                setattr(self, f, kw[f])

    def from_buffer(self, buffer, idx):
        for f,p in self._content:
            r,idx = p.get(buffer,idx)
            setattr(self,f,r)
        return idx,self
        
    def to_buffer(self):
        res = struct.pack('B', self.packetId)
        for f,p in self._content:
            res += p.put(getattr(self,f))
        return res

    def __str__(self):
        res = str(type(self)) + "("
        for f,_ in self._content:
            v = getattr(self, f, None)
            if type(v) == tuple:
                v = tuple(str(x) for x in v)
            res += f + "=" + str(v) + ", "
        res += ")"
        return res