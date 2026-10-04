---
item: SEC-01
action: update
evidence: |
  $ podman version --format '{{.Client.Version}}'
  5.7.0
  $ podman secret ls
  ID          NAME        DRIVER      CREATED     UPDATED
  → zero Podman secrets exist on this host.

  $ grep -rn 'EnvironmentFile\|--env-file\|Secret=' quadlet/ | wc -l
  18 references, ALL EnvironmentFile=/--env-file=. Zero Secret=.
  Confirms the item's premise: no service uses Podman secrets.

  $ podman run --rm --entrypoint /bin/sh docker.io/library/postgres@sha256:d74eeac9a... -c \
      'grep -n "POSTGRES_PASSWORD\|file_env" /usr/local/bin/docker-entrypoint.sh | head'
  235:	file_env 'POSTGRES_PASSWORD'
  → POSTGRES_PASSWORD_FILE IS honoured by the pinned image, so the Podman-secret
  migration is technically available, not blocked.

  Migration NOT applied: it changes live unit definitions and live credential
  delivery. Stops for operator approval per README §4.1 rule 14.
section: 14-secrets-and-service-identity
---
`update`, not `close` — the item asks for one of two things and only the second is
mine to do. The acceptance criterion is "either migrate … **or** record an approved
deviation with compensating controls". I have recorded the deviation in **§14.1.6**,
but **recorded is not approved**: §14.1.6 is headed "Recorded deviation" and opens
by stating the decision is reserved to the operator.

So SEC-01 should stay **Open** until the operator ratifies or rejects, at which
point the action becomes `close` either way. What changed is that the decision is
now fully evidenced and needs only a yes or no.

§14.1.6 records:

- **Why the mandated mechanism is unused.** Podman secrets would have to be
  populated *from* the wallet by a root or podman-owned helper at start-up, which
  relocates plaintext to a second long-lived store instead of removing it, and
  `Secret=` cannot be populated from a login-gated wallet at all. systemd
  `LoadCredential=` exists on the user manager but is not consumed by
  Podman-managed containers.
- **Six compensating controls**, each with the command that proves it: `umask 077`
  at fetcher line 14; `chmod 600`; atomic `.tmp`→`mv` write so a partial file is
  never read; `mastodon.env` ACL `user:ao-sales:r-- / group::--- / other::---`;
  `.gitignore:1` = `secrets/` with env files outside the worktree;
  `check-secrets-exposure.sh` for CI.
- **Env-file lifetime, stated precisely.** The item specifically asked for this
  and the honest answer is not the flattering one: the `0600` env files are **not
  shredded on exit**. They persist between starts and are overwritten in place;
  only the `.tmp` is removed, with `rm -f`, not `shred`. Only `post.sh` and
  `sign-manifest.sh` shred. §14.1.1 calls these files "a plaintext duplicate" —
  the deviation accepts that exposure and designates the wallet as system of
  record instead. I did not want to paper over this, since it is the weakest part
  of the deviation and the operator should see it plainly.
- **The migration path, proven available** (above): `Secret=` mounted at
  `/run/secrets/…` plus `Environment=POSTGRES_PASSWORD_FILE=/run/secrets/…`
  satisfies §14.1 for the four database services. Prepared, not applied.

**Operator decision requested — one of:**

1. **Ratify the §14.1.6 deviation** as written, including the non-shreded
   delivery-copy exposure. Then SEC-01 closes with no code change.
2. **Authorise the Podman-secret migration** for `ao-mastodon-db`, `ao-sales-db`,
   `ao-webodm-db`, `ao-fabrication-db`. Requires new credential delivery while
   services are live, so it needs a maintenance window.

I recommend (2) for the four database services only, since `file_env` is proven
to work there; the remaining consumers are not all `file_env`-aware and would
need separate handling.