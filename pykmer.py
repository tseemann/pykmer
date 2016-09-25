
# Some useful constants
m1 = 0x5555555555555555 # 01010101...
m2 = 0x3333333333333333 # 00110011...
m3 = 0x0F0F0F0F0F0F0F0F # 00001111...
m4 = 0x00FF00FF00FF00FF # 0818...
m5 = 0x0000FFFF0000FFFF # 016116...
m6 = 0x00000000FFFFFFFF # 032132

def readFasta(file):
    "Read a FASTA file, and generate (name, sequence) tuples"
    nm = None
    seq = []
    for l in file:
        l = l.strip()
        if len(l) and l[0] == '>':
            if nm is not None:
                yield (nm, ''.join(seq))
            nm = l[1:].strip()
            seq = []
        else:
            seq.append(l)
    if nm is not None:
        yield (nm, ''.join(seq))

def readFastq(file):
    "Read a FASTQ file, and generate (id, sequence, id2, quality) tuples"
    grp = []
    for l in file:
        l = l.strip()
        grp.append(l)
        if len(grp) == 4:
            yield tuple(grp)
            grp = []
    if grp == 4:
        yield tuple(grp)

nuc = { 'A':0, 'a':0, 'C':1, 'c':1, 'G':2, 'g':2, 'T':3, 't':3 }

def make_kmer(seq):
    "Turn a string in to an integer k-mer"
    r = 0
    for c in seq:
        if c not in nuc:
            return None
        r = (r << 2) | nuc[c]
    return r

def render(k, x):
    "Turn an integer k-mer in to a string"
    r = []
    for i in range(k):
        r.append("ACGT"[x&3])
        x >>= 2
    return ''.join(r[::-1])

def rev(x):
    "Reverse the bit-pairs in an integer"
    x = ((x >> 2) & m2) | ((x & m2) << 2)
    x = ((x >> 4) & m3) | ((x & m3) << 4)
    x = ((x >> 8) & m4) | ((x & m4) << 8)
    x = ((x >> 16) & m5) | ((x & m5) << 16)
    x = ((x >> 32) & m6) | ((x & m6) << 32)
    return x

def rc(k, x):
    "Compute the reverse complement of a k-mer"
    return rev(~x) >> (64 - 2*k)

def popcnt(x):
    "Compute the number of set bits in a 64-bit integer"
    x = (x & m1) + ((x >> 1) & m1)
    x = (x & m2) + ((x >> 2) & m2)
    x = (x & m3) + ((x >> 4) & m3)
    x = (x & m4) + ((x >> 8) & m4)
    x = (x & m5) + ((x >> 16) & m5)
    x = (x & m6) + ((x >> 32) & m6)
    return x & 0x7F

def ham(x, y):
    "Compute the hamming distance between two k-mers."
    z = x ^ y
    # NB: if k > 32, the constant below will need extending.
    v = (z | (z >> 1)) & m1
    return popcnt(v)

def ffs(x):
    "Find the position of the most significant bit"
    r = (x > 0xFFFFFFFF) << 5
    x >>= r
    s = (x > 0xFFFF) << 4
    x >>= s
    r |= s
    s = (x > 0xFF) << 3
    x >>= s
    r |= s
    s = (x > 0xF) << 2
    x >>= s
    r |= s
    s = (x > 0x3) << 1
    x >>= s
    r |= s
    r |= (x >> 1)
    return r


def lcp(k, x, y):
    "Find the length of the common prefix between 2 k-mers"
    z = x ^ y
    if z == 0:
        return k
    v = 1 + ffs(z) // 2
    return k - v

def kmers(k, str, bothStrands=False):
    "Extract k-mers from a string sequence"
    for i in range(len(str) - k + 1):
        x = make_kmer(str[i:i+k])
        if x:
            yield x
            if bothStrands:
                yield rc(k, x)
