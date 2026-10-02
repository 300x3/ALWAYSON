#!/usr/bin/env python3
"""ALWAYS ON - one-page landscape topology.
Single source of truth for content; emits .svg .png .html .json
Layout computed here so band order, boundaries and wrapping are deterministic."""
import json, os, html, re, shutil

# Output goes to the folder this script lives in, so a move of the tree cannot
# strand it writing into a directory that no longer exists. Override with
# ALWAYSON_TOPO_OUT to publish somewhere else.
OUT = os.environ.get("ALWAYSON_TOPO_OUT",
                     os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)

CLS = {  # colour = CLASS of thing
 "ext":    ("#eceff1", "#455a64"),
 "adp":    ("#fff3e0", "#ef6c00"),
 "work":   ("#e3f2fd", "#1565c0"),
 "ledger": ("#ede7f6", "#5e35b1"),
 "data":   ("#e8f5e9", "#1b5e20"),
 "host":   ("#eceff1", "#546e7a"),
 "hw":     ("#d7ccc8", "#4e342e"),
 "rf":     ("#fff9c4", "#f9a825"),
 "sec":    ("#f3e5f5", "#6a1b9a"),
}
ST = {"IMPLEMENTED": "#1b5e20", "IN PROGRESS": "#ef6c00", "PARTIAL": "#ef6c00",
      "PLANNED": "#546e7a", "BLOCKED": "#b71c1c"}

def N(i, band, cls, title, purpose, details, status, sec, note=""):
    return dict(id=i, band=band, cls=cls, title=title, purpose=purpose,
                details=details, status=status, sec=sec, note=note)

BANDS = [
 dict(key="ext",  n="1", title="OUTSIDE WORLD",
      purpose="Nothing here reaches an internal service except through a door",
      sec="ES.2 Master Topology"),
 dict(key="adp",  n="2", title="CONTROLLER ADAPTERS",
      purpose="A controller adapter is the only process allowed to cross this host's "
              "boundary, and it holds its own credentials, so nothing inside a domain can "
              "reach out on its own. It also carries the HTML views published by local "
              "servers (Gazebo and Foxglove, MeshChatX, WebODM, Grafana, Metabase), so the "
              "operator gets one page while the origin stays on loopback.",
      sec="3.1 Isolation Detail · 5.2 Adapters"),
 dict(key="work", n="3", title="WORKLOAD DOMAINS",
      purpose="A workload domain is one group of services on its own Internal=true network, "
              "with no public listener of any kind. A service joins exactly one domain and "
              "holds only the credentials that domain needs. Nothing crosses between two "
              "domains except a signed, minimised manifest through the gate.",
      sec="5.1 Workload Domains · ES.2"),
 dict(key="data", n="4", title="STORES AND REPORTING",
      purpose="PostgreSQL holds the operational record; Redis and Prometheus are never the record",
      sec="3.3 Databases · 6.A GUI Tools"),
 dict(key="field",n="5", title="FIELD, RADIO, THIS HOST",
      purpose="The aircraft, the two radios and the mesh — off-host kit, and the local services that serve it",
      sec="9.1 Field/LoRa · 9.2 MeshChatX · 8.1 Mapping Intake"),
 dict(key="sales",n="6", title="SALES", group="prog",
      purpose="The local programs a sale runs through — inference, the agent, the browser, "
              "backups. No live machinery is ever touched.",
      sec="ES.1 · 6.A · 17.1"),
 dict(key="sim",  n="7", title="SIMULATION, REHEARSED", group="prog",
      purpose="Both rehearsal worlds, run on this host — the flight rehearsal and the "
              "factory and kitchen rehearsal. Split out from sales because it rehearses the field kit; it sells nothing.",
      sec="10.1 · 10.2"),
 dict(key="sec",  n="8", title="SECRETS ON THIS HOST", group="prog",
      purpose="The one wallet that holds every secret. Nothing else on this host stores one, "
              "and it is only available after Plasma login.",
      sec="14.1 · 14.1.1"),
 dict(key="flow", n="9", title="WHAT ACTUALLY HAPPENS",
      purpose="A customer buys, a drone flies, a factory and kitchen are rehearsed — and the 3D model chain ties them together",
      sec="7.3 Sales · 8.3 Mapping · 8.6.4 Cross-Ref · 10.2.c Storage · 11.2 Ledger"),
]

NODES = [
 # ---- band 1 : outside ----
 N("x_cust","ext","ext","Customer","Buys a product",["Browser on the public site"],"IMPLEMENTED","7.3"),
 N("x_email","ext","ext","EMAIL TEMPLATE","The order template a customer fills in and sends",
   ["KIT REQUEST / order-request template","IMAP pull of the domain mailbox",
    "Arrives as a PDF, standardised and hashed"],"IN PROGRESS","ES.2, 7.1.1, 15.1.2"),
 N("x_store","ext","ext","Storefront 300x3.com","Shows the products; sells nothing itself",
   ["Static catalogue, docs, legal","No local ports, no secrets",
    "Checkout hands off to a hosted provider,","or routes the buyer to the email template"],
   "IMPLEMENTED","ES.2, 7.1"),
 N("x_social","ext","ext","Other social media","Where the fediverse chatbot also posts",
   ["Chatbot from the remote fediverse","routes its replies in here",
    "No service runs on this host for it"],"PLANNED","ES.2, 15.4.3"),
 N("x_pkg","ext","ext","Software source","Where signed builds and images are fetched from",
   ["Package and container registries","Signature and digest checked"],"PLANNED","5.2"),
 N("x_pay","ext","ext","Payment provider","Captures money, then signs an event",
   ["PayPal / Zelle / Coinbase","Cards never touch this host"],"PLANNED","ES.2, 7.2, 18.4"),
 N("x_fedi","ext","ext","Remote fediverse","Other servers we talk to",
   ["Mastodon.social + peers","ActivityPub, WebFinger"],"IN PROGRESS","ES.2, 15.4.3"),
 N("x_pcloud","ext","ext","pCloud","Publishes the site; holds the sale-transfer copies",
   ["Public folder out; transfers in","The backup is restic, not IPFS",
    "Encrypted, allowlisted"],"PLANNED","ES.2, 11.6, 17.1"),
 N("x_buyer","ext","ext","Authorised recipient","Receives a sold map or telemetry package",
   ["Private swarm / pinning / encryption","Package - hash - authorisation",
    "Blockchain sales listing, where applicable","Receives it for transfer, not recovery"],
   "PLANNED","ES.2, 11.6, 4.4"),
 # ---- band 2 : adapters ----
 N("a_pay","adp","adp","ao-ingress-payment","The only way a payment can get in",
   ["Zelle · PayPal · Coinbase","Verifies provider signature","Rate-limits, normalises"],"PLANNED","3.1, 5.2, 18.4"),
 N("a_arch","adp","adp","ao-egress-archive","ARCHIVED FOR DATA TRANSFER AND SALE — not a backup",
   ["Held so a sold package can be transferred","NOT a backup: restic is the backup (17.1)",
    "No restore, no recovery, no retention duty","Sold maps, imagery, telemetry/IoT packages",
    "IPFS: transfer verification + sale listing","Then encrypted pCloud replication",
    "Requires ao-sales authorisation first","Destination allowlist · separate credentials"],
   "PLANNED","3.1, 5.2, 11.6, 17.1"),
 N("a_build","adp","adp","ao-build-update","Software updates only — all host software",
   ["Fetches images/packages","Verifies digest, promotes",
    "Updates host software of every domain","NOT imagery: WebODM and photo",
    "processing/verification are ao-mapping's","ao-mapping does all WebODM work"],
   "PLANNED","5.2, 8.1"),
 N("a_cf","adp","adp","Cloudflare edge","Where TLS is terminated",
   ["mastodon.300x3.com","Tunnel ingress only"],"IMPLEMENTED","15.4.3"),
 N("a_tun","adp","adp","cloudflared-alwayson","Carries federation traffic inward",
   ["Cloudflared connector","Origin stays loopback"],"IMPLEMENTED","15.4.3"),
 N("a_html","adp","adp","ao-html-window","Public-facing HTML viewing for 300x3.com",
   ["View-only surface — displays HTML, takes no input","Publishes HTML content to 300x3.com only",
    "Similar to the local hosted iframes","Network 10.89.14.0/24 created 2026-10-01"],"PLANNED","ES.2, 5.2"),
 # ---- band 3 : workload domains ----
 N("w_sales","work","work","ao-sales","The only domain that touches customers directly",
   ["10.89.0.0/24","Coordinates social media, email and Mastodon,","the AI bot and chat, and the order-request",
    "and receipt workflows","Web origin 127.0.0.1:3000",
    "Public PDF intake forms are the exposure point","PDF intake and PDF output"],
   "IN PROGRESS","5.1, 15.1.2, 7.1.1"),
 N("w_pay","work","work","ao-payment","Turns a provider event into verified money",
   ["10.89.1.0/24","Webhook verifier · reconciler"],"PLANNED","5.1, 7.3"),
 N("w_field","work","work","ao-field","Listens to the drone and signs what it hears",
   ["10.89.2.0/24","Heltec gateway · RNS/MeshChatX"],"IN PROGRESS","5.1, 9.1, 9.2"),
 N("w_map","work","work","ao-mapping","Turns drone photos into a measured map",
   ["10.89.3.0/24","WebODM · NodeODM · intake"],"IMPLEMENTED","5.1, 8.1, 8.3"),
 N("w_veh","work","work","ao-sim-vehicle","Rehearses flights without a real aircraft",
   ["10.89.4.0/24","ROS 2 + Gazebo · DOMAIN_ID=21"],"IMPLEMENTED","5.1, 10.1"),
 N("w_fab","work","work","ao-sim-fabrication","Coordinates industrial engineering and production details, and runs the kitchen",
   ["10.89.5.0/24 · ROS 2 + Gazebo · DOMAIN_ID=22",
    "Receives specific production data from each machine",
    "Robot arms have their own computers",
    "Simulation only: it never commands live machinery",
    "Real machines are separate — see ao-fabrication"],
   "IMPLEMENTED","5.1, 10.2", "Headless verified; GUI workflow pending (6.A.1)"),
 N("w_fabd","work","work","ao-fabrication","Pulls data from the real machines into its own database",
   ["10.89.12.0/24 · Internal=true",
    "MainsailOS / Moonraker / Klipper on the","BigTreeTech CB1 / RPi of each individual",
    "3D printer and CNC machine",
    "Own database for industrial engineering","and fabrication optimisation work"],
   "PLANNED","5.1, 10.2, 3.3",
   "Operator instruction 2026-09-30; not yet in README v7 §3.3 target databases"),
 N("w_ing","work","ledger","ao-ledger-ingest","The one door into the ledger",
   ["10.89.6.0/24","mTLS · authz · validate · sign ·","idempotency · timestamp/nonce · audit"],
   "BLOCKED","5.1, 11.2", "Blocked on the Corda key/certificate ceremony (18.3)"),
 N("w_core","work","ledger","ao-ledger-core","Holds the authoritative ledger",
   ["10.89.7.0/24","Corda 5.2.2 · PKI · cordadb","(own database, roles, backup)"],
   "BLOCKED","5.1, 11.1"),
 N("w_data","work","work","ao-data","Carries approved references, nothing else",
   ["10.89.8.0/24","Narrow plumbing only"],"PLANNED","5.1, 6.A.3"),
 N("w_admin","work","work","ao-admin","Watches and reports; never a way in",
   ["10.89.9.0/24","Prometheus · Grafana · Metabase"],"IMPLEMENTED","5.1, 6.A"),
 # ---- band 4 : stores ----
 N("d_pg","data","data","PostgreSQL 18 (host cluster)","The operational record for every domain",
   ["127.0.0.1:5432 — one cluster, many databases",
    "salesdb · mastodon · webodm · grafana · metabase",
    "cordadb — Corda's database within it (own roles, backup)",
    "a_fab for ao-fabrication"],"IMPLEMENTED","3.3"),
 N("d_redis","data","data","Redis 8","Fast coordination — never the record",
   ["Cache · queues · locks"],"IMPLEMENTED","3.3"),
 N("d_prom","data","data","Prometheus TSDB","Security only — acts alone and independently",
   ["Security metrics · rules · alerts","Acts alone and independently",
    "Metabase never uses it as a datasource"],"IMPLEMENTED","ES.1, 17.2"),
 N("d_meta","data","data","Metabase","REPORTING — business and ad hoc analysis",
   ["SQL over read-only views","Sales · orders · marketing","Also Metabase's own application database"],
   "IMPLEMENTED","6.A.2, 11.2.1"),
 N("d_graf","data","data","Grafana","DASHBOARDS AND METRICS",
   ["Operational, live and business dashboards","PostgreSQL + Prometheus sources",
    "Also Grafana's own application database"],"IMPLEMENTED","6.A.2, ES.1"),
 N("d_sql","data","data","SQLite","The database engine itself — one file per program, never the record",
   ["MeshChatX · QGroundControl · and the","other local tools that keep state"],
   "IMPLEMENTED","3.3"),
]

