#!/bin/bash

# written by Chris.McDonald@uwa.edu.au

if [ $# != "2" ]; then
    echo "Usage: $0 adjacencyfile startstations.sh"
    exit 1
fi

# ---------------------------------------

MYSERVER="./station"
port="4000"

PATH="/bin:/usr/bin"

TMPA="/tmp/ap-a$$"
TMPB="/tmp/ap-b$$"
trap "rm -f $TMPA $TMPB ; exit 1" SIGINT SIGTERM

function find_ports_in_use() {
    case `uname` in
	Linux*)
	    /bin/netstat -tulpn 2>&1 | \
		cut -c21-40 | sed 's/.*\:\(.*\)/\1/'
	    ;;
	Darwin*)
	    /usr/sbin/netstat -an | grep -E '^tcp|udp' | \
		cut -c22-40 | sed 's/.*\.\(.*\)/\1/'
	    ;;
    esac | grep '^[0-9]' | sort -nu
}

function port_in_use() {
    grep -q "^$1\$" < $TMPA
}

function build_sed() {
    SED="sed "
    while read from neighbours ; do
	while true ; do
	    (( port = port + 1 ))
	    if port_in_use $port ; then
		continue
	    fi
	    tport=$port
	    (( port = port + 1 ))
	    if port_in_use $port ; then
		continue
	    fi
	    SED="$SED -e \"s/^$from /$from $tport $port /\" -e \"s/ $from/ $port/\""
	    break
	done
    done < $TMPB
    SED="$SED -e \"s,^,$MYSERVER ,\" -e \"s/\$/ \&/\""
}

# ---------------------------------------

find_ports_in_use	> $TMPA
expand < $1 | sed -e 's/^ //g' | tr -s ' ' > $TMPB
build_sed
eval $SED < $TMPB > $2

echo "input file '$1' - "
cat < $1
echo
echo "output file '$2' - "
cat < $2

rm -f $TMPA $TMPB
