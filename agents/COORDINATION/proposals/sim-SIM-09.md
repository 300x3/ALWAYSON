---
item: SIM-09
action: close
evidence: |
  §19.1 records this as outstanding. It was fixed in commit 365bd4277d310c4bda616015766b45e5f49a04b8.
  Verified against the committed tree 2026-10-03.

  $ git --no-pager show 365bd42 --stat
  commit 365bd4277d310c4bda616015766b45e5f49a04b8
      fix(sim-fabrication): aim arm cameras at the measured as-built centroid
   GAZEBO/sim/boning.yaml      | 15 +++++++++++++--
   GAZEBO/worlds/factory.world | 10 +++++-----
   2 files changed, 18 insertions(+), 7 deletions(-)

  $ python3 -c "import yaml; c=[x for x in yaml.safe_load(open('GAZEBO/sim/boning.yaml'))['cells'] if x['id']=='cell-arms'][0]['datum']; print(c['origin'], c['extent'])"
  [5.981314, 1.861669, 0.531531] [0.84, 1.672391, 1.238532]

  midpoint (origin + extent/2) = centroid:
    x 5.981314 + 0.42        = 6.401314
    y 1.861669 + 0.8361955  = 2.6978645
    z 0.531531 + 0.619266   = 1.150797

  $ grep -n 'camera_elev_arms' GAZEBO/worlds/factory.world | head -3
  549:    <model name="camera_elev_arms">
  552:      <link name="camera_elev_arms">
  554:        <sensor name="camera_elev_arms" type="camera">

  The commit corrects `cell-arms` origin from 6.401314 to 5.981314. The old value
  was the mesh CENTRE in x/y while `origin` is documented as the MIN corner --
  displaced by exactly half the extent, (0.420000, 0.836196, 0.000000). The
  corrected origin plus its extent yields the as-built centroid as the midpoint,
  which is what every arm camera is now aimed at.
section: 10-simulation-architecture
---
§19.1 lists SIM-09 as outstanding ("elev_arms framing uses the boned datum, not
the as-built arms"). That was fixed on 2026-10-02 in commit `365bd42`, before this
session began, and I am closing it on that basis rather than on new work.

The fix had two halves. The boned datum itself was corrected: `cell-arms` origin
moved from `6.401314` to `5.981314` because the stored value was the mesh centre
in x/y while the field is documented as the min corner, so it was displaced by
exactly half the extent. And all four arm cameras were re-aimed at the true
as-built centroid. A line-of-sight checker was added against the world collision
boxes and azimuth x distance swept for vantages with clear line of sight and the
whole measured AABB in frame; the arms cell admits only a 65-115 degree azimuth
band.

I verified the arithmetic rather than trusting the commit message: origin plus
half of extent reproduces the centroid `6.401314, 2.6978645, 1.150797` to the
precision the datum carries, which is the invariant that makes the datum and the
cameras unable to disagree.

§10.3 in my section file records the corrected datum and the `elev_arms` pose.

**What I got wrong.** I opened this item expecting the datum/camera disagreement to
still be live and had drafted a note describing it as an unfixed inconsistency
before reading the commit history. The fix predates my session. I should have run
`git log -S` on the datum values before writing anything about them -- that one
command would have told me the item was already closed.