NODES += [
 # ---- band 5 : field, radio, host ----
 N("h_rpi","field","hw","Raspberry Pi 5","Drone \u2014 KaliOS on the Raspberry Pi 5 with the Autopilot Module \u2014 OFF-HOST",
   ["MAVLink collector \u00b7 encrypted","telemetry spool \u00b7 RNS \u00b7 MeshChatX"],"IMPLEMENTED","9.1"),
 N("h_fc","field","hw","ArduPilot 3DR N1","Actually flies the drone \u2014 OFF-HOST",
   ["Flight controller","Waveshare SX1262 LoRa + GNSS"],"IMPLEMENTED","9.1"),
 N("h_people","field","rf","PEOPLE-RADIO","LoRaWAN human chat \u2014 ties to MeshChatX",
   ["Heltec LoRa 32 V3 \u00b7 SX1262","915 MHz / 125 kHz / SF7 / 17 dBm",
    "LoRaWAN-related communication","Carries MeshChatX text over LoRa"],"IMPLEMENTED","9.2, 9.3"),
 N("h_drone","field","rf","DRONE-RADIO","Local QGC missions to the drone, in flight",
   ["Heltec LoRa 32 V3 \u00b7 SX1262","917 MHz / 250 kHz / SF7 \u00b7 hidden",
    "Ties to QGroundControl","Sends local QGC missions to the",
    "QGC session on the Pi5 drone","So missions update MIDFLIGHT"],"IMPLEMENTED","9.2, 9.3"),
 N("h_webodm","field","host","WebODM web","Mapping UI on this workstation",
   ["127.0.0.1:8000","Loopback only"],"IMPLEMENTED","9.2.1"),
 N("h_gw","field","host","Heltec gateway service","Turns radio bytes into signed records",
   ["Serial framing \u00b7 RSSI/SNR \u00b7","replay defence \u00b7 signs manifests"],"IN PROGRESS","9.2"),
 N("h_mesh","field","host","MeshChatX","Local chat service on the mesh, end-to-end encrypted by Reticulum",
   ["https://127.0.0.1:18000 · loopback only","Strong modern encryption by default,",
    "ephemeral keys, forward secrecy",
    "Unencrypted links cannot be established"],"IMPLEMENTED","9.2.1, 9.4"),
 N("h_retic","field","host","Reticulum","Carries mesh traffic, end-to-end encrypted; bound to all IPv4",
   ["Public Gateway 0.0.0.0:4242","NOT loopback-restricted (9.4)",
    "All traffic encrypted by default,","ephemeral keys, forward secrecy",
    "Unencrypted links cannot be established"],"IN PROGRESS","9.3, 9.4"),
 N("h_mach","field","hw","3D printers and CNC machines","Real machines, not simulation nodes",
   ["printer-01 VERIFIED LIVE at 10.42.0.96","MainsailOS / Moonraker / Klipper",
    "on a BigTreeTech CB1 / Raspberry Pi",
    "Equipment LAN 10.42.0.0/24; DHCP from","the desktop; NOT part of any domain",
    "Collected by the host hop, never","commanded: Moonraker is read-only"],
   "IMPLEMENTED","ES.1, 10.2, 10.3, 3.3.0.1"),
 N("h_qgc","field","host","QGroundControl","Plans and watches missions; updates midflight",
   ["Mission planning desktop","KaliOS RPi5 fallback",
    "DRONE-RADIO delivers missions","to the QGC session on the Pi5"],"PARTIAL","ES.1, 9.1"),
 N("h_lm","sales","host","LM Studio","Runs the local models",
   ["127.0.0.1:1234","Local inference only, no outbound"],"IMPLEMENTED","ES.1, 6.A"),
 N("h_oc","sales","host","OpenClaw","The local agent that acts on the sale",
   ["127.0.0.1:18789 / 18790","Uses LM Studio and KDE Wallet"],"IN PROGRESS","ES.1, 6.A.3"),
 N("h_kpdf","sales","host","KIT REQUEST PDF intake","Written requests in, not sales out",
   ["intake-kit-request-pdf.sh","inbox · extracted · manifests · quarantine",
    "sale_logged=false · corda_state=NOT_SUBMITTED",
    "CONFIRMED SALE PDF OUTPUT"],
   "PARTIAL","15.1.2",
   "Script and 7 folders present, but no timer or unit, and manifests/ and extracted/ are empty — never run"),
 N("h_konq","sales","host","Konqueror","Dedicated browser for automation",
   ["Sales UI \u00b7 community \u00b7 dashboards","Tokodon removed"],"IMPLEMENTED","ES.1"),
 N("h_collect","data","host","ao-fabrication-collect","Host-side pull-only collector",
   ["Runs on the HOST, not in the domain:","ao-fabrication is Internal=true and",
    "cannot reach 10.42.0.0/24",
    "GETs Moonraker every 5 min; never","commands a machine",
    "Pushes over the podman bridge","10.89.12.1 to a_fab on 127.0.0.1:15433",
    "payload_sha256 makes a re-poll idempotent"],
   "IMPLEMENTED","3.3.0.1, 10.3"),
 N("h_restic","data","host","restic backup","3-2-1 encrypted backup for the whole host",
   ["Config · manifests · postgres dumps ·","photogrammetry manifests",
    "Nightly 03:30 · weekly verify · monthly restore test"],"IMPLEMENTED","17.1, ES.1"),
 N("h_wallet","sec","sec","KDE Wallet","The only source of secrets",
   ["kwalletd6 after Plasma login","fetch-kwallet-secret.sh"],"IMPLEMENTED","14.1, 14.1.1"),
 # ---- band 7 : simulation, rehearsed ----
 N("h_gaz","sim","host","Gazebo + ROS 2","Installed, but not set up with worlds",
   ["ROS 2 Lyrical + gz present","DOMAIN_ID 21 and 22 reserved"],"IN PROGRESS","10.1, 10.2",
   "Installed only, nothing running (2026-09-29)"),
 N("h_fox","sim","host","Foxglove","Not set up — no bridge, no worlds",
   ["No foxglove_bridge on this host","Loopback ws://127.0.0.1:8765"],"IN PROGRESS","10.1, 10.2",
   "No foxglove or foxglove_bridge binary found 2026-09-29; only stale ~/.ros/log bridge logs"),
 # ---- band 6 : flows, ordered so each chain is vertical and local ----
 N("f_sale1","flow","work","1 \u00b7 Catalogue to checkout","Customer picks and pays",
   ["Product modal, then hosted checkout","or a mailto order template"],"IMPLEMENTED","7.1.1, 7.3"),
 N("f_sale2","flow","work","2 \u00b7 Verified payment event","Money becomes a checked fact",
   ["Provider-signed webhook","or manual reconciliation"],"PLANNED","7.3"),
 N("f_sale3","flow","work","3 \u00b7 salesdb record","The sale is written down",
   ["Order \u00b7 receipt \u00b7 fulfilment \u00b7","entitlement state"],"PLANNED","7.3, 15.1"),
 N("f_sale4","flow","ledger","4 \u00b7 Signed receipt manifest","Proof ready to leave",
   ["Minimised, hashed, signed","Three evidence classes required"],"BLOCKED","11.2, 11.2.2"),
 N("f_cord","flow","ledger","5 \u00b7 Corda state","The sale is now provable",
   ["Transaction \u00b7 entitlement \u00b7","provenance \u00b7 approval"],"BLOCKED","11.2, 11.2.3"),
 N("f_pdfin","flow","work","PDF intake","The public form a customer fills in",
   ["KIT REQUEST / order-request email, or the public PDF intake form",
    "Standardised PDF, hashed and reviewed",
    "sale_logged=false · corda_state=NOT_SUBMITTED"],"IN PROGRESS","7.1.1, 15.1.2, 4.4"),
 N("f_pdfout","flow","data","PDF output","Receipts and reports the customer receives",
   ["Signed receipt / contract PDF","Sales and accounting report PDF",
    "Transaction folder, operator archive, ledger gateway"],
   "PLANNED","4.4, 7.2"),
 N("f_cad","flow","work","CAD / 3D model","Designs are identified, not just files",
   ["model_object_id +","model_revision_id"],"PLANNED","8.6.1, 8.6.4"),
 N("f_reg","flow","data","Model registry","Resolves a model to what it is",
   ["serial_number to product","correlation_id + receipt to sale","content_hash to artifact"],
   "PLANNED","8.6.3, 8.6.4"),
 N("f_corr","flow","data","Correlation tuple","The key every record shares",
   ["serial_number +","receipt_number +","event_timestamp_utc"],"IMPLEMENTED","11.2.1"),
 N("f_stor","flow","data","500GBPHOTOGRAM drive","The dedicated photogrammetry store",
   ["/media/scottw/500GBPHOTOGRAM","incoming \u00b7 validated \u00b7 rejected \u00b7 webodm \u00b7","deliverables \u00b7 manifests \u00b7 exports \u00b7 retention"],
   "IMPLEMENTED","8.1, 8.2"),
 N("f_map1","flow","work","Mapping \u00b7 ingest","Bad images are rejected early",
   ["Type \u00b7 SHA-256 \u00b7 EXIF \u00b7 mission","association \u00b7 quota \u00b7 quarantine"],"IMPLEMENTED","8.3"),
 N("f_map2","flow","work","Mapping \u00b7 process","Photos become a measured model",
   ["WebODM task, then Redis queue","NodeODM: ortho, cloud, DSM,","texture, report"],"IMPLEMENTED","8.3"),
 N("f_map3","flow","work","Mapping \u00b7 export","Results become provable goods",
   ["Hashes outputs, signs manifest,","stages the archive bundle"],"PLANNED","8.3, 8.6.4"),
 N("f_storflow","flow","work","Storage to shelf to robot","The fabrication flow being rehearsed",
   ["Carousel/conveyor, then pickup","to 3D print \u00b7 LPBF \u00b7 assembly \u00b7","fridge/pantry \u00b7 kitchen"],"PLANNED","10.2.c"),
]

# A band is a column; a band may hold several STACKED sections. A section is a
# titled group of cards, so "Outside world" can carry its own social-media and
# box-store parts instead of pretending they are one thing. A section with no
# cards still draws its box, so a deliberate gap shows as a gap.
#   (band, section title, [node ids], kind)   kind: "nodes" | "empty"
SECTIONS = [
 ("ext",  "Outside world", ["x_cust", "x_pay", "x_email"], "nodes"),
 ("ext",  "Social media",  ["x_fedi", "x_social"], "nodes"),
 ("ext",  "Box stores",    ["x_store", "x_pcloud"], "nodes"),
 ("ext",  "After sale",    ["x_buyer"], "nodes"),
 ("ext",  "Software supply", ["x_pkg"], "nodes"),

 ("adp",  "Controller adapters", ["a_pay", "a_tun", "a_cf", "a_build", "a_arch", "a_html"], "nodes"),
 ("work", None, ["w_pay", "w_sales", "w_admin", "w_veh", "w_field", "w_map", "w_data",
                 "w_fab", "w_fabd", "w_core", "w_ing"], "nodes"),

 ("data", "Stores and reporting", ["d_redis", "d_sql", "d_pg", "d_graf", "d_prom", "d_meta"], "nodes"),

 ("field", "Real fabrication machines", ["h_mach"], "nodes"),
 ("field", None, ["h_drone", "h_gw", "h_qgc", "h_rpi", "h_fc", "h_people", "h_mesh", "h_retic", "h_webodm"], "nodes"),

 ("data", "Fabrication collector (host-side)", ["h_collect"], "nodes"),
 ("data", "Host-wide encrypted backup", ["h_restic"], "nodes"),
 ("sales", "Sales on this host", ["h_oc", "h_lm", "h_konq", "h_kpdf"], "nodes"),
 ("sim", None, ["h_gaz", "h_fox"], "nodes"),
 ("sec", None, ["h_wallet"], "nodes"),

 ("flow", None, ["f_pdfin", "f_sale1", "f_sale2", "f_sale3", "f_sale4",
                 "f_pdfout", "f_cord", "f_cad",
                 "f_reg", "f_corr", "f_stor", "f_map1", "f_map2", "f_map3",
                 "f_storflow"], "nodes"),
]

# (src, dst, label, kind)  kind: ok=approved normal=rf=radio no=prohibited
EDGES = [
 # outside -> adapters
 ("x_cust","x_store","visits","normal"),
 ("x_cust","x_email","fills in and sends","normal"),
 ("x_store","x_email","order template","ok"),
 ("x_store","x_pay","hosted checkout","ok"),
 # the fediverse chatbot reaches other social platforms
 ("x_fedi","x_social","chatbot replies","normal"),
 ("x_pay","a_pay","signed webhook","ok"),
 ("x_email","a_cf","HTTPS 443","ok"),
 ("x_fedi","a_cf","HTTPS 443","ok"),
 ("a_cf","a_tun","tunnel","ok"),
 # adapters -> domains
 ("a_tun","w_sales","tunnel to loopback origin","ok"),
 ("a_pay","w_pay","verified event","ok"),
 ("w_sales","x_fedi","ActivityPub out via sales egress bridge","ok"),
 # purchase-request / receipt / work-order confirmations leave as PDFs by email
 ("w_sales","x_email","purchase request, receipt and work-order status PDFs","ok"),
 ("w_sales","a_arch","authorises the transfer","ok"),
 ("a_arch","x_pcloud","encrypted transfer copy","ok"),
 ("a_arch","x_buyer","post-sale IPFS transfer","ok"),
 ("a_html","x_store","publishes HTML content to 300x3.com","ok"),
 ("x_pkg","a_build","signed images and packages","ok"),
 ("h_restic","x_pcloud","replicated","normal"),
 # domains -> stores / ledger  (the six approved manifest paths of 4.4)
 ("w_field","w_ing","telemetry manifest","ok"),
 ("w_map","w_ing","mapping deliverable","ok"),
 ("w_veh","w_ing","vehicle sim manifest","ok"),
 ("w_fab","w_ing","fabrication manifest","ok"),
 ("w_sales","w_ing","receipt manifest","ok"),
 ("w_pay","w_ing","verified payment","ok"),
 ("w_ing","w_core","approved state transition","ok"),
 # the other three 4.4 paths (not manifests into the ledger, but NOT bypasses:
 # v6 4.4 makes all nine approved paths subject to the same eight controls)
 ("w_ing","w_field","signed mission release","ok"),
 ("w_map","f_map1","validated image set","ok"),
 ("w_core","d_meta","status via narrow API","ok"),
 # reporting (3.3.2 + 11.2.1 collapsed into one path)
 ("d_pg","d_meta","read-only views","ok"),
 ("d_pg","d_graf","PostgreSQL datasource","ok"),
 ("d_prom","d_graf","metrics","ok"),
 ("w_admin","d_pg","read-only bridge","normal"),
 ("h_webodm","w_map","loopback UI","normal"),
 ("h_gaz","w_veh","flight rehearsal","normal"),
 ("h_gaz","w_fab","factory and kitchen rehearsal","normal"),
 ("h_mach","h_collect","Moonraker read over the equipment LAN","ok"),
 ("h_collect","w_fabd","per-machine production data over 10.89.12.1","ok"),
 ("w_fabd","d_pg","own database a_fab","ok"),
 ("h_wallet","w_sales","secrets after login","normal"),
 ("h_lm","w_sales","local inference","normal"),
 ("h_oc","w_sales","agent actions","normal"),
 ("h_fox","w_veh","flight world","normal"),
 ("h_fox","w_fab","factory and kitchen world","normal"),
 ("h_mesh","h_retic","embedded RNS","normal"),
 ("h_konq","w_sales","operator GUI","normal"),
 ("h_kpdf","w_sales","PDF requests in","normal"),
 ("h_qgc","h_drone","local mission for the drone","rf"),
 ("h_drone","h_rpi","mission update midflight, no IP","rf"),
 ("h_people","h_mesh","LoRaWAN chat text","rf"),
 # radio: no IP path at all
 ("h_people","h_drone","separate bands 915 / 917 MHz","rf"),
 ("h_rpi","h_fc","MAVLink UART/USB","normal"),
 ("h_people","h_gw","USB serial","normal"),
 ("h_drone","h_gw","USB serial","normal"),
 ("h_gw","w_field","signed telemetry","ok"),
 # workflow chains
 ("x_email","f_pdfin","written intake","ok"),
 ("x_store","f_pdfin","public intake form","ok"),
 ("f_pdfin","f_sale1","standardised PDF","ok"),
 ("f_sale4","f_pdfout","signed receipt PDF","ok"),
 ("f_sale1","f_sale2","","ok"),
 ("f_sale2","f_sale3","","ok"),
 ("f_sale3","f_sale4","signed manifest","ok"),
 ("f_sale4","f_cord","","ok"),
 ("f_cord","f_reg","projection","normal"),
 ("f_cad","f_reg","model ids","ok"),
 ("f_reg","f_cord","manifest reference","ok"),
 ("f_map1","f_map2","","ok"),
 ("f_map2","f_map3","","ok"),
 ("f_map2","f_stor","projects","normal"),
 ("f_stor","f_map1","incoming","normal"),
 ("f_map3","w_ing","manifest","ok"),
 ("f_storflow","w_fab","simulated","normal"),
 ("f_corr","d_meta","join key","normal"),
 # PROHIBITED (v6 4.3)
 ("w_sales","w_veh","Sales to simulation","no"),
 ("w_sales","w_map","Sales to raw imagery","no"),
 ("w_field","x_pay","Field to payment provider","no"),
 ("w_map","w_field","Mapping to radios","no"),
 ("w_veh","h_rpi","Simulation to live drones","no"),
 ("w_fab","w_core","Simulation to Corda core","no"),
 ("x_pay","d_pg","Internet to database","no"),
 ("x_cust","w_core","Internet to ledger","no"),
]

NM = {n["id"]: n for n in NODES}

S = []
A = S.append

# ============================== LAYOUT =====================================
NW = 470
PAD_X, PAD_Y, GAP_Y, BAND_GAP = 52, 10, 10, 250
STEP_X = 15                     # spacing between two lines in one gap (see GAPW)
MARGIN_L, LEG_MIN = 44, 1080
MARGIN_R = 44               # matches MARGIN_L; the row used to end at the trim
FS_TITLE, FS_PURP, FS_DET, FS_ST = 29, 26, 26, 25
FS_SEC = 28                      # a stacked section title
LH = 28
LH_TITLE = 31                    # a title line is set larger than LH
FS_BT, FS_BP, FS_BS = 30, 25, 24  # band caption: title, purpose, muted sub-line
BT_STEP, BP_STEP, BS_STEP = 32, 29, 27
TXT_L, TXT_R = 22, 16        # text inset inside a node card

def tw(s, size, bold=False):
    """Conservative DejaVu Sans advance width of one line of text."""
    return len(s) * size * (0.62 if bold else 0.565)

def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= n:
            cur += " " + w
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    return out

def card_h(nd):
    """The height a card actually needs.

    The title and the purpose both WRAP, so counting each as a single line
    under-allocates the card and the status text runs out past the bottom
    border. Every line the renderer really draws has to be counted here:
    title lines advance by 25, purpose and detail lines by LH, plus the
    3px gap before the details, the 4px gap before the status, and the
    bottom padding. Deriving this once keeps the three height sites below
    (initial guess, per-band settle, group re-fill) from disagreeing.
    """
    return (PAD_Y + 18                          # top padding to first baseline
            + len(nd["_title"]) * LH_TITLE
            + len(nd["_purp"]) * LH
            + 3                                 # gap before the details
            + len(nd["_det"]) * LH
            + 4                                 # gap before the status
            + LH                                # the status line itself
            + 13 + PAD_Y)                       # descender room + bottom padding


