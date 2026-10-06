---
item: SEC-04
action: new
evidence: |
  ao-ingress-payment.service is running on a secret delivery copy that is older
  than the process reading it, and nothing reports it.

  $ systemctl --user is-active ao-ingress-payment.service
  active
  $ systemctl --user show ao-ingress-payment.service -p ActiveEnterTimestamp
  ActiveEnterTimestamp=Thu 2026-10-01 15:08:41 PDT 2026

  $ stat -c '%n mtime=%y' ~/.local/share/ao-secrets/payment.env
  payment.env mtime=2026-09-30 23:18:29.786526608 -0700

  → the env file predates the process by ~16h. Every start since 2026-10-01 has
  read a file frozen at 2026-09-30.

  The wallet folder the fetcher needs does not exist:

  $ python3 … folderList(h,'ao-secret-reader')
  ao-payment exists: False
  ao-archive exists: False

  wallet_folder_for maps payment-db-password and the three webhook entries to
  ao-payment (fetch-kwallet-secret.sh:90). fetch_secret exits 2 on an unmapped
  key and 3 on a missing entry.

  The failure is silenced, so it is invisible in the journal:

  $ grep -rn 'ExecStartPre=-' quadlet/
  quadlet/payment/ao-ingress-payment.container:63:ExecStartPre=-…fetch-kwallet-secret.sh %h/.local/share/ao-secrets/payment.env payment-credentials

  $ journalctl --user -u ao-ingress-payment.service --since 2026-10-01 \
      | grep -cE 'wallet entry unavailable|no wallet folder mapped'
  0
section: 14-secrets-and-service-identity
---

**New item, not a closure.** SEC-01 through SEC-03 are policy/documentation items blocked on
one operator decision. This is a different kind of thing: a live fault in the delivery
mechanism, found by re-measuring rather than inherited, and it is not covered by any of the
three.

Recorded as **§14.1.7**. What that subsection contains, all of it measured above: the absent
`ao-payment` folder; the file-older-than-process staleness; the `ExecStartPre=-` prefix that
silences the failure; the live `sales-db-password` embedded in the stale DSN and the resulting
correction to ST-12; and the guard carve-out that makes the file invisible.

Also added to §14.2.5 as **break-glass step 2**: compare env-file mtime against the unit's
`ActiveEnterTimestamp`. This is now the cheapest check in the list and the only reliable
signal for this class of fault, because a fetch failing under `-` produces no log line at
all. Existing steps renumbered 3–5 to make room; no step was removed.

Why this is not folded into SEC-01: SEC-01 asks the operator to ratify a deviation or
authorise a migration. This is a service running now on stale credential material, and it
needs a decision independently of how the deviation is ratified — the answer could be "create
the four wallet entries" whether or not the deviation is ever approved.

**Not fixed. Not touched.** The fix touches payment credentials and a running payment
service: a stop condition in this session's brief, and README §4.1 rules 12 and 14.
Specifically not done: creating the `ao-payment` folder or its four entries; removing or
altering the `-` prefix on line 63; restarting the unit; deleting `payment.env`. All four
are the operator's.

Recommended order, in the section and here: create the four `ao-payment` entries first — it
is ST-12's own outstanding action and fixes staleness as a side effect — then decide whether
the `-` prefix stays. Rotation of `sales-db-password` is **not** required: the value was
never committed to Git, a backup set, or an external network, and the exposure is a local
`0600` file. Rotation becomes required only if the operator judges the host account
untrusted.

Cross-group: the ST-12 row needs its "runs with no DSN" text corrected and ST-12 is the
compiler's, not mine. The `ao-payment` wallet-entry provisioning is already ST-12's
outstanding action.

What I got wrong: my first draft of the §14.1.7 evidence block quoted

    sed -n 's|^PAYMENT_DSN=.*|\1|p' payment.env

which is wrong twice — there is no capture group in that pattern, so `sed` exits with
"invalid reference \1", and even if it ran it would replace the whole line with the empty
string. I had pasted the pattern from memory instead of from the shell. I caught it because
the documented `wc -c` output was 49 and I re-ran the command to check; the bad form returns
0 *and* errors, so it could not have produced a wrong-but-plausible number silently.
Corrected in the section to the form actually run, and re-run to confirm 49 / `03521083973b`.

