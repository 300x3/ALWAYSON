---
item: SIM-06
action: keep-open
evidence: |
  Half the item is satisfied and half is untested. Measured 2026-10-03.

  Satisfied -- the image carries the plugin that caused the abort:
  $ podman run --rm --entrypoint /bin/bash localhost/gz-sim10-resolute:gui-svgfix \
      -lc 'dpkg -l qt6-svg-plugins | tail -1; ls /usr/share/gz/gz-rendering'
  ii  qt6-svg-plugins:amd64 6.10.2-2     amd64        Qt 6 SVG library plugins
  gz-rendering.tag.xml
  media
  ogre
  ogre2

  Not satisfied -- the unit cannot run unattended, and has never been started:
  $ systemctl --user show ao-sim-fabrication-gui-gz.service \
      -p LoadState -p UnitFileState -p ActiveState -p NRestarts
  LoadState=loaded
  ActiveState=inactive
  UnitFileState=generated
  NRestarts=0

  $ grep -A3 '\[Install\]' ~/.config/containers/systemd/ao-sim-fabrication-gui-gz.service
  no [Install] section -> the unit cannot autostart

  NRestarts=0 on a unit that has never run is NOT evidence that rendering works.
  I did not start the GUI: it opens a window on the operator's live desktop,
  which under the browser/GUI placement rule must be anchored bottom-left of DP-3
  and must not steal focus, and starting it is a visible action on their screen.
section: 10-simulation-architecture
---
SIM-06 stays open. I am not able to close it in this session and I want to be
precise about which half is why.

The image half is done and verified. `localhost/gz-sim10-resolute:gui-svgfix`
carries `qt6-svg-plugins 6.10.2-2` and `/usr/share/gz/gz-rendering` holds `media/`,
`ogre/` and `ogre2/`. Those are exactly the two conditions §19 names as the cause
of the abort -- the missing SVG plugin and the missing media root -- so the image
that will be used is no longer the one that failed.

The runnability half is not done, and this is the part that matters. The unit is
`UnitFileState=generated` with no `[Install]` section, so it cannot autostart, and
it reports `ActiveState=inactive`, `NRestarts=0`. That last figure is the trap: a
restart count of zero on a unit that has never been started is not a pass. If I
had reported SIM-06 as verified on the strength of `NRestarts=0` I would have
reported success for something I never ran.

I did not start the GUI. It renders into a window on the operator's live desktop,
which under the placement rule has to be anchored bottom-left of DP-3 via the
`ao-gazebo-monitor` KWin script and must not raise itself or steal focus. Launching
it unattended is a visible action on someone's screen, and the `ao-gazebo-monitor`
script is installed and present but I have not confirmed it catches this unit in
this session.

To close SIM-06 someone needs to start the unit with the operator present and
confirm the window lands bottom-left of DP-3 with no focus steal. That is a
human-in-the-loop check, not something I should claim from a container image
listing.

**What I got wrong.** `systemctl is-enabled` returned `generated` and I read it
as a failure; I should have asked what `generated` means for a Quadlet unit before
concluding anything from it. The actual blocker turned out to be the missing
`[Install]` section, which `is-enabled` does not tell you.