for nd in NODES:
    nd["_title"] = wrap(nd["title"], 26)
    nd["_purp"] = wrap(nd["purpose"], 34)
    nd["_det"] = list(nd["details"])
    nd["_h"] = card_h(nd)
    # hug the content: the card is only as wide as its widest line
    nd["_w"] = TXT_L + TXT_R + max(
        [tw(l, FS_TITLE, True) for l in nd["_title"]] +
        [tw(l, FS_PURP)      for l in nd["_purp"]] +
        [tw(l, FS_DET)       for l in nd["_det"]] +
        [tw(nd["status"], FS_ST, True)])

# Bands that carry the same `group` are STACKED in one column: each keeps its
# own border, caption and number, but sits above the next instead of beside it.
# Everything downstream that used to be per-band (x, width, routing channel) is
# really per-COLUMN, so it is derived from the group, not from the band.
GRP_ORDER, GRP_MEMBERS, GROUP_OF = [], {}, {}
for b in BANDS:
    g = b.get("group", b["key"])
    if g not in GRP_MEMBERS:
        GRP_MEMBERS[g] = []
        GRP_ORDER.append(g)
    GRP_MEMBERS[g].append(b["key"])
    GROUP_OF[b["key"]] = g

# ---- routing reservations (must be known before any x is fixed) ----
_BC = {n["id"]: GRP_ORDER.index(GROUP_OF[n["band"]]) for n in NODES}
_NB = {n["id"]: n["band"] for n in NODES}

# A link that skips a band cannot be drawn with a single vertical channel: one
# of its two horizontal legs would have to run straight down an intermediate
# node column.  Those links get a private lane in the strip above the band row.
LONG = sorted(((e[0], e[1]) for e in EDGES
               if abs(_BC[e[0]] - _BC[e[1]]) > 1),
              key=lambda ab: (min(_BC[ab[0]], _BC[ab[1]]), _BC[ab[0]], ab[0], ab[1]))

# Links into the LAST column ("9 - what actually happens") are the ones the
# eye finishes on, so they are carried along the BOTTOM of the page instead of
# the top: the long run across the page then sits under the stacks it serves
# rather than crowding the header, and the final approach into the last box
# rises from below instead of dropping from above.
LASTC = len(GRP_ORDER) - 1
BOTTOM = {ab for ab in LONG if LASTC in (_BC[ab[0]], _BC[ab[1]])}
LONG = [ab for ab in LONG if ab not in BOTTOM]
LONG_ALL = list(LONG) + list(BOTTOM)   # every skip link still needs a channel x

# ---- page header: four framing lines, then three that say how to read it ----
HDR = [
 ("ALWAYS ON \u2014 ONE-PAGE TOPOLOGY", 44, "#111827", "bold"),
 ("What every part of the system is for \u2014 the outside world, the only doors, "
  "the isolated domains, the single ledger gate, the stores", 23, "#37474f", "normal"),
 ("Nodes are the EXPECTED-TO-BE-INSTALLED system. A PLANNED or BLOCKED node is "
  "design, not live state. Authority: README v7 \u00a73.2 / \u00a73.3 / \u00a75.1 / \u00a75.2.",
  22, "#6b7280", "normal"),
]

HDR_Y, _hy = [], 74
for _i, _h in enumerate(HDR):
    HDR_Y.append(_hy)
    _hy += _h[1] + 18
HDR_RULE = _hy + 2

# A lane carries its label ON the horizontal run, and a label pill is PILL_H
# tall. At a pitch of 18 the pills of two neighbouring lanes overlapped and the
# de-collision pass could not rescue them, because every spot along the run was
# taken by the lane above. The pitch now clears a pill, which is what lets the
# labels sit on their own lines where they belong.
LN_TOP, LN_STEP = HDR_RULE + 56, 31
# Two skip-links can share a lane when the gaps they cross do not overlap, so
# their horizontal runs can never meet.  Giving each link a private lane instead
# stacked 15 rows across the page to carry work that needs far fewer.
LANE, _lanes = {}, []
for _ab in LONG:
    _ca, _cb = _BC[_ab[0]], _BC[_ab[1]]
    _lo, _hi = min(_ca, _cb), max(_ca, _cb) - 1
    for _i, _L in enumerate(_lanes):
        if _L[-1][1] < _lo:          # this lane's last run ends before ours starts
            _L.append((_lo, _hi))
            break
    else:
        _i = len(_lanes)
        _lanes.append([(_lo, _hi)])
    LANE[_ab] = LN_TOP + _i*LN_STEP
LN_BOT = LN_TOP + max(0, len(_lanes)-1)*LN_STEP + 10

# A same-band link runs down the gap beside its band, not inside it, so the
# band needs no internal gutter at all.  Only the first band has no gap on its
# left, so it alone keeps a narrow one.
SB_OFF = 18                       # same-band vertical, nudged off the channel
GUT = {}
for _i, b in enumerate(BANDS):
    if _i == 0:
        _m = max([len(_l) for (_s, _d, _l, _k) in EDGES
                  if _l and _BC[_s] == _BC[_d] == 0] or [0])
        GUT[b["key"]] = max(_m, sum(1 for (_s, _d, _l, _k) in EDGES
                  if _BC[_s] == _BC[_d] == 0))*STEP_X + 34
    else:
        GUT[b["key"]] = 0

# Top of the band row. LN_BOT is only the last LANE line, but the de-collision
# pass can push a label pill BELOW its lane when the strip above the bands is
# crowded, and a pill is PILL_H (24) tall and centred on the lane. So LN_BOT
# understates how far the drawing really reaches. At LN_BOT+18 the band tops
# landed at y=706 and cut through the "factory and kitchen world" pill at
# y=710..734, which sits over band 4. Two lines of clearance (2*LN_STEP) puts
# the row at y=768, clear of the lowest pill by 34px. This is a constant for
# the whole row: all nine band rects keep ONE top edge, so they stay in line.
MARGIN_T = LN_BOT + 18 + 2*LN_STEP

# Cards in a band are set to ONE width, the widest any of them needs, so the
# column reads as a single stack instead of a ragged right edge.  Uniform width
# would otherwise leave short lines floating in a wide card, so the text is
# re-wrapped to FILL that width: the same width yields fewer lines, so the band
# also gets shorter.  Repeat until the width stops growing (it converges in one
# or two passes because wrapping wider never needs more width).
def _measure(nd, tw_, tmax, dmax, xmax=999):
    nd["_title"] = wrap(nd["title"], tmax)
    nd["_purp"] = wrap(nd["purpose"], dmax)
    # Each detail is a separate attribute and stays on its own line(s): wrap
    # each independently. Joining them first made the width measure read one
    # long line and blew the column out to 7893px.
    nd["_det"] = [sl for d in nd["details"] for sl in wrap(d, xmax)]
    return TXT_L + TXT_R + max(
        [tw_(l, FS_TITLE, True) for l in nd["_title"]] +
        [tw_(l, FS_PURP)      for l in nd["_purp"]] +
        [tw_(l, FS_DET)       for l in nd["_det"]] +
        [tw_(nd["status"], FS_ST, True)])

for b in BANDS:
    _ns = [n for n in NODES if n["band"] == b["key"]]
    if not _ns:
        continue
    _tmax, _dmax = 26, 34
    for _pass in range(6):
        _wmax = max(_measure(n, tw, _tmax, _dmax) for n in _ns)
        # widest text line the card can hold at this width, in characters
        _tcap = max(6, int((_wmax - TXT_L - TXT_R) / (FS_TITLE * 0.62)))
        _dcap = max(8, int((_wmax - TXT_L - TXT_R) / (FS_DET * 0.565)))
        _nt, _nd = min(_tmax, _tcap), min(_dmax, _dcap)
        if (_nt, _nd) == (_tmax, _dmax):
            break
        _tmax, _dmax = _nt, _nd
    _wmax = max(_measure(n, tw, _tmax, _dmax) for n in _ns)
    for n in _ns:
        n["_w"] = _wmax
        n["_h"] = card_h(n)

# A band is only as wide as its own widest card, but it must also fit the
# widest SECTION title it carries, or the header would spill past the border.
# Stacked bands SHARE a column, so the width is the widest of the whole group:
# a narrow box in the stack would otherwise be narrower than the one above it.
colw = {}
for g in GRP_ORDER:
    cards, heads = [], []
    gut = 0
    for bk in GRP_MEMBERS[g]:
        cards += [n["_w"] for n in NODES if n["band"] == bk]
        heads += [tw(st, FS_SEC, True) + 34
                  for sbk, st, _l, _k in SECTIONS if sbk == bk and st]
        gut = max(gut, GUT[bk])
    colw[g] = max(cards + heads) + PAD_X*2 + gut
# The operator asked for the fonts to grow WITHOUT the layout changing: the
# same columns, at the same x, at the same width, with the extra room taken
# from whitespace. Without this pin a larger font widens every text run,
# hence every card, hence every column, and the whole page simply scales up
# (measured: +95 to +145px per column, every band sliding right).
# With the widths pinned here the text instead re-wraps INSIDE the card it
# already had, and the growth is absorbed vertically - taller cards, softer
# gaps - instead of horizontally. Values are the 2026-10-02 pre-bump build,
# verified against the longest single word (no word can overflow a card) and
# the widest section title at the new 26pt.
FROZEN_COLW = {"ext": 921, "adp": 696, "work": 718, "data": 775,
               "field": 583, "prog": 650, "flow": 865}
for _g in GRP_ORDER:
    if _g in FROZEN_COLW:
        colw[_g] = FROZEN_COLW[_g]
# Now the group's inner width is known: re-fill every card in the group to
# exactly that width and re-wrap its text. A narrower band therefore gains the
# extra width instead of ending flush against the border.
for g in GRP_ORDER:
    gut = max(GUT[bk] for bk in GRP_MEMBERS[g])
    _tgt = colw[g] - PAD_X*2 - gut
    _ns = [n for bk in GRP_MEMBERS[g] for n in NODES if n["band"] == bk]
    if not _ns:
        continue
    _tmax, _dmax, _xmax = 999, 999, 999
    for _pass in range(8):
        _wmax = max(_measure(n, tw, _tmax, _dmax, _xmax) for n in _ns)
        # Derive the caps from the TARGET width, not from the previous width.
        # Deriving from _tmax/_dmax (the caps themselves) made this a no-op, so
        # the text kept its natural wrap while the card widened around it.
        _inner = _tgt - TXT_L - TXT_R
        _nt = max(6, int(_inner / (FS_TITLE * 0.62)))
        _nd = max(8, int(_inner / (FS_DET * 0.565)))
        _nx = _nd
        _nt, _nd, _nx = min(_tmax, _nt), min(_dmax, _nd), min(_xmax, _nx)
        if (_nt, _nd, _nx) == (_tmax, _dmax, _xmax):
            break
        _tmax, _dmax, _xmax = _nt, _nd, _nx
    _final = max(_measure(n, tw, _tmax, _dmax, _xmax) for n in _ns)
    # Wrap to a slightly NARROWER target than the card so the text always
    # keeps a visible right-hand gap instead of running flush to the border.
    if _final > _tgt - 14:
        _scale = (_tgt - 14 - TXT_L - TXT_R) / max(1.0, _final - TXT_L - TXT_R)
        _scale = (colw[g] - PAD_X*2 - gut - TXT_L - TXT_R) / max(1.0, _final - TXT_L - TXT_R)
        _tmax = max(6, int(_tmax * _scale * 0.98))
        _dmax = max(8, int(_dmax * _scale * 0.98))
        _xmax = max(12, int(_xmax * _scale * 0.98))
        _final = max(_measure(n, tw, _tmax, _dmax, _xmax) for n in _ns)
    for n in _ns:
        n["_w"] = _tgt
        n["_h"] = card_h(n)

# every band in a group reports the GROUP width, so captions and section rules
# are measured against the box they are actually drawn in.
for b in BANDS:
    colw[b["key"]] = colw[GROUP_OF[b["key"]]]

# ---- each gap is sized to the linework it actually carries ----------------
# One BAND_GAP for every gap was the main reason the picture read as a tangle.
# Gap 2 alone carries 23 crossing links plus 12 same-column runs, but every gap
# got the same 250px, so its usable span held only ~13 slots: the rest were
# clamped onto each other and drew as one thick line. Each gap is now given
# room for its own traffic, so lines stay 15px apart everywhere and the eye can
# follow each one. Widths come from the counts, so adding a link widens the gap
# it needs rather than silently overlapping its neighbours.
GAP_PAD = 74                    # clear space either side of the file of lines
_gapload = [0]*(len(GRP_ORDER)+1)
for (_a, _b, _l, _k) in EDGES:
    _ca, _cb = _BC[_a], _BC[_b]
    if _ca == _cb:
        if _ca > 0:
            _gapload[_ca] += 1
    else:
        for _g in range(min(_ca, _cb), max(_ca, _cb)):
            _gapload[_g] += 1
