<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# IN GAZEBO, HOW DO I EDIT THE LOCATION OF THE DEFAULT CAMERA?

To set the **startup view camera** in a Gazebo world, put its pose in the world file’s `<gui>` section. The exact syntax depends on whether you use modern Gazebo Sim (`gz sim`, Fortress/Garden/Harmonic/Ionic) or Gazebo Classic (`gazebo` / `gzclient`).

## Gazebo Sim: `gz sim`

In your `.sdf` / `.world` file, add or edit the `MinimalScene` GUI plugin:

```xml
<sdf version="1.9">
  <world name="default">

    <gui fullscreen="0">
      <plugin filename="gz-sim-minimal-scene-system"
              name="gz::sim::systems::MinimalScene">
        <!-- x y z roll pitch yaw; angles in radians -->
        amera_pose>8 -10 6 0 0.35 0.9</camera_pose>
      </plugin>
    </gui>

    <!-- physics, models, lights, etc. -->

  </world>
</sdf>
```

`camera_pose` is:

```text
x y z roll pitch yaw
```

- `x y z`: camera location in metres, world frame
- `roll pitch yaw`: orientation in radians

For example:

```xml
amera_pose>0 -12 8 0 0.45 1.57</camera_pose>
```

places the camera 12 m in negative Y, 8 m up, with yaw near $90^\circ$. The `MinimalScene` plugin is the normal Gazebo Sim mechanism for setting the initial GUI camera pose. [^1_1]

### Practical method: capture a view you like

1. Launch your world.
2. Navigate using the GUI until the view is right.
3. Read the live GUI camera pose:
```bash
gz topic -e -t /gui/camera/pose
```

4. Copy the reported `position` and orientation.
5. Convert the quaternion orientation to roll/pitch/yaw before placing it in `amera_pose>`; the SDF tag uses Euler angles in radians, not a quaternion. [^1_2][^1_1]

You can also move the camera live using Gazebo Transport:

```bash
gz service -s /gui/move_to/pose \
  --reqtype gz.msgs.GUICamera \
  --reptype gz.msgs.Boolean \
  --timeout 2000 \
  --req 'pose: {
    position: {x: 8, y: -10, z: 6}
    orientation: {x: 0, y: 0, z: 0, w: 1}
  }'
```

That service expects a quaternion orientation. It is useful for iterating on a good view, but placing the final result in the world file makes it persistent. [^1_2]

## Gazebo Classic: `gazebo`

For Classic, use a `amera>` inside `<gui>`:

```xml
<sdf version="1.6">
  <world name="default">

    <gui fullscreen="0">
      amera name="user_camera">
        <!-- x y z roll pitch yaw; radians -->
        <pose>8 -10 6 0 0.35 0.9</pose>
      </camera>
    </gui>

  </world>
</sdf>
```

The camera `name` is important. Common values found across Classic versions include `user_camera` and, in some older configurations, `gzclient_camera`. The pose fields are space-separated and use metres/radians. [^1_3]

You can also inspect/change it interactively in the Classic GUI:

1. Open the left-side **World** tab.
2. Expand **GUI**.
3. Modify the camera pose values.
4. Copy the values into the world’s `<gui>amera>...</camera></gui>` block for a persistent default. [^1_4]

## Recommended workflow

For a robotics or drone world with a large origin-centered test area:

```xml
amera_pose>15 -20 14 0 0.45 0.93</camera_pose>
```

Then tune from there. A useful stable layout is to place the camera diagonally above and behind the vehicle, rather than directly overhead, so you retain both altitude and heading cues.

The key distinction is:


| Simulator | Persistent startup-camera configuration |
| :-- | :-- |
| Gazebo Sim (`gz sim`) | `<gui><plugin ... MinimalScene>amera_pose>...</camera_pose>` |
| Gazebo Classic (`gazebo`) | `<gui>amera name="user_camera"><pose>...</pose></camera>` |

<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://docs.lxrobotics.com/knowledge-base/gazebo/set-initial-camera-pose-gazebo

[^1_2]: https://automaticaddison.com/how-to-change-the-default-gazebo-camera-view/

[^1_3]: https://robotics.stackexchange.com/questions/25450/is-there-a-way-to-modify-the-default-camera-position-in-the-world-file

[^1_4]: https://classic.gazebosim.org/tutorials?tut=guided_b2

[^1_5]: https://gazebosim.org/api/sim/10/tutorials.html

[^1_6]: https://robotics.stackexchange.com/questions/115454/how-to-set-a-default-camera-pose-in-gazebo-harmonic-ubuntu-24-04

[^1_7]: http://www.youtube.com/watch?v=uDpOx21bpy4

