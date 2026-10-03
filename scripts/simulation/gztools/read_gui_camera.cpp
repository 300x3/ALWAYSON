// Print the live Gazebo GUI viewport camera pose from /gui/camera/pose.
#include <gz/transport/Node.hh>
#include <gz/msgs/pose.pb.h>
#include <cmath>
#include <cstdio>
#include <thread>
int main()
{
  gz::transport::Node node;
  node.SubscribeRaw("/gui/camera/pose",
    [](const char *data, const size_t size, const gz::transport::MessageInfo &)
    {
      gz::msgs::Pose p;
      p.ParseFromArray(data, static_cast<int>(size));
      const auto q = p.orientation();
      const auto s = p.position();
      const double w = q.w(), x = q.x(), y = q.y(), z = q.z();
      const double roll = std::atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y));
      const double pit = std::asin(std::max(-1.0, std::min(1.0, 2*(w*y - z*x))));
      const double yaw = std::atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z));
      printf("pos= %.4f %.4f %.4f  rpy= %.5f %.5f %.5f\n",
             s.x(), s.y(), s.z(), roll, pit, yaw);
      fflush(stdout);
    });
  std::this_thread::sleep_for(std::chrono::seconds(5));
  return 0;
}
