CC = g++
CFLAGS = -std=c++11 -Wall -pedantic -Werror
DEPS = node.h station.h
OBJ = station.o node.o util.o udp.o tcp.o frame.o
RM = rm -f

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

station: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	$(RM) $(OBJ)