[^1_8]: https://deepwiki.com/gazebosim/gazebo-classic/4.1-scene-visual-and-camera

[^1_9]: https://answers.gazebosim.org/question/8548/

[^1_10]: https://playerstage.sourceforge.net/doc/Gazebo-manual-0.5-html/classCamera.html

[^1_11]: https://www.youtube.com/watch?v=fiRRzJV1YIw

[^1_12]: https://www.youtube.com/watch?v=apXWVucpJSA

[^1_13]: https://www.youtube.com/watch?v=ZfiJhiA1ksA

[^1_14]: https://www.youtube.com/watch?v=jgXeIXrckBc

[^1_15]: https://www.youtube.com/watch?v=K4rHglJW7Hg

[^1_16]: https://www.youtube.com/watch?v=K1OB2Ky9gpc

[^1_17]: https://www.youtube.com/watch?v=HDboF7Itra8

[^1_18]: https://www.youtube.com/watch?v=tzN0QT1id0M

[^1_19]: https://www.youtube.com/watch?v=E7njvQ5BDPg


---

# AS A LANGUAGE MODEL

```
As a language model, I don’t have a persistent visual environment or direct access to your Gazebo instance. But I can help you edit the world/SDF configuration correctly if you paste the relevant `<world>` / `<gui>` section and tell me whether you are launching **Gazebo Classic** (`gazebo`) or **Gazebo Sim** (`gz sim`).
```


---

# GAZEBO SIM

For **Gazebo Sim** (`gz sim`), edit the GUI’s `MinimalScene` plugin configuration in the world SDF. The `<camera_pose>` is the startup pose for the interactive 3D-view camera.

```xml
<gui fullscreen="0">
  <plugin filename="MinimalScene" name="3D View">
    <gz-gui>
      <title>3D View</title>
      <property type="bool" key="showTitleBar">false</property>
      <property type="string" key="state">docked</property>
    </gz-gui>

    <engine>ogre2</engine>
    <scene>scene</scene>

    <!-- x y z roll pitch yaw; rotations are radians -->
    <camera_pose>8 -10 6 0 0.35 0.9</camera_pose>
  </plugin>
</gui>
```

Gazebo Sim defines the value as:

```text
X Y Z Roll Pitch Yaw
```

So this example starts the view camera at:

- $x=8$ m
- $y=-10$ m
- $z=6$ m
- roll $=0$
- pitch $=0.35$ rad
- yaw $=0.9$ rad

`<camera_pose>` belongs **inside the `MinimalScene` GUI plugin**, not as a normal model `<pose>` or a simulated camera sensor configuration. It affects the GUI viewport only.[^3_1]

## Minimal patch

If your world already has this:

```xml
<gui fullscreen="0">
  <plugin filename="MinimalScene" name="3D View">
    ...
  </plugin>
</gui>
```

add only:

```xml
<camera_pose>-6 0 6 0 0.5 0</camera_pose>
```

For a roughly diagonal overhead drone/robot test-range perspective, start with:

```xml
<camera_pose>12 -12 10 0 0.55 0.78</camera_pose>
```


## If your world has no `<gui>` block

```
Add the complete GUI block directly under `<world>`, alongside things such as `<physics>`, `<gravity>`, `<model>`, and system plugins:
```

```xml
<sdf version="1.9">
  <world name="my_world">

    <gui fullscreen="0">
      <plugin filename="MinimalScene" name="3D View">
        <gz-gui>
          <title>3D View</title>
          <property type="bool" key="showTitleBar">false</property>
          <property type="string" key="state">docked</property>
        </gz-gui>
        <engine>ogre2</engine>
        <scene>scene</scene>
        <camera_pose>12 -12 10 0 0.55 0.78</camera_pose>
      </plugin>
    </gui>

    <!-- world contents -->
  </world>
</sdf>
```

Without a world-specific GUI configuration, Gazebo Sim uses its default GUI configuration, commonly stored under:

```bash
~/.gz/sim/<major-version>/gui.config
```

A `<gui>` element in your world takes precedence, which is the better approach when each robot, airframe, or test world needs its own useful initial viewpoint.[^3_2]

## Important distinction

This is the **operator viewport camera**, not a camera sensor mounted on a robot. A robot camera sensor still needs a link/sensor definition such as:

```xml
<sensor name="front_camera" type="camera">
  <camera>
    <image>
      <width>1280</width>
      <height>720</height>
    </image>
  </camera>
</sensor>
```

The GUI `MinimalScene` plugin creates the user camera and accepts an optional `<camera_pose>`; its default pose is `(0, 0, 5, 0, 0, 0)` if you do not specify one.[^3_3]

