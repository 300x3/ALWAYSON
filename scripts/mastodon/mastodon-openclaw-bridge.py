#!/usr/bin/env python3
"""Permanent Mastodon mention bridge for the local @bot account.

Polls Mastodon notifications, asks OpenClaw/Nemotron for a reply, and posts the
reply as a public threaded response. It starts at the current notification
cursor so historical mentions are not answered unexpectedly.
"""
import html
import json
import os
import re
import subprocess
import time
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

STATE_FILE = Path('/home/scottw/.openclaw/mastodon-bridge-state.json')
LOG_FILE = Path('/home/scottw/.openclaw/mastodon-bridge.log')
WALLET_HELPER = Path('/ALWAYSON/scripts/ops/wallet-read-secret.py')
WALLET_NAME = 'kdewallet'
WALLET_FOLDER = 'ao-mastodon'
WALLET_KEY = 'openclaw-bot-access-token'
# mastodon-web runs RAILS_ENV=production and upstream hardcodes
# config.force_ssl = true (config/environments/production.rb), which no
# environment variable can turn off. Plain HTTP to :3000 is answered with
# "301 -> https://127.0.0.1:3000/...", so urllib used to follow that redirect,
# attempt a TLS handshake against a Puma that speaks no TLS, and die with
# "SSL: RECORD_LAYER_FAILURE" - crash-looping on every restart and, on each
# attempt, pushing TLS bytes into Puma ("Are you trying to open an SSL
# connection to a non-SSL Puma?").
#
# The loopback proxy at :3300 terminates TLS and injects
# X-Forwarded-Proto: https, so it serves the API directly with no redirect and
# no handshake against Puma. Its certificate is self-signed for 127.0.0.1, so
# it is pinned explicitly below rather than disabling verification.
API = 'https://127.0.0.1:3300'
API_CA = '/ALWAYSON/secrets/mastodon/mastodon-local.crt'
API_SSL = ssl.create_default_context(cafile=API_CA)
MODEL = 'lmstudio/nvidia/nemotron-3-nano-4b'
POLL_SECONDS = 10
MAX_REPLY_CHARS = 480


def log(message):
    line = f'{time.strftime("%Y-%m-%dT%H:%M:%S%z")} {message}'
    print(line, flush=True)
    try:
        with LOG_FILE.open('a') as f:
            f.write(line + '\n')
    except OSError:
        pass


# A public reply must never carry internal paths, hosts, or ports. The
# Project Gutenberg Catechism link is public and stays; everything else that
# looks like internal infrastructure is removed before posting.
_INTERNALS = (
    re.compile(r'https?://\S*?(\d{1,3}(?:\.\d{1,3}){3}|localhost|\.local\b|\.internal\b)\S*', re.I),
    re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    re.compile(r'(?::|\s)(?:/|~/)[\w.~-]+(?:/[\w.~-]+){2,}'),
    re.compile(r'\b(?:127\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\S*:?\d*\b'),
    re.compile(r'\b(?:localhost|127\.|192\.168\.|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\S*:\d{2,5}\b', re.I),
    re.compile(r'\b[\w.-]*\.(?:local|internal|lan|home|corp)\b', re.I),
)
_PATHY = re.compile(r'\s*\(?\[?(?:local|internal) (?:file )?path[^\])]*\]?\)?', re.I)


def scrub_internals(text):
    """Strip filesystem paths and internal endpoints from a public reply."""
    cleaned = _PATHY.sub('', text)
    for pattern in _INTERNALS:
        cleaned = pattern.sub('[redacted]', cleaned)
    return re.sub(r'[ \t]{2,}', ' ', cleaned).strip()


class CredentialUnavailable(RuntimeError):
    """The Mastodon access token could not be read from KDE Wallet."""


def credentials():
    """Return the bot access token.

    KDE Wallet is the single source of truth (README 14.1.1, rule 7). There is
    deliberately NO plaintext-file fallback: the previous ENV_FILE fallback
    pointed at secrets/mastodon/openclaw-mastodon.env, which document B
    shredded during the secret consolidation. That made the path unreachable, so
    a wallet failure would have died with a bare FileNotFoundError on a file
    that must not come back.

    On wallet failure we retry rather than exit, because the common cause is
    simply that the wallet has not finished unlocking at login - a readiness
    race, not a credential fault.
    """
    token = read_wallet_token()
    if token:
        return token
    raise CredentialUnavailable(
        f'no {WALLET_KEY!r} in KDE Wallet folder {WALLET_FOLDER!r} '
        f'(wallet {WALLET_NAME!r}). The wallet is likely still locked; '
        f'if it stays empty, check that the entry exists. '
        f'There is intentionally no plaintext-file fallback.'
    )


