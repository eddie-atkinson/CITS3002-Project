CC = g++
CFLAGS = -std=c++11 -Wall -pedantic -Werror
OBJ = node.o udp.o tcp.o frame.o journey.o util.o response.o station.o
RM = rm -f

%.o: %.cpp %.h
	$(CC) -c -o $@ $< $(CFLAGS)

station: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	$(RM) $(OBJ)
