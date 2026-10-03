# 20. Status References

Read before changing the platform. The repository README, the local working folder, the
verification evidence, the version matrix, and the issue log are the current state; a change
that contradicts any of them is either wrong or needs a recorded deviation stated beside the requirement it departs from.

```text
README.md
VERSION
git log
docs/compliance/installation-status.md
/ALWAYSON/
```

Implementation references that sit outside the repository:

```text
/home/scottw/.openclaw/openclaw.json      community publication bridge, carried inside ao-sales
/home/scottw/.cloudflared/config.yml     tunnel credentials, 0400, mirrored to KDE Wallet
```

Never add API keys, passwords, tunnel credential JSON, or any other secret to this list.
