
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <immintrin.h>

#include "profile.h"

#define VTARGET 0x300000000000ULL

#define CACHELINE 64
#define SETS 128
#define PAGE 4096


void allocate_buffer(unsigned long long p, int fd)
{
    /* allocate buffer that is a particular page number offset from the base, is RWX and contains usable instructions
     * in case we want to execute it. it all points to the same physical page so we don't have to worry about the effects
     * of the cache too much when calculating latency, but ought to be just seeing the TLB latency.
     */
	assert(p >= 0);
	volatile char *target = (void *) (VTARGET+p*PAGE);
	volatile char *ret;
	ret = mmap((void *) target, PAGE, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_SHARED|MAP_FILE|MAP_FIXED, fd, 0);
	if(ret == MAP_FAILED) {
		perror("mmap");
           exit(1);
	}
	if(ret != (volatile char *) target) { fprintf(stderr, "Wrong mapping\n"); exit(1); }
    *ret;
	memset((char *) ret, 0xc3, PAGE); /* RETQ instruction */
}

#include "tvlb.h"

int main(int argc, char *argv[])
{
    const char *progname = argv[0];
	int fd = createfile(SHAREFILE);
    unsigned long long repetitions=1000;
    int c;
    int cpu=1;  /* logical core */
    int datapages = 0, codepages = 0;
#define MAXPAGES 3000
	static unsigned long long pagelist_code[MAXPAGES], pagelist_data[MAXPAGES];

    unsigned long long pageno;

    while ((c = getopt (argc, argv, "r:c:D:C:")) != -1) {
    switch (c)
      {
      case 'D':
          pageno = atoi(optarg);
          pagelist_data[datapages++] = pageno;
	      allocate_buffer(pageno, fd);
          break;
      case 'C':
          pageno = atoi(optarg);
          pagelist_code[codepages++] = pageno;
	      allocate_buffer(pageno, fd);
          break;
	  case 'c':
		cpu=atoi(optarg);
		break;
 	  case 'r':
        repetitions = atoll(optarg);
        break;
	  default:
	    fprintf(stderr, "usage\n");
        abort ();
      }
    }

	argc -= optind;
    argv += optind;

    if(argc > 0) {
            fprintf(stderr, "usage: %s [-c<cpu>] [-r<repetitions>] [-Ddatapage] [-Ccodepage]\n", progname);
            exit(1);
    }

    pin_cpu(cpu);

	if(repetitions < 0) { fprintf(stderr, "args\n"); return 1; }
    fprintf(stderr, "# cpu %d repetitions %llu\n", cpu, repetitions);

	int a;
    int r;

    for(r = 0; r < repetitions; r++) {
    	for(a = 0; a < datapages; a++) {
    		unsigned long long p = pagelist_data[a];
    		volatile int *probe = (volatile int *) (VTARGET+(p*PAGE));

            *probe;
            data_barrier(); // for timing info
    	}

    	for(a = 0; a < codepages; a++) {
    		unsigned long long p = pagelist_code[a];
    		void (*probe)(void) =  (void (*)(void)) (VTARGET+(p*PAGE));
            probe();
    	}

    }

	return 0;
}