def read_wallet_token():
    try:
        result = subprocess.run(
            [str(WALLET_HELPER), WALLET_NAME, WALLET_FOLDER, WALLET_KEY],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ''
    token = result.stdout.strip() if result.returncode == 0 else ''
    return token


def request(token, path, method='GET', data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    headers = {'Authorization': 'Bearer ' + token, 'Host': 'localhost:3000'}
    if body:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = urllib.request.Request(API + path, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=45, context=API_SSL) as response:
        return json.load(response)


def read_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(last_id):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps({'lastNotificationId': str(last_id), 'updatedAt': time.time()}, indent=2) + '\n')
    tmp.replace(STATE_FILE)


def text_from_html(value):
    value = re.sub(r'<br\s*/?>', '\n', value or '', flags=re.I)
    value = re.sub(r'</p\s*>', '\n', value, flags=re.I)
    value = re.sub(r'<[^>]+>', '', value)
    return html.unescape(value).strip()


def find_text(value):
    if isinstance(value, dict):
        for key in ('finalAssistantVisibleText', 'finalAssistantRawText', 'text'):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key].strip()
        for child in value.values():
            found = find_text(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_text(child)
            if found:
                return found
    return ''


def ask_openclaw(status_id, author, body):
    prompt = (
        'A Mastodon user mentioned you. Write a concise public reply for this conversation. '
        f'Parent author: {author}. Parent post: {body}\n'
        'Reply with only the reply text, no preamble or quotes.\n\n'
        'If the post asks who God is, who Jesus is, whether Jesus is God, the Trinity, or '
        'any other doctrine, answer it in a few plain conversational sentences, the way a '
        'person who has read the Catechism would talk - not like a citation machine. Do not '
        'add paragraph numbers or bracket references. Say in your first sentence exactly '
        '"JESUS CHRIST IS GOD." when the post asks who God is, and in that case only, close '
        'with the link https://www.gutenberg.org/ebooks/1722 inviting them to read it. For '
        'any other doctrinal question, offer that link only if the person seems genuinely '
        'interested in reading more. The full text is at '
        '/home/scottw/.openclaw/workspace/memory/lcms-large-catechism.md - read or grep it so '
        'you are accurate, but never invent a quotation and never mention the file path. '
        'Stay within the character limit by being concise, not by dropping the answer.'
    )
    result = subprocess.run(
        ['/home/scottw/.npm-global/bin/openclaw', 'agent', '--session-key',
         f'agent:main:mastodon-{status_id}', '--model', MODEL, '--message', prompt,
         '--thinking', 'off', '--json'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    if result.returncode:
        raise RuntimeError(f'OpenClaw exited {result.returncode}')
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError('OpenClaw returned invalid JSON') from exc
    answer = find_text(payload)
    if not answer:
        raise RuntimeError('OpenClaw returned no visible reply')
    answer = scrub_internals(answer)
    return answer[:MAX_REPLY_CHARS]


def main():
    # Wait for the wallet rather than crash-looping. A locked wallet at login is
    # a readiness race, not a fault; the service stays up and picks up the token
    # as soon as the wallet is readable.
    token = None
    waited = 0
    while token is None:
        try:
            token = credentials()
            if waited:
                log(f'wallet readable after {waited}s; continuing')
        except CredentialUnavailable as exc:
            if waited == 0:
                log(f'waiting for KDE Wallet: {exc}')
            waited += 15
            time.sleep(15)
    account = request(token, '/api/v1/accounts/verify_credentials')
    bot_id = str(account['id'])
    state = read_state()
    last_id = state.get('lastNotificationId')
    if not last_id:
        existing = request(token, '/api/v1/notifications?limit=40')
        last_id = max((str(n['id']) for n in existing), default='0')
        write_state(last_id)
        log(f'initialized notification cursor at {last_id}; historical mentions skipped')
    while True:
        try:
            items = request(token, '/api/v1/notifications?limit=40')
            # Guard against a cursor left over from a different database. The
            # notifications table was repopulated directly in PostgreSQL on
            # 2026-10-01, which restarted the id sequence at 1 while the
            # cursor on disk still read 13. Every notification then failed
            # `int(nid) <= int(last_id)` and was skipped forever, with no error
            # and no log line - the bridge looked healthy and replied to nothing.
            # If the newest notification is older than our cursor, the ids have
            # gone backwards and the cursor is meaningless: rewind to 0.
            newest = max((int(n['id']) for n in items), default=0)
            if last_id != '0' and newest and newest < int(last_id):
                log(f'cursor {last_id} is ahead of newest notification {newest}; '
                    'notification ids were reset - reprocessing from the start')
                last_id = '0'
                write_state(last_id)
            for notification in sorted(items, key=lambda n: int(n['id'])):
                nid = str(notification['id'])
                if last_id != '0' and int(nid) <= int(last_id):
                    continue
                last_id = nid
                write_state(last_id)
                if notification.get('type') not in ('mention', 'status'):
                    continue
                status = notification.get('status') or {}
                if str((status.get('account') or {}).get('id')) == bot_id:
                    continue
                sid = str(status.get('id') or '')
                if not sid:
                    continue
                author = (status.get('account') or {}).get('acct', 'unknown')
                body = text_from_html(status.get('content'))[:2500]
                try:
                    answer = ask_openclaw(sid, author, body)
                    # Mastodon only federates a reply to remote inboxes when the
                    # parent author is MENTIONED in it (or follows the bot).
                    # FanOutOnWriteService reaches remote followers only via
                    # deliver_to_all_followers! (the bot's own followers) and
                    # deliver_to_mentioned_followers! (mentions joined against
                    # those followers). With 0 followers and 0 mentions on the
                    # reply, BOTH sets are empty, no ActivityPub::DeliveryWorker
                    # is ever created, and the reply silently stays on this
                    # instance - even though the worker logs report "done".
                    # So the mention is load-bearing, not decoration.
                    if author and '@' not in answer.split()[0]:
                        answer = f'@{author} {answer}'
                    posted = request(token, '/api/v1/statuses', 'POST', {
                        'status': answer, 'in_reply_to_id': sid, 'visibility': 'public',
                    })
                    log(f'replied to status {sid} from {author}: {posted.get("id")}')
                except Exception as exc:
                    log(f'failed status {sid}: {exc}')
            time.sleep(POLL_SECONDS)
        except Exception as exc:
            log(f'poll error: {exc}; retrying')
            time.sleep(30)


if __name__ == '__main__':
    main()
