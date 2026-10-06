---
item: SEC-01
action: update
evidence: |
  Re-measured independently 2026-10-05, not inherited from the 10-04 pass.

  Premise of the item — "no service uses Podman secrets" — still holds:

    $ podman version --format '{{.Client.Version}}'
    5.7.0
    $ podman secret ls
    ID          NAME        DRIVER      CREATED     UPDATED
    (header only — zero secrets)
    $ grep -rn 'Secret=' quadlet/ | wc -l          -> 0
    $ grep -rn 'LoadCredential' quadlet/ scripts/  -> 0
    $ grep -rn 'EnvironmentFile=' quadlet/ | wc -l  -> 17

  The §14.1.6 compensating controls are real and still in place:

    fetch-kwallet-secret.sh:14   umask 077
    fetch-kwallet-secret.sh:193  } > "$OUTPUT_FILE.tmp"
    fetch-kwallet-secret.sh:195  mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
    fetch-kwallet-secret.sh:196  chmod 600 "$OUTPUT_FILE"
    fetch-kwallet-secret.sh:31   trap cleanup_tmp EXIT      (rm -f, NOT shred)
    .gitignore:1                 secrets/
    $ bash scripts/validation/check-secrets-exposure.sh
    OK: no secret-shaped content in tracked files      (rc=0)

  NEW this pass — one claim inside §14.1.6 re-measured. `mastodon.env` is NOT 0600,
  it is 0640 with an ACL (the other eight delivery files are 0600):

    $ stat -c '%a %s' ~/.local/share/ao-secrets/mastodon.env
    640 1041
    $ getfacl -p ~/.local/share/ao-secrets/mastodon.env
    user::rw-  user:ao-sales:r--  group::---  mask::r--  other::---

  `docs/runbooks/secrets.md` remains stale and is still not edited by me (not my file).
section: 14-secrets-and-service-identity
---
`update`, unchanged from the 10-04 proposal, and for the same reason: the item asks for
either a migration **or** an approved deviation, and only the second is mine to do.
§14.1.6 records the deviation with its compensating controls; **recorded is not approved**.
SEC-01 should stay **Open** pending the operator's ratification decision, and the action
becomes `close` either way once they answer.

What this pass adds is verification that every control §14.1.6 leans on is still real —
`umask 077`, the atomic `.tmp`→`mv` write, `chmod 600`, `.gitignore`, and the CI exposure
check all re-measured green — plus the confirmation that Podman secrets remain unused
(`Secret=` 0, `LoadCredential` 0, `podman secret ls` empty), so the migration option is
still on the table and un-started.

I also re-measured the delivery-set modes rather than trusting the note in §14.1.6: eight
files are `0600`, and `mastodon.env` is `0640` carrying `user:ao-sales:r--` with
`other::---`. The exception was already recorded; this pass confirms it independently.

**The operator decision is unchanged and still needs one word:** ratify §14.1.6 as written,
or authorise the Podman-secret migration for the database services. Not applied by me — it
changes live credential delivery (README §4.1 rule 14).