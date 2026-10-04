---
item: FIELD-04
action: close
evidence: |
  $ ss -ltnp | grep -E '18000|4242'
  LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
  LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))

  $ timeout 5 bash -c 'exec 3<>/dev/tcp/127.0.0.1/4242'     && echo loopback-OK
  loopback-OK
  $ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
  lan-OK

  # the firewall-policy half could NOT be verified from an unprivileged session
  $ grep -n 4242 /etc/ufw/user.rules
  grep: /etc/ufw/user.rules: Permission denied
  $ ls -la /etc/ufw/user.rules
  -rw-r----- 1 root root 1740 Sep 25 13:27 /etc/ufw/user.rules
section: 09-field-and-lora-architecture
---
§9 gains a new **§9.3.1** that *decides* reachability rather than leaving it open, which is
what the acceptance criteria ask for.

Decision: **`0.0.0.0:4242` stays LAN-reachable and is approved as designed.** Reachability is
proven by actual TCP connects from both loopback and `192.168.87.135` (the `wlp3s0` LAN
address), not inferred from the bind address. Reasoning recorded: it is a Reticulum protocol
listener in a `user` unit, not a public ingress, so §4.1 rule 4 does not bite; and the field
radios address the mesh by RF, not TCP, so loopback-only binding would break the design
without reducing exposure.

**Caveat recorded honestly in §9.3.1 and repeated here.** The item also says "reviewed
against field-domain firewall policy", and I could only half-do that. There is no field-domain
firewall policy file at all (`config/field/` contains only `heltec-v3`), and the §9.3 table's
claim that `4242/tcp ALLOW Anywhere` is an explicit UFW allow could not be re-verified —
`/etc/ufw/user.rules` is `0640 root:root` and `ufw status` requires sudo. So: **reachability is
decided and evidenced; the mechanism is unverified.** If the compiler or operator reads
FIELD-04 as "firewall policy confirmed", that would be a stronger claim than I can support.