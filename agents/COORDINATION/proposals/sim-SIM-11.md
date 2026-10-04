---
item: SIM-11
action: update
evidence: |
  §19.1 describes the manifest as recording 5371 bytes against a world of "~18 KB".
  The drift is larger than recorded: the SIZE AND THE HASH both disagree.
  Measured 2026-10-03.

  $ python3 -c "import json,hashlib,pathlib;
      m=json.load(open('artifacts/fabrication-simulation-manifests/factory-world-v1.json'));
      w=pathlib.Path('GAZEBO/worlds/factory.world').read_bytes();
      print('manifest size :',m['content_size_bytes']); print('actual   size :',len(w));
      print('manifest sha  :',m['content_hash_sha256']);
      print('actual   sha  :',hashlib.sha256(w).hexdigest())"
  manifest size : 5371
  actual   size : 63205
  manifest sha  : 64eacbbf9ab041c11ca10bba55ac5dd733705615b0b83ab69919fa71656f84e5
  actual   sha  : bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053

  The world has since been rebuilt repeatedly after signing -- camera re-aiming
  (365bd42), generated rl_objects, safety_zones and conveyor_loops blocks, mesh
  shading (fa3f8f6, c24f673, ec34c71) -- so a signed manifest cannot track it by
  hand.

  Re-signing requires the `ao-sim-fabrication` key, which is a signing operation
  under README 4.1 rule 7. I did not perform it and did not read the key.
section: 10-simulation-architecture
---
SIM-11 is real and I am escalating it rather than closing it, because closing it
would require a signing operation I am not permitted to perform unattended.

The §19 description understates the drift. It records a size mismatch -- 5371
bytes recorded against a world of roughly 18 KB. The world is now **63205 bytes**,
almost twelve times the recorded size, and the `content_hash_sha256` no longer
matches either. Recorded hash `64eacbbf…`, actual `bce32f2a…`. Both fields are
wrong, which means this cannot be closed by correcting a number in the manifest.
The manifest has to be re-exported from the current world and re-signed.

That is why I stopped. Re-signing uses the `ao-sim-fabrication` key and is a
signing operation covered by README §4.1 rule 7; it needs explicit human approval
before it touches anything. I did not read the key, locate it, or attempt the
export.

The underlying cause is structural and worth recording: the manifest is signed
against a file that then keeps changing. Camera re-aiming, three generated model
blocks and four mesh-shading commits all landed after it was signed. Until
signing is tied to the export step rather than run by hand, this item will
reopen every time anyone edits the world.

§10.3 in my section file records the measured sizes and hashes.