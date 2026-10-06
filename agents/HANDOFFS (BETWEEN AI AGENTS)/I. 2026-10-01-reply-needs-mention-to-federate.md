# COORDINATION — I: bot replies never left the instance — replies need an explicit @mention to federate

**From:** Cline session, 2026-10-01 (late afternoon)
**Scope:** `mastodon-openclaw-bridge.service` — corrects document **H**
**State:** Root cause found, fixed, **VERIFIED PUBLICLY** (`replies_count: 1` on
`mastodon.social`). **NOT committed.** Script is outside the repo.

**This document retracts two claims I made in H.** Read it before trusting H.

---

## Read this first

1. **RETRACTION (H): I said the reply "federated out". It did not.** I saw
   `ActivityPub::DeliveryWorker ... INFO: done` and called that proof. It was
   **not** — that inner `DistributionWorker` ran with an *empty* delivery set and
   the `DeliveryWorker` I grepped was a **different, unrelated job**. The reply
   never left the instance. **I verified the wrong thing and said so with
   confidence.** A worker log saying "done" means the job ran, not that it sent
   anything.
2. **RETRACTION (H): I answered the wrong post.** Notification ids are in
   **processing order, not chronological order**. I set the cursor to `4`
   believing id 5 was the newest mention. It was the *oldest* (21:28). Your post
   was notification **id 1** (22:52). I answered a stale backlog post instead of
   the one you were looking at.
3. **The real cause: a Mastodon reply only reaches a remote inbox if the parent
   author is @mentioned in it, or follows the bot.** The bot has **zero
   followers** and the reply mentioned **nobody**, so both delivery sets were
   empty and nothing was ever queued. The `@author` prefix is load-bearing
   infrastructure, not decoration.
4. **"Nothing here" was correct and I should have believed it sooner.** The local
   database had the reply; the public timeline did not. Local presence ≠ public
   presence.

---

## Evidence: the delivery sets were empty

```
$ rails runner
reply id=117368134418083152 visibility=public reply?=true
in_reply_to_account_id=117367694533297015 (300x3@mastodon.social)
mentions on reply=0 -> []

deliver_to_all_followers!          -> @account.followers_for_local_distribution.count = 0
deliver_to_mentioned_followers!    -> mentions JOIN followers_for_local_distribution = 0

=> NOBODY is in either delivery set, so no DeliveryWorker is ever created.
```

From `app/services/fan_out_on_write_service.rb`:

```ruby
def deliver_to_all_followers!
  @account.followers_for_local_distribution...      # the BOT's followers -> 0
end

def deliver_to_mentioned_followers!
  @status.mentions.joins(:account).merge(@account.followers_for_local_distribution)...
end
```

Both paths reach remote servers **only through the bot's follower set**. With no
followers, a mention-less public reply is silently local. `visibility: public`
alone does **not** federate a reply.

### Proof it was invisible in public

```
$ curl https://mastodon.social/api/v1/statuses/117368106037492186
replies_count: 0                      # operator's post, nothing there

$ curl -H 'Accept: application/activity+json' \
    https://mastodon.300x3.com/users/bot/statuses/117368134418083152
status=200                            # our copy existed... locally and publicly
```

The status was fetchable at its canonical URL — but nothing had been *pushed* to
`mastodon.social`, so it never appeared in the thread. **These are different
things and I conflated them.**

---

## The fix

`~/.local/bin/mastodon-openclaw-bridge.py`, before posting:

```python
# Mastodon only federates a reply to remote inboxes when the parent author is
# MENTIONED in it (or follows the bot). ... So the mention is load-bearing,
# not decoration.
if author and '@' not in answer.split()[0]:
    answer = f'@{author} {answer}'
```


---

## Verified — publicly, this time

Cursor reset to `0` so notification **1** (your post) was answered first:

```
$ tail -1 ~/.openclaw/mastodon-bridge.log
2026-10-01T16:07:57-0700 replied to status 117368106646301274 from
300x3@mastodon.social: 117368165343122068

reply text="@300x3@mastodon.social I'm online and functioning normally—just checking in!"
mentions=["300x3@mastodon.social"]        # <- the fix, working
```

A **real** `DeliveryWorker` fired and did work (0.72s, vs nothing before):

```
class=DistributionWorker            jid=24d40bd7 INFO: start / done
class=ActivityPub::DistributionWorker jid=95d7e7cd INFO: start / done
class=ActivityPub::DeliveryWorker   jid=e61378b2 INFO: start
class=ActivityPub::DeliveryWorker   jid=e61378b2 elapsed=0.72 INFO: done
```

**And confirmed from the outside, on mastodon.social's own API:**

```
$ curl https://mastodon.social/api/v1/statuses/117368106037492186
replies_count: 1

$ curl https://mastodon.social/api/v1/statuses/117368106037492186/context
descendants: 1
   https://mastodon.300x3.com/users/bot/statuses/117368165343122068
```

mastodon.social fetched and displays our reply. **Full round trip confirmed from
the remote end.** §19.3 item 16 is genuinely done now.

---

## Traps

- **`DeliveryWorker ... done` is not proof of delivery.** There are several
  `DeliveryWorker` jobs; grep the one whose `jid` correlates with your status, and
  confirm the *delivery set was non-empty*. The definitive check is the **remote
  server's** view (`replies_count` / `/context`), not our logs.
- **Notification ids are insertion order, not time order.** After the backlog
  drained, id 1 was the *newest* post and id 5 the *oldest*. Never infer
  "newest" from the highest id. Sort by `created_at` if you care.
- **`Delivery` is not a model** (`NameError`); 4.3 records delivery attempts
  elsewhere. Don't go looking for a delivery table.
- **More 4.3 schema traps:** `Status#local_only` **does not exist** (the column
  is `local`) — reading it raised `NoMethodError` and I briefly misreported
  `local_only=true`. `users.username` and `accounts.acct` **also do not exist**;
  `User#locked?` does not exist either. Use `Account.find_by(username:,
  domain:)`.
- **A public reply with no mention and no followers does not federate.** This is
  the single most counter-intuitive behaviour in this whole subsystem and it
  fails *silently*.

---

## Housekeeping

- Cursor pinned to `5`, so notifications **2, 3, 4** (the 21:08–21:28 backlog)
  are **not** answered. They are stale test posts; three more public replies
  needs operator approval (rule 14). Say the word and I will answer them.
- All probe scripts removed from `mastodon-web:/tmp`; verified clean.
- Files changed, **UNCOMMITTED**:
  ```
  ~/.local/bin/mastodon-openclaw-bridge.py   (mention prefix + cursor guard)
  COORDINATION BETWEEN AI/I. 2026-10-01-reply-needs-mention-to-federate.md  (NEW)
  README.md                                   (§19.3 items 14/16 correction)
  ```
- Still outstanding from H: the bridge script is **not in git**, and its
  `ENV_FILE` fallback points at a file B deleted.
- Letters taken today: A, B, C, D, E, F, G, H, **I**. Next session takes **J**.
