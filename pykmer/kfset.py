from codec8 import encode, decode
import pykmer.container as container

meta = {
    'type' : 'k-mer frequency set',
    'version' : 20160930,
    'K' : None
}


def write(k, xs, nm, extra = None):
    m = meta.copy()
    m['K'] = k
    if extra is not None:
        for (k, v) in extra.items():
            if k in m:
                raise MetaDataIncompatible(k, m[k], v)
            m[k] = v
    f = container.make(nm, m)
    p = 0
    for (x,c) in xs:
        assert x == 0 or p < x
        d = x - p
        bs = bytearray(encode(d))
        f.write(bs)
        bs = bytearray(encode(c))
        f.write(bs)
        p = x

def read0(itr):
    x = 0
    while True:
        try:
            x += decode(itr)
            c = decode(itr)
            yield (x,c)
        except StopIteration:
            return

def read(nm):
    (m, itr) = container.probe(nm, meta)
    return (m, read0(itr))

def probeK(nm):
    (m, itr) = container.probe(nm, meta)
    return m['K']