# A gap holds two files of lines (one per direction) plus the centre channel.
GAPW = [max(BAND_GAP, 2*(STEP_X*(n//2 + 1)) + GAP_PAD) if n else BAND_GAP
        for n in _gapload]

xs, x = {}, MARGIN_L
for i, g in enumerate(GRP_ORDER):
    xg = x
    for bk in GRP_MEMBERS[g]:
        xs[bk] = xg
    x = xg + colw[g] + GAPW[i]

body_top = MARGIN_T
BAND_HEAD = 150        # minimum caption block; real height is measured per box

def head_h(bk, bw):
    """Caption block a box actually needs: number+title, purpose, then the
    muted sub-line, all measured from how the text really wraps. A fixed
    BAND_HEAD overran the cards in the narrow columns (the purpose alone
    takes 9 lines in box 2)."""
    b = next(x for x in BANDS if x["key"] == bk)
    tl = len(wrap(f'{b["n"]} · {b["title"]}', max(12, int((bw-46)/(FS_BT*0.62)))))
    pl = len(wrap(b["purpose"], max(12, int((bw-46)/(FS_BP*0.565)))))
    sl = len(wrap(b["sec"], max(12, int((bw-46)/(FS_BS*0.565)))))
    # The gap under the purpose has to be a FULL LINE at the purpose's own
    # size. It was a fixed 12px, which cleared 19pt text and then let the muted
    # sub-line sit on top of the last purpose line once the font grew.
    return max(BAND_HEAD,
               44 + (tl-1)*BT_STEP + 16,
               76 + pl*BP_STEP + 10 + (sl-1)*BS_STEP)

HEAD = {b["key"]: head_h(b["key"], colw[b["key"]]) for b in BANDS}
# One top edge for the whole row, so the nine boxes still read as one line.
# It must be MARGIN_T alone. This used to be MARGIN_T + max(HEAD.values()),
# which added the DEEPEST caption (band 2, ~347px, because its purpose wraps to
# nine lines in a 696px column) above ALL nine band rects and drew nothing in it
# -- a ~347px void between the lane linework and the top of the bands. Every
# caption and card is placed relative to _by, and _by already carried the
# offset, so the slack did NOT go below a short caption's sub-line as the old
# comment claimed; it went above the box. Each band reserves only what its own
# caption needs via b["_sy"] = b["_by"] + HEAD[bk].
ROW_TOP = MARGIN_T
SEC_HEAD = 40          # a section title above its cards
SEC_GAP = 18           # space between two stacked sections
EMPTY_H = 96           # a section that holds nothing still shows its box
BOX_GAP = 18           # space between two boxes stacked in one column

def sec_h(ids, kind):
    if kind == "empty":
        return EMPTY_H
    if not ids:
        return 0
    return sum(NM[i]["_h"] for i in ids) + GAP_Y*(len(ids)-1)

def band_h(bk):
    """Height of one band = its sections stacked, each under its own title."""
    ss = [s for s in SECTIONS if s[0] == bk]
    h = 0
    for k, (sk, st, ids, kind) in enumerate(ss):
        h += (SEC_GAP if k else 0)
        if st:
            h += SEC_HEAD
        h += sec_h(ids, kind)
    return h

# Each box gets its OWN top and height. Stacked boxes therefore have different
# heights, and a single-box column is stretched to the full row height so the
# row still reads as one line of boxes.
for g in GRP_ORDER:
    _y = ROW_TOP
    for bk in GRP_MEMBERS[g]:
        b = next(x for x in BANDS if x["key"] == bk)
        b["_by"] = _y
        b["_bh"] = HEAD[bk] + band_h(bk) + 34
        _y += b["_bh"] + BOX_GAP

def grp_h(g):
    ms = GRP_MEMBERS[g]
    return sum(next(x for x in BANDS if x["key"] == bk)["_bh"] for bk in ms) \
        + BOX_GAP*(len(ms)-1)

maxh = max(grp_h(g) for g in GRP_ORDER)
# a column holding one box only is as tall as the tallest column
for g in GRP_ORDER:
    if len(GRP_MEMBERS[g]) == 1:
        next(x for x in BANDS if x["key"] == GRP_MEMBERS[g][0])["_bh"] = maxh

for b in BANDS:
    bk = b["key"]
    b["_secs"] = [s for s in SECTIONS if s[0] == bk]
    # Cards start directly under the caption in EVERY box. Bottom-justifying
    # the single-section boxes (2, 3, 5) pushed their first card ~1200px down and
    # read as a mistake, so the slack is left BELOW the stack instead: all the
    # section titles still share one baseline across the row.
    y = b["_by"] + HEAD[bk]
    b["_sy"] = y
    for sk, st, ids, kind in b["_secs"]:
        if st:
            b.setdefault("_head", []).append((st, y))
            y += SEC_HEAD
        if kind == "empty":
            b.setdefault("_empty", []).append((y, EMPTY_H))
            y += EMPTY_H
            continue
        for j, nid in enumerate(ids):
            n = NM[nid]
            n["_x"], n["_y"], n["_w"] = xs[bk] + PAD_X + GUT[bk], y, n["_w"]
            n["_cx"], n["_cy"] = n["_x"] + n["_w"]/2, n["_y"] + n["_h"]/2
            y += n["_h"] + (GAP_Y if j < len(ids)-1 else 0)
    b["_sh"] = y - b["_sy"]

BH = maxh
BODY_BOT = max(b["_by"] + b["_bh"] for b in BANDS)
DET = [
 ("h_storefront", "Storefront", "ext", "x_store", None),
 ("checkout", "Provider-hosted\ncheckout", "adp", "x_pay", None),
 ("ingress", "CONTROLLED INGRESS\nPayment / Community /\nSale transfer / Build-update", "adp", "a_pay",
   "adapters are the only doors"),
 ("domains", "WORKLOAD DOMAINS\nSales · Payment · Field ·\nMapping · Simulation", "work", "w_sales", None),
 ("manifest", "SIGNED MINIMISED\nMANIFEST\nSHA-256 · signature", "ledger", "f_sale4", None),
 ("ingest", "LEDGER-INGEST GATE\nmTLS · authorise · validate\nverify signature · idempotent\naudit", "ledger", "w_ing", None),
 ("corda", "Corda LEDGER-CORE\nreceipt · entitlement\nprovenance", "ledger", "w_core", None),
]
# Bottom area: the route detail on the left, the legend beside it.  Both are
# anchored to the band row, so the last row can never fall off the canvas.
# Bottom lanes for the links into the last column, and the footer clears them.
BOT_STEP = 27
BOT_N = len(BOTTOM)
# One lane per link. They used to be packed 12px apart and several links shared
# a lane, so their labels landed on each other; a lane is now a private lane at
# a pitch that clears a label pill.
BOT_LANE = {}
for _i, _ab in enumerate(sorted(BOTTOM, key=lambda ab: (_BC[ab[0]], ab))):
    BOT_LANE[_ab] = BODY_BOT + 26 + _i*BOT_STEP
BOT_STRIP = (26 + max(0, BOT_N-1)*BOT_STEP + 12) if BOT_N else 0
FOOT_TOP = BODY_BOT + 32 + BOT_STRIP
DX, DH, DG = MARGIN_L, 150, 50
DW = max(max(tw(_l, 17, True) for _l in _d[1].split("\n")) for _d in DET) + 44
DY = FOOT_TOP + 30
LEG_X = DX + 7*DW + 6*DG + 70
_lastg = GRP_ORDER[-1]
# A box border is drawn at xs-PAD_X, so the row really starts PAD_X LEFT of
# the first content origin; measure from there or box 9 overhangs the page.
_rowL = MARGIN_L

def tspan(x, y, s, size, fill, weight="normal", anchor="start", op=1.0, dbase=None):
    db = f' dominant-baseline="{dbase}"' if dbase else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans, Verdana, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{db} opacity="{op}">{esc(s)}</text>')
def esc(s):
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

# ---- legend, drawn into whatever sink it is given so its height can be
# ---- measured before the canvas is declared ----
def build_legend(sink, lx, ly):
    """Four short columns keep the panel low, so the bottom area stays shallow."""
    o = sink.append if hasattr(sink, "append") else sink
    o(tspan(lx+24, ly+46, "HOW TO READ THIS PAGE", 24, "#111827", "bold"))
    o(tspan(lx+24, ly+76, "A numbered BAND is one box.  Inside it, a small titled "
       "SECTION groups the cards that belong to it.  A card is one component.",
       16, "#4b5563", "italic"))
    o(tspan(lx+24, ly+100, "Colour = what KIND of thing it is.  The status word "
       "= whether it exists yet.",
       16, "#4b5563", "italic"))
    # The five columns do not carry equal content: COLOUR and its sub-kinds are
    # short labels, while LINES/READING ORDER and RULES hold running prose that
    # wraps. Splitting the width evenly therefore made the prose column wrap far
    # more than it needed to, and its extra lines made the whole legend the
    # tallest thing on the page. Weight the columns toward the prose instead.
    # The columns carry very unequal content. COLOUR and its sub-kinds are short
    # labels; LINES is four fixed two-line entries; the rest is running prose that
    # wraps. Splitting the width evenly made the prose column wrap far more than
    # it needed to, and stacking the fixed line key on top of the prose made that
    # column the tallest thing on the page, so the legend - not the band row -
    # set the canvas height and pulled the aspect ratio below its floor.
    # Weight the columns by content, and give LINES a column of its own.
    _W = [0.78, 0.78, 0.95, 0.80, 1.50, 1.45]   # COLOUR, sub-kinds, STATUS,
                                                  # LINES, prose, RULES
    _tot = sum(_W)
    _cols, _acc = [], 0
    for _w in _W:
        _cols.append(int((LEG_W - 48) * _acc / _tot)); _acc += _w
    x0, xb, x1, xL, x2, x3 = (lx + 24 + c for c in _cols)
    cw = max((_cols[i+1] - _cols[i]) for i in range(len(_W) - 1))
    y0 = ya = yb = y1 = yL = y2 = y3 = ly + 132
    o(tspan(x0, y0, "COLOUR", 17, "#111827", "bold")); y0 += 30

    def group(y, cls, label, kids, gx=None):
        """A parent colour drawn as a full-width box, with its own sub-kinds
        as boxes directly beneath it. Two categories are not really one thing,
        so the legend says so instead of hiding the split in a flat list."""
        f_, b_ = CLS[cls]
        gx = x0 if gx is None else gx
        gw = max(col0w, max(tw(kl, 15) for kl, _, _ in kids) + 26)
        gw = min(cw, gw)
        o(f'<rect x="{gx:.0f}" y="{y-19:.0f}" width="{gw:.0f}" height="26" rx="5" '
          f'fill="{f_}" stroke="{b_}" stroke-width="2"/>')
        o(tspan(gx+11, y, label, 17, "#111827", "bold"))
        y += 16
        n = len(kids)
        kw = (gw - 14 - (n-1)*8) / n
        nch = max(6, int((kw-14)/(15*0.565)))
        nlines = 1
        # wrap first so every sibling box gets the SAME height, not its own
        wrapped = [wrap(kl, nch) for kl, _, _ in kids]
        nlines = max(len(w) for w in wrapped)
        for i, ((kl, kf, kb), lns) in enumerate(zip(kids, wrapped)):
            kx = (x0 if gx is None else gx) + i*(kw+8)
            bh = 12 + nlines*16
            o(f'<rect x="{kx:.0f}" y="{y:.0f}" width="{kw:.0f}" height="{bh:.0f}" rx="5" '
              f'fill="{kf}" stroke="{kb}" stroke-width="1.6" stroke-dasharray="4 3"/>')
            for j, ln in enumerate(lns):
                o(tspan(kx+7, y+16+j*16, ln, 15, "#37474f", "italic"))
        # reserve the FULL sub-box height, not a guess, or the next row lands on top
        return y + 12 + nlines*16 + 18

    # The COLOUR column draws boxes, so a box far wider than its text reads as
    # empty. Hug the widest label instead of stretching to the full column.
    col0w = min(cw, max(tw(l, 17) for l in
                    ["Controlled adapter", "Workload domain", "Ledger authority",
                     "Host-local service", "Physical hardware", "Radio / RF",
                     "Secret authority", "Outside world",
                     "Data store / reporting"]) + 26)

    def swatch(y, k, lab, sx):
        f_, b_ = CLS[k]
        o(f'<rect x="{sx:.0f}" y="{y-11}" width="17" height="14" rx="3" '
          f'fill="{f_}" stroke="{b_}" stroke-width="2"/>')
        o(tspan(sx+30, y, lab, 17, "#1f2937"))

    # COLOUR is by far the tallest list, so it is split across two columns: the
    # first four entries here, the rest in `xb`. Each keeps its own y cursor and
    # the panel is only as tall as the tallest of the five.
    for k, lab in [("adp","Controlled adapter"),
                   ("work","Workload domain"),
                   ("ledger","Ledger authority")]:
        swatch(ya, k, lab, x0); ya += 27

    _e = CLS["ext"]; _d = CLS["data"]
    ya = group(ya, "ext", "Outside world", [
        ("Box stores", "#eceff1", _e[1]),
        ("Social media", "#eceff1", _e[1])])
    for k, lab in [("host","Host-local service"),
                   ("hw","Physical hardware"),
                   ("rf","Radio / RF"),
                   ("sec","Secret authority")]:
        swatch(yb, k, lab, xb); yb += 27

    yb = group(yb, "data", "Data store / reporting", [
        ("SQL databases, mostly local", "#e8f5e9", _d[1])], gx=xb)
    yb += 14
    o(tspan(x1, y1, "STATUS", 17, "#111827", "bold")); y1 += 26
    nch = max(10, int((cw-16)/(15*0.565)))   # fit the real column, not a fixed 20
    for k, lab in [("IMPLEMENTED","Built and running as designed"),
                   ("IN PROGRESS","Partly built, tests open"),
                   ("PARTIAL","Works, not yet proven end to end"),
                   ("PLANNED","Designed, not yet deployed"),
                   ("BLOCKED","Waiting on an operator action")]:
        o(tspan(x1, y1, k, 16, ST[k], "bold"))
        for _j, _l in enumerate(wrap(lab, nch)):
            o(tspan(x1, y1+17+_j*17, _l, 15, "#1f2937"))
        y1 += 22 + len(wrap(lab, nch))*17
    o(tspan(xL, yL, "LINES", 17, "#111827", "bold")); yL += 26
    for c, w, da, mk, l1, l2 in [
            ("#2e7d32", 3.5, None,  "ar_ok", "Approved path", "mTLS, signed, audited"),
            ("#607d8b", 2.0, "6 4",  "ar_n",  "Ordinary internal", "grey dashed, unsigned"),
            ("#f9a825", 4.5, "11 5", "ar_rf", "Radio link", "no IP, no firewall"),
            ("#c62828", 2.2, "3 5",  "ar_no", "PROHIBITED", "README v7 \u00a74.3 forbids it")]:
        da_ = f' stroke-dasharray="{da}"' if da else ""
        op = ' opacity="0.6"' if mk == "ar_no" else ""
        o(f'<line x1="{xL}" y1="{yL-4}" x2="{xL+30}" y2="{yL-4}" stroke="{c}" '
          f'stroke-width="{w}"{da_} marker-end="url(#{mk})"{op}/>')
        o(tspan(xL+44, yL, l1, 16, "#c62828" if mk == "ar_no" else "#1f2937",
                "bold" if mk == "ar_no" else "normal"))
        o(tspan(xL+44, yL+17, l2, 15, "#6b7280")); yL += 42
    # The reading instructions used to sit under the page title, where they read
    # as a second legend competing with this one. They belong here, with the
    # rest of the key.
    nch2 = max(10, int((cw-16)/(15*0.565)))
    y2 += 10
    o(tspan(x2, y2, "READING ORDER", 17, "#111827", "bold")); y2 += 24
    for _l in wrap("Read left to right: outside, doors, isolated domains, the "
                   "stores, field, sales, then the rehearsed worlds and the "
                   "wallet kept apart, and what actually happens.", nch2):
        o(tspan(x2, y2, _l, 15, "#1f2937")); y2 += 18
    y2 += 10
    o(tspan(x2, y2, "CARDS AND LANES", 17, "#111827", "bold")); y2 += 24
    for _l in wrap("A card: the bold name is the thing, the italic line is what "
                   "it is for, the plain lines are how it is bounded, and the "
                   "coloured word is its build state.", nch2):
        o(tspan(x2, y2, _l, 15, "#1f2937")); y2 += 18
    y2 += 6
    for _l in wrap("A lane carries a link that skips a band: it leaves the card, "
                   "runs clear of the boxes, then enters the card it belongs "
                   "to. Lanes under the header serve the middle of the page; "
                   "lanes along the bottom serve the final box.", nch2):
        o(tspan(x2, y2, _l, 15, "#1f2937")); y2 += 18
    o(tspan(x3, y3, "FIVE RULES THAT HOLD IT TOGETHER", 17, "#111827", "bold")); y3 += 26
    nch3 = max(10, int((cw-40)/(16*0.565)))  # fit the real column, not a fixed 22
    for i, r in enumerate(RULES, 1):
        o(tspan(x3, y3, f"{i}.", 16, "#1565c0", "bold"))
        for _j, _l in enumerate(wrap(r, nch3)):
            o(tspan(x3+24, y3, _l, 16, "#1f2937")); y3 += 20
        y3 += 4
    return max(ya, yb, y1, yL, y2, y3)

RULES = ["Every workload network is Internal=true.",
         "Nothing crosses a domain boundary except a signed, minimised manifest.",
         "Payment cards never touch this host.",
         "PostgreSQL holds the record; Corda holds the proof.",
         "Secrets come from KDE Wallet, after Plasma login."]

_rowR = xs[GRP_MEMBERS[_lastg][0]] + colw[_lastg]   # the band rect is drawn at xs
band_row_w = _rowR - _rowL
LEG_W = max(LEG_MIN, _rowR - LEG_X) + 120
LEG_H = build_legend([], LEG_X, FOOT_TOP) - FOOT_TOP + 38
canvas_w = max(_rowR + MARGIN_R, LEG_X + LEG_W + MARGIN_R)
canvas_h = max(DY + DH + 70 + 3*30, FOOT_TOP + LEG_H) + 28

# ---- svg document header ----
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
  f'viewBox="0 0 {canvas_w} {canvas_h}">')
A('<defs>'
  '<marker id="ar_ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  '<path d="M 0 0 L 10 5 L 0 10 z" fill="#2e7d32"/></marker>'
  '<marker id="ar_n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
  '<path d="M 0 0 L 10 5 L 0 10 z" fill="#607d8b"/></marker>'
  '<marker id="ar_rf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  '<path d="M 0 0 L 10 5 L 0 10 z" fill="#f9a825"/></marker>'
  '<marker id="ar_no" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  '<path d="M 0 0 L 10 5 L 0 10 z" fill="#c62828"/></marker>'
  '</defs>')
A(f'<rect width="{canvas_w}" height="{canvas_h}" fill="#ffffff"/>')
A(tspan(MARGIN_L, HDR_Y[0], HDR[0][0], HDR[0][1], HDR[0][2], HDR[0][3]))
for _i in range(1, len(HDR)):
    A(tspan(MARGIN_L, HDR_Y[_i], HDR[_i][0], HDR[_i][1], HDR[_i][2], HDR[_i][3]))
A(f'<line x1="{MARGIN_L}" y1="{HDR_RULE}" x2="{canvas_w-MARGIN_L}" y2="{HDR_RULE}" '
  f'stroke="#d1d5db" stroke-width="2"/>')

# ---- band containers (boundaries) ----
BAND_FILL = {"ext":"#f7f9fa","adp":"#fffaf3","work":"#f4f9fe",
             "data":"#f4fbf5","field":"#fffdf3","sales":"#f3f0fd",
             "sim":"#f2faf6","sec":"#fbf3fb",
             "flow":"#fafbfc"}
BAND_BORD = {"ext":"#455a64","adp":"#ef6c00","work":"#1565c0",
             "data":"#1b5e20","field":"#f9a825","sales":"#5e35b1",
             "sim":"#00695c","sec":"#6a1b9a",
             "flow":"#546e7a"}
for b in BANDS:
    bx, by = xs[b["key"]], b["_by"]
    bw, bh = colw[b["key"]], b["_bh"]
    A(f'<g class="band" data-band="{b["key"]}" data-title="{b["n"]} · {b["title"]}">')
    A(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="20" ry="20" '
      f'fill="{BAND_FILL[b["key"]]}" stroke="{BAND_BORD[b["key"]]}" stroke-width="3" '
      f'stroke-dasharray="none"/>')
    for _k, _l in enumerate(wrap(f'{b["n"]} · {b["title"]}',
                                 max(12, int((bw-46)/(FS_BT*0.62))))):
        A(tspan(bx+22, by+44+_k*BT_STEP, _l, FS_BT, BAND_BORD[b["key"]], "bold"))
    for _k, _l in enumerate(wrap(b["purpose"], max(12, int((bw-46)/(FS_BP*0.565))))):
        A(tspan(bx+22, by+76+_k*BP_STEP, _l, FS_BP, "#4b5563"))
    _sl = wrap(b["sec"], max(12, int((bw-46)/(FS_BS*0.565))))
    for _k, _l in enumerate(_sl):
        A(tspan(bx+22, by+HEAD[b["key"]]-10-(len(_sl)-1-_k)*BS_STEP, _l, FS_BS, "#9ca3af"))
    A('</g>')

# ---- stacked section titles, and the empty sections that still show a box ----
for b in BANDS:
    bk = b["key"]
    bord = BAND_BORD[bk]
    for st, sy in b.get("_head", []):
        for _k, _l in enumerate(wrap(st, max(12, int((colw[bk]-46)/(FS_SEC*0.62))))):
            A(tspan(xs[bk] + PAD_X + 2, sy + 24 + _k*(FS_SEC+3), _l, FS_SEC, bord, "bold"))
        A(f'<line x1="{xs[bk]+PAD_X}" y1="{sy+34}" x2="{xs[bk]+colw[bk]-PAD_X-GUT[bk]}" '
          f'y2="{sy+34}" stroke="{bord}" stroke-width="1.4" opacity="0.35"/>')
    for ey, eh in b.get("_empty", []):
        ex, ew2 = xs[bk] + PAD_X, colw[bk] - PAD_X*2 - GUT[bk]
        A(f'<rect x="{ex}" y="{ey}" width="{ew2}" height="{eh}" rx="10" ry="10" '
          f'fill="none" stroke="{bord}" stroke-width="2" stroke-dasharray="7 5" '
          f'opacity="0.5"/>')
        A(tspan(ex + ew2/2, ey + eh/2 - 4, "no component here yet", 17, bord, "normal", "middle"))
        A(tspan(ex + ew2/2, ey + eh/2 + 20, "reserved", 15, "#9ca3af", "italic", "middle"))

# ---- edges: orthogonal routes through dedicated channels ----

def bcol(nid):
    return _BC[nid]

# a vertical channel sits in the middle of each gap between two bands
CHAN = [xs[GRP_MEMBERS[g][0]] + colw[g] + GAPW[i]/2 - PAD_X
        for i, g in enumerate(GRP_ORDER[:-1])]

# Long links share the gaps, so give each one its own x clear of the centre
# line that the ordinary adjacent-band links use.
_users = {}
for ab in LONG_ALL:
    ca, cb = _BC[ab[0]], _BC[ab[1]]
    for g in (min(ca, cb), max(ca, cb)-1):
        _users.setdefault(g, []).append(ab)
# ---- one dedicated x per edge, inside the gap it crosses ----------------
# Every vertical keeps a hard clearance (CLR) from BOTH column borders of the
# gap it runs in, and each gap's verticals are spread evenly across the WHOLE
# usable width instead of clustering on the centre line. Two things follow:
# no line ever clips the right edge of a column (the 6/7/8 stack was the
# worst), and the vertical-to-horizontal corners are separated left to right
# across every gap, so a line can be followed from card to card.
# Overlap is then only ever intentional: edges that share a source card leave
# it side by side, and nothing else ever lies on the same line.
CLR = 30                          # clear space between a vertical and a border

# per gap: (left column's right edge, right column's left edge)
_GEO = []
for _i in range(len(GRP_ORDER) - 1):
    _L = xs[GRP_MEMBERS[GRP_ORDER[_i]][0]] + colw[GRP_ORDER[_i]]
    _R = xs[GRP_MEMBERS[GRP_ORDER[_i + 1]][0]]
    _GEO.append((_L, _R))

# collect per gap: (edge, which_side). side only breaks the insertion order
# for the degenerate g<0 case (column 0's internal links); a real gap now
# carries every edge it sees as one evenly spread file.
_gusers = {}
for (s_, d_, _l, _k) in EDGES:
    ca, cb = _BC[s_], _BC[d_]
    if ca == cb:
        g = ca - 1
        # same-column verticals live in the gap LEFT of their own column and
        # anchor beside their own stack, so a card's stub stays short.
        _gusers.setdefault(g, []).append(((s_, d_), +1)) if g >= 0 else \
            _gusers.setdefault(-1, []).append(((s_, d_), -1))
    else:
        lo, hi = min(ca, cb), max(ca, cb)
        _gusers.setdefault(lo, []).append(((s_, d_), +1))   # entry into B
        _gusers.setdefault(hi-1, []).append(((s_, d_), -1)) # exit from A
        for g in range(lo+1, hi-1):
            _gusers.setdefault(g, []).append(((s_, d_), +1))

EDGEX = {}
for g, lst in _gusers.items():
    seen, abs_ = {}, []
    for ab, side in lst:
        if ab in seen:
            continue
        seen[ab] = side
        abs_.append(ab)
    n = len(abs_)
    if g >= 0:
        _L, _R = _GEO[g]
        lo_x, hi_x = _L + CLR, _R - CLR
        if n == 1:
            _xs = [(lo_x + hi_x) / 2]
        else:
            _step = (hi_x - lo_x) / (n - 1)   # one x per edge, full-gap spread
            _xs = [lo_x + k * _step for k in range(n)]
    else:
        # column 0's internal links draw in the card gutter (see route());
        # keep a harmless fan around the centre so the key still resolves.
        _xs = [CHAN[0] + (k - (n-1)/2) * STEP_X for k in range(n)]
    for ab, x in zip(abs_, _xs):
        EDGEX[(ab[0], ab[1], g)] = x


# ---- attachment points: every link meets its card at its OWN spot ---------
# route() used to leave every card from its exact vertical centre, so a card
# with nine links drew nine lines that shared the first 200px of their run and
# were impossible to tell apart.  Each link now gets its own port, fanned down
# the edge of the card it belongs to, in a fixed order so the picture is
# stable between builds.  Lines leaving one card are then evenly stacked and
# each one can be followed from the card to wherever it goes.
PORT = {}
_in  = {}
_out = {}
for (_s, _d, _l, _k) in EDGES:
    _out.setdefault(_s, []).append((_d, _l, _k))
    _in .setdefault(_d, []).append((_s, _l, _k))
PORT_STEP = 15
def _ports(node, lst):
    """Distinct y values down the middle of the card's left or right edge."""
    n = NM[node]
    top, bot = n["_y"] + 16, n["_y"] + n["_h"] - 16
    if not lst:
        return {}
    span = bot - top
    k = len(lst)
    ys = []
    for i in range(k):
        if k == 1:
            ys.append((top + bot) / 2)
        else:
            ys.append(top + span * i / (k - 1))
    return dict(zip(lst, ys))
for _n in set(list(_out) + list(_in)):
    for _side, _lst in (("o", sorted(_out.get(_n, []))),
                        ("i", sorted(_in.get(_n, [])))):
        _m = _ports(_n, _lst)
        for _key, _y in _m.items():
            PORT[(_n, _side) + _key] = _y

# Two cards in the same column can still be handed the same y, and then their
# stubs share a horizontal run for no reason. Ports are therefore made unique
# WITHIN each band column and side, so the only lines that ever run together
# are lines that genuinely belong to the same stack.
_bycol = {}
for (n_, side, o_, l_, k_), y_ in PORT.items():
    _bycol.setdefault((_BC[n_], side), []).append((y_, (n_, side, o_, l_, k_)))
for _k, _lst in _bycol.items():
    _lst.sort()
    for _i in range(1, len(_lst)):
        if abs(_lst[_i][0] - _lst[_i-1][0]) < PORT_STEP:
            PORT[_lst[_i][1]] = _lst[_i-1][0] + PORT_STEP

def port_a(a, b, lab, kind):
    return PORT.get((a, "o", b, lab, kind), NM[a]["_cy"])

def port_b(a, b, lab, kind):
    return PORT.get((b, "i", a, lab, kind), NM[b]["_cy"])

def clamp_cor(lx, g, w):
    """Keep a cross-band label pill wholly inside the gap it belongs to."""
    _L, _R = _GEO[g]
    lo, hi = _L + 6, _R - 6
    if hi - lo < w:
        return (_L + _R) / 2
    return min(max(lx, lo + w/2), hi - w/2)

def route(a, b, lw=0, lab="", kind="ok"):
    """Orthogonal route: out of A, vertical in a channel, into B."""
    A_, B_ = NM[a], NM[b]
    ca, cb = bcol(a), bcol(b)
    if ca == cb:
        # same column: run down the gutter beside the boxes
        gx = (EDGEX.get((a, b, ca-1), CHAN[ca-1] + SB_OFF) if ca > 0
              else A_["_x"] - GUT[_NB[a]]/2)
        x1, y1 = A_["_x"], port_a(a, b, lab, kind)
        x2, y2 = B_["_x"], port_b(a, b, lab, kind)
        return (f"M {x1} {y1} L {gx} {y1} L {gx} {y2} L {x2} {y2}",
                (gx, (y1 + y2) / 2), True)
    lo, hi = min(ca, cb), max(ca, cb)
    if hi - lo >= 2:
        ab = (a, b)
        yA, yB = port_a(a, b, lab, kind), port_b(a, b, lab, kind)
        gA, gB = (lo, hi-1) if cb > ca else (hi-1, lo)
        xs_ = EDGEX.get((a, b, gA), CHAN[gA])
        xd_ = EDGEX.get((a, b, gB), CHAN[gB])
        if cb > ca:     # left to right
            x1, x2 = A_["_x"] + A_["_w"], B_["_x"]
        else:           # right to left
            x1, x2 = A_["_x"], B_["_x"] + B_["_w"]
        if ab in BOTTOM:
            # same shape as the top lane, mirrored: drop below every box,
            # run the page under the stacks, then rise into the last box
            yL = BOT_LANE[ab]
            return (f"M {x1} {yA} L {xs_} {yA} L {xs_} {yL} L {xd_} {yL} "
                    f"L {xd_} {yB} L {x2} {yB}",
                    (clamp_cor((x1+xs_)/2, gA, lw), yA-7), cb > ca)
        # skips a band: leave A, climb to this link's private lane, cross over
        # the whole row above every band, then drop into B
        yL = LANE[ab]
        # The label rides the lane itself, centred in the horizontal run.  It
        # used to sit 7px above the source card, which pushed it down into the
        # narrow gap between two stacks -- the one place on the page with no
        # room, and the reason those labels collided and read badly.  The strip
        # above the bands is wide and almost empty by design, so the label goes
        # there.  The pill is opaque white, so it masks the line it names.
        lx = (xs_ + xd_) / 2
        if xd_ - xs_ > lw + 8:                 # keep it inside its own run
            lx = min(max(lx, xs_ + lw/2 + 4), xd_ - lw/2 - 4)
        return (f"M {x1} {yA} L {xs_} {yA} L {xs_} {yL} L {xd_} {yL} "
                f"L {xd_} {yB} L {x2} {yB}",
                (lx, yL), cb > ca)
    ch = EDGEX.get((a, b, lo), CHAN[lo])
    if cb > ca:   # left to right
        x1, y1 = A_["_x"] + A_["_w"], port_a(a, b, lab, kind)
        x2, y2 = B_["_x"], port_b(a, b, lab, kind)
    else:         # right to left
        x1, y1 = A_["_x"], port_a(a, b, lab, kind)
        x2, y2 = B_["_x"] + B_["_w"], port_b(a, b, lab, kind)
    return (f"M {x1} {y1} L {ch} {y1} L {ch} {y2} L {x2} {y2}",
            (clamp_cor((x1+ch)/2, lo, lw), y1-7), cb > ca)

STYLE = {"ok":  dict(c="#2e7d32", w=2.6, dash=None,  m="ar_ok",  op=1.0),
         "normal": dict(c="#78909c", w=1.7, dash="6 4", m="ar_n",  op=0.85),
         "rf":  dict(c="#f9a825", w=4.0, dash="12 6", m="ar_rf", op=1.0),
         "no":  dict(c="#c62828", w=2.0, dash="3 6", m="ar_no",  op=0.5)}
for (s_, d_, lab, kind) in EDGES:
    st = STYLE[kind]
    dd, (lx, ly), vert = route(s_, d_, len(lab)*11.2 + 24 if lab else 0, lab, kind)
    da = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
    lj = "round"
    # class/data-a/data-b are inert for print and for inkscape, and they are what
    # lets the HTML viewer trace one node's links: the SVG is flat, so without
    # them the browser cannot tell which line belongs to which card.
    A(f'<path class="edge" data-a="{s_}" data-b="{d_}" data-kind="{kind}" '
      f'd="{dd}" fill="none" stroke="{st["c"]}" stroke-width="{st["w"]}"{da} '
      f'opacity="{st["op"]}" marker-end="url(#{st["m"]})" stroke-linejoin="{lj}"/>')

# ---- edge labels, de-collided so no two pills overlap ----
PILL_FS, PILL_H, PILL_PAD = 18, 24, 12

def pillw(lab):
    """True pill width. The old len*8.0 guess was ~15% narrow for bold 15px
    DejaVu, so the text spilled out of its own white pill and visually collided
    with neighbours even when the rects did not touch."""
    return tw(lab, PILL_FS, bold=True) + PILL_PAD*2

def pill(lx, ly, lab, c, ea="", eb=""):
    """Text is centred in the pill on BOTH axes. It used to be drawn with its
    baseline on the pill's mid-line, so the glyphs sat high and spilled toward
    the top edge; dominant-baseline=central puts the true visual centre of the
    text on the true visual centre of the pill."""
    wpx = pillw(lab)
    A(f'<g class="epill" data-a="{ea}" data-b="{eb}">')
    A(f'<rect x="{lx-wpx/2:.1f}" y="{ly-PILL_H/2:.1f}" width="{wpx:.1f}" '
      f'height="{PILL_H}" rx="{PILL_H/2}" fill="#ffffff" opacity="1.0" '
      f'stroke="{c}" stroke-width="0.9"/>')
    A(tspan(lx, ly, lab, PILL_FS, c, "bold", "middle", dbase="central"))
    A('</g>')

placed = []
# the node cards are reserved first, so a label can never be pushed onto one
for n in NODES:
    placed.append((n["_x"], n["_y"], n["_w"], n["_h"]))

def free(x, y, w, h, pad=0):
    for (px, py, pw, ph) in placed:
        if (x < px+pw+pad and x+w > px-pad and y < py+ph+pad and y+h > py-pad):
            return False
    return True

# A small outward spiral: 8 directions, but only a short way.
#
# This used to run out to k=25 (~650px). That is what put "tunnel to loopback
# origin" and both ao-egress-archive labels far ABOVE the line they name: the
# ideal spot on the path was taken by an earlier label, so the search fled until
# it found air, and a label far from its line is worse than one touching a
# neighbour. A label must stay readable as belonging to its path, so the search
# is capped at ~2 pill heights and, failing that, the label KEEPS its ideal
# point on the line and is reported instead of being exiled.
PILL_R = PILL_H*2 + 4
RINGS = [0]
for k in range(1, 7):
    RINGS += [k*18, -k*18, k*26, -k*26, k*36, -k*36, k*26+k*18, k*26-k*18,
              -k*26+k*18, -k*26-k*18]
# The ring list is built once from PILL_R; the cap below is the tolerance for a
# genuinely crowded junction. Two pill-heights was not enough at the busiest
# lane junctions, but it stays an order of magnitude tighter than the old 650px
# walk that put labels in entirely the wrong part of the page.
RINGS = [r for r in RINGS if abs(r) <= PILL_R*3.0] or [0]

# Skip-link labels ride a lane, and each lane is its own horizontal strip. They
# are placed FIRST and in lane order: interleaved with the other labels, a later
# lane's pill could claim the middle of an earlier lane's run and push that
# lane's own label off its line entirely, which is how "PDF requests in" ended
# up with nowhere to go. Every lane is now occupied by its own label before any
# ordinary label competes for the space.
def _lanekey(e):
    s_, d_, lab, kind = e
    ab = (s_, d_)
    if ab in m_lane_y:
        return (0, m_lane_y[ab])
    return (1, 0)


m_lane_y = dict(LANE)
m_lane_y.update(BOT_LANE)
unplaced = []
for (s_, d_, lab, kind) in sorted(EDGES, key=_lanekey):
    if not lab:
        continue
    st = STYLE[kind]
    w = pillw(lab)
    dd, (lx, ly), vert = route(s_, d_, w, lab, kind)
    hit = False
    for dx in RINGS:
        for dy in RINGS:
            if not (dx or dy):
                if free(lx-w/2, ly-PILL_H/2, w, PILL_H, pad=PILL_PAD):
                    hit = True; break
                continue
            if free(lx+dx-w/2, ly+dy-PILL_H/2, w, PILL_H, pad=PILL_PAD):
                lx, ly = lx+dx, ly+dy
                hit = True; break
        if hit:
            break
    if not hit:
        # Leave it ON its line. A label overlapping a neighbour is recoverable by
        # eye; one floating in empty space reads as belonging to nothing.
        unplaced.append(lab)
    placed.append((lx-w/2, ly-PILL_H/2, w, PILL_H))
    pill(lx, ly, lab, st["c"], s_, d_)

if unplaced:
    print("  WARNING labels with no free spot:", unplaced)



# ---- nodes ----
# Each card is wrapped in a <g class="card" data-id="..."> so the HTML viewer can
# highlight one card, trace its links and dim the rest. The wrapper is a plain
# grouping element: inkscape and the print pipeline treat it as a no-op, so the
# PDF and PNG are byte-for-byte the same drawing.
NID = {}
for n in NODES:
    NID[n["title"].split(" ")[0].lower()] = n.get("id", n["title"])
for n in NODES:
    fill, bord = CLS[n["cls"]]
    x, y, w, h = n["_x"], n["_y"], n["_w"], n["_h"]
    _nid = n.get("id", "")
    _bnd = n.get("band", "")
    # html.escape, NOT json.dumps: dumps leaves the quote characters in the
    # value, so the side panel rendered the title as "PostgreSQL 18".
    _lbl = html.escape(n["title"], quote=True)
    _st  = html.escape(n["status"], quote=True)
    A(f'<g class="card" data-id="{_nid}" data-band="{_bnd}" data-title="{_lbl}" data-status="{_st}">')
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" ry="12" fill="{fill}" '
      f'stroke="{bord}" stroke-width="2.5"/>')
    A(f'<rect x="{x}" y="{y}" width="7" height="{h}" rx="3" fill="{bord}"/>')
    ty = y + PAD_Y + 18
    for l in n["_title"]:
        A(tspan(x+20, ty, l, FS_TITLE, "#111827", "bold")); ty += LH_TITLE
    for l in n["_purp"]:
        A(tspan(x+20, ty, l, FS_PURP, "#4b5563", "italic")); ty += LH
    ty += 3
    for l in n["_det"]:
        A(tspan(x+20, ty, l, FS_DET, "#1f2937")); ty += LH
    ty += 4
    A(tspan(x+20, ty, n["status"], FS_ST, ST[n["status"]], "bold"))
    A('</g>')

# ============================== LEGEND ====================================
# The legend now sits in the bottom area beside the route detail, so the whole
# right-hand column of the page is free.
A(f'<rect x="{LEG_X}" y="{FOOT_TOP}" width="{LEG_W}" height="{LEG_H}" rx="20" ry="20" '
  f'fill="#fafbfd" stroke="#455a64" stroke-width="3"/>')
build_legend(A, LEG_X, FOOT_TOP)

# DX, DY, DW, DH, DG and LEG_X are anchored to the band row in the layout above.
A(tspan(DX, DY - 28, "THE ONE ROUTE EVERYTHING TAKES  —  README v7 \u00a73.1 Isolation Detail \u00b7 \u00a74.4 Approved Internal Paths",
       21, "#111827", "bold"))
for i, (key, lab, cls, anchor, note) in enumerate(DET):
    f_, b_ = CLS[cls]
    x = DX + i*(DW+DG)
    lines = lab.split("\n")
    h = DH
    A(f'<rect x="{x}" y="{DY}" width="{DW}" height="{h}" rx="12" fill="{f_}" '
      f'stroke="{b_}" stroke-width="2.5"/>')
    ty = DY + 32
    for ln in lines:
        A(tspan(x+DW/2, ty, ln, 17, "#111827", "bold", "middle")); ty += 21
    if i < len(DET)-1:
        A(f'<line x1="{x+DW}" y1="{DY+h/2}" x2="{x+DW+DG}" y2="{DY+h/2}" '
          f'stroke="#2e7d32" stroke-width="3" marker-end="url(#ar_ok)"/>')
# the three 4.4 paths that are not manifests into the ledger (v6 4.4 makes all
# nine approved paths subject to the same eight controls - none of them bypasses)
A(tspan(DX, DY + DH + 38, "Three more approved paths, same eight controls:", 18, "#111827", "bold"))
BYPASS = [
 ("Ledger status \u2192 authorised service, gated", "w_core", "d_meta"),
 ("Mission release \u2192 MeshChatX \u2192 QGC per drone", "w_ing", "w_field"),
 ("Image set \u2192 WebODM folder, synced after landing", "w_map", "f_map1"),
]
for i, (lab, a, b) in enumerate(BYPASS):
    y = DY + DH + 70 + i*30
    A(f'<line x1="{DX}" y1="{y-5}" x2="{DX+42}" y2="{y-5}" stroke="#2e7d32" '
      f'stroke-width="2.6" marker-end="url(#ar_ok)"/>')
    A(tspan(DX+54, y, lab, 17, "#1f2937"))
# the eight mandatory controls
CX = DX + 3*(DW+DG) + 36
A(tspan(CX, DY + DH + 38, "Every cross-domain request MUST have all eight:", 18, "#111827", "bold"))
CTRL = ["Mutual TLS", "Dedicated service certificate", "Signed payload where provenance matters",
        "Schema validation", "Timestamp + nonce (replay defence)", "Durable idempotency key",
        "Audit record", "Explicit authorisation policy"]
CTRL_W = max(tw(c, 16) for c in CTRL) + 40
CTRL_PITCH = max(360, (LEG_X - 40 - CX) // 2)
for i, c in enumerate(CTRL):
    col, row = i % 2, i // 2
    x = CX + col*CTRL_PITCH
    y = DY + DH + 70 + row*30
    A(f'<rect x="{x}" y="{y-14}" width="17" height="17" rx="4" fill="#2e7d32"/>')
    A(tspan(x+26, y, c, 16, "#1f2937"))

A('</svg>')
svg = "\n".join(S)
open(os.path.join(OUT, "alwayson-single-topology.svg"), "w").write(svg)


# ------------------------------- .html -------------------------------------
# The viewer is written here rather than by hand so it can never drift out of
# sync with the SVG: same canvas, same viewBox, inlined so the file works from
# a memory stick with no network. The graphic is 5454px wide, which is far
# wider than any screen, so it gets pan/zoom rather than a scaled-to-fit image
# that would make the body text unreadable.
HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  html,body{margin:0;height:100%;background:#e8eaed;
            font:14px/1.4 "DejaVu Sans",Verdana,system-ui,sans-serif;color:#111827}
  #bar{display:flex;gap:8px;align-items:center;padding:6px 10px;background:#1f2937;
       color:#f9fafb;position:sticky;top:0;z-index:10;box-shadow:0 1px 4px #0006}
  #bar button{font:inherit;padding:4px 10px;border:1px solid #4b5563;border-radius:6px;
              background:#374151;color:#f9fafb;cursor:pointer}
  #bar button:hover{background:#4b5563}
  #bar button[aria-pressed="true"]{background:#2563eb;border-color:#2563eb}
  #z{font-variant-numeric:tabular-nums;min-width:5.5em;text-align:center}
  #view{position:absolute;inset:41px 0 0 0;overflow:hidden;cursor:grab;background:#f6f7f9}
  #view.drag{cursor:grabbing}
  #stage{position:absolute;top:0;left:0;transform-origin:0 0;
         box-shadow:0 2px 18px #0003;background:#fff}
  #stage svg{display:block}
  #hint{position:absolute;right:10px;bottom:8px;color:#6b7280;font-size:12px;
        background:#ffffffee;padding:3px 8px;border-radius:6px;pointer-events:none}
  /* ---- interaction -------------------------------------------------- */
  /* Dimming is done on a wrapper class rather than per-element inline styles so
     that clearing it is one classList.remove() and cannot leave the page half
     faded. transition gives the glow a moment to bloom instead of snapping. */
  #stage.tracing .card{opacity:.16;transition:opacity .18s}
  #stage.tracing .card.hit{opacity:1}
  #stage.tracing .card.sel{opacity:1}
  #stage.tracing .edge{opacity:.07;transition:opacity .18s}
  #stage.tracing .edge.hit{opacity:1}
  #stage.tracing .epill{opacity:.12;transition:opacity .18s}
  #stage.tracing .epill.hit{opacity:1}
  #stage.tracing .epill.hit rect{stroke-width:2}
  #stage .card{transition:opacity .18s}
  /* A traced link thickens and takes a halo, so the eye follows the line
     instead of losing it among the 261 crossings. */
  #stage .edge.hit{stroke-width:5.5;filter:drop-shadow(0 0 3px currentColor)}
  #stage .edge.hit[data-kind="rf"]{stroke-width:7}
  #stage .card.hit rect:first-of-type{stroke-width:4}
  #stage .card.sel rect:first-of-type{stroke-width:5.5;
        filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}
  #stage .card{cursor:pointer}
  #stage .epill text{pointer-events:none}
  #stage .epill rect{pointer-events:none}
  /* Collapsing hides a band and every link that touches it, so the remaining
     cards are no longer threaded through by lines that go nowhere. */
  #stage.collapsing .band[data-band="__HIDDEN__"]{display:none}
  /* ---- single-band pages -------------------------------------------- */
  /* Each band is also a standalone page, reflowed onto its own sheet so the
     text is roughly three times larger than on the full spread. They are
     inlined rather than linked so the viewer still works with no network and
     no folder alongside it. */
  #zmenu{position:fixed;inset:0;z-index:40;background:#0009;
         display:flex;align-items:center;justify-content:center}
  #zmenu[hidden]{display:none}
  #zmenu-in{background:#fff;border-radius:14px;padding:18px 22px;max-width:640px;
            box-shadow:0 10px 40px #0007}
  .zt{font-weight:700;font-size:15px;margin-bottom:12px}
  .zd{color:#6b7280;font-size:12px;margin-top:14px;line-height:1.5}
  #zbtns{display:flex;flex-wrap:wrap;gap:6px}
  #zbtns button{font:inherit;padding:7px 12px;border:1px solid #4b5563;border-radius:8px;
                background:#374151;color:#f9fafb;cursor:pointer}
  #zbtns button:hover{background:#2563eb;border-color:#2563eb}
  #zclose{margin-top:14px;font:inherit;padding:6px 12px;border:1px solid #d1d5db;
          border-radius:8px;background:#f3f4f6;cursor:pointer}
  #zmodal{position:fixed;inset:0;z-index:50;background:#e8eaed;display:flex;
          flex-direction:column}
  #zmodal[hidden]{display:none}
  #zmodal-bar{display:flex;align-items:center;justify-content:space-between;
              padding:6px 12px;background:#1f2937;color:#f9fafb;font-size:14px}
  #zmodal-bar button{font:inherit;padding:4px 10px;border:1px solid #4b5563;
                     border-radius:6px;background:#374151;color:#f9fafb;cursor:pointer}
  #zmodal-body{flex:1;overflow:auto;padding:14px;display:flex;
               justify-content:center;align-items:flex-start}
  #zmodal-body svg{background:#fff;box-shadow:0 2px 18px #0003;
                   width:100%;height:auto;max-width:1500px}
  @media print{
    #zmodal{position:static}
    #zmodal-bar{display:none}
    #zmodal-body{overflow:visible;padding:0}
    #zmodal-body svg{max-width:none;width:100%}
    #zmenu,#bar,#view,#panel,#bandbar,#hint{display:none!important}
  }
  #bandbar{position:absolute;left:8px;top:49px;z-index:8;display:flex;gap:4px;
           flex-wrap:wrap;max-width:60%}
  #bandbar button{font:inherit;font-size:12px;padding:2px 7px;border-radius:5px;
                  border:1px solid #9ca3af;background:#fffffff0;cursor:pointer;color:#111827}
  #bandbar button:hover{background:#e5e7eb}
  #bandbar button[aria-pressed="true"]{background:#111827;color:#f9fafb;border-color:#111827}
  #bandbar button.sel{outline:2px solid #2563eb;outline-offset:1px}
  #panel{position:absolute;right:0;top:41px;width:330px;max-height:calc(100% - 41px);
         overflow:auto;background:#fffffff2;backdrop-filter:blur(3px);
         border-left:1px solid #d1d5db;padding:10px 12px;font-size:13px;
         display:none;z-index:9;box-shadow:-2px 0 10px #0002}
  #panel.on{display:block}
  /* The panel is opaque, so it would sit on top of the very columns it
     describes. Shifting the stage left by the panel width keeps both the
     traced card and its list visible at the same time. */
  #view.sidestep{--panel:330px}
  #panel h2{margin:0 0 2px;font-size:15px;color:#111827}
  #panel .st{font-weight:bold;margin-bottom:6px}
  #panel ul{margin:6px 0 0;padding-left:16px}
  #panel li{margin:2px 0}
  #panel .dim{color:#6b7280;font-size:12px}
  #panel button{font:inherit;margin-top:8px;padding:3px 9px;border:1px solid #4b5563;
                border-radius:6px;background:#374151;color:#f9fafb;cursor:pointer}
  #find{padding:3px 7px;border:1px solid #4b5563;border-radius:6px;
        background:#111827;color:#f9fafb;width:150px}
  @media print{#bar,#hint,#panel{display:none}#view{position:static;overflow:visible}
               #stage{position:static;box-shadow:none;transform:none}
               @page{size:A3 landscape;margin:8mm}}
