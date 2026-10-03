<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# what version of gazebo and ros2 are compatible with ubuntu 26 lts

For **Ubuntu 26.04 LTS (“Resolute Raccoon”)**, the intended Tier-1 ROS 2 release is **ROS 2 Lyrical Luth**. The recommended Gazebo pairing is **Gazebo Jetty LTS**, using the `ros-lyrical-ros-gz` integration packages.[^1_1][^1_2]

## Recommended stack

| Layer | Use | Notes |
| :-- | :-- | :-- |
| OS | Ubuntu 26.04 LTS | Native target platform for ROS 2 Lyrical |
| ROS 2 | **Lyrical Luth** | ROS 2’s current long-term-support release for Ubuntu 26.04 [^1_1] |
| Simulator | **Gazebo Jetty LTS** | Recommended / supported ROS–Gazebo pairing with Lyrical [^1_2][^1_3] |
| Integration | `ros-lyrical-ros-gz` | Provides the ROS 2 ↔ Gazebo bridge, image transport, simulation launch tooling, and related packages |

For a new robotics, drone, autonomy, or SLAM workstation on 26.04, I would use:

```text
Ubuntu 26.04
ROS 2 Lyrical
Gazebo Jetty
ros-lyrical-ros-gz
```


## Important distinction: modern Gazebo

Use the **modern Gazebo** family—packages and commands typically prefixed `gz`, such as:

```bash
gz sim
gz topic
gz service
```

Avoid starting a fresh project with **Gazebo Classic** (`gazebo`, typically Gazebo 11). Classic is end-of-life and is not the appropriate supported target for Ubuntu 26.04 / ROS 2 Lyrical. The modern ROS integration is `ros_gz`, not the older `gazebo_ros_pkgs` workflow.[^1_2][^1_3]

## Compatibility matrix

The currently documented pairings are:


| ROS 2 distribution | Primary Ubuntu target | Recommended Gazebo |
| :-- | --: | :-- |
| Humble Hawksbill | 22.04 | Gazebo Fortress LTS |
| Jazzy Jalisco | 24.04 | Gazebo Harmonic LTS |
| Kilted Kaiju | 24.04 | Gazebo Ionic |
| **Lyrical Luth** | **26.04** | **Gazebo Jetty LTS** |
| Rolling | Development platforms | Gazebo Jetty, but moving target |

Gazebo’s compatibility guidance specifically lists **Lyrical + Jetty** as the recommended combination. Some other combinations can technically be built or made operational, but they may need source builds, version pinning, or manual bridge/package resolution and are a poor foundation for a long-lived robot stack.[^1_3][^1_2]

## Installation direction

Once the ROS 2 Lyrical and Gazebo repositories provide their normal 26.04 binary packages, the high-level install is expected to look like:

```bash
sudo apt update
sudo apt install ros-lyrical-desktop
sudo apt install ros-lyrical-ros-gz
```

Then source the environment:

```bash
source /opt/ros/lyrical/setup.bash
echo 'source /opt/ros/lyrical/setup.bash' >> ~/.bashrc
```

For a development machine, also install the usual ROS build and diagnostic baseline:

```bash
sudo apt install \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  ros-dev-tools
```


## Practical caveat

Ubuntu 26.04 is newer than the very well-established 24.04/Jazzy/Harmonic stack. If your real objective is a **production robot, drone simulation environment, Nav2/MoveIt workflow, or a project relying on third-party vendor packages**, check whether every dependency you need already publishes Lyrical/26.04 binaries.

If one of your essential packages is only supported through Jazzy today, the lower-risk alternative is:

```text
Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic
```

That is still an excellent, long-support baseline. But for a clean 26.04 build intended to track the official platform, choose **ROS 2 Lyrical + Gazebo Jetty**.[^1_1][^1_2]

<span style="display:none">[^1_10][^1_4][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.ros.org/blog/getting-started/

[^1_2]: https://gazebosim.org/docs/latest/ros_installation/

[^1_3]: https://gazebosim.org/docs/fortress/ros_installation/

[^1_4]: https://askubuntu.com/questions/1567187/which-version-of-gazebo-for-ubuntu-26-04

[^1_5]: https://www.reddit.com/r/robotics/comments/1fhvr00/need_a_little_help_on_running_gazebo_on_ubuntu/

[^1_6]: https://robotics.stackexchange.com/questions/29282/which-gazebo-versions-supported-for-ubuntu-22-04jammy

[^1_7]: https://singleboardblog.com/how-to-install-ros-2-and-gazebo-on-ubuntu/

[^1_8]: https://github.com/Comet-Robotics/URC/discussions/23

[^1_9]: https://forums.developer.nvidia.com/t/cannot-install-ros-2-gazebo-and-doosan-packages-on-jetson-orin-nano-ubuntu-22-04/351692

[^1_10]: https://github.com/osrf/gazebo_tutorials/blob/master/ros_wrapper_versions/tutorial.md

