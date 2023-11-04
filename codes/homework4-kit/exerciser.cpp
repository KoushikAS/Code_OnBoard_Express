#include "exerciser.h"

#include <iostream>

using namespace std;
void exercise(connection * C) {
  query1(C, 1, 35, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
  query2(C, "Orange");
  query3(C, "BostonCollege");
  query4(C, "NC", "DarkBlue");
  query5(C, 5);
}
