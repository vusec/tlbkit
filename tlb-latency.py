
import sys
import multiprocessing
import subprocess
import tlblib
from scipy import stats
import numpy
import os
import cpuid
import cpus
import perf
from sklearn.linear_model import LinearRegression

cpu_uarch=cpuid.cpu_microarchitecture()[0]

"""
dtlb_load_misses.stlb_hit
dtlb_load_misses.miss_causes_a_walk
"""

def linear_regression(xx,yy):
    nx,ny = numpy.asarray(xx), numpy.asarray(yy)
    nx,ny = nx.reshape(-1, 1), ny.reshape(-1, 1)
    reg = LinearRegression().fit(nx, ny)
    slope = reg.coef_[0][0]
    return slope

def hit_miss_comparison(m1,m2,c1,c2,name):
    print name, 'misses for miss/no-miss set: %.2f vs %.2f.' % (m1,m2), 'Cycles per iteration: %.1f vs %.1f' % (c1,c2)
    if m2 >= 1:
        raise Exception('The no-miss rate is 1 or larger, this likely means the assumptions (eviction set) of this experiment are wrong.')
    if m2 >= 0.3:
        print 'WARNING: miss rate is quite large for the no-miss set! Possibly wrong set or noisy data.'
    if m1 < 1:
        print 'WARNING: miss rate is quite small for the no-miss set! Possibly wrong set or noisy data.'
    if m1 <= m2:
        raise Exception('More misses in the miss vs no-miss case makes no sense.')
    if c1 <= c2:
        raise Exception('More cycles in the miss vs no-miss case makes no sense.')
    extra_misses = m1-m2
    extra_cycles = c1-c2
    print 'Extra misses: %.2f extra cycles: %.2f cycles per miss: %.2f' % (extra_misses, extra_cycles, extra_cycles/extra_misses)

def test_latency_and_miss_per_iteration(pagelist,event,name):
    cpu = 1 # just a single process so doesn't matter, but we should pin it
    xx,yy,ycycles=[],[],[]
    print 'calculating', event, 'and cycles slope for', name, 
    sys.stdout.flush()
    for iterations in range(0,20000000,5000000):
                   pagelist_args = ['-D'+str(x) for x in pagelist]
                   cmdlist=["perf", "stat", "-x,", "-e", event+",cycles", "./c/tvlb-verbatim", "-r", str(iterations), "-c"+str(cpu)]+pagelist_args
                   print '.',
                   sys.stdout.flush()
                   p1 = subprocess.Popen(cmdlist, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                   o1, stderrdata1 = p1.communicate()
                   if p1.returncode != 0:
                       print 'stdout:', o1
                       print 'stderr:', stderrdata1
                       raise Exception('command failed')
                   yset1 = perf.out_to_fields(o1)
                   xx.append(iterations)
                   yy.append(yset1[event])
                   ycycles.append(yset1['cycles'])

    event_per_iteration = linear_regression(xx,yy)
    cycles_per_iteration = linear_regression(xx,ycycles)

    print 'done. misses: %.1f, cycles: %.1f' % (event_per_iteration,cycles_per_iteration)

    return event_per_iteration,cycles_per_iteration

if __name__ == "__main__":
    print ''
    print ' * Probing set sizes'
    print ''

    for l1_size in range(1,10):
        l1_pagelist_misses=tlblib.generate_set_l1(1,l1_size+1)
        l1misses1,l1cycles1 = test_latency_and_miss_per_iteration(l1_pagelist_misses, 'dtlb_load_misses.stlb_hit', 'l1 miss test size ' + str(l1_size))
        if l1misses1 > 1:
            print 'Found'
            print ''
            break
    for l2_size in range(7,16):
        l2_pagelist_misses=tlblib.generate_set_l2_general(1,l2_size+1)
        l2misses1,l2cycles1 = test_latency_and_miss_per_iteration(l2_pagelist_misses, 'dtlb_load_misses.miss_causes_a_walk', 'l2 miss test size ' + str(l2_size))
        if l2misses1 > 1:
            print 'Found'
            print ''
            break
    print 'L1 size:', l1_size, 'L2 size:', l2_size

    l1_setsize=l1_size
    l2_setsize=l2_size

    print 'Assuming L1dTLB set size:', l1_setsize
    print 'Assuming L2dTLB/STLB set size:', l2_setsize

    l1_pagelist_misses=tlblib.generate_set_l1(1,l1_setsize+1)
    l1_pagelist_no_misses=list(l1_pagelist_misses)
    l1_pagelist_no_misses[-1] += 1
    l1_pagelist_no_misses[-2] += 1

    l2_pagelist_misses=tlblib.generate_set_l2_general(1,l2_setsize+1)
    l2_pagelist_no_misses=list(l2_pagelist_misses)
    l2_pagelist_no_misses[-1] += 1
    l2_pagelist_no_misses[-2] += 1

    print ''
    print ' * Configuring miss and no-miss TLB sets of equal size'
    print ''

    print 'l1 misses:   ', l1_pagelist_misses
    print 'l1 no misses:', l1_pagelist_no_misses
    print 'l2 misses:   ', l2_pagelist_misses
    print 'l2 no misses:', l2_pagelist_no_misses

    print ''
    print ' * Probing miss rate and latency differences of miss and no-miss sets of equal size'
    print ''

    l1misses1,l1cycles1 = test_latency_and_miss_per_iteration(l1_pagelist_misses, 'dtlb_load_misses.stlb_hit', 'l1 miss list')
    l1misses2,l1cycles2 = test_latency_and_miss_per_iteration(l1_pagelist_no_misses, 'dtlb_load_misses.stlb_hit', 'l1 no-miss list')
    l2misses1,l2cycles1 = test_latency_and_miss_per_iteration(l2_pagelist_misses, 'dtlb_load_misses.miss_causes_a_walk', 'l2 miss list')
    l2misses2,l2cycles2 = test_latency_and_miss_per_iteration(l2_pagelist_no_misses, 'dtlb_load_misses.miss_causes_a_walk', 'l2 no-miss list')

    print ''
    print ' * Results'
    print ''

    hit_miss_comparison(l1misses1,l1misses2,l1cycles1,l1cycles2, 'L1TLB')
    hit_miss_comparison(l2misses1,l2misses2,l2cycles1,l2cycles2, 'L2TLB')