</style>
</head>
<body>
<div id="bar">
  <button id="fit"  title="Fit the whole page">Fit</button>
  <button id="one"  title="Actual size">1:1</button>
  <button id="out"  title="Zoom out">&minus;</button>
  <span id="z">100%</span>
  <button id="in"   title="Zoom in">+</button>
  <button id="lref" title="Jump to the legend">Legend</button>
  <button id="lmid" title="Jump to the seam where the two print halves meet">Seam</button>
  <input id="find" placeholder="find a node&hellip;" title="Jump to a node by name">
  <button id="clr" title="Clear the highlight (Esc)">Clear</button>
  <button id="print" title="Print the whole page">Print</button>
  <button id="zband" title="Open a single band as its own full-size page">Zoom band&hellip;</button>
</div>
<div id="zmenu" hidden>
  <div id="zmenu-in">
    <div class="zt">Open one band as a single page &mdash; larger text, nothing else on the page</div>
    <div id="zbtns"></div>
    <div class="zd">Each band also exists as its own file in <b>bands/</b>:
      <b>band-1.svg / .png / .pdf</b> &hellip; <b>band-9</b>, all generated from this same model.</div>
    <button id="zclose">Close</button>
  </div>
</div>
<div id="zmodal" hidden>
  <div id="zmodal-bar"><span id="zmodal-t"></span><button id="zmodal-x">Close</button></div>
  <div id="zmodal-body"></div>