<span style="display:none">[^3_10][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://gazebosim.org/docs/ionic/sdf_worlds/

[^3_2]: https://gazebosim.org/api/sim/7/gui_config.html

[^3_3]: https://gazebosim.org/api/gui/7/classplugins_1_1MinimalScene.html

[^3_4]: https://gazebosim.org/api/sim/7/server_config.html

[^3_5]: https://github.com/gazebosim/gz-sim/blob/main/examples/worlds/default.sdf

[^3_6]: https://answers.gazebosim.org/question/23878

[^3_7]: https://www.reddit.com/r/ROS/comments/w13qmf/how_do_i_place_a_top_down_view_camera_in_gazebo/

[^3_8]: https://robotics.stackexchange.com/questions/115454/how-to-set-a-default-camera-pose-in-gazebo-harmonic-ubuntu-24-04

[^3_9]: https://docs.lxrobotics.com/knowledge-base/gazebo/set-initial-camera-pose-gazebo

[^3_10]: https://automaticaddison.com/how-to-change-the-default-gazebo-camera-view/


---

# I SIMPLY NEED TO MOVE THE CAMERA CLOSER AND HAVE ITS LOCATION PERSIST AFTER REBOOT AS DEFAULT

Yes—don’t edit the world file. In **Gazebo Sim**, move the 3D-view camera where you want it, then save the **client configuration**. That makes the view persist across Gazebo restarts and system reboots.

## Fastest method

1. Launch Gazebo Sim normally.
2. Use the mouse controls in the 3D View to move/zoom the camera closer.
3. In the Gazebo window, open the **top-left menu**.
4. Select **Save client configuration**.

That writes your current GUI layout and `MinimalScene` camera pose to Gazebo Sim’s per-user default configuration. Subsequent `gz sim` sessions will use that camera pose automatically.[^4_1][^4_2]

## Where it saves

The persistent default is normally:

```bash
~/.gz/sim/<major-version>/gui.config
```

Examples:

```bash
~/.gz/sim/8/gui.config     # commonly Gazebo Harmonic
~/.gz/sim/9/gui.config     # newer release family
~/.gz/sim/10/gui.config    # newer release family
```

Determine your installed major version with:

```bash
gz sim --versions
```

Then inspect the saved pose:

```bash
grep -A2 -B2 camera_pose ~/.gz/sim/*/gui.config
```

Gazebo creates this per-user file on first run and normally does not overwrite it automatically, so it survives a reboot.[^4_2][^4_1]

## Exact manual edit

Close Gazebo first, then open your active configuration:

```bash
nano ~/.gz/sim/8/gui.config
```

Find the `MinimalScene` / `3D View` plugin and change or add:

```xml
<camera_pose>-3 0 2.5 0 0.45 0</camera_pose>
```

The six fields are:

```text
x y z roll pitch yaw
```

To move **closer**, primarily reduce the magnitude of the X/Y position and/or reduce Z. For example, if the current value is:

```xml
<camera_pose>-6 0 6 0 0.5 0</camera_pose>
```

a closer equivalent is:

```xml
<camera_pose>-3 0 3 0 0.5 0</camera_pose>
```

Gazebo Sim’s own world example uses `-6 0 6 0 0.5 0`; `<camera_pose>` is the GUI camera’s XYZ position followed by roll, pitch, and yaw in radians.[^4_3]

## One caveat

If you launch Gazebo with a custom GUI config, such as:

```bash
gz sim my_world.sdf --gui-config /path/to/custom.config
```

that explicit file overrides the normal `~/.gz/sim/.../gui.config` default. In that case, save or edit **that custom `.config` file** instead. Likewise, GUI configuration specified in a world’s `<gui>` block can affect the scene setup; an explicit `--gui-config` takes highest priority.[^4_4]

<span style="display:none">[^4_10][^4_5][^4_6][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://gazebosim.org/api/sim/8/gui_config.html

[^4_2]: https://gazebosim.org/api/sim/9/gui_config.html

[^4_3]: https://gazebosim.org/docs/harmonic/sdf_worlds/

[^4_4]: https://gazebosim.org/api/sim/10/gui_config.html

[^4_5]: https://gazebosim.org/api/gazebo/6/gui_config.html

[^4_6]: https://deepwiki.com/gazebosim/gz-gui/4.4-scene-configuration-example

[^4_7]: https://github.com/gazebosim/gz-sim

[^4_8]: https://gazebosim.org/api/sim/7/gui_config.html

[^4_9]: https://docs.lxrobotics.com/knowledge-base/gazebo/set-initial-camera-pose-gazebo

[^4_10]: https://robotics.stackexchange.com/questions/115454/how-to-set-a-default-camera-pose-in-gazebo-harmonic-ubuntu-24-04

