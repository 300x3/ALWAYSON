#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/add-firefox-server-bookmarks.py
# Adds the "SERVERS (THIS MACHINE)" folder to the bookmarks toolbar of a
# standard Firefox profile (places.sqlite) with one bookmark per locally
# hosted service that is actually running and reachable over HTTP(S).
#
# MUST run while that Firefox is closed: Firefox caches Places in memory and
# rewrites the database on exit, so rows added while it runs are lost.
# Always back up places.sqlite (+ -wal/-shm) before running.
#
# ITEMS below was verified live on 2026-10-01 with curl against the host's
# listening sockets and `podman ps`; see README work queue. Only services that
# answered an HTTP probe are listed. Re-verify with:
#   for u in <urls>; do curl -sk -o /dev/null -m 6 -w "%{http_code} $u\n" "$u"; done
#
# Usage: python3 add-firefox-server-bookmarks.py <profile-dir> [--dry-run] [--folder-id N]
import os
import sqlite3
import sys
import time
import uuid

FOLDER_TITLE = "SERVERS (THIS MACHINE)"
ITEMS = [
    ("ALWAYS ON Console", "http://127.0.0.1:8099/"),
    ("ALWAYS ON Sim (Foxglove + ROS 2)", "http://127.0.0.1:8099/sim"),
    ("Podman Manager", "http://127.0.0.1:8099/podman"),
    ("Gazebo Portal (factory.world)", "http://127.0.0.1:8765/"),
    ("Grafana", "http://127.0.0.1:3001/"),
    ("Metabase", "http://127.0.0.1:3002/"),
    ("Prometheus", "http://127.0.0.1:9090/"),
    ("Mastodon (local)", "https://127.0.0.1:3300/"),
    ("OpenClaw Control", "http://127.0.0.1:18789/"),
    ("MeshChatX (Reticulum)", "https://127.0.0.1:18000/"),
    ("Domoticz", "http://127.0.0.1:8080/"),
    ("WebODM", "http://127.0.0.1:8000/"),
    ("CUPS (printers)", "http://127.0.0.1:631/"),
]

# Deliberately NOT bookmarked:
#   http://127.0.0.1:3484/  ClineKanban - not listening.
#   http://10.42.0.96/config Mainsail - different machine, unreachable.
#   http://127.0.0.1:1234/  LM Studio  - bearer-token API, no browsable UI.
#   http://127.0.0.1:4000/  Mastodon streaming - WebSocket API, not a UI.
#   http://127.0.0.1:18790/ OpenClaw chat relay - a bare / is a 404, reached
#                                    through the Cloudflare Tunnel hostname.
#   http://127.0.0.1:3300/  Mastodon over PLAIN http - the :3300 proxy is a TLS
#                                    listener now, so plain http to it fails.
#                                    Use https://127.0.0.1:3300/ instead.
#   http://127.0.0.1:3000/  Mastodon direct - answers "301 ->
#                                    https://127.0.0.1:3000/" because upstream
#                                    hardcodes config.force_ssl = true, and
#                                    Puma speaks no TLS. Bookmarking it hangs
#                                    the browser on a render-blocking
#                                    stylesheet. Use the :3300 proxy instead.


def guid():
    return uuid.uuid4().hex[:12]


def now_us():
    return int(time.time() * 1_000_000)


def cols(cur, table):
    """Column name -> (notnull, default) for a table."""
    return {r[1]: (r[3], r[4]) for r in cur.execute("PRAGMA table_info(%s)" % table)}


def origin_id(cur, url):
    """Return a moz_origins.id for the URL, creating the row when needed."""
    ocols = cols(cur, "moz_origins")
    if "prefix" not in ocols or "host" not in ocols:
        return None
    scheme, _, rest = url.partition("://")
    host = rest.split("/", 1)[0]
    prefix = "%s://%s" % (scheme, host)
    row = cur.execute(
        "SELECT id FROM moz_origins WHERE prefix=? AND host=?", (prefix, host)
    ).fetchone()
    if row:
        return row[0]
    names = ["prefix", "host", "frecency"]
    values = [prefix, host, -1]
    for name, (notnull, default) in ocols.items():
        if name in names or name == "id":
            continue
        if notnull and default is None:
            names.append(name)
            values.append(0)
    cur.execute(
        "INSERT INTO moz_origins (%s) VALUES (%s)"
        % (", ".join(names), ", ".join("?" * len(names))),
        values,
    )
    return cur.lastrowid