</div>
<div id="view"><div id="stage">__SVG__</div></div>
<div id="panel"></div>
<div id="bandbar"></div>
<div id="hint">drag to pan &middot; wheel to zoom &middot; double-click to fit &middot;
  <b>hover</b> a card to trace its links &middot; <b>click</b> to pin &middot; <b>Esc</b> to clear</div>
<script>
const W=__W__, H=__H__, SEAM=__SEAM__;
const view=document.getElementById('view'), stage=document.getElementById('stage'),
      zl=document.getElementById('z');
let z=1, x=0, y=0;
const PANEL_W=330;
let side=false;                       // is the detail panel open?
function apply(){
  // The panel is opaque and sits on the right, so when it is open the page is
  // nudged left by half its width. This has to be done here, in the pan maths,
  // because apply() owns stage.style.transform and would overwrite a CSS rule.
  const off=side?-PANEL_W/2:0;
  stage.style.transform='translate('+(x+off)+'px,'+y+'px) scale('+z+')';
  zl.textContent=Math.round(z*100)+'%';
}
function fit(){
  const r=view.getBoundingClientRect();
  z=Math.min(r.width/W, r.height/H)*0.97;
  x=(r.width-W*z)/2; y=(r.height-H*z)/2; apply();
}
function clamp(){
  const r=view.getBoundingClientRect(), w=W*z, h=H*z;
  const right=side?r.width-PANEL_W:r.width;
  x=Math.min(0,Math.max(right-w,x)); y=Math.min(0,Math.max(r.height-h,y));
}
const $=id=>document.getElementById(id);
$('fit').onclick=fit;
$('one').onclick=()=>{z=1;x=0;y=0;apply();};
$('in').onclick =()=>{z=Math.min(6,z*1.25);apply();};
$('out').onclick=()=>{z=Math.max(0.02,z/1.25);apply();};
$('lref').onclick=()=>{z=1;x=view.getBoundingClientRect().width-W;y=0;clamp();apply();};
$('lmid').onclick=()=>{z=0.6;x=view.getBoundingClientRect().width/2-SEAM*z;
                       y=0;clamp();apply();};
