#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/add-firefox-server-bookmarks.py
# Adds the "ALWAYS ON Servers" folder to the bookmarks toolbar of a standard
# Firefox profile (places.sqlite) with one bookmark per local service.
#
# MUST run while that Firefox is closed: Firefox caches Places in memory and
# rewrites the database on exit, so rows added while it runs are lost.
# Always back up places.sqlite (+ -wal/-shm) before running.
#
# Usage: python3 add-firefox-server-bookmarks.py <profile-dir> [--dry-run]
import os
import sqlite3
import sys
import time
import uuid

FOLDER_TITLE = "ALWAYS ON Servers"
ITEMS = [
    ("ALWAYS ON Console", "http://127.0.0.1:8099/"),
    ("WebODM", "http://127.0.0.1:8000/"),
    ("Foxglove (ROS 2 + Gazebo)", "http://127.0.0.1:8099/sim"),
    ("Podman", "http://127.0.0.1:8099/podman"),
    ("Grafana", "http://127.0.0.1:3001/"),
    ("Metabase", "http://127.0.0.1:3002/"),
    ("Prometheus", "http://127.0.0.1:9090/"),
    ("Mastodon (local)", "http://127.0.0.1:3300/"),
    ("OpenClaw", "http://127.0.0.1:18789/"),
    ("MeshChatX", "https://127.0.0.1:18000/"),
    ("Domoticz", "http://127.0.0.1:8080/"),
]


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


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: add-firefox-server-bookmarks.py <profile-dir> [--dry-run]")
    profile = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    db = os.path.join(profile, "places.sqlite")
    if not os.path.exists(db):
        sys.exit("places.sqlite not found in %s" % profile)
    if os.path.exists(os.path.join(profile, "lock")):
        sys.exit("profile locked - close Firefox first (%s/lock exists)" % profile)

    con = sqlite3.connect(db)
    cur = con.cursor()
    row = cur.execute(
        "SELECT id FROM moz_bookmarks WHERE guid='toolbar_____'"
    ).fetchone()
    if not row:
        sys.exit("bookmarks toolbar folder not found")
    toolbar_id = row[0]

    stamp = now_us()
    existing = cur.execute(
        "SELECT id FROM moz_bookmarks WHERE parent=? AND title=? AND type=2",
        (toolbar_id, FOLDER_TITLE),
    ).fetchone()
    if existing:
        folder_id = existing[0]
        print("folder exists (id %d) - adding missing bookmarks only" % folder_id)
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