def place_id(cur, url, title):
    """Return an existing or new moz_places.id for the URL."""
    row = cur.execute("SELECT id FROM moz_places WHERE url=?", (url,)).fetchone()
    if row:
        cur.execute(
            "UPDATE moz_places SET title=COALESCE(title, ?),"
            " foreign_count=COALESCE(foreign_count, 0)+1 WHERE id=?",
            (title, row[0]),
        )
        return row[0]
    pcols = cols(cur, "moz_places")
    host = url.split("://", 1)[-1].split("/", 1)[0]
    values = {
        "url": url,
        "title": title,
        "rev_host": host[::-1] + ".",
        "visit_count": 0,
        "hidden": 0,
        "typed": 0,
        "frecency": -1,
        "guid": guid(),
        "foreign_count": 1,
        "url_hash": 0,
        "recalc_frecency": 1,
        "alt_frecency": 0,
        "recalc_alt_frecency": 0,
        "origin_id": origin_id(cur, url),
    }
    names = []
    vals = []
    for name, (notnull, default) in pcols.items():
        if name == "id":
            continue
        if name in values:
            names.append(name)
            vals.append(values[name])
        elif notnull and default is None:
            names.append(name)
            vals.append(0)
    cur.execute(
        "INSERT INTO moz_places (%s) VALUES (%s)"
        % (", ".join(names), ", ".join("?" * len(names))),
        vals,
    )
    return cur.lastrowid


