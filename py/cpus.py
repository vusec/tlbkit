
def corelist(allthreads=True):
        """ return array of processor tuples that share a core, i.e. sibling hyperthreads """
	cpulines=open('/proc/cpuinfo').read().split('\n')
	package=None
	core=None
	thread=None

	d=dict()

	package=None
	logical_id=None

	for line in cpulines:
		fields=line.split(':')
		try:
			n=int(fields[1])
		except:
			continue
		if 'processor' in line:
			assert logical_id == None
			logical_id=n
		elif 'physical id' in line:
			assert package == None
			package=n
		elif 'core id' in line:
			assert package != None
			assert logical_id != None
			full_core_id=(package,n)
			if not full_core_id in d:
				d[full_core_id] = []
			if allthreads:
				d[full_core_id].append(logical_id)
			else:
				d[full_core_id]=logical_id
			package=None
			logical_id=None
		else:
			continue
	return [d[l] for l in sorted(d)]

#l=corelist()
#print(l)

