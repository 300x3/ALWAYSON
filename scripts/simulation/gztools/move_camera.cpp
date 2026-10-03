// Call the Gazebo GUI's /gui/move_to/pose service to place the viewport camera.
#include <gz/transport/Node.hh>
#include <gz/msgs/pose.pb.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
int main(int argc, char **argv)
{
  if (argc < 7) {fprintf(stderr, "usage: x y z roll pitch yaw\n"); return 1;}
  double v[6];
  for (int i = 0; i < 6; ++i) v[i] = atof(argv[i + 1]);
  gz::transport::Node node;
  gz::msgs::Pose m;
  m.mutable_position()->set_x(v[0]);
  m.mutable_position()->set_y(v[1]);
  m.mutable_position()->set_z(v[2]);
  const double cr = cos(v[3]/2), sr = sin(v[3]/2);
  const double cp = cos(v[4]/2), sp = sin(v[4]/2);
  const double cy = cos(v[5]/2), sy = sin(v[5]/2);
  auto q = m.mutable_orientation();
  q->set_w(cr*cp*cy + sr*sp*sy);
  q->set_x(sr*cp*cy - cr*sp*sy);
  q->set_y(cr*sp*cy + sr*cp*sy);
  q->set_z(cr*cp*sy - sr*sp*cy);
  const bool ok = node.Request("/gui/move_to/pose", m);
  printf("/gui/move_to/pose %s  pos=%.3f %.3f %.3f rpy=0 %.5f %.5f\n",
         ok ? "OK" : "FAIL", v[0], v[1], v[2], v[4], v[5]);
  return ok ? 0 : 1;
}
