"""Presentation: rows to Markdown and HTML.

Holds no policy and makes no network calls. The table column order (HEADERS)
and the CSS live here, so a layout change cannot reach back into collection.
"""
from __future__ import annotations

import re

# Imported names, not copies: render() primes the collector's apt-candidate
# caches with `_CAND_VER.clear()` / `.update()` between runs. Those are in-place
# mutations of a shared dict, which survive the import. A `global` REBINDING
# would not, which is why the collector owns OFFLINE and CACHE_TTL and the
# entrypoint sets them as attributes (see provenance-log.py set_offline()).
from .collector import (COLLECTED, cache_ttl, _CACHE_HITS, _CACHE_STALE, _CAND_VER,
                        apt_candidate_map, containers, desktop_apps,
                        desktop_owner_packages, direct_and_unmanaged,
                        download_cell, flatpaks, gazebo_summary, kde_block,
                        ros_summary, snaps, third_party_apt, ubuntu_headline,
                        ubuntu_summary)
from .common import norm, now_utc
from .policy import pin_policy, update_risk





HEADERS = ["Item", "Via", "Publisher", "Repository / archive", "Pinned",
           "Version here", "Up to date?", "Released", "Installed identity",
           "Released identity", "Installed", "Download / source page"]



def _fmt_age(seconds):
    s = int(seconds)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    return f"{s // 3600}h"



