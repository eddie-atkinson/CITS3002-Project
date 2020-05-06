#!/bin/bash

# written by Chris.McDonald@uwa.edu.au

PATH="/bin:/usr/bin"

echo ports in use:

case `uname` in
    Linux*)
	if [ -x /bin/netstat ]; then
	    /bin/netstat -tulpn 2>&1 | cut -c21-40 | sed 's/.*\:\(.*\)/\1/'
	else
	    echo "Your computer does not have netstat installed"
	    echo "You will need to run     'sudo apt install net-tools'"
	    exit 1
	fi
        ;;
    Darwin*)
        /usr/sbin/netstat -an | grep -E '^tcp|udp' | cut -c22-40 | sed 's/.*\.\(.*\)/\1/'
        ;;
esac | grep '^[0-9]' | sort -nu