$('print').onclick=()=>window.print();

/* ---- per-band pages ----------------------------------------------------
   Nine standalone sheets, one per numbered band, inlined so the viewer is
   still a single self-contained file. Opening one swaps the whole view, so
   Escape or Close always lands back on the full spread. */
const BANDPAGES=__BANDS__;
const zmenu=$('zmenu'), zmodal=$('zmodal'), zbody=$('zmodal-body');
BANDPAGES.forEach(b=>{
  const btn=document.createElement('button');
  btn.textContent=b.n+' \u00b7 '+b.title;
  btn.title=b.purpose;
  btn.onclick=()=>{ zmenu.hidden=true; openBand(b.n); };
  $('zbtns').appendChild(btn);
});
$('zband').onclick=()=>{ zmenu.hidden=!zmenu.hidden; };
$('zclose').onclick =()=>{ zmenu.hidden=true; };
$('zmodal-x').onclick=()=>{ zmodal.hidden=true; };
zmenu.addEventListener('click',e=>{ if(e.target===zmenu) zmenu.hidden=true; });
function openBand(n){
  const b=BANDPAGES.find(x=>x.n===n); if(!b) return;
  $('zmodal-t').textContent='Band '+b.n+' of 9 \u00b7 '+b.title;
  zbody.innerHTML=b.svg;
  zmodal.hidden=false;
}
addEventListener('keydown',e=>{
  if(e.key==='Escape'){ if(!zmodal.hidden){ zmodal.hidden=true; }
                        else if(!zmenu.hidden){ zmenu.hidden=true; } }
});

/* ---- tracing: one card in, its links lit, the rest pushed back ----------
   The SVG is a flat list of shapes, so the links between cards are rebuilt here
   from the data-a/data-b the generator wrote onto every path. That adjacency
   is the whole feature: hover a card and the browser can finally answer "what
   does this touch?", which a printed page can only make you look up. */
const cards=[...stage.querySelectorAll('.card')];
const edges=[...stage.querySelectorAll('.edge')];
const pills=[...stage.querySelectorAll('.epill')];
const byId={}; cards.forEach(c=>byId[c.dataset.id]=c);
const ADJ={}; cards.forEach(c=>ADJ[c.dataset.id]=new Set([c.dataset.id]));
const LINKS={};
edges.forEach(e=>{
  const a=e.dataset.a, b=e.dataset.b;
  if(ADJ[a]&&ADJ[b]){ADJ[a].add(b); ADJ[b].add(a);
    (LINKS[a]=LINKS[a]||[]).push({o:b,e:e});}
  if(LINKS[b]) LINKS[b].push({o:a,e:e});
});
const panel=$('panel');

function trace(id, pin){
  if(!id){ stage.classList.remove('tracing');
           cards.forEach(c=>c.classList.remove('hit','sel'));
           edges.forEach(e=>e.classList.remove('hit'));
           pills.forEach(p=>p.classList.remove('hit'));
           panel.classList.remove('on'); side=false; apply(); return; }
  const near=ADJ[id]||new Set([id]);
  stage.classList.add('tracing');
  cards.forEach(c=>{ c.classList.remove('hit','sel');
    c.classList.toggle('hit', near.has(c.dataset.id));
    if(c.dataset.id===id && pin) c.classList.add('sel'); });
  edges.forEach(e=>{ const on=(e.dataset.a===id||e.dataset.b===id);
    e.classList.toggle('hit', on); });
  pills.forEach(pl=>{ const on=(pl.dataset.a===id||pl.dataset.b===id);
    pl.classList.toggle('hit', on); });
  show(id, near);
}
function show(id, near){
  const c=byId[id]; if(!c) return;
  if(!side){ side=true; }
  const out=[];
  for(const e of edges){
    if(e.dataset.a!==id && e.dataset.b!==id) continue;
    const o=byId[e.dataset.b===id?e.dataset.a:e.dataset.b];
    const kind={ok:'approved path',normal:'ordinary internal',rf:'radio link',no:'PROHIBITED'}[e.dataset.kind]||e.dataset.kind;
    out.push('<li>'+(o?o.dataset.title:e.dataset.b)+' <span class="dim">&mdash; '+kind+'</span></li>');
  }
  clamp();
  panel.innerHTML='<h2>'+c.dataset.title+'</h2><div class="st" style="color:#37474f">'
    +c.dataset.status+'</div><div class="dim">touches '+((near.size-1))+' other node(s)</div>'
    +(out.length?'<ul>'+out.join('')+'</ul>':'<div class="dim">no links drawn</div>')
    +'<button id="pin">Unpin</button>';
  panel.classList.add('on');
  panel.querySelector('#pin').onclick=()=>trace(null);
}
let pinned=null;
cards.forEach(c=>{
  c.addEventListener('mouseenter',()=>{ if(!pinned) trace(c.dataset.id,false); });
  c.addEventListener('mouseleave',()=>{ if(!pinned) trace(null); });
  c.addEventListener('click',e=>{ e.stopPropagation();
    if(pinned===c.dataset.id){ pinned=null; trace(null); }
    else { pinned=c.dataset.id; trace(c.dataset.id,true); } });
});
view.addEventListener('click',()=>{ if(pinned){pinned=null; trace(null);} });
addEventListener('keydown',e=>{ if(e.key==='Escape'){pinned=null;trace(null);} });

/* Centre a node and open its trace -- used by the find box, so you can go
   straight to a component instead of hunting for it across 5,454px. */
function goto(id){
  const c=byId[id]; if(!c) return false;
  const r=c.getBoundingClientRect(), v=view.getBoundingClientRect();
  z=Math.max(z,0.85);
  x=v.width/2-(r.left-v.left+r.width/2)*z;

  y=v.height/2-(r.top-v.top+r.height/2)*z;
  clamp(); pinned=id; trace(id,true); apply(); return true;
}
/* ---- band collapse ------------------------------------------------------
   A band is a whole numbered box. Folding one away also hides every link that
   touches it, which is the point: the remaining picture stops being threaded
   through by lines whose far end has vanished. */
const bands=[...stage.querySelectorAll('.band')];
const bb=$('bandbar');
const bandOf={}; cards.forEach(c=>bandOf[c.dataset.id]=c.dataset.band);
function refoldLinks(){
  const hid=stage.dataset.hidden;
  stage.querySelectorAll('.edge,.epill').forEach(el=>{
    const t=(el.dataset.a&&bandOf[el.dataset.a]===hid)
         ||(el.dataset.b&&bandOf[el.dataset.b]===hid);
    el.style.display=t?'none':'';
  });
}
bands.forEach(b=>{
  const key=b.dataset.band;
  const btn=document.createElement('button');
  btn.textContent=b.dataset.title.split(' · ')[0]+' · '+b.dataset.title.split(' · ')[1].slice(0,10);
  btn.title='Collapse / expand band: '+b.dataset.title;
  btn.onclick=()=>{
    const hidden=stage.classList.contains('collapsing')&&stage.dataset.hidden===key;
    if(stage.dataset.hidden){
      stage.querySelector('.band[data-band="__HIDDEN__"]')
          .setAttribute('data-band', stage.dataset.hidden);
    }
    stage.classList.remove('collapsing'); delete stage.dataset.hidden;
    document.querySelectorAll('#bandbar button').forEach(x=>x.setAttribute('aria-pressed','false'));
    if(!hidden){
      // The band element itself carries the key, so the stylesheet rule above
      // does the hiding and this only records which one is folded.
      stage.querySelector('.band[data-band="'+key+'"]').setAttribute('data-band','__HIDDEN__');
      stage.classList.add('collapsing'); stage.dataset.hidden=key;
      btn.setAttribute('aria-pressed','true');
      pinned=null; trace(null);
    }
    refoldLinks(); requestAnimationFrame(fit);
  };
  bb.appendChild(btn);
});
$('clr').onclick=()=>{pinned=null;trace(null);
  if(stage.dataset.hidden)
    stage.querySelector('.band[data-band="__HIDDEN__"]')
        .setAttribute('data-band', stage.dataset.hidden);
  stage.classList.remove('collapsing'); delete stage.dataset.hidden;
  document.querySelectorAll('#bandbar button').forEach(x=>x.setAttribute('aria-pressed','false'));
  refoldLinks(); fit();};