def firefox_running(profile):
    """True if a Firefox process is actually using this profile.

    A profile 'lock' entry is not a reliable signal: snap Firefox leaves a
    stale `lock` symlink behind after a clean exit, so a file-presence test
    blocks every run. Check for a live process instead.

    Matching is done on /proc/<pid>/exe rather than the command line: this
    script's own argv contains both the word "firefox" and the profile path,
    so a `ps args` grep matches itself and always reports "running".

    Snap Firefox is handled specially: it does NOT pass "-profile <dir>", so
    the profile path never appears in its cmdline and a cmdline-only test
    wrongly reports "not running" while the profile is very much in use - which
    lets a write land in a live places.sqlite that Firefox later overwrites
    from memory. When a snap firefox binary is alive and its cmdline does not
    name a profile, we cannot attribute it, so we assume it is ours and block.
    Erring toward "busy" only costs a re-run; erring toward "idle" corrupts.
    """
    real = os.path.realpath(profile)
    snap_seen = False
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            exe = os.path.realpath(os.readlink("/proc/%d/exe" % pid))
            with open("/proc/%d/cmdline" % pid, "rb") as fh:
                cmdline = fh.read().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue  # process exited, or not ours to inspect
        if os.path.basename(exe) not in ("firefox", "firefox-bin"):
            continue
        if "ms-playwright" in exe:  # our automation browser, throwaway profile
            continue
        if real in cmdline:
            return True
        if exe.startswith("/snap/firefox"):
            snap_seen = True
    return snap_seen


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: add-firefox-server-bookmarks.py <profile-dir> [--dry-run]")
    profile = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    db = os.path.join(profile, "places.sqlite")
    if not os.path.exists(db):
        sys.exit("places.sqlite not found in %s" % profile)
    if firefox_running(profile):
        sys.exit("Firefox is running with %s - close it first" % profile)

    con = sqlite3.connect(db)
    cur = con.cursor()
    row = cur.execute(
        "SELECT id FROM moz_bookmarks WHERE guid='toolbar_____'"
    ).fetchone()
    if not row:
        sys.exit("bookmarks toolbar folder not found")
    toolbar_id = row[0]

    stamp = now_us()
    # Resolve the folder. --folder-id targets one explicitly (needed when the
    # operator has moved the folder, or when a stale duplicate still exists).
    forced = None
    if "--folder-id" in sys.argv:
        forced = int(sys.argv[sys.argv.index("--folder-id") + 1])
    if forced is not None:
        row = cur.execute(
            "SELECT id, parent, title FROM moz_bookmarks WHERE id=? AND type=2",
            (forced,),
        ).fetchone()
        if not row:
            sys.exit("no bookmark folder with id %d" % forced)
        folder_id = row[0]
        print("using folder id %d %r (parent %d) as instructed" % (folder_id, row[2], row[1]))
    else:
        # Find the folder by title ANYWHERE, not just directly under the toolbar.
        # An earlier version scoped this to parent=toolbar, so if the operator
        # had dragged the folder somewhere else the lookup missed and a SECOND
        # folder with the same title was created. Look globally, prefer a
        # toolbar-parented folder, and refuse to guess when ambiguous.
        matches = cur.execute(
            "SELECT id, parent FROM moz_bookmarks WHERE title=? AND type=2", (FOLDER_TITLE,)
        ).fetchall()
        on_toolbar = [m for m in matches if m[1] == toolbar_id]
        if len(on_toolbar) == 1:
            folder_id = on_toolbar[0][0]
            print("folder exists on toolbar (id %d) - adding missing bookmarks only" % folder_id)
        elif len(matches) == 1:
            folder_id = matches[0][0]
            print(
                "NOTE: folder %r (id %d) is not on the toolbar - it lives under "
                "parent %d (the operator probably moved it). Reusing it rather "
                "than creating a duplicate." % (FOLDER_TITLE, folder_id, matches[0][1])
            )
        elif len(matches) > 1:
            sys.exit(
                "several folders titled %r exist (ids %s) - pass --folder-id N to "
                "choose one, after deleting the stale duplicate in Firefox"
                % (FOLDER_TITLE, ", ".join(str(m[0]) for m in matches))
            )
        else:
            cur.execute(
                "INSERT INTO moz_bookmarks (type, parent, position, title, dateAdded,"
                " lastModified, guid) VALUES (2, ?, 0, ?, ?, ?, ?)",
                (toolbar_id, FOLDER_TITLE, stamp, stamp, guid()),
            )
            folder_id = cur.lastrowid
            print("created folder %r (id %d) on bookmarks toolbar" % (FOLDER_TITLE, folder_id))

    position = cur.execute(
        "SELECT COALESCE(MAX(position), -1) FROM moz_bookmarks WHERE parent=?",
        (folder_id,),
    ).fetchone()[0]
    added = 0
    for title, url in ITEMS:
        ok = cur.execute(
            "SELECT b.id FROM moz_bookmarks b JOIN moz_places p ON p.id=b.fk"
            " WHERE b.parent=? AND p.url=?",
            (folder_id, url),
        ).fetchone()
        if ok:
            print("  present: %s" % title)
            continue
        position += 1
        pid = place_id(cur, url, title)
        cur.execute(
            "INSERT INTO moz_bookmarks (type, fk, parent, position, title, dateAdded,"
            " lastModified, guid) VALUES (1, ?, ?, ?, ?, ?, ?, ?)",
            (pid, folder_id, position, title, stamp, stamp, guid()),
        )
        added += 1
        print("  added: %s -> %s" % (title, url))

    if dry_run:
        con.rollback()
        print("dry run: rolled back (%d would be added)" % added)
    else:
        con.commit()
        print("committed: %d bookmark(s) added" % added)

    entries = cur.execute(
        "SELECT b.title, p.url FROM moz_bookmarks b LEFT JOIN moz_places p ON p.id=b.fk"
        " WHERE b.parent=? ORDER BY b.position",
        (folder_id,),
    ).fetchall()
    print("folder now holds %d entries:" % len(entries))
    for title, url in entries:
        print("   %-28s %s" % (title, url))
    con.close()


if __name__ == "__main__":
    main()
