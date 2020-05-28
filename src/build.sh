rm killfile
killall ./station
sleep 5
./assignports.sh adjacency startstations.sh 
./makeform.sh startstations.sh myform.html 
make clean 
make -j 4 
./station_randomiser.py
./startstations.sh &&
sleep 5
firefox myform.html &