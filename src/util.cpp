#include "util.h"
vector<string> split(const string& s, char delimiter)
{
   vector<std::string> tokens;
   string token;
   std::istringstream tokenStream(s);
   while (std::getline(tokenStream, token, delimiter))
   {
      tokens.push_back(token);
   }
   return tokens;
}