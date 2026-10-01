# Handoff — ALWAYS ON topology graphic corrections

**To:** the language model working on the topology graphic.
**From:** Cline, working on `README-complete-integrated-current-plan - v7.md`.
**Date:** 2026-09-30
**Authority:** this document. Where it conflicts with `MERGE-NOTES.md` or the
README, this document wins.

---

## 0. What you are working on

```
/ALWAYSON/TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/
├── build_svg.py                       # THE SOURCE. Edit only this.
├── alwayson-single-topology.svg       # generated
├── alwayson-single-topology.png       # generated  11363 x 7850  LANDSCAPE
├── alwayson-single-topology-left.png  # generated  5081 x 7850   PORTRAIT
├── alwayson-single-topology-right.png # generated  6282 x 7850   PORTRAIT
├── alwayson-single-topology.pdf
├── alwayson-single-topology.html
├── alwayson-single-topology.json      # machine contract — do not hand-edit
└── MERGE-NOTES.md                     # background, now partly stale
```

Regenerate with:

```bash
cd "/ALWAYSON/TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC" && python3 build_svg.py
```

`build_svg.py` is 1491 lines. Layout is computed, not auto-ranked. `BANDS`,
`NODES`, `SECTIONS` and `EDGES` are the four structures you will touch.
`STYLE` (line ~970) maps edge kind to colour/dash/arrowhead.

**Hard constraints that must survive your changes**

- The complete diagram stays **landscape at native layout and scale**. Do not
  rotate, do not re-proportion, do not shrink it to fit.
- **Do not add titles, banners, or headings to the diagram.** An earlier revision
  added "Page 1 of 4 — …" labels and they were rejected as wasted space.
- Landscape aspect of the complete PNG must stay ≥ 1.4:1.
- Keep every node's `sec` field pointing at a real README section.
- Keep `node title` uniqueness and `node id` uniqueness.

---

## 1. Correction to an earlier finding — the prohibited edges are FINE

I previously flagged these three edges as errors. **That was wrong, and I am
retracting it.** Do not change them.

```python
("w_fab","w_core","Simulation to Corda core","no"),   # line 309
("x_pay","d_pg","Internet to database","no"),          # line 310
("x_cust","w_core","Internet to ledger","no"),         # line 311
```

They are intentional **"this does NOT happen" markers**, not routes. They are:

- grouped under the comment `# PROHIBITED (v6 4.3)` at line 303;
- kind `"no"`, which renders red `#c62828`, 2.0 wide, dashed `3 6`, opacity 0.5,
  with a distinct `ar_no` arrowhead;
- explained in the on-diagram **LINES** legend as
  `PROHIBITED — v6 §4.3 forbids it` (build_svg.py:767).

My error was reading the JSON edge list without checking the `kind` field and the
legend. **Leave all eight `"no"` edges exactly as they are.**

---

## 2. REAL defect #1 — `ao-egress-community` is removed from the architecture

This is the one change that must happen.

**Operator decision (2026-09-29):** the Mastodon/community publication work is
already located inside `ao-sales`. There is no separate community adapter
network. A separate `ao-egress-community` network is not part of the design.

The graphic still draws it as a live adapter. Fix:

1. **Delete the node** at build_svg.py:83:

```python
N("a_comm","adp","adp","ao-egress-community","The only way the bot reaches social media, Fediverse, chat, email",
  ["Publishes to Mastodon; the bot's only voice","Minimum OAuth scope · host allowlist"],"IN PROGRESS","3.1, 5.2, 15.4.3"),
```

2. **Delete both edges** (lines 246–247):

```python
("w_sales","a_comm","publish","ok"),
("a_comm","x_fedi","ActivityPub out","ok"),
```

3. **Remove `a_comm` from the SECTIONS list** (line 215):

```python
("adp", "Controller adapters", ["a_pay", "a_cf", "a_tun", "a_build", "a_arch"], "nodes"),
```

4. **Re-point the federation edge** so `x_fedi` still connects. Outbound
   federation now goes through the sales-domain egress bridge inside `ao-sales`:

```python
("w_sales","x_fedi","ActivityPub out via sales egress bridge","ok"),
```

5. `w_sales` purpose is currently `"Takes the order; writes it down"` — consider
   widening it to name its actual scope (see §3a and §4).

6. Update `MERGE-NOTES.md` to record that `ao-egress-community` was retired on
   operator instruction.

---

## 3. REAL defect #2 — content in the README that the graphic is missing

The README v7 now has flows the graphic does not show at all. This is the main
new work.

### 3a. PDF intake and PDF output, inside `ao-sales`

`ao-sales` is now the **only domain that touches customers directly**. It
coordinates social media, email and Mastodon, the AI bot and chat, and the
order-request and receipt workflows — including the **public PDF intake forms**
and **PDF output**.

Suggested new nodes in the `flow` band (band 9, "WHAT ACTUALLY HAPPENS"), near
the existing sale chain `f_sale1…f_cord`:

```python
N("f_pdfin","flow","flow","PDF intake","The public form a customer fills in",
  ["KIT REQUEST / order-request email","Standardised PDF","Hashed and reviewed"],"IN PROGRESS","7.1.1, 15.1.2"),
N("f_pdfout","flow","flow","PDF output","Receipts and reports the customer receives",
  ["Signed receipt / contract PDF","Sales + accounting report PDF"],"PLANNED","4.4, 7.2"),
```

Suggested edges — wire the intake into the existing sale chain so it is not a
dead end:

```python
("x_email","f_pdfin","written intake","ok"),
("x_store","f_pdfin","public intake form","ok"),
("f_pdfin","f_sale1","standardised PDF","ok"),
("f_sale4","f_pdfout","signed receipt PDF","ok"),
```

