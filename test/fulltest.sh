set -e

if [ ! -d test ]
then    echo 'please run me from the top dir.'
        exit 1
fi

for d in results-*
do  if [ ! -d $d ]
    then echo "expecting results-.. to be a dir"
         exit 1
    fi
    rm -f $d/*
    echo "$d placeholder" >$d/readme
done

rm -rf env
make -C c clean
make -C c
virtualenv -p python2.7 env
./env/bin/pip install -r requirements.txt
echo -1 | sudo tee /proc/sys/kernel/perf_event_paranoid
./env/bin/python py/crossthread.py
./env/bin/python py/tlb-latency.py