def render(inv, codename, offline):
    """One table. Every row, the same twelve columns, top to bottom."""
    # Prime the apt lookup maps with ONE call each. Doing this per row spawned
    # ~230 apt subprocesses and the run stopped completing in reasonable time.
    _CAND_VER.clear()
    # Only packages that actually appear as a row need a lookup. Querying all
    # 4,493 installed packages meant hundreds of apt round trips for ~230 answers.
    all_pkgs = {t["package"] for t in inv.get("apt_packages", [])
                if t["release"].startswith("Third-party")}
    all_pkgs |= desktop_owner_packages()
    _CAND_VER.update(apt_candidate_map(all_pkgs))
    cont, sn, fl = containers(offline), snaps(offline), flatpaks(offline)
    direct = direct_and_unmanaged(offline, inv)
    # The Ubuntu archive collapses to ONE row: 3,863 packages already covered by
    # apt and unattended-upgrades, which was 90 percent of the document and told
    # an operator nothing. Third-party repositories are listed individually,
    # because an update to those is a decision rather than a background event.
    ubuntu = ubuntu_summary(inv)
    ros = ros_summary(inv)
    gz = gazebo_summary(inv)
    third = [t for t in third_party_apt(inv) if "ros.org" not in (t["publisher"] or "")]
    apps = desktop_apps(inv)
    kde_row, kde_members = kde_block(inv)
    platform = ([kde_row] if kde_row else []) + [ubuntu_headline(inv)] + ubuntu + ros + gz
    rows = platform + cont + sn + fl + apps + third + direct

    n_ubuntu = sum(1 for t in inv.get("apt_packages", [])
                   if t["release"].startswith("Ubuntu"))
    behind = len([r for r in rows if match_of(r) == "**NO**"])
    current = len([r for r in rows if match_of(r) == "yes"])
    unknown = len([r for r in rows if match_of(r) == "?"])
    local = len([r for r in rows if match_of(r) == "local"])
    summary = len([r for r in rows if match_of(r) == "summary"])
    # Hand the collected rows back to main(). Rebuilding them there re-ran every
    # network lookup and every apt query a second time, doubling an online run.
    COLLECTED["rows"] = rows
    COLLECTED["counts"] = (behind, current, unknown, local, summary)
    COLLECTED["kde_members"] = kde_members
    COLLECTED["kde_row"] = kde_row

    L = []
    w = L.append
    w(f"# Software status - {inv['os']['pretty']} - {now_utc()[:10]}")
    w("")
    freshest = max(_CACHE_HITS.values(), default=None)
    oldest = None
    if _CACHE_HITS:
        ages = [a for a in _CACHE_HITS.values()]
        oldest, freshest = max(ages), min(ages)
    banner = []
    if offline:
        banner.append("**Offline run: cached upstream data only, no network was "
                      "contacted.**")
    if oldest is not None:
        _ttl = cache_ttl()
        ttl = f"{_ttl // 3600}h" if _ttl else "bypassed, every lookup forced"
        banner.append(f"Upstream data re-checked between "
                      f"{_fmt_age(freshest)} and {_fmt_age(oldest)} ago "
                      f"(cache TTL {ttl}).")
    if _CACHE_STALE:
        banner.append(f"**{len(_CACHE_STALE)} upstream lookups could not be "
                      f"re-checked and fell back to a STALE cached value.**")
    if banner:
        w(" ".join(banner))
        w("")

    # A container whose digest could not be fetched shows "-" in Released hash,
    # which is indistinguishable at a glance from "nothing to compare". Say
    # which ones failed so a blank is never read as a clean result.
    unresolved = [r["item"] for r in rows
                  if str(r.get("via", "")).startswith("container")
                  and str(r.get("rel_hash", "-")) == "-"
                  and not r.get("local")]
    if unresolved:
        w(f"**{len(unresolved)} container(s) have no Released hash:** "
          f"{', '.join(sorted(unresolved))}. Each is a distinct condition — a "
          f"local build, a floating tag, or an upstream fetch that failed; "
          f"expand the row to see which.")
        w("")
    w(f"**{len(rows)} items.** {behind} behind - {current} up to date - "
      f"{unknown} no version published - {local} local build - {summary} summary. "
      f"Plus {n_ubuntu} Ubuntu archive packages collapsed into one row: Canonical "
      f"ships and manages those, so itemising them told an operator nothing. "
      f"Generated by `scripts/build-update/provenance-log.py`; read-only.")
    w("")
    w("Publisher for snaps is the store account; a trailing `**` marks a "
      "**verified** publisher, not a claim of review. Container publishers are "
      "the registry namespace, which is where the image is hosted, NOT proof of "
      "who built it. `Installed identity` is a digest only for containers; for "
      "packages it is a dpkg-manifest hash, for snaps a revision, and for "
      "roll-ups an aggregate label.")
    w("")
    # TRIAGE FIRST. The full inventory is 229 rows and the items needing a
    # decision are scattered through it. Both reviewers of this document said
    # the same thing: it proves provenance rigorously and fails at triage, so
    # the actionable set is lifted to the top where the eye lands.
    action = [r for r in rows if match_of(r) in ("**NO**",)]
    if action:
        w("## Needs action")
        w("")
        w(f"**{len(action)} item(s) are behind.** Everything else in this "
          f"document is inventory and needs no decision.")
        w("")
        w("| Item | Via | Here | Target | Pin policy | Why it cannot simply be updated | Command to apply |")
        w("|---|---|---|---|---|---|---|")
        for r in sorted(action, key=lambda x: (x.get("via", ""), x["item"])):
            risk = update_risk(r)
            pol = pin_policy(str(r["item"]))[0]
            cmd = (r.get("download") or "no automated command")
            w(f"| `{r['item']}` | {r.get('via','-')} | `{r.get('pinned','-')}` | "
              f"`{str(r.get('released','-')).split(' ')[0]}` | {pol} | {risk} | "
              f"{('[cmd](' + cmd + ')' if cmd.startswith('http') else '`' + cmd + '`')} |")
        w("")
        w("**Nothing here has been updated.** Applying any of these is an "
          "operator decision; several carry exclusions recorded in "
          "`docs/runbooks/software-update.md` (WebODM and the payment path "
          "require prior verification).")
        w("")
    w("## Full inventory")
    w("")
    # The last column mixes three different kinds of evidence, so the header
    # names all three rather than calling them all "Installed":
    #   (apt history) - a real Install: stanza in /var/log/apt/history.log.
    #   (dpkg mtime)  - no apt record; the mtime of the dpkg manifest, which
    #                   dpkg rewrites on every unpack. That is install OR last
    #                   upgrade and cannot be told apart from the filesystem.
    #   - (pre-window upgrade D) - apt shows an upgrade but no install, so the
    #                   package predates the retained log window.
    w("Last column: `(apt history)` is the real install date from "
      "`/var/log/apt/history.log`. `(dpkg mtime)` means no apt record exists "
      "and the value is the dpkg manifest mtime, which is install OR last "
      "upgrade and cannot be distinguished. `- (pre-window upgrade D)` means "
      "apt shows the package upgraded on D but installed it before the "
      "retained log window.")
    w("")
    w("| Item | Via | Publisher | Repository / archive | Pinned | Version here | "
      "Up to date? | Released | Installed identity | Released identity | Installed | Download / source page |")
    w("|---|---|---|---|:---:|---|:---:|---|---|---|---|---|")
    rank = {"**NO**": 0, "?": 1, "summary": 2, "local": 3, "yes": 4}
    # ALL platform rows, in reading order: the desktop, the OS, the packages the
    # OS carries, the robot stack bound to it, and the simulator. A partial list
    # here silently pushed KDE and UBUNTU down into the ordinary ranking.
    platform_order = {"KDE Plasma Desktop": 0, "UBUNTU": 1,
                      "Ubuntu archive packages": 2, "ROS 2": 3, "Gazebo Sim": 4}
    def sortkey(x):
        # The three platform rows lead the table, in order, so the base system,
        # the robot stack bound to it, and the simulator read together.
        for k, n in platform_order.items():
            if str(x.get("item", "")).startswith(k):
                return (-1, n, "")
        return (rank.get(match_of(x), 5), 9, str(x.get("item", "")).lower())
    for r in sorted(rows, key=sortkey):
        cell = download_cell(r)
        mark = "\u2705" if r.get("is_pinned") else "\u274c"
        up = {"yes": "yes", "**NO**": "**NO**", "?": "?",
              "local": "local", "summary": "not applicable (roll-up)"}[match_of(r)]
        tag = r.get("tag")
        rel = f"`{r['released']}`" + (f" ({tag})" if tag else "")
        item = f"`{r['item']}`"
        if r.get("italic"):
            item = f"*{item}*"
        w(f"| {item} | {r['via']} | {r['publisher']} | {r['repo']} | {mark} | "
          f"`{r['pinned']}` | {up} | {rel} | `{r.get('pin_hash', '-')}` | "
          f"`{r.get('rel_hash', '-')}` | {r.get('date', '-')} | {cell} |")
    w("")
    return "\n".join(L) + "\n" + rollup_details_md(rows, kde_members) + "\n"



