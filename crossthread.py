
import multiprocessing
import subprocess
import tlblib
from scipy import stats
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import cpuid
import cpus
import perf

cpu_uarch=cpuid.cpu_microarchitecture()[0]

def test_cores(argtype,setsize,nsets,event,pdfname, level, iterate=50000):
    events=[event]
    print 'reading cpu info from /proc/cpuinfo'
    corelist=cpus.corelist()
    corepair=corelist[1]
    print 'picking 2nd pair of logical processors:', corepair
    c1, c2 = corepair
    misses=numpy.zeros((nsets,nsets))
    numpyfn='results/' + pdfname+'-'+str(iterate)+'.npy'
    if not os.path.isfile(numpyfn):
           for set_id1 in range(nsets):
               for set_id2 in range(nsets):
                   if level == 1:
                       pagelist1=tlblib.generate_set_l1(set_id1, setsize)
                       pagelist2=tlblib.generate_set_l1(set_id2, setsize)
                   elif level == 2:
                       pagelist1=tlblib.generate_set_l2_general(set_id1, setsize)
                       pagelist2=tlblib.generate_set_l2_general(set_id2, setsize)
                       print pagelist1,pagelist2
                   else:
                        raise Exception('no')
                   pagelist_args1 = [argtype+str(x) for x in pagelist1]
                   pagelist_args2 = [argtype+str(x) for x in pagelist2]
                   cmdlist=["perf", "stat", "-x,", "-e", ",".join(events), "./c/tvlb-verbatim", "-r", str(iterate)]
                   print 'popen 1:', cmdlist+pagelist_args1, 'cpu', c1
                   print 'popen 2:', cmdlist+pagelist_args2, 'cpu', c2
                   p1 = subprocess.Popen(cmdlist+["-c"+str(c1)]+pagelist_args1, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                   p2 = subprocess.Popen(cmdlist+["-c"+str(c2)]+pagelist_args2, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                   o1, stderrdata1 = p1.communicate()
                   o2, stderrdata2 = p2.communicate()
                   if p1.returncode != 0:
                       print 'stdout:', o1
                       print 'stderr:', stderrdata1
                       raise Exception('popen 1 failed')
                   if p2.returncode != 0:
                       print 'stdout:', o2
                       print 'stderr:', stderrdata2
                       raise Exception('popen 2 failed')
                   yset1 = perf.out_to_fields(o1)
                   yset2 = perf.out_to_fields(o2)
                   print 'yset1:', yset1[event],yset2[event],c1,c2,set_id1,set_id2
                   misses[set_id2,set_id1] = ((float(yset1[event])+yset2[event])/iterate)/2.0
               #print misses
           #print '%7d' % (misses/iterate),
           print 'cores:', c1, c2
           print misses
           numpy.save(numpyfn, misses)
    return numpy.load(numpyfn)

if __name__ == "__main__":
    """
    Do measurements by invoking test_cores() for every desired measurement (TLB type and level).
    Plot the result using matplotlib.
    """
    numpy.set_printoptions(threshold=numpy.nan, linewidth=numpy.nan, precision=1)
    l2size=128

#    test_cores('-D',3,l2size,'dtlb_load_misses.miss_causes_a_walk', cpu_uarch + '-stlb-sets.pdf', 2)
    l1dtlb = test_cores('-D',3,16,'dtlb_load_misses.stlb_hit', cpu_uarch + '-dtlb-sets.pdf', 1)
    l1itlb = test_cores('-C',3,16,'itlb_misses.stlb_hit', cpu_uarch + '-itlb-sets.pdf', 1)

    f, axarr = plt.subplots(nrows=1, ncols=2)
    f.tight_layout()
    matplotlib.rc('font', size=5)
    plt.subplot(1,2,1, adjustable='box', aspect=0.8)
    pcm = plt.pcolormesh(l1dtlb)
    plt.xticks([0,4,8,12,16])
    plt.yticks([0,4,8,12,16])
    plt.gca().invert_yaxis()
    plt.xlabel('TLB set')
    plt.ylabel('TLB set')
    plt.title('L1 dtlb')

    plt.subplot(1,2,2, adjustable='box', aspect=0.8)
    pcm = plt.pcolormesh(l1itlb)
    plt.gca().invert_yaxis()
    plt.xticks([0,4,8])
    plt.yticks([0,4,8])
    plt.xlabel('TLB set')
    plt.ylabel('TLB set')
    plt.title('L1 itlb')

    f.subplots_adjust(right=0.8)
    cbar_ax = f.add_axes([0.85, 0.38, 0.05, 0.25])
    f.colorbar(pcm, cax=cbar_ax)

    plt.savefig('results/' + cpu_uarch + '-tlbsets-ht.pdf', bbox_inches='tight')
    plt.savefig('results/' + cpu_uarch + '-tlbsets-ht.png', bbox_inches='tight')
    plt.close()

