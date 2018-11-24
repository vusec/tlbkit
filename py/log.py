import logging
import cpuid

def log(farg, *args):
    lgr.info(farg, *args)

cpu_uarch=cpuid.cpu_microarchitecture()[0]
fn='results-latencies/' + cpu_uarch + '.log'
lgr = logging.getLogger('tlblatency')
fh = logging.FileHandler(fn)
lgr.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fh.setFormatter(frmt)
lgr.addHandler(fh)
sh=logging.StreamHandler()
sh.setFormatter(frmt)
lgr.addHandler(sh)

log('logging to %s', fn)
