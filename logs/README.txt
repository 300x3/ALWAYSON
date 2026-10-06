ALWAYS ON logs and journals (README Section 16.3)

This is the canonical location. See README 16.3 for the table of every entry
and README 18.7 for why the earlier "LOGS-JOURNALS/" name was wrong.

ROTATION
  Staged: /ALWAYSON/config/host/logrotate-alwayson.conf
  NOT yet installed -- /etc/logrotate.d/ needs root. Outstanding work item 61
  in README section 19.2.

  Policy: daily, 14 kept, no compression. Compression is omitted on purpose --
  it is the only part of logrotate that reads whole files, and rotation itself
  is just a rename. Measured cost of a full system pass: 0.008s, once a day.

  Only the top-level *.log files are rotated. The subdirectories
  (operations/, gpu-runtime/, backup/, installation/) are per-operation record
  sets and are NOT rotated -- truncating them would destroy audit history.
  Their retention is undecided: work item 62.

  Until the policy is installed, nothing here is rotated. sim-gz-server.log
  grows continuously while the Gazebo server runs.

NOTHING ELSE LOGS HERE
  32 of the 33 deployed ao-* containers and services log to journald, not to
  this folder. Only ao-sim-fabrication-gz writes a file here. journald is not
  an unset default: it self-caps and currently holds 4 GB.

  MeshChatX writes its own log inside its own storage directory, which also
  holds identities, the session secret and a 455 MB mbtiles archive. Its log
  cannot be moved without moving that application data.

CHECKING
  ./scripts/validation/check-logs-journals.sh
  Exits 0 if every Section 16.3 entry exists and is fresh, 1 if one is
  missing, 2 if one is stale.

HANDLING
  Classified per README 4.2. Never write a secret value into any file here.
