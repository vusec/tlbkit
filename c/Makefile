CFLAGS=-Wall -O3 -D_GNU_SOURCE -Werror -pie -fpic -g
LDFLAGS=-lpthread

all: tvlb-verbatim

tvlb-verbatim: tvlb-verbatim.c tvlb.h
	$(CC) -o tvlb-verbatim tvlb-verbatim.c $(LDFLAGS) $(CFLAGS)

clean:
	rm -f *.o tvlb-verbatim *.png *.pyc

