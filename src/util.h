#ifndef UTIL_H
#define UTIL_H
#include "common.h"
#include "journey.h"
#include <string.h>
#include <time.h>
list<string> split(const string &s, char delimiter);
string http_string(int response_code, string response_msg,
                   list<string> messages);
#endif