def rollup_details_md(rows, kde_members=None):
    """The collapsible drill-down blocks that follow the main table.

    Split out of `render()` so it can be tested: `render()` spends hundreds of
    apt round trips, which is not something a unit test should pay for to
    assert a formatting rule.
    """
    out = []
    w = out.append
    rolled = [(r["item"], r["members"]) for r in rows
              if r.get("members") and not r.get("package_rollup")]
    if rolled:
        w("")
        w("<details><summary>Rolled-up launchers — expand to list every "
          f"application entry ({sum(len(m) for _, m in rolled)} entries "
          f"across {len(rolled)} groups)</summary>")
        w("")
        w("| Package / group | Launchers |")
        w("|---|---|")
        for item, members in sorted(rolled):
            w(f"| `{item}` | {', '.join(members)} |")
        w("")
        w("</details>")
    # A package roll-up has thousands of members. Joining them into one table
    # cell produced a single 40,000-character line -- technically a drill-down,
    # practically unreadable, and worse than the count it replaced. One member
    # per row, in its own collapsible block per roll-up.
    for r in rows:
        if not (r.get("package_rollup") and r.get("members")):
            continue
        w("")
        w(f"<details><summary>{r['item']} — expand to list all "
          f"{len(r['members'])} packages with their installed versions"
          "</summary>")
        w("")
        w("| Package | Installed version |")
        w("|---|---|")
        for m in r["members"]:
            name, _, ver = m.rpartition(" (")
            w(f"| `{name}` | `{ver.rstrip(')')}` |")
        w("")
        w("</details>")
    if kde_members:
        w("")
        w(f"<details><summary>KDE Plasma Desktop — expand to list all "
          f"{len(kde_members)} components</summary>")
        w("")
        w("| Component | Owning package |")
        w("|---|---|")
        for nm, pk in kde_members:
            w(f"| {nm} | {('`' + pk + '`') if pk else '-'} |")
        w("")
        w("</details>")
    return "\n".join(out)



UNKNOWN = ("-", "no upstream", "no upstream feed", "no feed", "unreachable",
           "not recorded", "not installed by a package", "")



def _is_digest(v):
    return "sha256:" in str(v)



