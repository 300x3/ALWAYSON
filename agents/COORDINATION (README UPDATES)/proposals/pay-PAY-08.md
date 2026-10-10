---
item: PAY-08
action: close
evidence: |
  md5sum assets/images/weather-balloon-canrad.png -> 65180695e0de6a6c168a75641f421bd0 (710908 B, 1024x496)
  md5sum source /home/scottw/Pictures/WEATHER BALLOON-CANRAD.png -> 65180695e0de6a6c168a75641f421bd0 (match)
  backup of wrong file at /tmp/weather-balloon-canrad.bak-20261009-202403.png (362073 B, bafb7ffe)
  stray .bak-source copy removed from deployed assets dir
  68/68 data-item blocks JSON-parse; both Balloon blocks list images=[005-0d04b808bf8b.png, weather-balloon-canrad.png]
section: 07-public-storefront-and-payment-policy
---
PAY-08 re-copy executed under operator APPROVED 2026-10-09. The deployed
asset was the wrong file (362073 B, md5 bafb7ffe); backed it to /tmp, copied
the correct source (710908 B, md5 65180695, 1024x496) into
***CURRENT***/assets/images/weather-balloon-canrad.png. Structure half was
already correct (both Balloon data-item blocks list 2 images, refcount 2,
68/68 JSON-parse) so no index.html edit was needed. Modal now renders 2-up.
What I got wrong: my second backup cp landed a .bak-source file inside the
deployed assets dir; removed it immediately. Verified no stray files remain.
