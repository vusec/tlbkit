import unittest
import subprocess
import collections

def popcount_py(x):
        return bin(x).count("1")

def elem_id_l2(el,xorsize=7):
    """ return set id for a particular page number by XORing
        together the lowest 'xorsize' bits.  the default (7)
        is the skylake addressing function.
    """
    v1 = el % (2**xorsize)
    v2 = (el>>xorsize) % (2**xorsize)
    return v1 ^ v2

def elem_id_l1(el):
    """ set number for L1 tlb on all known uarchs """
    return el % 16

def generate_set_l1(ident,size=8):
    assert ident >= 0
    l=[]
    x=ident
    while len(l) < size:
        l.append(x)
        x += 16
    assert len(l) == size
    return l

def generate_set_l2(ident,size=13):
    assert ident >= 0
    assert ident < 256
    l=[]
    for x in range(2**18):
        assert len(l) < size
        if elem_id_l2(x) == ident:
            l.append(x)
        if len(l) == size:
             return l
    return l

def generate_set_l2_general(ident,size=13):
    """ return list of page numbers that collide in L2 TLB, likely
        independent of addressing function """
    assert ident >= 0
    assert ident < 256
    l=[]
    k=0
    for x in range(size):
        k+=1
        l.append(k * 2**16 + ident)
    assert len(l) == size
    return l

class TestTLBLib(unittest.TestCase):
    def xorlist(self, inlist):
        """ xor successive elements together, just for the unit test. """
        x = [inlist[i+1]^inlist[i] for i in range(len(inlist)-1)]
        return x
    def test_elem(self):
        """ test we generate a xor pattern for each set, based on experimental
            data
        """
        my_xorlist=[129, 387, 129, 903, 129, 387, 129, 1935, 129, 387,
           129, 903, 129, 387, 129, 3999, 129, 387, 129, 903, 129, 387,
           129, 1935, 129, 387, 129, 903, 129, 387, 129, 8127, 129, 387,
           129, 903, 129, 387, 129, 1935, 129, 387, 129, 903, 129, 387,
           129, 3999, 129, 387, 129, 903, 129, 387, 129, 1935, 129, 387,
           129, 903, 129, 387, 129, 16383, 129, 387, 129, 903, 129, 387,
           129, 1935, 129, 387, 129, 903, 129, 387, 129, 3999, 129, 387,
           129, 903, 129, 387, 129, 1935, 129, 387, 129, 903, 129, 387,
           129, 8127, 129, 387, 129, 903, 129, 387, 129, 1935, 129, 387,
           129, 903, 129, 387, 129, 3999, 129, 387, 129, 903, 129, 387,
           129, 1935, 129, 387, 129, 903, 129, 387, 129]
        generated=set()
	for i in range(128):
            s=generate_set_l2(i,128)
            self.assertEqual(my_xorlist, self.xorlist(s))
            for e in s:
                """ some internal consistency tests """
		self.assertEqual(elem_id_l2(e), i)
                assert e not in generated
                assert e >= 0
                assert e < 2**14
                generated.add(e)
	self.assertEqual(len(generated), 16384)

if __name__ == "__main__":
    unittest.main()
