
def out_to_fields(o):
        """
        parse output of perf command in 'o' executed with -x for machine-readable
        output, and return a dict of counter(str) -> value(int)
        """
        yset=dict()
        lines=[x for x in o.split('\n') if len(x) > 0 and x[0] != '#']
        for l in lines:
            fields=l.split(',')
            if len(fields) < 3:
                print 'not seeing expected output here:', fields
            e=fields[2]
            v=int(fields[0])
            yset[e] = v
        return yset

