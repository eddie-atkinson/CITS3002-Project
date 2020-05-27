#include "response.h"
Response::Response(int remaining_responses, Frame* frame, int time, string stop)
    : remaining_responses(remaining_responses)
    , frame(frame)
    , time(time)
    , stop(stop)
{
}
string Response::to_string()
{
    ostringstream ss;
    ss << "Remaining responses: " << remaining_responses << endl
       << "Frame origin: " << frame->origin << endl
       << "Frame destination: " << frame->dest << endl
       << "Frame time: " << frame->time << endl
       << "Best time: " << time << endl
       << "Best stop: " << stop << endl;
    return ss.str();
}