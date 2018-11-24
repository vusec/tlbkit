
#ifndef _TVLB_H
#define _TVLB_H 1

#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <linux/hw_breakpoint.h>

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/ioctl.h>

#include <stdlib.h>

#ifndef NO_PTHREAD
#include <pthread.h>
#include <sched.h>
#endif


#define PAGE 4096
#define SHAREFILE  ".tvlbsinglepagefile"
#define SYNCFILE   ".tvlbsyncfile"
#define SECRETBITS 256

static int createfile(const char *fn)
{
        int fd;
#ifndef NO_PTHREAD
        struct stat sb;
        char sharebuf[PAGE];
        if(stat(fn, &sb) != 0 || sb.st_size != PAGE) {
                fd = open(fn, O_RDWR | O_CREAT | O_TRUNC, 0644);
                if(fd < 0) {
			perror("open");
                        fprintf(stderr, "createfile: couldn't create shared file %s\n", fn);
                        exit(1);
                }
                if(write(fd, sharebuf, PAGE) != PAGE) {
                        fprintf(stderr, "createfile: couldn't write shared file\n");
                        exit(1);
                }
                return fd;
        }

        assert(sb.st_size == PAGE);
#endif

        fd = open(fn, O_RDWR, 0644);
        if(fd < 0) {
            perror(fn);
                fprintf(stderr, "createfile: couldn't open shared file\n");
                exit(1);
        }
        return fd;

}

#ifndef NO_PTHREAD
static int am_pinned = 0;
static void pin_cpu(size_t i)
{
        cpu_set_t cpu_set;
        pthread_t thread;

        thread = pthread_self();

        assert (i >= 0);
        assert (i < CPU_SETSIZE);

        CPU_ZERO(&cpu_set);
        CPU_SET(i, &cpu_set);

        int v = pthread_setaffinity_np(thread, sizeof cpu_set, &cpu_set);
        if(v != 0) { perror("pthread_setaffinity_np"); exit(1); }
        fprintf(stderr, "# cpu %d\n", (int) i);
        am_pinned=1;
}
#endif

#endif