What I got wrong, second: I initially recorded the seven `ao-*` folders as holding "39
entries". Measured, it is **37**; 39 is `ao-*` (37) plus `Passwords` (2), which is how §14.1.4
phrases it. The number I gave was wrong, but the conclusion drawn from it — that §14.1.4's 39
is still current — survived, because 37+2=39 exactly. I only caught this because the count
felt high and I re-measured instead of asserting it. Total across all 15 folders is 52,
including 11 unrelated application folders; an unqualified "entries in the wallet" count is
meaningless, and that is the trap.


  ### Supporting measurement detail

`grep -rn 'ExecStartPre=-' quadlet/` returns exactly one hit — this line. The `-`
makes systemd discard the exit status, converting a recurring hard fetch
failure into silence.

The stale file is NOT inert, and §19 ST-12's "runs with no DSN" is wrong:

    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env | wc -c
    49
    $ … | tr -d '\n' | sha256sum | cut -c1-12
    03521083973b

48-char password, sha256 prefix identical to the LIVE `sales-db-password`
(§14.1.6 records `03521083973b`, len 48). The DSN is
`postgresql://sales_migration_role:<password>@127.0.0.1:15432/salesdb` and it is
present. ST-12's conclusion that the adapter "cannot accept a payment" rests
on a measurement that does not hold.

`check-secrets-exposure.sh` cannot see the file either:

    $ bash scripts/validation/check-secrets-exposure.sh
    OK: no secret-shaped content in tracked files      (rc=0)

Cause is the carve-out at `check-secrets-exposure.sh:79` — `PAYMENT_DSN` is not
in `$secret_key_re` because the key name is a DSN, not a "secret-shaped" name.

## Third pass, 2026-10-04 (this session)

### This proposal did not parse until this pass

**The defect, and it mattered.** When I read this file back to merge it, `yaml.safe_load` on its
frontmatter failed outright:

    YAML ERROR: while scanning an alias
      in "<unicode string>", line 37, column 1:
    **New item, not a closure.** SEC ...
    expected alphabetic or numeric character, but found '*'

`grep -n '^---'` returned exactly two hits — line 1 and line 119. The closing fence was
missing, so lines 37–117 (the entire prose body) were absorbed into the `evidence:` block scalar,
and a bare `**bold**` line is not valid YAML. Any merge script that parses these proposals would
have raised on this file, or silently skipped it. **The one proposal describing a live
unreported payment fault was the one that could not be read.**

Fixed: the frontmatter now closes after the evidence, and the orphaned duplicate evidence block
that had been stranded after the body (lines 94–119, a second copy of the `-`-prefix and DSN
measurements) is re-indented into prose under a "Supporting measurement detail" heading. Nothing
was deleted; the duplicated measurements were kept because they are evidence. Verified by
parsing all four `sec-*.md` files:

    sec-SEC-01.md OK action=update item=SEC-01
    sec-SEC-02.md OK action=update item=SEC-02
    sec-SEC-03.md OK action=close  item=SEC-03
    sec-SEC-04.md OK action=new    item=SEC-04

**I own this defect.** The file is a `sec-*` proposal, so it is mine; I am not reporting it as
someone else's.

### Re-verification: the fault is still live

Re-measured from scratch, not inherited:

    $ systemctl --user is-active ao-ingress-payment.service
    active
    $ systemctl --user show ao-ingress-payment.service -p ExecStartPre
    ExecStartPre={ … ignore_errors=yes ; … }

`ignore_errors=yes` is systemd's own rendering of the `-`, so the silencing is confirmed from
runtime state, not only from the quadlet source. `payment.env` mtime is still 2026-09-30
23:18:29 against an `ActiveEnterTimestamp` of 2026-10-01 15:08:41. `hasFolder` confirms
`ao-payment` and `ao-archive` absent, the other seven `ao-*` folders present.

### What I got wrong

A regex. I enumerated `legacy-alwayson-folder.env` with `^([A-Za-z0-9_]+)=` and got **zero
pairs**, when `wc -l` says the file has 4 lines and 3 of the 4 key names contain hyphens. Read
literally, "zero pairs" would have meant the file holding three live database passwords was now
empty — a false claim about a security improvement that never happened. Corrected to
`^([A-Za-z0-9_-]+)=`, which reproduces §14.1.6's table exactly. **A zero from a parser needs an
independent check before it is recorded.**

Two API traps, also recorded in §14.1.7.1: `folderList` returned 14022 rows on one call and
14274 on the next on an unchanged wallet, so it is unusable as a count — use `hasFolder`, which
is what `kwallet-provision.sh:42` uses. And `entryList` (`as`) is not `entriesList` (`a{sv}`);
calling `int()` on the former raises `TypeError`.