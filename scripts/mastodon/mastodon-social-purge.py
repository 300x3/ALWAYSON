#!/usr/bin/env python3
"""Bulk-delete your own mastodon.social posts, newest first, with a date floor.

Why this exists
---------------
mastodon.social rejects API calls authenticated with a session cookie
(`GET /api/v1/accounts/verify_credentials` -> 401 with and without a valid
`X-CSRF-Token`). A logged-in browser can only delete ~40 posts per 30-minute
window through the UI, which took three windows to clear a couple of hundred
test posts on 2026-10-01. An OAuth access token bypasses that: the REST API
accepts it directly and the rate limit is far more generous.

This script therefore takes a token you supply. It does NOT create, store or
read one for you.

Getting a token
---------------
On mastodon.social: Preferences -> Development -> Access token -> Generate.
Grant `read:accounts` and `write:statuses`. Then, without putting it in the
repo or your shell history:

    read -rs MASTODON_SOCIAL_TOKEN && export MASTODON_SOCIAL_TOKEN
    python3 scripts/mastodon/mastodon-social-purge.py --keep-since 2026-09-03
    unset MASTODON_SOCIAL_TOKEN

Safety rails
------------
* Refuses to run without `--yes`; without it this is a dry run that lists.
* Only ever deletes statuses whose author is the token owner, re-verified per
  status from the API, so it cannot delete anyone else's posts.
* Never touches posts on or after `--keep-since`; `--keep-since` is the
  boundary you keep (2026-09-03 on 2026-10-01).
* Deletion on mastodon.social is permanent and federated Delete activities are
  broadcast. Take a copy of the timeline first if you need one.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = 'https://mastodon.social'


def api(token, path, method='GET', body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Accept', 'application/json')
    if body is not None:
        data = json.dumps(body).encode()
        req.data = data
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


def collect(token, max_id=None, pages=40):
    """Walk the account's own statuses, newest first."""
    out, params = [], {'limit': '40', 'exclude_replies': 'false',
                       'exclude_reblogs': 'true'}
    if max_id:
        params['max_id'] = max_id
    for _ in range(pages):
        q = urllib.parse.urlencode(params)
        status, data = api(token, f'/api/v1/accounts/verify_credentials')
        if status != 200:
            sys.exit(f'cannot verify token (HTTP {status}): {data}')
        me = data
        status, data = api(token, f"/api/v1/accounts/{me['id']}/statuses?{q}")
        if status != 200:
            print(f'stopping: HTTP {status} {data}', file=sys.stderr)
            break
        if not data:
            break
        out.extend(data)
        params['max_id'] = data[-1]['id']
        if len(data) < 40:
            break
    return out, me


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keep-since', required=True,
                    help='ISO date; posts on/after this are NEVER deleted (e.g. 2026-09-03)')
    ap.add_argument('--yes', action='store_true', help='actually delete (default: dry run)')
    ap.add_argument('--dry-limit', type=int, default=20,
                    help='in a dry run, show at most N (default 20)')
    args = ap.parse_args()

    token = os.environ.get('MASTODON_SOCIAL_TOKEN', '').strip()
    if not token:
        sys.exit('MASTODON_SOCIAL_TOKEN is not set. See the docstring for how to '
                 'create one without putting it in your shell history.')

    keep_from = datetime.fromisoformat(args.keep_since).replace(tzinfo=timezone.utc)
    statuses, me = collect(token)
    print(f'account: {me["acct"]} ({me["id"]})')
    print(f'fetched {len(statuses)} statuses; keeping anything on/after {args.keep_since}')

    doomed = []
    for s in statuses:
        created = datetime.fromisoformat(s['created_at'].replace('Z', '+00:00'))
        if created >= keep_from:
            break                      # newest-first, so everything after is older
        # belt and braces: only ever delete our own
        if str(s.get('account', {}).get('id')) != str(me['id']):
            continue
        doomed.append((s, created))

    print(f'would delete {len(doomed)}')
    for s, d in doomed[:args.dry_limit if not args.yes else 5]:
        print(f'  {d.date()}  {s["id"]}  {(s.get("content") or "")[:60]!r}')
    if len(doomed) > (args.dry_limit if not args.yes else 5):
        print(f'  ... and {len(doomed) - (args.dry_limit if not args.yes else 5)} more')

    if not args.yes:
        print('\nDRY RUN. Re-run with --yes to delete.')
        return
    if not doomed:
        print('nothing to do.')
        return

    print(f'\ndeleting {len(doomed)} posts...')
    for i, (s, _) in enumerate(doomed, 1):
        status, body = api(token, f'/api/v1/statuses/{s["id"]}', method='DELETE')
        if status in (200, 202):
            print(f'  [{i}/{len(doomed)}] deleted {s["id"]}')
        else:
            print(f'  [{i}/{len(doomed)}] FAILED {s["id"]} HTTP {status} {body}',
                  file=sys.stderr)
            if status == 429:
                wait = body
                print('  rate limited; sleeping 60s', file=sys.stderr)
                time.sleep(60)
        time.sleep(0.4)
    print('done.')


if __name__ == '__main__':
    main()