$('find').addEventListener('keydown',e=>{
  if(e.key!=='Enter') return;
  const q=e.target.value.trim().toLowerCase(); if(!q) return;
  const hit=cards.find(c=>c.dataset.title.toLowerCase().includes(q))
          || cards.find(c=>c.dataset.id.toLowerCase()===q);
  if(hit) goto(hit.dataset.id);
  else { e.target.style.outline='2px solid #dc2626';
         setTimeout(()=>e.target.style.outline='',600); }
});
view.addEventListener('wheel',e=>{
  e.preventDefault();
  const r=view.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const f=Math.exp(-e.deltaY*0.0015), nz=Math.min(6,Math.max(0.02,z*f));
  x=mx-(mx-x)*(nz/z); y=my-(my-y)*(nz/z); z=nz; clamp(); apply();
},{passive:false});
let drag=null;
view.addEventListener('pointerdown',e=>{
  drag={x:e.clientX,y:e.clientY,ox:x,oy:y};
  view.classList.add('drag'); view.setPointerCapture(e.pointerId);
});
view.addEventListener('pointermove',e=>{
  if(!drag)return; x=drag.ox+(e.clientX-drag.x); y=drag.oy+(e.clientY-drag.y);
  clamp(); apply();
});
view.addEventListener('pointerup',e=>{drag=null;view.classList.remove('drag');});
view.addEventListener('dblclick',fit);
addEventListener('resize',()=>{clamp();apply();});
fit();
</script>
</body>
</html>
"""
# The seam used for the two print halves, so the viewer can point at it. A cut is
# only safe if it misses every card, every text run and every edge-label pill;
# the thin lane lines are fine to cut, because they carry on onto the other page.
# This is the same rule used to place the actual PNG split, so the button in the
# viewer lands exactly where the paper folds.
#
# Verified against the rendered PNG: the corridor it reports at svg x=3299 is
# card-free across the full band row, and it sits in the gutter immediately left
# of the section 4 (Stores and reporting) column, whose box starts at x=3301.885.
# Every band therefore stays whole in one half. (Checked with PIL column-ink
# analysis, and by reading the emitted PNGs.)
def _seam_scan():
    import xml.etree.ElementTree as ET
    NS = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg)
    cards, texts, pills = [], [], []

    def walk(e):
        tag = e.tag.replace(NS, "")
        if tag == "rect":
            try:
                x = float(e.get("x", 0)); w = float(e.get("width", 0))
                h = float(e.get("height", 0))
            except ValueError:
                x = w = h = 0.0
            # The page background spans the whole canvas. Treating it as a card
            # blocks every column and silently forces the unsafe midpoint fallback.
            if w >= canvas_w*0.98:
                pass
            elif w > 150 and h > 40:
                y = float(e.get("y", 0) or 0)
                cards.append((x, x+w, y, y+h))
            elif 20 < w < 220:
                y = float(e.get("y", 0) or 0)
                pills.append((x, x+w, y, y+h))
        elif tag == "text":
            # A <text> may hold many <tspan> lines. Concatenating them (as the
            # old regex did) inflates the width enormously and made every
            # column look blocked. Measure each line separately instead.
            x = float(e.get("x", 0) or 0)
            fs = float(e.get("font-size", 15) or 15)
            anch = e.get("text-anchor") or "start"
            spans = e.findall(f"{NS}tspan")
            if spans:
                for sp in spans:
                    sx = float(sp.get("x", x) or x)
                    sfs = float(sp.get("font-size", fs) or fs)
                    sa = sp.get("text-anchor") or anch
                    t = "".join(sp.itertext())
                    if t.strip():
                        sy = float(sp.get("y", 0) or 0)
                        a, b = _span_x(sx, t, sfs, sa)
                        texts.append((a, b, sy - sfs, sy + sfs*0.3))
            else:
                t = "".join(e.itertext())
                if t.strip():
                    sy = float(e.get("y", 0) or 0)
                    a, b = _span_x(x, t, fs, anch)
                    texts.append((a, b, sy - fs, sy + fs*0.3))
        for c in e:
            walk(c)

    def _span_x(x, t, fs, anch):
        # 0.62em average advance is deliberately generous, so the seam errs
        # toward leaving a gap rather than clipping a glyph.
        w = len(t) * fs * 0.62
        if anch == "middle":
            return (x - w/2, x + w/2)
        if anch == "end":
            return (x - w, x)
        return (x, x + w)

    walk(root)

    # Two corrections over the original whole-canvas scan.
    #
    # 1. A fold may only cut the BAND ROW, never the header or the footer. The
    #    legend and the "read me" blocks sit below the columns and are wide, so
    #    they made every candidate x look blocked and the scan returned an empty
    #    list, after which it fell through to the unsafe midpoint. Restricting
    #    the test to the vertical span of the columns is what makes a clear
    #    corridor findable at all.
    #
    # 2. "Never cut a card" is necessary but not sufficient: cutting down the
    #    MIDDLE of a band column leaves a half-column on each page, which is
    #    unreadable and loses the band heading. Prefer the gutter immediately
    #    before a column, so every band stays whole in one half.
    #
    # NOTE: do NOT reach for DY or DY+DH here. DY is the y of the small
    # "route" strip at the BOTTOM of the page (4099) and DH is that strip's
    # 150-unit height, so a DY+DH window tests empty space under the diagram.
    # The band row is bounded by the band boxes themselves: BODY_BOT is their
    # bottom edge and the top edge is the smallest _by across all bands.
    BAND_Y1 = BODY_BOT
    BAND_Y0 = min(b["_by"] for b in BANDS)

    def clear_in_band(cx):
        return not any(a-2 <= cx <= b+2 and y0 < BAND_Y1 and y1 > BAND_Y0
                       for a, b, y0, y1 in cards + texts + pills)

    lo, hi = int(canvas_w*0.25), int(canvas_w*0.75)
    mid = canvas_w // 2
    # Prefer the clear column closest to the midpoint. Taking the first clear
    # column left-to-right would put the fold as far left as it can legally go,
    # which makes one print half much narrower than the other.
    best = [cx for cx in range(lo, hi) if clear_in_band(cx)]
    gutters = [cx for cx in range(lo, hi)
               if clear_in_band(cx)
               and clear_in_band(cx - 1)
               and any(a - 4 <= cx <= a and y0 < BAND_Y1 and y1 > BAND_Y0
                       for a, _b, y0, y1 in cards + texts + pills)]
    if gutters:
        return min(gutters, key=lambda cx: (abs(cx - mid), cx))
    if best:
        return min(best, key=lambda cx: (abs(cx - mid), cx))
    return mid

# ====================== PER-BAND ZOOM PAGES ==============================
# Nine more pages, one per numbered band, for reading a band on its own.
#
# Each page is REFLOWED, not cropped. A crop of the poster would still carry the
# poster's 7,100-unit width, so the text would stay exactly as small as it always
# was. Instead every band is re-laid-out into a compact ~2,400-unit page: the
# cards keep the same font sizes but now sit on a page under a third of the
# width, so the same 17px is roughly three times larger relative to the paper
# and is readable without a magnifier. Cards flow into a grid rather than one
# tall column, which is what keeps a whole band on ONE page.
#
# Every link that touches the band is listed underneath with its other end, so
# the page answers "what does this connect to" without the rest of the picture.
BP_W = 2400
BP_M, BP_GUT, BP_COLGUT = 56, 18, 22
BP_MIN_H, BP_MAX_H = 900, 1700


def band_card_lines(n, inner):
    """Wrap one card's text to the zoom page's narrower card."""
    t = wrap(n["title"], max(8, int(inner/(FS_TITLE*0.62))))
    p = wrap(n["purpose"], max(10, int(inner/(FS_PURP*0.565))))
    d = [sl for x in n["details"] for sl in wrap(x, max(10, int(inner/(FS_DET*0.565))))]
    return t, p, d


def band_card_h(t, p, d):
    return (PAD_Y + 18 + len(t)*25 + len(p)*LH + 3 + len(d)*LH + 4 + LH
            + 13 + PAD_Y)


def band_layout(b):
    """Decide the page height, column count and per-card wrap BEFORE drawing.

    The page size has to be settled first, because the opening <svg> tag and the
    background rectangle both quote it. So this measures the band and returns
    everything band_page needs, and the drawing pass just follows it.
    """
    ns = [NM[i] for _s, _t, ids, _k in b["_secs"] for i in ids]
    links = [(a, d_, l, k) for (a, d_, l, k) in EDGES
             if NM[a]["band"] == b["key"] or NM[d_]["band"] == b["key"]]
    hy = 74 + 60
    for _ln in wrap(b["purpose"], 96):
        hy += 31
    hy += 6 + 22
    top = hy + 34 + 30 + ((len(links)+1)//2)*27 + 16 + 26
    best = None
    for cols in (5, 4, 3, 2, 1):
        cw = (BP_W - 2*BP_M - (cols-1)*BP_COLGUT)/cols
        laid = [band_card_lines(n, cw - TXT_L - TXT_R) for n in ns]
        hs = [band_card_h(*L) for L in laid]
        rows = [hs[i::cols] for i in range(cols)]
        tall = max((sum(r) + BP_GUT*max(0, len(r)-1) for r in rows), default=0)
        if tall <= BP_MAX_H - top - 46:
            best = (cols, cw, laid, hs, tall)
            break
    if best is None:
        cw = BP_W - 2*BP_M
        laid = [band_card_lines(n, cw - TXT_L - TXT_R) for n in ns]
        hs = [band_card_h(*L) for L in laid]
        best = (1, cw, laid, hs, sum(hs) + BP_GUT*max(0, len(hs)-1))
    cols, cw, laid, hs, tall = best
    h = max(BP_MIN_H, min(BP_MAX_H, int(top + tall + 46)))
    return dict(ns=ns, links=links, cols=cols, cw=cw, laid=laid, hs=hs, h=h)


def band_page(b, idx):
    """One standalone page for one numbered band."""
    bk = b["key"]
    L_ = band_layout(b)
    ns, links, cols, cw, laid, hs = (L_["ns"], L_["links"], L_["cols"],
                                     L_["cw"], L_["laid"], L_["hs"])
    BP_H = L_["h"]
    out = []
    def A(x): out.append(x)
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{BP_W}" height="{BP_H}" '
      f'viewBox="0 0 {BP_W} {BP_H}">')
    A('<defs>'
      '<marker id="z_ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
      'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
      'fill="#2e7d32"/></marker>'
      '<marker id="z_n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
      'markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
      'fill="#607d8b"/></marker>'
      '<marker id="z_rf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
      'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
      'fill="#f9a825"/></marker>'
      '<marker id="z_no" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
      'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
      'fill="#c62828"/></marker></defs>')
    bord = BAND_BORD[bk]
    A(f'<rect width="{BP_W}" height="{BP_H}" fill="#ffffff"/>')
    A(f'<rect x="10" y="10" width="{BP_W-20}" height="{BP_H-20}" rx="18" ry="18" '
      f'fill="{BAND_FILL[bk]}" stroke="{bord}" stroke-width="5"/>')

    y = 74
    A(tspan(BP_M, y, f'{b["n"]} \u00b7 {b["title"]}', 46, "#111827", "bold"))
    y += 60
    for ln in wrap(b["purpose"], 96):
        A(tspan(BP_M, y, ln, 24, "#4b5563")); y += 31
    y += 6
    A(tspan(BP_M, y, f'Authority: {b["sec"]}', 19, "#6b7280", "normal"))
    y += 22
    A(f'<line x1="{BP_M}" y1="{y}" x2="{BP_W-BP_M}" y2="{y}" stroke="{bord}" '
      f'stroke-width="2.5" opacity="0.5"/>')

    # ---- every link that touches this band, listed before the cards so the
    # ---- page reads top-down: what it is, what it connects to, what is in it
    links = [(a, d_, l, k) for (a, d_, l, k) in EDGES
             if NM[a]["band"] == bk or NM[d_]["band"] == bk]
    y += 34
    A(tspan(BP_M, y, f'CONNECTIONS ({len(links)})', 24, "#111827", "bold"))
    y += 30
    MK = {"ok": "z_ok", "normal": "z_n", "rf": "z_rf", "no": "z_no"}
    COLS = {"ok": "#2e7d32", "normal": "#607d8b", "rf": "#f9a825", "no": "#c62828"}
    half = (len(links) + 1) // 2
    for i, (a, d_, l, k) in enumerate(links):
        cx = BP_M + (i // half)*(BP_W - 2*BP_M)//2
        cy = y + (i % half)*27
        out_ = NM[a]["band"] == bk
        other = d_ if out_ else a
        arrow = "\u25b6" if out_ else "\u25c0"
        # The arrow CHARACTER carries the direction. It used to be drawn a
        # second time as an SVG marker on a stub line, so every row opened with
        # two arrows pointing at each other and read as two separate links.
        A(f'<rect x="{cx}" y="{cy-13}" width="5" height="15" rx="2" fill="{COLS[k]}"/>')
        s2 = f'{arrow}  {NM[other]["title"]}'
        if l:
            s2 += f'  \u2014  {l}'
        A(tspan(cx+16, cy, s2, 18, "#1f2937"))
    y += half*27 + 16
    A(f'<line x1="{BP_M}" y1="{y}" x2="{BP_W-BP_M}" y2="{y}" stroke="{bord}" '
      f'stroke-width="2.5" opacity="0.5"/>')

    # ---- cards, flowed into as many columns as fit above the footer ----
    # Page height, column count and card wraps all come from the pre-pass.
    top = y + 26
    # lay out column by column, balancing heights
    colh = [0.0]*cols
    order = sorted(range(len(ns)), key=lambda i: -hs[i])
    slot = [0]*len(ns)
    for i in order:
        c = min(range(cols), key=lambda k: colh[k])
        slot[i] = c
        colh[c] += hs[i] + BP_GUT
    ytop = [top]*cols
    for i, n in enumerate(ns):
        c = slot[i]
        x = BP_M + c*(cw + BP_COLGUT)
        yy = ytop[c]
        t, pp, d = laid[i]
        h = hs[i]
        fill, bo = CLS[n["cls"]]
        A(f'<g class="zcard" data-id="{n["id"]}">')
        A(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{cw:.1f}" height="{h:.1f}" rx="12" ry="12" '
          f'fill="{fill}" stroke="{bo}" stroke-width="2.5"/>')
        A(f'<rect x="{x:.1f}" y="{yy:.1f}" width="7" height="{h:.1f}" rx="3" fill="{bo}"/>')
        ty = yy + PAD_Y + 18
        for l in t:
            A(tspan(x+20, ty, l, FS_TITLE, "#111827", "bold")); ty += LH_TITLE
        for l in pp:
            A(tspan(x+20, ty, l, FS_PURP, "#4b5563", "italic")); ty += LH
        ty += 3
        for l in d:
            A(tspan(x+20, ty, l, FS_DET, "#1f2937")); ty += LH
        ty += 4
        A(tspan(x+20, ty, n["status"], FS_ST, ST[n["status"]], "bold"))
        if n.get("note"):
            for l in wrap(n["note"], max(12, int((cw-TXT_L-TXT_R)/(13*0.565))))[:3]:
                A(tspan(x+20, ty+LH+2, l, 13, "#9ca3af", "italic"))
        A('</g>')
        ytop[c] = yy + h + BP_GUT

    A(tspan(BP_M, BP_H-26, f'ALWAYS ON \u00b7 band {b["n"]} of 9 \u00b7 {len(ns)} component(s) '
      f'\u00b7 derived from the one-page topology, same data', 17, "#9ca3af"))
    A('</svg>')
    return "\n".join(out)


_seam = _seam_scan()

BDIR = os.path.join(OUT, "bands")
os.makedirs(BDIR, exist_ok=True)
_band_svgs = {}
for _i, _b in enumerate(BANDS, start=1):
    _s = band_page(_b, _i)
    _f = os.path.join(BDIR, f"band-{_b['n']}.svg")
    open(_f, "w").write(_s)
    _band_svgs[_b["n"]] = _s

open(os.path.join(OUT, "alwayson-single-topology.html"), "w").write(
    HTML.replace("__TITLE__", "ALWAYS ON — single-page topology")
        .replace("__SVG__", svg)
        .replace("__W__", repr(round(canvas_w, 2)))
        .replace("__H__", repr(round(canvas_h, 2)))
        .replace("__SEAM__", str(_seam))
        .replace("__BANDS__", json.dumps(
            [dict(n=_b["n"], title=_b["title"], purpose=_b["purpose"],
                  svg=_band_svgs[_b["n"]]) for _b in BANDS])))

json.dump(dict(
    title="ALWAYS ON single-page topology",
    authority="README v7 3.2 Canonical Implementation Status (expected-to-be-installed)",
    semantics=dict(
        colour="encodes the CLASS of thing a node is",
        status="IMPLEMENTED | IN PROGRESS | PARTIAL | PLANNED | BLOCKED",
        edges=("green solid = approved (mTLS, signed, audited); "
               "grey dashed = ordinary internal; "
               "amber heavy dashed = radio (no IP); "
               "red dotted = PROHIBITED by 4.3")),
    bands=BANDS, nodes=NODES,
    edges=[dict(src=a, dst=b, label=l, kind=k) for a, b, l, k in EDGES],
), open(os.path.join(OUT, "alwayson-single-topology.json"), "w"), indent=1)


# ============================== RENDER =====================================
# The SVG is the master. The raster and vector-page artefacts are DERIVED from
# it and must never be edited by hand: a hand-made PNG silently goes stale the
# moment the source is regenerated, and the reader is left reviewing a picture
# of a topology that no longer exists.
#
# inkscape is used because it is what is installed; cairosvg is not. Every
# artefact is rendered from the same freshly written SVG, and the two portrait
# panels are cut at exactly the seam the HTML viewer reports, so the fold lands
# in the same place in all three.
SVG_P = os.path.join(OUT, "alwayson-single-topology.svg")

# 200 dpi keeps the fine detail (edge-label pills, card rules) legible when the
# page is printed at A3/A2 without going so large the file becomes unusable.
PNG_DPI = 200


def _run(cmd):
    import subprocess
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed ({r.returncode}): "
                           f"{(r.stderr or r.stdout or '').strip()[:400]}")
    return r


def render():
    if not shutil.which("inkscape"):
        print("render: SKIPPED — inkscape not found; "
              ".png/.pdf/panels are now stale, do not trust them")
        return False

    png = os.path.join(OUT, "alwayson-single-topology.png")
    pdf = os.path.join(OUT, "alwayson-single-topology.pdf")
    _run(["inkscape", SVG_P, "--export-type=png",
          f"--export-dpi={PNG_DPI}", f"--export-filename={png}"])
    _run(["inkscape", SVG_P, "--export-type=pdf",
          f"--export-filename={pdf}"])

    # The two portrait panels. The cut is at the seam the HTML viewer already
    # points at, so "page 2 of 2" in the viewer is the same fold as the paper.
    from PIL import Image
    # This PNG is rendered here from our own SVG at 200 dpi, not fetched from
    # anywhere, so PIL's decompression-bomb guard (meant for untrusted input)
    # only aborts a legitimate 16000px-wide print render.
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(png)
    W, H = im.size
    cut = int(round(_seam / canvas_w * W))
    cut = max(1, min(W - 1, cut))
    im.crop((0, 0, cut, H)).save(
        os.path.join(OUT, "alwayson-single-topology-left.png"))
    im.crop((cut, 0, W, H)).save(
        os.path.join(OUT, "alwayson-single-topology-right.png"))

    # The complete diagram must stay landscape. This is a hard constraint, so
    # it is asserted here rather than left for a human to spot in the output.
    assert W > H, f"complete diagram is PORTRAIT ({W}x{H}); it must stay landscape"
    assert W / H >= 1.4, f"aspect {W/H:.3f} is under the 1.4:1 minimum"
    print(f"render: png {W}x{H} ({W/H:.3f} landscape)  "
          f"panels cut at x={cut}px = svg {_seam:.0f} of {canvas_w:.0f}")
    return True


# ---- the nine single-band pages -------------------------------------------
# Written next to the master SVG and rendered from it, exactly like the poster:
# a hand-made zoom page would go stale the moment the model changed.


def render_bands():
    """Rasterise and vectorise each band page from the SVG just written."""
    if not shutil.which("inkscape"):
        print("render_bands: SKIPPED - inkscape not found; band pages are stale")
        return False
    for _b in BANDS:
        _n = _b["n"]
        _src = os.path.join(BDIR, "band-" + _n + ".svg")
        _run(["inkscape", _src, "--export-type=png", "--export-dpi=150",
              "--export-filename=" + os.path.join(BDIR, "band-" + _n + ".png")])
        _run(["inkscape", _src, "--export-type=pdf",
              "--export-filename=" + os.path.join(BDIR, "band-" + _n + ".pdf")])
    from PIL import Image
    for _b in BANDS:
        with Image.open(os.path.join(BDIR, f"band-{_b['n']}.png")) as _im:
            assert _im.size[0] > _im.size[1], (
                f"band {_b['n']} page is portrait {_im.size}; expected landscape")
    print(f"render_bands: {len(BANDS)} band pages -> {os.path.relpath(BDIR, OUT)}/")
    return True


render()
render_bands()
print(f"svg {canvas_w}x{canvas_h}  nodes={len(NODES)} edges={len(EDGES)}")