def _digest_of(v):
    """Hex after sha256:, ignoring any trailing " (tag)" annotation."""
    m = re.search(r"sha256:([0-9a-f]{8,})", str(v))
    return m.group(1) if m else ""



def same_version(a, b, exact=False):
    """Compare two version-ish values.

    Three traps, each of which once produced a confident "yes" on data that
    differed: digests must not go through norm() (which takes the "256" out of
    "sha256"); Debian revisions must not be stripped (1.2.15.3-1ubuntu1.5 and
    ...-1ubuntu1.7 both reduce to 1.2.15.3); everything else compares on the
    numeric core.
    """
    a, b = str(a), str(b)
    if _is_digest(a) or _is_digest(b):
        da, db = _digest_of(a), _digest_of(b)
        return bool(da) and da == db
    if exact:
        return a.strip() == b.strip()
    return norm(a) == norm(b)



NOT_A_VALUE = (
    "no upstream feed publishes updates", "no upstream digest published",
    "no repository checksum", "no candidate published", "candidate unavailable",
    "no vendor feed publishes updates", "no repository publishes updates",
    "no release feed configured", "no upstream digest for this tag",
    "revision not published", "no package repository", "version not recorded",
    "no version published", "remote unreachable", "channel unreachable",
)



def match_of(r):
    # A row with nothing to compare against is not "behind" - it is simply a
    # summary. The collapsed Ubuntu row compares two prose strings and would
    # otherwise always read as a finding.
    if r.get("nocompare"):
        return "summary"
    if r.get("force_match"):
        return r["force_match"]
    # If either side is an explicit "this is not a value" marker, there is
    # nothing to compare. Two identical error strings once compared equal and
    # produced a confident "yes" on a row whose version was never even read.
    for k in ("pinned", "released"):
        if str(r.get(k, "")).strip().lower() in NOT_A_VALUE:
            return "?"
    # Compare hashes when both are present. Display strings are for reading; a
    # comparison against "no version tag" or a rolling alias proves nothing.
    ph, rh = str(r.get("pin_hash", "")), str(r.get("rel_hash", ""))
    if _is_digest(ph) or _is_digest(rh):
        da, db = _digest_of(ph), _digest_of(rh)
        if da and db:
            return "yes" if da == db else "**NO**"
        return "?"
    pin = str(r.get("pinned", "-"))
    rel = str(r.get("released", "-")).split(" (")[0].strip()
    if r.get("local"):
        return "local"
    if rel in UNKNOWN:
        return "?"
    if "no version" in pin:
        return "?"
    return "yes" if same_version(pin, rel, r.get("exact", False)) else "**NO**"



CSS = ("body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1600px;"
       "margin:2rem auto;padding:0 1rem;color:#1c1c1e;background:#fff}"
       "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:12.5px}"
       "th,td{border:1px solid #d0d3d6;padding:.3rem .45rem;text-align:left;vertical-align:top}"
       "th{background:#e9ecef;position:sticky;top:0}"
       "tr:nth-child(even) td{background:#f8f9fa}"
       "code{background:#eef1f5;padding:.1rem .3rem;border-radius:3px;font-size:11.5px}"
       "details{margin:1rem 0}summary{cursor:pointer;font-weight:600}"
       # The inline roll-up drill-down lives inside a table cell, where a 1rem
       # block margin would break the row height and a 6.6pt print rule would
       # hide it entirely. It has to stay compact and always open when printed.
       "details.drill{margin:.15rem 0}details.drill>summary{font-weight:500;"
       "font-size:10.5px;color:#495057}details.drill ul{margin:.2rem 0 0 1rem;"
       "padding-left:.6rem}@media print{details.drill{display:block}"
       "details.drill ul{display:block}}"
       "h1,h2{border-bottom:1px solid #d0d3d6;padding-bottom:.3rem}"
       "blockquote{border-left:4px solid #adb5bd;margin:1rem 0;padding:.4rem 1rem;color:#495057}""h1{font-size:15pt} .counts{font-size:9pt;color:#444;margin:.2rem 0 .6rem}""tr.behind td{background:#fdecea}""@page{size:A4 landscape;margin:9mm}""thead{display:table-header-group} tr{page-break-inside:avoid}""body{font-size:6.6pt} table{font-size:6.2pt} th,td{padding:1px 2px}""code{font-size:5.8pt;background:none;padding:0}")



