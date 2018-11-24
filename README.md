Setup
========

To run:

0. Have perf and a compiler installed

1. build the C program

$ make -C c

2. set up the puthon environment

$ rm -rf env
$ virtualenv -p python2.7 env
$ ./env/bin/pip install -r requirements.txt

3. perf privileges for unprivileged users:

$ echo -1 | sudo tee /proc/sys/kernel/perf_event_paranoid

Inter-hyperthread tlb interference shown using performance counters
===================================================================

under some tlb size and structure assumptions (works on skylake), probe
cross-thread tlb interference

$ ./env/bin/python crossthread.py

on skylake, the results should look like in the demo/ dir.

Calculate TLB miss latency
=============================

$ ./env/bin/python tlb-latency.py

on skylake, the results should look like in demo/skylake-latencies.txt.

Enjoy!

Ben

