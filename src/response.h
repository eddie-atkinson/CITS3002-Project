// Include guard
#ifndef RESPONSE_H
#define RESPONSE_H
#include "common.h"
#include "frame.h"
#include "journey.h"

class Response {
public:
    int remaining_responses;
    class Frame* frame;
    int time;
    string stop;
    Response(int remaining_responses, Frame* frame, int time, string stop);
    string to_string();
};
#endif