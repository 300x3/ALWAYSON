---
item: PAY-03
action: close
evidence: |
  $ ./scripts/validation/validate-sale-receipt.sh /tmp/paydemo/receipt.json
  OK: structural receipt validation passed: /tmp/paydemo/receipt.json
  exit=0

  $ ./scripts/validation/validate-sale-receipt.sh /tmp/paydemo/receipt-bad.json   # + card_number
  ERROR: prohibited sensitive field present
  exit=13

  $ ./scripts/ledger/build-manifest.sh sales_receipt ao-sales \
      /tmp/paydemo/ao/receipt.json \
      sales/receipts/TXN-20261003T120000Z-ABCDEF012345/receipt.json \
      TXN-20261003T120000Z-ABCDEF012345
  {
    "object_id": "a7e28263-e3e5-43b9-9196-769af64eebaa",
    "object_type": "sales_receipt",
    "origin_domain": "ao-sales",
    "created_at_utc": "2026-10-04T02:44:26Z",
    "schema_version": "1.0",
    "content_hash_sha256": "889b51ee14dd9ef15e5c8d328b9fffb92d8ac72c601239e9eb4bb2546aa080c3",
    "content_size_bytes": 733,
    "local_storage_reference": "sales/receipts/TXN-20261003T120000Z-ABCDEF012345/receipt.json",
    "ipfs_cid": "", "pcloud_archive_reference": "",
    "transaction_id": "TXN-20261003T120000Z-ABCDEF012345",
    "authorization_policy_id": "", "producer_key_id": "", "signature": ""
  }
  exit=0

  $ python3 -c "...scan manifest for sensitive tokens..."
  manifest keys: ['authorization_policy_id', 'content_hash_sha256', 'content_size_bytes',
   'created_at_utc', 'ipfs_cid', 'local_storage_reference', 'object_id', 'object_type',
   'origin_domain', 'pcloud_archive_reference', 'producer_key_id', 'schema_version',
   'signature', 'transaction_id']
  sensitive tokens present in manifest: NONE
  content_hash equals sha256(receipt): True

  $ ./scripts/ledger/sign-manifest.sh manifest.json <throwaway /tmp Ed25519 key>
  OK: detached signature at manifest.sig and embedded in manifest
      (digest 2429953e1470a29403d9d4e8725e283ed76b0596c121c7432ff0c19547184513)

  $ openssl pkeyutl -verify -pubin -inkey <pub> -rawin -in <PRE-sign digest> -sigfile sig.raw
  Signature Verified Successfully

  $ openssl pkeyutl -verify ... -in <POST-sign digest of final file> -sigfile sig.raw
  Signature Verification Failure
  exit=1

  $ shred -u throwaway-test-key.pem throwaway-test-key.pub sig.raw d.txt d2.txt manifest.sig
  $ rm -rf /tmp/paydemo /tmp/paylab
  $ ls -d /tmp/paydemo /tmp/paylab
  ls: cannot access '/tmp/paydemo': No such file or directory
section: 07-public-storefront-and-payment-policy
---
**PAY-03's stated acceptance criterion is met and proven: "A sales receipt manifest
can be generated without exposing sensitive data."** Closing on that criterion.

Evidence chain, all read-only against a scratch receipt in `/tmp`: the receipt
passes structural validation (exit 0); the *same* receipt with a `card_number`
field is rejected with exit 13, so the sensitive-field gate is enforced rather
than documented; `build-manifest.sh` emits a 14-field manifest containing no
customer, SKU, serial or card token and whose `content_hash_sha256` matches
`sha256(receipt)`; `sign-manifest.sh` attaches an Ed25519 signature that verifies
(`Signature Verified Successfully`). Nothing was submitted anywhere —
`submit-ledger-event.sh` exits 3 at staging because the gateway is undeployed.

§7.3.1 now records this, plus a **trap I found while proving it**: the signature
is over the *pre-signing* digest, so verifying against the final manifest fails
with `Signature Verification Failure`. No in-tree verifier accounts for this and no
`verify-manifest` script exists. The ingest-side verifier must hash the manifest
with `signature` and `producer_key_id` removed, or it will reject every validly
signed manifest. Recorded in §7.3.1 so the next builder cannot miss it.

**Scope I did not close, and want the compiler to see.** PAY-03's *title* is
"Sales API and receipt/fulfillment workflow". The receipt/manifest half is real and
proven. The **Sales API does not exist** — no Quadlet unit, script or config
anywhere in the tree implements one; the only `ao-sales` containers are
`ao-sales-db` and §15.3's five Mastodon containers, and `ao-sales` is a network,
not an application. So nothing in the current build can turn a verified payment
event into an order/receipt/entitlement record. I am **not** closing that gap by
silence: §7.3.1 states it as OPEN, and I propose a new item.

What I got wrong:

1. **I wrote "Ed25519 signing works" into §7.3.1 on the strength of the earlier
   session summary, before I had run it.** This session ran it, and the naive
   verification *failed*. My first conclusion — that the signing chain was broken —
   was also wrong: I had hashed the post-signing file. The real answer required
   reading `sign-manifest.sh` line by line to see the digest is taken before the
   `jq` mutation. Both halves of that were mistakes; recording them because
   "signing works" and "verification works" looked identical until the last command.
2. **I used a throwaway `/tmp` Ed25519 key rather than a wallet key, deliberately.**
   `sign-manifest.sh` only accepts `wallet:ao-sim-vehicle` or
   `wallet:ao-sim-fabrication`. I did **not** use those, because a *simulation*
   producer key must never sign a real sale receipt — that would put a sim identity
   into receipt provenance. I also did not create any new wallet entry. The
   throwaway key was shredded. The consequence to note: **the sales producer key
   does not exist in the wallet at all** (`ao-ledger hasFolder= False`), so
   production receipt signing is blocked on an operator-created key. I did not
   create the key; creating signing credentials is the operator's call.