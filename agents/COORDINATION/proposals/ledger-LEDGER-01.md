---
item: LEDGER-01
action: update
evidence: |
  $ cd /ALWAYSON/data/corda-install && sha256sum -c corda-combined-worker-5.2.2.0.jar.sha256sum
  corda-combined-worker-5.2.2.0.jar: OK

  $ getent passwd ao-ledger
  ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nlogi

  $ getent passwd alwayson-ledger ; echo $?
  2
section: 11-ledger-provenance-archive-and-ipfs
---
**Re-verified a third time, 2026-10-04.** Every command above was re-run from
scratch and reproduced identically, including all three `sha256sum -c` sidecars:

```text
$ cd /ALWAYSON/data/corda-install && sha256sum -c *.sha256sum
corda-cli-installer-5.2.2.0.zip: OK
corda-combined-worker-5.2.2.0.jar: OK
notary-plugin-non-validating-server-5.2.2.0-package.cpb: OK
```

Still no key generated, exported, or activated. Also noted in §11.10: the same
runbook block this proposal quotes has **two further false claims** ("linger
enabled", "systemd user unit installed") which make its start command
unrunnable. LEDGER-01 remains open and operator-only.

**Stays open. Stopped deliberately — this is a hard stop condition.** The
acceptance criteria permit closure only after an operator ceremony is performed
and recorded, and explicitly forbid generating, replacing, exporting or
activating production ledger keys without explicit approval (README §4.1
rule 14). I did neither.

Added §11.7 recording the three ordered blockers: the TLS chain/keystores
(operator-held KWallet passphrases under `ao-ledger`), the `cordadb` owner role
password, and the encrypted worker config.

## Documentation bug found — wrong service account name

`docs/runbooks/ledger-bootstrap.md` says the service account is
**`alwayson-ledger`**. That account **does not exist**. The real account is
**`ao-ledger`** (uid 994). `alwayson-ledger` is the *home directory*, not a
username:

```text
$ getent passwd ao-ledger
ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin
```

An agent trusting the runbook would build the node under the wrong identity, or
conclude the account is missing and create a duplicate. `/home/alwayson-ledger`
is unreadable by `scottw`, so a direct `ls` returns `Permission denied` — that
is **correct**, not a fault. Do not "fix" it by loosening the mode or running the
node as `scottw`.

The same error appears in `logs/operations/2026-09-28-corda4-retirement.md`,
which refers to uid 994 as `alwayson-ledger`. **Both files are outside my
ownership, so I have not edited them — reporting instead.** The correction is
recorded in §11.7 of my own section.

Artifacts verified present: Corda 5.2.2 worker JAR, CLI installer, notary
plugin, all with checksum sidecars, `sha256sum -c` OK.