---
item: OPS-36
action: new
evidence: |
  $ for p in '~/.local/share/MeshChatX/meshchatx.sqlite' \
            '~/.local/share/meshchatx/meshchatx.db' \
            '~/.local/share/QGroundControl.org/QGroundControl.db' \
            '~/.config/QGroundControl.org/QGroundControl.db' \
            '~/.mozilla/firefox/*/places.sqlite' \
            '~/.config/BraveSoftware/Brave-Browser/Default/History'; do
        printf '%-58s ' "$p"; eval "ls $p" >/dev/null 2>&1 && echo PRESENT || echo ABSENT; done
  ~/.local/share/MeshChatX/meshchatx.sqlite             ABSENT
  ~/.local/share/meshchatx/meshchatx.db                 ABSENT
  ~/.local/share/QGroundControl.org/QGroundControl.db    ABSENT
  ~/.config/QGroundControl.org/QGroundControl.db        ABSENT
  ~/.mozilla/firefox/*/places.sqlite                   ABSENT
  ~/.config/BraveSoftware/Brave-Browser/Default/History ABSENT

  # where the data actually is:
  -rw-r--r-- 18083840  ~/.reticulum-meshchatx/identities/<hash>/database.db
  ~/snap/firefox/common/.mozilla/firefox/<id>/places.sqlite

  # QGroundControl's only SQLite is a map tile cache, not an app store:
  $ python3 -c "...sqlite3.open('qgcMapCache.db',uri=True)..."
  ['Tiles', 'TileSets', 'SetTiles', 'TilesDownload']  ->  16 tiles, 1 tileset

  $ snap list | grep -iE 'brave'
  brave  1.96.61  690  latest/stable  brave**
section: 03-high-level-architecture
---
# The monitoring collector declares four store paths that do not exist on this host

`scripts/operations/collect-system-health.py` is an OPS-group file, so I report rather than
fix. Four of its declared stores point at paths that are absent:

| Declared store | Declared path | Reality |
|---|---|---|
| `db-meshchatx` | `~/.local/share/MeshChatX/meshchatx.sqlite`, `~/.local/share/meshchatx/meshchatx.db` | **both absent**; the real store is `~/.reticulum-meshchatx/identities/<hash>/database.db` — 18 MB, 44+ tables |
| `db-qgroundcontrol` | `~/.local/share/QGroundControl.org/QGroundControl.db`, `~/.config/QGroundControl.org/QGroundControl.db` | **both absent**; QGroundControl has **no application database at all** |
| `db-browser-firefox-places` | `~/.mozilla/firefox/*/places.sqlite` | absent — Firefox is a **snap**; the profile is `~/snap/firefox/common/.mozilla/firefox/<id>/places.sqlite` |
| `db-browser-brave-history` | `~/.config/BraveSoftware/Brave-Browser/Default/History` | absent — Brave is a snap with **no profile directory at all** |

**The failure direction is safe, and that matters for how this gets prioritised.** The
collector reports an absent store as absent and reads nothing. So this does not cause a
privacy leak and needs no emergency handling — but it does mean four entries in the declared
inventory report a wrong answer, and two stores are effectively unobserved despite §3.3.1
listing them as SQLite stores in the program-to-database map.

The MeshChatX case is the significant one: there is a live 18 MB database holding 8862
announces and 3048 crawl tasks that reporting does not currently cover. The QGroundControl
case is different in kind — there is nothing to cover, because the database §3.3.1 described
does not exist. I have corrected both rows in §3.3.1 to say what actually exists.

**Two judgement calls for whoever picks this up, not decisions I should make:**

- **The Firefox and Brave fixes are browser stores**, which are under an explicit operator
  exclusion from collection (2026-10-03). Correcting the *path* is a fidelity fix; it
  would also make the collector start finding stores that are currently reported absent.
  That is arguably what the inventory intends, but it touches the exclusion decision, so I
  have left it alone rather than quietly widening what is read.
- **MeshChatX and QGroundControl are not excluded** and fixing their paths only widens
  accurate coverage of already-declared stores — lower risk, and probably the right first
  move.

## What I got wrong

See `spec-NET-51.md` for the full list. The one relevant here: I asserted a general claim
about the collector's coverage without first enumerating what it actually covers, and the
enumeration is what found the gap. Same failure mode twice this pass.