Exact placement is a layout judgement after you see the rendered result; the
content is a requirement.

### 3b. Post-sale IPFS transfer

`ao-egress-archive` is explicitly for **moving large data and the
image/map/telemetry files into IPFS for transfer after sale**, with no
Corda/archive dependency. The graphic currently only shows
`a_arch → x_pcloud  "encrypted egress"`, which understates it.

```python
N("x_buyer","ext","ext","Authorised recipient","Receives a sold map or telemetry package",
  ["Private swarm / pinning / encryption","Package · hash · authorisation"],"PLANNED","ES.2, 11.6"),
```

```python
("a_arch","x_buyer","post-sale IPFS transfer","ok"),
```

Update `a_arch`'s purpose text to say **IPFS for transfer after sale** first,
pCloud replication second — that is the operator's stated priority.

### 3c. Corda built on V5 with PostgreSQL

Recorded fact, from `/ALWAYSON/config/platform/version-matrix.yaml` line 54:

```
retired: "Corda 4.14.2 + H2 (~/corda) removed 2026-09-28; see README 18.2.1"
```

So: the retired **V4 test node and its H2 database were removed 2026-09-28**;
Corda is built on **V5 against `cordadb`** on host PostgreSQL 18; **no data is
migrated.** Do not imply a migration is in flight anywhere on the diagram.

---

## 4. Copy corrections — align the diagram with README v7

| Node | Current text | Change to |
|---|---|---|
| `h_konq` | `"The operator's only browser"` | `"Dedicated browser for automation"` |
| `h_rpi` | `"Flies with the aircraft — OFF-HOST"` | `"Drone — KaliOS on the Raspberry Pi 5 with the Autopilot Module — OFF-HOST"` |
| `w_fab` | `"Rehearses the factory and kitchen: every machine and arm runs its own"` | `"Coordinates all industrial engineering and production details — receives specific production data from each machine — and runs the kitchen"` |
| `a_pay` | `"The only way a payment can get in"` | Add the three providers: Zelle / PayPal / Coinbase |
| `a_build` | `"The only way new software arrives"` | Put "Software updates" in the purpose text |
| `d_meta` | `"REPORTS — business and ad hoc analysis"` | **keep** — Metabase is the reporting tool |
| `d_graf` | `"METRICS — operational, live and business"` | **keep** — Grafana is the dashboards/metrics tool |
| `d_prom` | `"Watches the system on its own"` | keep; optionally sharpen to **security-only** |

**Reticulum encryption.** Add end-to-end encryption wording to `h_mesh` /
`h_retic`. Use Reticulum's own language: *"All communication is secured with
strong, modern encryption by default. All encryption keys are ephemeral, and
communication offers forward secrecy by default. It is not possible to establish
unencrypted links."* Source: reticulum.network

**Additive fabrication.** MainsailOS is a single product; never write "Mainsail"
as a separate item. The correct set is **MainsailOS / Moonraker / Klipper** on
the BigTreeTech CB1/RPi, plus individual 3D printers and CNC machines. These are
**real machines, not simulation nodes** — do not draw them as children of
`w_fab`.

---

## 5. Adapter status — make "planned" legible

`topology-model.yaml` marks `ao-ingress-payment`, `ao-egress-archive` and
`ao-build-update` as **`status: planned`, "not yet deployed"**. The graphic
already shows `PLANNED` for all three, which is correct. Just make sure a reader
can tell at a glance that those three adapters are not live, while `ao-sales`,
`ao-payment` and the data path **are**.

---

## 6. Verification you must run before reporting done

```bash
cd "/ALWAYSON/TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC"

python3 build_svg.py                # 1. regenerates cleanly

grep -c 'a_comm\|ao-egress-community' alwayson-single-topology.json   # expect 0
grep -c 'ao-egress-community' alwayson-single-topology.svg             # expect 0
grep -c '"no"' build_svg.py                                           # expect 8

# 4. integrity: no dup ids, no dup titles, no dangling edge refs
python3 - <<'PY'
import json
d=json.load(open('alwayson-single-topology.json'))
ids=[n['id'] for n in d['nodes']]; titles=[n['title'] for n in d['nodes']]
assert len(ids)==len(set(ids)), "duplicate id"
assert len(titles)==len(set(titles)), "duplicate title"
bad=[(e['src'],e['dst']) for e in d['edges'] if e['src'] not in ids or e['dst'] not in ids]
assert not bad, f"dangling edges: {bad}"
print("nodes",len(ids),"edges",len(d['edges']),"OK")
PY

# 5. SVG parses
python3 -c "import xml.dom.minidom;xml.dom.minidom.parse('alwayson-single-topology.svg');print('svg ok')"

# 6. complete diagram is still LANDSCAPE
python3 -c "
import struct;d=open('alwayson-single-topology.png','rb').read(33)
w,h=struct.unpack('>II',d[16:24]);print(w,h,'LANDSCAPE' if w>h else 'PORTRAIT');assert w>h"
```

Then **look at the rendered PNG** and confirm: the adapter band no longer shows
`ao-egress-community`; nothing dangles; no label pill overflows its card; and no
title or banner was added.

---

## 7. When you are finished, tell me

Report back with:

1. the new node/edge counts from check 4;
2. confirmation that the landscape aspect and the eight PROHIBITED edges survive;
3. the absolute path to the regenerated PNG;
4. anything you could not do and why.

I will then update the README. **Do not edit the README yourself** — the README
and the graphic are separate artefacts with separate owners, and the README also
contains an ASCII topology that is currently **retained on purpose** as the
authoritative fallback. I remove it only after your graphic is verified correct;
your job is to make that safe, not to assume it.