def rows_to_html(rows, counts, title, kde_members=None):
    """Emit the table straight to HTML, bypassing python-markdown.

    python-markdown's table extension does not finish on a table this size, so
    the markdown round-trip is skipped and the rows are written directly. Same
    data, same columns.
    """
    import html as H
    out = [f"<!doctype html><html><head><meta charset='utf-8'>"
           f"<title>{H.escape(title)}</title><style>{CSS}</style></head><body>",
           f"<h1>{H.escape(title)}</h1>", f"<p class='counts'>{H.escape(counts)}</p>",
           "<table><thead><tr>" + "".join(f"<th>{H.escape(h)}</th>" for h in HEADERS)
           + "</tr></thead><tbody>"]
    rank = {"**NO**": 0, "?": 1, "summary": 2, "local": 3, "yes": 4}
    # ALL platform rows, in reading order: the desktop, the OS, the packages the
    # OS carries, the robot stack bound to it, and the simulator. A partial list
    # here silently pushed KDE and UBUNTU down into the ordinary ranking.
    platform_order = {"KDE Plasma Desktop": 0, "UBUNTU": 1,
                      "Ubuntu archive packages": 2, "ROS 2": 3, "Gazebo Sim": 4}
    def sortkey(x):
        # The three platform rows lead the table, in order, so the base system,
        # the robot stack bound to it, and the simulator read together.
        for k, n in platform_order.items():
            if str(x.get("item", "")).startswith(k):
                return (-1, n, "")
        return (rank.get(match_of(x), 5), 9, str(x.get("item", "")).lower())
    for r in sorted(rows, key=sortkey):
        dl = r.get("download", "-")
        dl_cell = (f'<a href="{H.escape(str(dl))}">get</a>' if str(dl).startswith("http")
                   else H.escape(str(dl)))
        tag = r.get("tag")
        rel = H.escape(str(r["released"])) + (f" ({H.escape(str(tag))})" if tag else "")
        _it = H.escape(str(r["item"]))
        _item = f"<em><code>{_it}</code></em>" if r.get("italic") else f"<code>{_it}</code>"
        # A roll-up row is a dead end without its members: "plasma-workspace
        # (28 launchers)" tells an operator nothing they cannot act on unless
        # they can see which 28. The markdown path has a <details> block per
        # roll-up, but the HTML table did not - those members were computed,
        # carried on the row, and then silently dropped. So they are drilled
        # into inline here, on the row itself, where the count promised them.
        members = r.get("members") or []
        if members:
            lis = "".join(f"<li>{H.escape(str(m))}</li>" for m in members)
            _item += (f"<details class='drill'><summary>"
                      f"{len(members)} entries</summary>"
                      f"<ul>{lis}</ul></details>")
        cells = [_item,
                 H.escape(str(r["via"])), H.escape(str(r["publisher"])),
                 H.escape(str(r["repo"])),
                 "&#10003;" if r.get("is_pinned") else "&#10007;",
                 f"<code>{H.escape(str(r['pinned']))}</code>",
                 H.escape(str(match_of(r)).replace("**", "")),
                 f"<code>{rel}</code>",
                 f"<code>{H.escape(str(r.get('pin_hash', '-')))}</code>",
                 f"<code>{H.escape(str(r.get('rel_hash', '-')))}</code>",
                 H.escape(str(r.get('date', '-'))), dl_cell]
        cls = "behind" if match_of(r) == "**NO**" else ""
        out.append(f"<tr class='{cls}'>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    if kde_members:
        items = "".join(f"<li>{H.escape(str(n))}"
                         + (f" &mdash; <code>{H.escape(str(p))}</code>" if p else "")
                         + "</li>" for n, p in kde_members)
        out.append(f"<details><summary>KDE Plasma Desktop &mdash; expand to list all "
                   f"{len(kde_members)} components</summary><ul>{items}</ul></details>")
    out.append("</body></html>")
    return "\n".join(out)



def to_html(text: str) -> str:
    import markdown as md
    body = md.markdown(text, extensions=["tables", "fenced_code", "toc"])
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>ALWAYS ON — Software Provenance</title><style>{CSS}</style>"
            f"</head><body>{body}</body></html>")
