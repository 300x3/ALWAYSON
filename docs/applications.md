# ALWAYS ON — Exhaustive Software Inventory

> Generated `2026-10-02T02:37:16+00:00` by `scripts/build-update/inventory-full.py`.
> Do not hand-edit; regenerate with:
>
> ```bash
> /ALWAYSON/scripts/build-update/inventory-full.py --markdown \
>   --out /ALWAYSON/docs/applications.md
> ```

Host: **Ubuntu 26.04.1 LTS** — codename `resolute`, version `26.04`, kernel `7.0.0-38-generic`.

Every item is tagged **first** to the Ubuntu LTS release it belongs to, and
only then to the repository that delivers it. That ordering answers the
question that matters when deciding what to update: is this part of the
supported platform, or is it something a third party ships?

## Totals

| Category | Count |
|---|---|
| apt packages installed | **4229** |
| — of which Ubuntu 26.04 LTS | **3863** |
| — of which third-party repositories | **363** |
| — of which in no apt index | **3** |
| apt packages behind `Candidate` | **4** |
| Desktop applications (`.desktop`) | **319** |
| Applications with no package manager | **15** |
| Executables in `~/.local/bin` | **88** |
| pip / pipx / npm-global | **39** |
| Snap packages | **17** |
| Flatpak applications | **1** |
| Quadlet containers | **21** |

## APT packages, grouped by release

⚠️ marks a package that has a newer `Candidate` than what is installed.

### Ubuntu (resolute-backports) — 1 packages

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `yt-dlp` | `2026.03.17-1` | resolute-backports | universe |

</details>

### Ubuntu LTS security — 452 packages

<details><summary>Show all 452</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `accountsservice` | `23.13.9-8ubuntu5.2` | resolute-security | main |
| `avahi-daemon` | `0.8-18ubuntu1.1` | resolute-security | main |
| `avahi-utils` | `0.8-18ubuntu1.1` | resolute-security | main |
| `bind9-dnsutils` | `1:9.20.24-1ubuntu0.3` | resolute-security | main |
| `bind9-host` | `1:9.20.24-1ubuntu0.3` | resolute-security | main |
| `bind9-libs` | `1:9.20.24-1ubuntu0.3` | resolute-security | main |
| `bpftool` | `7.7.0+7.0.0-38.38` | resolute-security | main |
| `bsdextrautils` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `bsdutils` | `1:2.41.3-3ubuntu2.2` | resolute-security | main |
| `bubblewrap` | `0.11.1-1ubuntu0.3` | resolute-security | main |
| `build-essential` | `12.12ubuntu2.26.04.2` | resolute-security | main |
| `bzip2` | `1.0.8-6ubuntu0.1` | resolute-security | main |
| `bzip2-doc` | `1.0.8-6ubuntu0.1` | resolute-security | main |
| `ca-certificates` | `20260601~26.04.1` | resolute-security | main |
| `clamav` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `clamav-base` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `clamav-daemon` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `clamav-freshclam` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `clamdscan` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `cpio` | `2.15+dfsg-2.1ubuntu0.1` | resolute-security | main |
| `cups` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-bsd` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-client` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-common` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-core-drivers` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-daemon` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-ipp-utils` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-ppdc` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `cups-server-common` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `curl` | `8.18.0-1ubuntu2.7` | resolute-security | main |
| `diffutils` | `1:3.12-1ubuntu0.1` | resolute-security | main |
| `dirmngr` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `distro-info-data` | `0.72-0ubuntu0.26.04.1` | resolute-security | main |
| `dnsmasq-base` | `2.92-1ubuntu0.4` | resolute-security | main |
| `dracut-install` | `110-11ubuntu0.1` | resolute-security | main |
| `eject` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `fdisk` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `fonts-opensymbol` | `4:102.12+LibO26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `gawk` | `1:5.3.2-1ubuntu1.1` | resolute-security | main |
| `ghostscript` | `10.06.0~dfsg-3ubuntu1.1` | resolute-security | main |
| `gir1.2-girepository-3.0` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `gir1.2-glib-2.0` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `gir1.2-glib-2.0-dev` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `gir1.2-packagekitglib-1.0` | `1.3.4-3ubuntu1.2` | resolute-security | main |
| `gir1.2-polkit-1.0` | `127-2ubuntu1.1` | resolute-security | main |
| `gir1.2-poppler-0.18` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `gir1.2-udisks-2.0` | `2.10.91-1ubuntu2.1` | resolute-security | main |
| `girepository-tools` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `gnu-coreutils` | `9.7-3ubuntu2.1` | resolute-security | main |
| `gnupg` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gnupg-agent` | `2.4.8-4ubuntu3.1` | resolute-security | universe |
| `gnupg-l10n` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gnupg-utils` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gnutls-bin` | `3.8.12-2ubuntu1.1` | resolute-security | universe |
| `gpg` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gpg-agent` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gpg-wks-client` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gpgconf` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gpgsm` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gpgv` | `2.4.8-4ubuntu3.1` | resolute-security | main |
| `gstreamer1.0-gl` | `1.28.2-1ubuntu0.1` | resolute-security | main |
| `gstreamer1.0-pipewire` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `gstreamer1.0-plugins-bad` | `1.28.2-1ubuntu1.2` | resolute-security | universe |
| `gstreamer1.0-plugins-base` | `1.28.2-1ubuntu0.1` | resolute-security | main |
| `gstreamer1.0-plugins-extra` | `1.28.2-1ubuntu1.2` | resolute-security | main |
| `gstreamer1.0-plugins-good` ⚠️ | `1.28.2-2ubuntu0.3` | resolute-security | main |
| `gstreamer1.0-x` | `1.28.2-1ubuntu0.1` | resolute-security | main |
| `gzip` | `1.14-1~exp2ubuntu1.1` | resolute-security | main |
| `hplip` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `hplip-data` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `inetutils-telnet` | `2:2.7-2ubuntu1.1` | resolute-security | main |
| `jq` | `1.8.1-4ubuntu2` | resolute-security | main |
| `kdenlive` | `4:25.12.3-0ubuntu1.1` | resolute-security | universe |
| `kdenlive-data` | `4:25.12.3-0ubuntu1.1` | resolute-security | universe |
| `krb5-locales` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `krb5-multidev` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libaccountsservice0` | `23.13.9-8ubuntu5.2` | resolute-security | main |
| `libaom-dev` | `3.13.1-2ubuntu0.1` | resolute-security | main |
| `libaom3` | `3.13.1-2ubuntu0.1` | resolute-security | main |
| `libaprutil1t64` | `1.6.3-3ubuntu3.1` | resolute-security | main |
| `libarchive-dev` | `3.8.5-1ubuntu2.2` | resolute-security | main |
| `libarchive13t64` | `3.8.5-1ubuntu2.2` | resolute-security | main |
| `libasound2-data` | `1.2.15.3-1ubuntu1.1` | resolute-security | main |
| `libasound2-dev` | `1.2.15.3-1ubuntu1.1` | resolute-security | main |
| `libasound2t64` | `1.2.15.3-1ubuntu1.1` | resolute-security | main |
| `libatopology2t64` | `1.2.15.3-1ubuntu1.1` | resolute-security | main |
| `libattr1` | `1:2.5.2-4ubuntu0.1` | resolute-security | main |
| `libattr1-dev` | `1:2.5.2-4ubuntu0.1` | resolute-security | main |
| `libauthen-sasl-perl` | `2.2000-1ubuntu0.1` | resolute-security | main |
| `libavahi-client3` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libavahi-common-data` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libavahi-common3` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libavahi-core7` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libavahi-glib1` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libavahi-ui-gtk3-0` | `0.8-18ubuntu1.1` | resolute-security | main |
| `libblkid-dev` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libblkid1` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libbz2-1.0` | `1.0.8-6ubuntu0.1` | resolute-security | main |
| `libbz2-dev` | `1.0.8-6ubuntu0.1` | resolute-security | main |
| `libc-bin` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libc-dev-bin` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libc-gconv-modules-extra` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libc6` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libc6-dbg` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libc6-dev` | `2.43-2ubuntu2.4` | resolute-security | main |
| `libcaca0` | `0.99.beta20-6ubuntu2.1` | resolute-security | main |
| `libclamav12` | `1.5.4+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `libcups2t64` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `libcupsimage2t64` | `2.4.16-1ubuntu1.3` | resolute-security | main |
| `libcurl3t64-gnutls` | `8.18.0-1ubuntu2.7` | resolute-security | main |
| `libcurl4-gnutls-dev` | `8.18.0-1ubuntu2.7` | resolute-security | main |
| `libcurl4t64` | `8.18.0-1ubuntu2.7` | resolute-security | main |
| `libeditorconfig0` | `0.12.10+~0.17.1-3ubuntu0.1` | resolute-security | main |
| `libevent-2.1-7t64` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libevent-core-2.1-7t64` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libevent-dev` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libevent-extra-2.1-7t64` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libevent-openssl-2.1-7t64` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libevent-pthreads-2.1-7t64` | `2.1.12-stable-10ubuntu0.2` | resolute-security | main |
| `libexif-dev` | `0.6.25-2ubuntu0.1` | resolute-security | main |
| `libexif-doc` | `0.6.25-2ubuntu0.1` | resolute-security | main |
| `libexif12` | `0.6.25-2ubuntu0.1` | resolute-security | main |
| `libexpat1` | `2.7.4-1ubuntu0.2` | resolute-security | main |
| `libexpat1-dev` | `2.7.4-1ubuntu0.2` | resolute-security | main |
| `libfdisk1` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libfreerdp-client3-3` | `3.32.0+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `libfreerdp3-3` | `3.32.0+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `libfreetype-dev` | `2.14.2+dfsg-1ubuntu0.1` | resolute-security | main |
| `libfreetype6` | `2.14.2+dfsg-1ubuntu0.1` | resolute-security | main |
| `libgcrypt20` | `1.12.0-2ubuntu1.1` | resolute-security | main |
| `libgif-dev` | `5.2.2-1ubuntu3.2` | resolute-security | main |
| `libgif7` | `5.2.2-1ubuntu3.2` | resolute-security | main |
| `libgio-2.0-dev` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libgio-2.0-dev-bin` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libgirepository-2.0-0` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libgit2-1.9` | `1.9.1+ds-1ubuntu1.2` | resolute-security | main |
| `libglib2.0-0t64` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libglib2.0-bin` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libglib2.0-data` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libglib2.0-dev` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libglib2.0-dev-bin` | `2.88.0-1ubuntu0.1` | resolute-security | main |
| `libgnutls-dane0t64` | `3.8.12-2ubuntu1.1` | resolute-security | main |
| `libgnutls-openssl27t64` | `3.8.12-2ubuntu1.1` | resolute-security | main |
| `libgnutls28-dev` | `3.8.12-2ubuntu1.1` | resolute-security | main |
| `libgnutls30t64` | `3.8.12-2ubuntu1.1` | resolute-security | main |
| `libgphoto2-6t64` | `2.5.33-1ubuntu1.1` | resolute-security | main |
| `libgphoto2-dev` | `2.5.33-1ubuntu1.1` | resolute-security | main |
| `libgphoto2-l10n` | `2.5.33-1ubuntu1.1` | resolute-security | main |
| `libgphoto2-port12t64` | `2.5.33-1ubuntu1.1` | resolute-security | main |
| `libgraphite2-3` | `1.3.14-11ubuntu1.1` | resolute-security | main |
| `libgs-common` | `10.06.0~dfsg-3ubuntu1.1` | resolute-security | main |
| `libgs10` | `10.06.0~dfsg-3ubuntu1.1` | resolute-security | main |
| `libgs10-common` | `10.06.0~dfsg-3ubuntu1.1` | resolute-security | main |
| `libgssapi-krb5-2` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libgssrpc4t64` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libgstreamer-gl1.0-0` | `1.28.2-1ubuntu0.1` | resolute-security | main |
| `libgstreamer-plugins-bad1.0-0` | `1.28.2-1ubuntu1.2` | resolute-security | universe |
| `libgstreamer-plugins-base1.0-0` | `1.28.2-1ubuntu0.1` | resolute-security | main |
| `libgstreamer-plugins-extra1.0-0` | `1.28.2-1ubuntu1.2` | resolute-security | main |
| `libheif-dev` | `1.21.2-3ubuntu0.6` | resolute-security | universe |
| `libheif-plugin-aomdec` | `1.21.2-3ubuntu0.6` | resolute-security | main |
| `libheif-plugin-aomenc` | `1.21.2-3ubuntu0.6` | resolute-security | main |
| `libheif-plugin-j2kdec` | `1.21.2-3ubuntu0.6` | resolute-security | universe |
| `libheif-plugin-libde265` | `1.21.2-3ubuntu0.6` | resolute-security | universe |
| `libheif-plugin-x265` | `1.21.2-3ubuntu0.6` | resolute-security | universe |
| `libheif1` | `1.21.2-3ubuntu0.6` | resolute-security | main |
| `libhpmud0` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `libhtml-parser-perl` | `3.83-1ubuntu0.1` | resolute-security | main |
| `libhttp-daemon-perl` | `6.16-1ubuntu0.26.04.1` | resolute-security | main |
| `libhttp-date-perl` | `6.06-1ubuntu0.26.04.1` | resolute-security | main |
| `libidn12` | `1.43-2ubuntu0.26.04.1` | resolute-security | main |
| `libinput-bin` | `1.31.1-1ubuntu1.2` | resolute-security | main |
| `libinput-dev` | `1.31.1-1ubuntu1.2` | resolute-security | main |
| `libinput10` | `1.31.1-1ubuntu1.2` | resolute-security | main |
| `libjbig2dec0` | `0.20-1ubuntu0.26.04.1` | resolute-security | main |
| `libjq1` | `1.8.1-4ubuntu2` | resolute-security | main |
| `libjxl-dev` | `0.11.1-6ubuntu4.2` | resolute-security | main |
| `libjxl0.11` | `0.11.1-6ubuntu4.2` | resolute-security | main |
| `libk5crypto3` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkadm5clnt-mit12` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkadm5srv-mit12` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkdb5-10t64` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkf6coreaddons-data` | `6.24.0-0ubuntu1.1` | resolute-security | universe |
| `libkf6coreaddons6` | `6.24.0-0ubuntu1.1` | resolute-security | universe |
| `libkrb5-3` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkrb5-dev` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `libkrb5support0` | `1.22.1-2ubuntu4.1` | resolute-security | main |
| `liblastlog2-2` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `liblcms2-2` | `2.17-1ubuntu0.2` | resolute-security | main |
| `liblcms2-dev` | `2.17-1ubuntu0.2` | resolute-security | main |
| `liblcms2-utils` | `2.17-1ubuntu0.2` | resolute-security | main |
| `libldb2` | `2:2.11.0+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libminizip-dev` | `1:1.3.dfsg+really1.3.1-1ubuntu3.1` | resolute-security | universe |
| `libminizip1t64` | `1:1.3.dfsg+really1.3.1-1ubuntu3.1` | resolute-security | universe |
| `libmlt++7` | `7.36.1-1ubuntu3.1` | resolute-security | universe |
| `libmlt-data` | `7.36.1-1ubuntu3.1` | resolute-security | universe |
| `libmlt7` | `7.36.1-1ubuntu3.1` | resolute-security | universe |
| `libmount-dev` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libmount1` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libmysqlclient-dev` | `8.4.11-0ubuntu0.26.04.1` | resolute-security | main |
| `libmysqlclient24` | `8.4.11-0ubuntu0.26.04.1` | resolute-security | main |
| `libnfs14` | `5.0.2-1ubuntu1.1` | resolute-security | main |
| `libnghttp2-14` | `1.68.0-2ubuntu0.2` | resolute-security | main |
| `libnghttp2-dev` | `1.68.0-2ubuntu0.2` | resolute-security | main |
| `libnm0` | `1.54.3-2ubuntu3.1` | resolute-security | main |
| `libnss-systemd` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libnss3` | `2:3.120-1ubuntu2.1` | resolute-security | main |
| `libnss3-dev` | `2:3.120-1ubuntu2.1` | resolute-security | main |
| `libnss3-tools` | `2:3.120-1ubuntu2.1` | resolute-security | main |
| `libntfs-3g89t64` | `1:2022.10.3-5ubuntu1.1` | resolute-security | main |
| `libnvidia-cfg1-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-common-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-compute-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-decode-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-encode-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-extra-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-fbc1-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libnvidia-gl-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `libopenjp2-7` | `2.5.4-1ubuntu0.1` | resolute-security | main |
| `libopenjp2-7-dev` | `2.5.4-1ubuntu0.1` | resolute-security | main |
| `libpackagekit-glib2-18` | `1.3.4-3ubuntu1.2` | resolute-security | main |
| `libpam-modules` | `1.7.0-5ubuntu3.2` | resolute-security | main |
| `libpam-modules-bin` | `1.7.0-5ubuntu3.2` | resolute-security | main |
| `libpam-runtime` | `1.7.0-5ubuntu3.2` | resolute-security | main |
| `libpam-systemd` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libpam0g` | `1.7.0-5ubuntu3.2` | resolute-security | main |
| `libpcap0.8t64` | `1.10.6-1ubuntu1.1` | resolute-security | main |
| `libperl5.40` | `5.40.1-7ubuntu0.3` | resolute-security | main |
| `libpipewire-0.3-0t64` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `libpipewire-0.3-common` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `libpipewire-0.3-modules` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `libpolkit-agent-1-0` | `127-2ubuntu1.1` | resolute-security | main |
| `libpolkit-gobject-1-0` | `127-2ubuntu1.1` | resolute-security | main |
| `libpoppler-cpp3` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `libpoppler-dev` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `libpoppler-glib8t64` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `libpoppler-private-dev` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `libpoppler-qt6-3t64` | `26.01.0-2ubuntu0.1` | resolute-security | universe |
| `libpoppler156` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `libpq-dev` | `18.6-0ubuntu0.26.04.1` | resolute-security | main |
| `libpq5` | `18.6-0ubuntu0.26.04.1` | resolute-security | main |
| `libpython3.14` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `libpython3.14-dev` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `libpython3.14-minimal` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `libpython3.14-stdlib` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `librabbitmq4` | `0.15.0-1ubuntu0.26.04.2` | resolute-security | main |
| `libraw23t64` | `0.21.5b-1ubuntu1.1` | resolute-security | main |
| `libreoffice-base-core` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-calc` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-common` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-core` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-draw` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-impress` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-kf6` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | universe |
| `libreoffice-math` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-plasma` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | universe |
| `libreoffice-qt6` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | universe |
| `libreoffice-style-breeze` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | universe |
| `libreoffice-style-colibre` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-calc` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-common` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-draw` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-impress` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-math` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-uiconfig-writer` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libreoffice-writer` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libroc0.4` | `0.4.0+dfsg-5ubuntu3.1` | resolute-security | main |
| `libruby3.3` | `3.3.8-2ubuntu3.1` | resolute-security | main |
| `libsane-hpaio` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `libslirp0` | `4.9.1-1ubuntu1.1` | resolute-security | main |
| `libsmartcols1` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libsmbclient0` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libspa-0.2-bluetooth` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `libspa-0.2-modules` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `libsqlite3-0` | `3.46.1-9ubuntu0.3` | resolute-security | main |
| `libsqlite3-dev` | `3.46.1-9ubuntu0.3` | resolute-security | main |
| `libssh-4` | `0.11.3-1ubuntu2.1` | resolute-security | main |
| `libssh2-1-dev` | `1.11.1-1ubuntu0.26.04.4` | resolute-security | main |
| `libssh2-1t64` | `1.11.1-1ubuntu0.26.04.4` | resolute-security | main |
| `libssl-dev` | `3.5.5-1ubuntu3.7` | resolute-security | main |
| `libssl3t64` | `3.5.5-1ubuntu3.7` | resolute-security | main |
| `libsystemd-dev` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libsystemd-shared` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libsystemd0` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libtalloc2` | `2:2.4.3+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libtdb1` | `2:1.4.14+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libtevent0t64` | `2:0.17.1+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libtiff-dev` | `4.7.0-3ubuntu5` | resolute-security | main |
| `libtiff6` | `4.7.0-3ubuntu5` | resolute-security | main |
| `libtiffxx6` | `4.7.0-3ubuntu5` | resolute-security | main |
| `libudev-dev` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libudev1` | `259.5-0ubuntu3.4` | resolute-security | main |
| `libudisks2-0` | `2.10.91-1ubuntu2.1` | resolute-security | main |
| `libunbound8` | `1.24.2-1ubuntu2.2` | resolute-security | main |
| `libuno-cppu3t64` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libuno-cppuhelpergcc3-3t64` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libuno-purpenvhelpergcc3-3t64` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libuno-sal3t64` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libuno-salhelpergcc3-3t64` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `libuuid1` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `libvncclient1` | `0.9.15+dfsg-3ubuntu0.2` | resolute-security | main |
| `libwbclient0` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `libwebsockets-dev` | `4.3.5-3ubuntu1.1` | resolute-security | universe |
| `libwebsockets-evlib-ev` | `4.3.5-3ubuntu1.1` | resolute-security | universe |
| `libwebsockets-evlib-glib` | `4.3.5-3ubuntu1.1` | resolute-security | universe |
| `libwebsockets-evlib-uv` | `4.3.5-3ubuntu1.1` | resolute-security | universe |
| `libwebsockets19t64` | `4.3.5-3ubuntu1.1` | resolute-security | universe |
| `libwinpr3-3` | `3.32.0+dfsg-0ubuntu0.26.04.1` | resolute-security | main |
| `libwww-perl` | `6.81-1ubuntu0.1` | resolute-security | main |
| `libxfont2` | `1:2.0.6-2ubuntu0.2` | resolute-security | main |
| `libxml2-16` | `2.15.2+dfsg-0.1ubuntu0.2` | resolute-security | main |
| `libxml2-dev` | `2.15.2+dfsg-0.1ubuntu0.2` | resolute-security | main |
| `libxml2-utils` | `2.15.2+dfsg-0.1ubuntu0.2` | resolute-security | main |
| `libxpm-dev` | `1:3.5.17-1ubuntu0.26.04.2` | resolute-security | main |
| `libxpm4` | `1:3.5.17-1ubuntu0.26.04.2` | resolute-security | main |
| `linux-generic` | `7.0.0-38.38` | resolute-security | main |
| `linux-headers-7.0.0-31` | `7.0.0-31.31` | resolute-security | main |
| `linux-headers-7.0.0-31-generic` | `7.0.0-31.31` | resolute-security | main |
| `linux-headers-7.0.0-34` | `7.0.0-34.34` | resolute-security | main |
| `linux-headers-7.0.0-34-generic` | `7.0.0-34.34` | resolute-security | main |
| `linux-headers-generic` | `7.0.0-38.38` | resolute-security | main |
| `linux-image-7.0.0-31-generic` | `7.0.0-31.31` | resolute-security | main |
| `linux-image-7.0.0-34-generic` | `7.0.0-34.34` | resolute-security | main |
| `linux-image-generic` | `7.0.0-38.38` | resolute-security | main |
| `linux-libc-dev` | `7.0.0-38.38` | resolute-security | main |
| `linux-main-modules-zfs-7.0.0-31-generic` | `7.0.0-31.31+2` | resolute-security | main |
| `linux-main-modules-zfs-7.0.0-34-generic` | `7.0.0-34.34` | resolute-security | main |
| `linux-modules-7.0.0-31-generic` | `7.0.0-31.31` | resolute-security | main |
| `linux-modules-7.0.0-34-generic` | `7.0.0-34.34` | resolute-security | main |
| `linux-perf` | `7.0.0-38.38` | resolute-security | main |
| `linux-tools-7.0.0-31` | `7.0.0-31.31` | resolute-security | main |
| `linux-tools-7.0.0-31-generic` | `7.0.0-31.31` | resolute-security | main |
| `linux-tools-7.0.0-34` | `7.0.0-34.34` | resolute-security | main |
| `linux-tools-7.0.0-34-generic` | `7.0.0-34.34` | resolute-security | main |
| `linux-tools-common` | `7.0.0-38.38` | resolute-security | main |
| `locales` | `2.43-2ubuntu2.4` | resolute-security | main |
| `login` | `1:4.16.0-2+really2.41.3-3ubuntu2.2` | resolute-security | main |
| `melt` | `7.36.1-1ubuntu3.1` | resolute-security | universe |
| `mount` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `nano` | `8.7.1-1ubuntu0.1` | resolute-security | main |
| `network-manager` | `1.54.3-2ubuntu3.1` | resolute-security | main |
| `network-manager-l10n` | `1.54.3-2ubuntu3.1` | resolute-security | main |
| `ntfs-3g` | `1:2022.10.3-5ubuntu1.1` | resolute-security | main |
| `nvidia-compute-utils-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-dkms-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-driver-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-firmware-580-580.178.04` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-kernel-common-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-kernel-source-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `nvidia-utils-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `openjdk-11-jdk-headless` | `11.0.32.1+1-1ubuntu1~26.04` | resolute-security | universe |
| `openjdk-11-jre-headless` | `11.0.32.1+1-1ubuntu1~26.04` | resolute-security | universe |
| `openjdk-17-jdk-headless` | `17.0.20.1+1-1~26.04` | resolute-security | universe |
| `openjdk-17-jre-headless` | `17.0.20.1+1-1~26.04` | resolute-security | universe |
| `openjdk-25-jdk` | `25.0.4.1+1-1~26.04.4` | resolute-security | main |
| `openjdk-25-jdk-headless` | `25.0.4.1+1-1~26.04.4` | resolute-security | main |
| `openjdk-25-jre` | `25.0.4.1+1-1~26.04.4` | resolute-security | main |
| `openjdk-25-jre-headless` | `25.0.4.1+1-1~26.04.4` | resolute-security | main |
| `openssh-client` | `1:10.2p1-2ubuntu3.6` | resolute-security | main |
| `openssl` | `3.5.5-1ubuntu3.7` | resolute-security | main |
| `openssl-provider-legacy` | `3.5.5-1ubuntu3.7` | resolute-security | main |
| `openvpn` | `2.7.0-1ubuntu1.3` | resolute-security | main |
| `packagekit` | `1.3.4-3ubuntu1.2` | resolute-security | main |
| `perl` | `5.40.1-7ubuntu0.3` | resolute-security | main |
| `perl-base` | `5.40.1-7ubuntu0.3` | resolute-security | main |
| `perl-modules-5.40` | `5.40.1-7ubuntu0.3` | resolute-security | main |
| `pipewire` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `pipewire-alsa` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `pipewire-audio` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `pipewire-bin` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `pipewire-pulse` | `1.6.2-1ubuntu1.2` | resolute-security | main |
| `pkexec` | `127-2ubuntu1.1` | resolute-security | main |
| `polkitd` | `127-2ubuntu1.1` | resolute-security | main |
| `poppler-utils` | `26.01.0-2ubuntu0.1` | resolute-security | main |
| `postgresql-18` | `18.6-0ubuntu0.26.04.1` | resolute-security | main |
| `postgresql-18-jit` | `18.6-0ubuntu0.26.04.1` | resolute-security | main |
| `postgresql-client-18` | `18.6-0ubuntu0.26.04.1` | resolute-security | main |
| `printer-driver-hpcups` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `printer-driver-postscript-hp` | `3.24.4+dfsg0-0ubuntu8.1` | resolute-security | main |
| `python3-cryptography` | `46.0.5-1ubuntu2.2` | resolute-security | main |
| `python3-httplib2` | `0.22.0-1ubuntu0.1` | resolute-security | main |
| `python3-idna` | `3.11-1ubuntu0.1` | resolute-security | main |
| `python3-jwt` | `2.10.1-4ubuntu1.1` | resolute-security | main |
| `python3-ldb` | `2:2.11.0+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `python3-pil` | `12.1.1-2ubuntu1.3` | resolute-security | main |
| `python3-pil.imagetk` | `12.1.1-2ubuntu1.3` | resolute-security | universe |
| `python3-requests` | `2.32.5+dfsg-1ubuntu1.1` | resolute-security | main |
| `python3-samba` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `python3-talloc` | `2:2.4.3+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `python3-tdb` | `2:1.4.14+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `python3-tornado` | `6.5.4-0.1ubuntu0.1` | resolute-security | main |
| `python3-uno` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `python3-urllib3` | `2.6.3-1ubuntu1.1` | resolute-security | main |
| `python3-webob` | `1:1.8.9-1ubuntu0.1` | resolute-security | main |
| `python3.14` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `python3.14-dev` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `python3.14-gdbm` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `python3.14-minimal` | `3.14.4-1ubuntu0.2` | resolute-security | main |
| `python3.14-tk` | `3.14.4-1ubuntu0.2` | resolute-security | universe |
| `python3.14-venv` | `3.14.4-1ubuntu0.2` | resolute-security | universe |
| `qml6-module-org-kde-coreaddons` | `6.24.0-0ubuntu1.1` | resolute-security | universe |
| `remmina` | `1.4.43+dfsg-0ubuntu0.26.04.2` | resolute-security | main |
| `remmina-common` | `1.4.43+dfsg-0ubuntu0.26.04.2` | resolute-security | main |
| `remmina-plugin-rdp` | `1.4.43+dfsg-0ubuntu0.26.04.2` | resolute-security | main |
| `remmina-plugin-secret` | `1.4.43+dfsg-0ubuntu0.26.04.2` | resolute-security | main |
| `remmina-plugin-vnc` | `1.4.43+dfsg-0ubuntu0.26.04.2` | resolute-security | main |
| `rfkill` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `rsync` | `3.4.1+ds1-7ubuntu0.3` | resolute-security | main |
| `rsyslog` | `8.2512.0-1ubuntu4.2` | resolute-security | main |
| `ruby3.3` | `3.3.8-2ubuntu3.1` | resolute-security | main |
| `samba-common` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `samba-common-bin` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `samba-libs` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `sed` | `4.9-2ubuntu1` | resolute-security | main |
| `smbclient` | `2:4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `snapd` | `2.76.3+ubuntu26.04` | resolute-security | main |
| `socat` | `1.8.1.1-1ubuntu0.1` | resolute-security | main |
| `spice-vdagent` | `0.23.0-1ubuntu0.1` | resolute-security | main |
| `sudo` | `1.9.17p2-1ubuntu3.1` | resolute-security | main |
| `sudo-rs` | `0.2.13-0ubuntu1.2` | resolute-security | main |
| `systemd` | `259.5-0ubuntu3.4` | resolute-security | main |
| `systemd-coredump` | `259.5-0ubuntu3.4` | resolute-security | universe |
| `systemd-cryptsetup` | `259.5-0ubuntu3.4` | resolute-security | main |
| `systemd-resolved` | `259.5-0ubuntu3.4` | resolute-security | main |
| `systemd-sysv` | `259.5-0ubuntu3.4` | resolute-security | main |
| `tar` | `1.35+dfsg-4ubuntu0.4` | resolute-security | main |
| `tdb-tools` | `2:1.4.14+samba4.23.6+dfsg-1ubuntu2.2` | resolute-security | main |
| `telnet` | `0.17+2.7-2ubuntu1.1` | resolute-security | main |
| `tzdata` | `2026c-0ubuntu0.26.04.1` | resolute-security | main |
| `tzdata-legacy` | `2026c-0ubuntu0.26.04.1` | resolute-security | main |
| `ubuntu-pro-client` | `37.2ubuntu0.1` | resolute-security | main |
| `ubuntu-pro-client-l10n` | `37.2ubuntu0.1` | resolute-security | main |
| `udev` | `259.5-0ubuntu3.4` | resolute-security | main |
| `udisks2` | `2.10.91-1ubuntu2.1` | resolute-security | main |
| `uno-libs-private` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `update-notifier-common` | `3.207.2` | resolute-security | main |
| `ure` | `4:26.2.5.2-0ubuntu0.26.04.1` | resolute-security | main |
| `util-linux` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `util-linux-extra` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `uuid-dev` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `uuid-runtime` | `2.41.3-3ubuntu2.2` | resolute-security | main |
| `vim` | `2:9.1.2141-1ubuntu4.9` | resolute-security | main |
| `vim-common` | `2:9.1.2141-1ubuntu4.9` | resolute-security | main |
| `vim-runtime` | `2:9.1.2141-1ubuntu4.9` | resolute-security | main |
| `vim-tiny` | `2:9.1.2141-1ubuntu4.9` | resolute-security | main |
| `wget` | `1.25.0-2ubuntu4.4` | resolute-security | main |
| `wireless-regdb` | `2026.05.30-0ubuntu1~26.04.1` | resolute-security | main |
| `xdg-desktop-portal` | `1.21.1+ds-1ubuntu3.1` | resolute-security | main |
| `xserver-xorg-video-nvidia-580` | `580.178.04-0ubuntu0.26.04.1` | resolute-security | restricted |
| `xxd` | `2:9.1.2141-1ubuntu4.9` | resolute-security | main |
| `zlib1g` | `1:1.3.dfsg+really1.3.1-1ubuntu3.1` | resolute-security | main |
| `zlib1g-dev` | `1:1.3.dfsg+really1.3.1-1ubuntu3.1` | resolute-security | main |

</details>

### Ubuntu LTS updates — 197 packages

<details><summary>Show all 197</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `alsa-ucm-conf` ⚠️ | `1.2.15.3-1ubuntu1.5` | resolute-updates | main |
| `apparmor` | `5.0.2-0ubuntu1~26.04.1` | resolute-updates | main |
| `apport` | `2.34.1-0ubuntu0.1` | resolute-updates | main |
| `apport-kde` | `2.34.1-0ubuntu0.1` | resolute-updates | universe |
| `at-spi2-common` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `at-spi2-core` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `base-files` | `14ubuntu6.2` | resolute-updates | main |
| `bluez` | `5.85-4ubuntu0.2` | resolute-updates | main |
| `bluez-cups` | `5.85-4ubuntu0.2` | resolute-updates | main |
| `bluez-obexd` | `5.85-4ubuntu0.2` | resolute-updates | main |
| `breeze` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `breeze-cursor-theme` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `breeze-wallpaper` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `console-setup` | `1.237ubuntu3.1` | resolute-updates | main |
| `console-setup-linux` | `1.237ubuntu3.1` | resolute-updates | main |
| `cups-filters` | `2.0.1-0ubuntu4.1` | resolute-updates | main |
| `cups-filters-core-drivers` | `2.0.1-0ubuntu4.1` | resolute-updates | main |
| `dmidecode` | `3.6-2ubuntu1` | resolute-updates | main |
| `drkonqi` ⚠️ | `6.6.4-0ubuntu1` | resolute-updates | universe |
| `firefox` | `1:1snap1-0ubuntu9.1` | resolute-updates | main |
| `fwupd` | `2.1.1-1ubuntu3.1` | resolute-updates | main |
| `gimp` | `3.2.2-1ubuntu0.26.04.1` | resolute-updates | universe |
| `gimp-data` | `3.2.2-1ubuntu0.26.04.1` | resolute-updates | universe |
| `gir1.2-atk-1.0` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `gir1.2-atspi-2.0` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `gir1.2-gimp-3.0` | `3.2.2-1ubuntu0.26.04.1` | resolute-updates | universe |
| `glycin-loaders` | `2.1.5+ds-0ubuntu0.2` | resolute-updates | main |
| `glycin-thumbnailers` | `2.1.5+ds-0ubuntu0.2` | resolute-updates | main |
| `grub-common` | `2.14-2ubuntu2.1` | resolute-updates | main |
| `grub-pc` | `2.14-2ubuntu2.1` | resolute-updates | main |
| `grub-pc-bin` | `2.14-2ubuntu2.1` | resolute-updates | main |
| `grub2-common` | `2.14-2ubuntu2.1` | resolute-updates | main |
| `gtk-update-icon-cache` | `4.22.4+ds-0ubuntu0.1` | resolute-updates | main |
| `iproute2` | `6.19.0-1ubuntu1.1` | resolute-updates | main |
| `kactivitymanagerd` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kde-config-screenlocker` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kde-config-updates` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kde-spectacle` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kde-style-breeze` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kde-style-breeze-data` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kde-style-breeze-qt5` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kde-style-oxygen-qt6` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kdeplasma-addons-data` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `keyboard-configuration` | `1.237ubuntu3.1` | resolute-updates | main |
| `kglobalacceld` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kinfocenter` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `knighttime` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kscreen` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `ksystemstats` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kwin-addons` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kwin-common` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kwin-data` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kwin-decoration-oxygen` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kwin-style-aurorae` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `kwin-style-breeze` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `kwin-wayland` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `language-pack-en` | `1:26.04+20260818` | resolute-updates | main |
| `language-pack-en-base` | `1:26.04+20260818` | resolute-updates | main |
| `libadwaita-1-0` | `1.9.1-0ubuntu0.1` | resolute-updates | main |
| `libapparmor1` | `5.0.2-0ubuntu1~26.04.1` | resolute-updates | main |
| `libatk-bridge2.0-0t64` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `libatk1.0-0t64` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `libatspi2.0-0t64` | `2.60.4-0ubuntu0.1` | resolute-updates | main |
| `libaudit-common` | `1:4.1.2-1ubuntu0.1` | resolute-updates | main |
| `libaudit1` | `1:4.1.2-1ubuntu0.1` | resolute-updates | main |
| `libbatterycontrol6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libbluetooth3` | `5.85-4ubuntu0.2` | resolute-updates | main |
| `libcalamares3.3` | `3.3.14-0ubuntu25.26.04.1` | resolute-updates | universe |
| `libegl-mesa0` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libflashrom1` | `1.6.0-2ubuntu1.1` | resolute-updates | main |
| `libfprint-2-2` | `1:1.95.1+tod1-0ubuntu2` | resolute-updates | main |
| `libfprint-2-tod1` | `1:1.95.1+tod1-0ubuntu2` | resolute-updates | main |
| `libfwupd3` | `2.1.1-1ubuntu3.1` | resolute-updates | main |
| `libgbm-dev` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libgbm1` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libgimp-3.0-0` | `3.2.2-1ubuntu0.26.04.1` | resolute-updates | universe |
| `libgl1-mesa-dev` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libgl1-mesa-dri` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libglx-mesa0` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `libglycin-2-0` | `2.1.5+ds-0ubuntu0.2` | resolute-updates | main |
| `libgtk-4-1` | `4.22.4+ds-0ubuntu0.1` | resolute-updates | main |
| `libgtk-4-bin` | `4.22.4+ds-0ubuntu0.1` | resolute-updates | main |
| `libgtk-4-common` | `4.22.4+ds-0ubuntu0.1` | resolute-updates | main |
| `libkf6guiaddons-bin` | `6.24.0-0ubuntu1.1` | resolute-updates | universe |
| `libkf6guiaddons-data` | `6.24.0-0ubuntu1.1` | resolute-updates | universe |
| `libkf6guiaddons6` | `6.24.0-0ubuntu1.1` | resolute-updates | universe |
| `libkfontinst6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libkfontinstui6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libkglobalacceld0` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libklipper6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libklookandfeel6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libkmpris6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libknighttime0` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libkquickimageeditor1` | `0.6.0-2ubuntu0.1` | resolute-updates | universe |
| `libkscreenlocker6` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguard-bin` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguard-data` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguardformatter2` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguardsensorfaces2` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguardsensors2` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libksysguardsystemstats2` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libkwin6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libkworkspace6-6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libmalcontent-0-0` | `0.14.0-0ubuntu1.2` | resolute-updates | main |
| `libmalcontent-common` | `0.14.0-0ubuntu1.2` | resolute-updates | main |
| `libnetplan1` | `1.2-1ubuntu5.1` | resolute-updates | main |
| `libnotificationmanager1` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `liboxygenstyle6-6` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `liboxygenstyleconfig6-6` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libpciaccess-dev` | `0.18.1-1ubuntu4.1` | resolute-updates | main |
| `libpciaccess0` | `0.18.1-1ubuntu4.1` | resolute-updates | main |
| `libplasma7` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libplasmaquick7` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libpowerdevilcore2` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `libprocesscore10` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `libtaskmanager6` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `linux-firmware-amd-graphics` | `20260319.git217ca6e4-0ubuntu3.1` | resolute-updates | main |
| `linux-firmware-amd-misc` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-broadcom-wireless` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-intel-graphics` | `20260319.git217ca6e4-0ubuntu2.1` | resolute-updates | main |
| `linux-firmware-intel-misc` | `20260319.git217ca6e4-0ubuntu1.2` | resolute-updates | main |
| `linux-firmware-intel-wireless` | `20260319.git217ca6e4-0ubuntu2.1` | resolute-updates | main |
| `linux-firmware-marvell-prestera` | `20260319.git217ca6e4-0ubuntu1.2` | resolute-updates | main |
| `linux-firmware-marvell-wireless` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-mediatek` | `20260319.git217ca6e4-0ubuntu1.2` | resolute-updates | main |
| `linux-firmware-mellanox-spectrum` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-misc` | `20260319.git217ca6e4-0ubuntu2.2` | resolute-updates | main |
| `linux-firmware-netronome` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-nvidia-graphics` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-qlogic` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-qualcomm-graphics` | `20260319.git217ca6e4-0ubuntu1.1` | resolute-updates | main |
| `linux-firmware-qualcomm-misc` | `20260319.git217ca6e4-0ubuntu2.1` | resolute-updates | main |
| `linux-firmware-qualcomm-wireless` | `20260319.git217ca6e4-0ubuntu1.2` | resolute-updates | main |
| `linux-firmware-realtek` | `20260319.git217ca6e4-0ubuntu1.2` | resolute-updates | main |
| `linux-headers-7.0.0-38` | `7.0.0-38.38` | resolute-updates | main |
| `linux-headers-7.0.0-38-generic` | `7.0.0-38.38` | resolute-updates | main |
| `linux-image-7.0.0-38-generic` | `7.0.0-38.38` | resolute-updates | main |
| `linux-main-modules-zfs-7.0.0-38-generic` | `7.0.0-38.38` | resolute-updates | main |
| `linux-modules-7.0.0-38-generic` | `7.0.0-38.38` | resolute-updates | main |
| `linux-tools-7.0.0-38` | `7.0.0-38.38` | resolute-updates | main |
| `linux-tools-7.0.0-38-generic` | `7.0.0-38.38` | resolute-updates | main |
| `mesa-libgallium` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `mesa-vulkan-drivers` | `26.0.8-1ubuntu0.3` | resolute-updates | main |
| `netplan-generator` | `1.2-1ubuntu5.1` | resolute-updates | main |
| `netplan.io` | `1.2-1ubuntu5.1` | resolute-updates | main |
| `orca` | `50.2-0ubuntu0.1` | resolute-updates | main |
| `plasma-calendar-addons` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-dataengines-addons` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-desktop` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-desktop-data` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-desktoptheme` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-discover` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-discover-backend-fwupd` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-discover-backend-snap` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-discover-common` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-discover-notifier` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-integration` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `plasma-keyboard` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-nm` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-pa` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `plasma-runners-addons` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-session-wayland` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-systemmonitor` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-theme-oxygen` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `plasma-wallpapers-addons` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-welcome` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `plasma-workspace` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma-workspace-data` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `plasma5-integration` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `powerdevil` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `powerdevil-data` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `print-manager` | `6:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `python-apt-common` | `3.1.0ubuntu1.1` | resolute-updates | main |
| `python3-apport` | `2.34.1-0ubuntu0.1` | resolute-updates | main |
| `python3-apt` | `3.1.0ubuntu1.1` | resolute-updates | main |
| `python3-distupgrade` | `1:26.04.25` | resolute-updates | main |
| `python3-netplan` | `1.2-1ubuntu5.1` | resolute-updates | main |
| `python3-problem-report` | `2.34.1-0ubuntu0.1` | resolute-updates | main |
| `python3-software-properties` | `0.120.1` | resolute-updates | main |
| `qml6-module-org-kde-breeze` | `6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `qml6-module-org-kde-guiaddons` | `6.24.0-0ubuntu1.1` | resolute-updates | universe |
| `qml6-module-org-kde-kquickimageeditor` | `0.6.0-2ubuntu0.1` | resolute-updates | universe |
| `qml6-module-org-kde-ksysguard` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `rust-coreutils` | `0.10.0-1ubuntu2~26.04.1` | resolute-updates | main |
| `sddm-theme-breeze` | `4:6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `software-properties-common` | `0.120.1` | resolute-updates | main |
| `software-properties-qt` | `0.120.1` | resolute-updates | universe |
| `systemsettings` | `4:6.6.5-0ubuntu0.1` | resolute-updates | universe |
| `thermald` | `2.5.11-0ubuntu1.1` | resolute-updates | main |
| `ubuntu-kernel-accessories` | `1.570.4` | resolute-updates | main |
| `ubuntu-minimal` | `1.570.4` | resolute-updates | main |
| `ubuntu-release-upgrader-core` | `1:26.04.25` | resolute-updates | main |
| `ubuntu-release-upgrader-qt` | `1:26.04.25` | resolute-updates | universe |
| `ubuntu-standard` | `1.570.4` | resolute-updates | main |
| `xdg-desktop-portal-kde` | `6.6.6-0ubuntu0.1` | resolute-updates | universe |
| `xserver-common` | `2:21.1.22-1ubuntu1.2` | resolute-updates | main |
| `xserver-xorg-core` | `2:21.1.22-1ubuntu1.2` | resolute-updates | main |

</details>

### Ubuntu resolute LTS (base) — 3213 packages

<details><summary>Show all 3213</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `3cpio` | `0.14.0-1ubuntu1` | resolute | main |
| `7zip` | `26.00+dfsg-1` | resolute | universe |
| `aardvark-dns` | `1.16.0-3` | resolute | universe |
| `accountwizard` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `acl` | `2.3.2-2` | resolute | main |
| `adduser` | `3.153ubuntu1` | resolute | main |
| `adwaita-icon-theme` | `50.0-1` | resolute | main |
| `aha` | `0.5.1-3build2` | resolute | universe |
| `akonadi-backend-sqlite` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `akonadi-contacts-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `akonadi-mime-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `akonadi-server` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `akregator` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `alkimia-bin` | `8.2.1-1` | resolute | universe |
| `alkimia-data` | `8.2.1-1` | resolute | universe |
| `alsa-base` | `1.0.25+dfsg-0ubuntu9` | resolute | main |
| `alsa-topology-conf` | `1.2.5.1-3build1` | resolute | main |
| `alsa-utils` | `1.2.15.2-1ubuntu1` | resolute | main |
| `amd64-microcode` | `3.20251202.1ubuntu2` | resolute | main |
| `anacron` | `2.3-45ubuntu1` | resolute | main |
| `ant` | `1.10.15-1build1` | resolute | universe |
| `ant-optional` | `1.10.15-1build1` | resolute | universe |
| `antlr` | `2.7.7+dfsg-14build2` | resolute | universe |
| `appmenu-gtk-module-common` | `25.04-1build1` | resolute | universe |
| `appmenu-gtk3-module` | `25.04-1build1` | resolute | universe |
| `apport-symptoms` | `0.25build1` | resolute | main |
| `appstream` | `1.1.2-1` | resolute | main |
| `apt` | `3.2.0` | resolute | main |
| `apt-config-icons` | `1.1.2-1` | resolute | main |
| `apt-config-icons-hidpi` | `1.1.2-1` | resolute | main |
| `apt-config-icons-large` | `1.1.2-1` | resolute | main |
| `apt-config-icons-large-hidpi` | `1.1.2-1` | resolute | main |
| `apt-transport-https` | `3.2.0` | resolute | universe |
| `aptitude` | `0.8.13-7ubuntu5` | resolute | universe |
| `aptitude-common` | `0.8.13-7ubuntu5` | resolute | universe |
| `ark` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `aspell` | `0.60.8.2-3` | resolute | main |
| `aspell-en` | `2020.12.07-0-1.1build1` | resolute | main |
| `assistant-qt6` | `6.10.2-1` | resolute | universe |
| `audacious` | `4.5.1-1` | resolute | universe |
| `audacious-plugins` | `4.5.1-1build1` | resolute | universe |
| `audacious-plugins-data` | `4.5.1-1build1` | resolute | universe |
| `audacity` | `3.7.7+dfsg-1` | resolute | universe |
| `audacity-data` | `3.7.7+dfsg-1` | resolute | universe |
| `autoconf` | `2.72-3.1ubuntu2` | resolute | main |
| `automake` | `1:1.18.1-3build1` | resolute | main |
| `autotools-dev` | `20240727.1build1` | resolute | main |
| `babeltrace2` | `2.1.2-1build2` | resolute | universe |
| `baloo6` | `6.24.0-0ubuntu1` | resolute | universe |
| `base-passwd` | `3.6.8` | resolute | main |
| `bash` | `5.3-2ubuntu1` | resolute | main |
| `bash-completion` | `1:2.16.0-8build1` | resolute | main |
| `bc` | `1.07.1-4build1` | resolute | main |
| `binutils` | `2.46-3ubuntu2` | resolute | main |
| `binutils-common` | `2.46-3ubuntu2` | resolute | main |
| `binutils-dev` | `2.46-3ubuntu2` | resolute | main |
| `binutils-x86-64-linux-gnu` | `2.46-3ubuntu2` | resolute | main |
| `bluedevil` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `bnd` | `5.0.1-5build1` | resolute | universe |
| `bolt` | `0.9.10-1` | resolute | main |
| `bpfcc-tools` | `0.35.0+ds-1ubuntu2` | resolute | main |
| `bpftrace` | `0.25.0-1ubuntu1` | resolute | main |
| `breeze-gtk-theme` | `6.6.4-0ubuntu1` | resolute | universe |
| `brz` | `3.3.21-1build1` | resolute | universe |
| `btrfs-progs` | `6.17.1-1build1` | resolute | main |
| `buildah` | `1.42.1+ds1-2build1` | resolute | universe |
| `bup` | `0.33.9-1.2build1` | resolute | universe |
| `bup-doc` | `0.33.9-1.2build1` | resolute | universe |
| `busybox-initramfs` | `1:1.37.0-7ubuntu1` | resolute | main |
| `busybox-static` | `1:1.37.0-7ubuntu1` | resolute | main |
| `ca-certificates-java` | `20260311` | resolute | main |
| `calibre` | `9.2.1+ds+~0.10.5-2build1` | resolute | universe |
| `calibre-bin` | `9.2.1+ds+~0.10.5-2build1` | resolute | universe |
| `catatonit` | `0.2.1-2build1` | resolute | universe |
| `catdoc` | `1:0.95-6build1` | resolute | universe |
| `cfortran` | `20210827-1` | resolute | universe |
| `chrony` | `4.8-2ubuntu1` | resolute | main |
| `clamtk` | `6.07-2` | resolute | universe |
| `clinfo` | `3.0.25.02.14-1build1` | resolute | universe |
| `cmake` | `4.2.3-2ubuntu2` | resolute | main |
| `cmake-data` | `4.2.3-2ubuntu2` | resolute | main |
| `colcon` | `0.20.0-1` | resolute | universe |
| `colord` | `1.4.8-3` | resolute | main |
| `colord-data` | `1.4.8-3` | resolute | main |
| `comerr-dev` | `2.1-1.47.2-3ubuntu4` | resolute | main |
| `command-not-found` | `23.04.0build1` | resolute | main |
| `conmon` | `2.1.13+ds1-2` | resolute | universe |
| `containernetworking-plugins` | `1.1.1+ds1-3build2` | resolute | universe |
| `containers-storage` | `1.61.0+ds1-6` | resolute | universe |
| `convertall` | `0.8.0-3build1` | resolute | universe |
| `coreutils` | `9.5-1ubuntu2+0.0.0~ubuntu25` | resolute | main |
| `coreutils-from-uutils` | `0.0.0~ubuntu25` | resolute | main |
| `cpp` | `4:15.2.0-5ubuntu1` | resolute | main |
| `cpp-15` | `15.2.0-16ubuntu1` | resolute | main |
| `cpp-15-x86-64-linux-gnu` | `15.2.0-16ubuntu1` | resolute | main |
| `cpp-16` | `16-20260322-1ubuntu1` | resolute | universe |
| `cpp-16-x86-64-linux-gnu` | `16-20260322-1ubuntu1` | resolute | universe |
| `cpp-x86-64-linux-gnu` | `4:15.2.0-5ubuntu1` | resolute | main |
| `cppcheck` | `2.19.0-3` | resolute | universe |
| `cppzmq-dev` | `4.10.0-1build2` | resolute | universe |
| `cracklib-runtime` | `2.9.6-5.2build3` | resolute | main |
| `criu` | `4.2-1ubuntu2` | resolute | universe |
| `cron` | `3.0pl1-200ubuntu1` | resolute | main |
| `cron-daemon-common` | `3.0pl1-200ubuntu1` | resolute | main |
| `crun` | `1.21-1ubuntu3` | resolute | universe |
| `cryfs` | `1.0.3-1` | resolute | universe |
| `cryptsetup` | `2:2.8.4-1ubuntu4` | resolute | main |
| `cryptsetup-bin` | `2:2.8.4-1ubuntu4` | resolute | main |
| `cryptsetup-initramfs` | `2:2.8.4-1ubuntu4` | resolute | main |
| `cups-browsed` | `2.1.1-0ubuntu3` | resolute | main |
| `cups-pk-helper` | `0.2.6-2.1build1` | resolute | main |
| `dash` | `0.5.12-12ubuntu3` | resolute | main |
| `dbus` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-bin` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-daemon` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-session-bus-common` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-system-bus-common` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-user-session` | `1.16.2-2ubuntu4` | resolute | main |
| `dbus-x11` | `1.16.2-2ubuntu4` | resolute | main |
| `dc` | `1.07.1-4build1` | resolute | main |
| `dconf-gsettings-backend` | `0.49.0-4` | resolute | main |
| `dconf-service` | `0.49.0-4` | resolute | main |
| `debconf` | `1.5.92` | resolute | main |
| `debconf-i18n` | `1.5.92` | resolute | main |
| `debconf-kde-data` | `1.2.0-2ubuntu1` | resolute | universe |
| `debconf-kde-helper` | `1.2.0-2ubuntu1` | resolute | universe |
| `debianutils` | `5.23.2build1` | resolute | main |
| `default-jdk` | `2:1.25-77` | resolute | main |
| `default-jdk-headless` | `2:1.25-77` | resolute | main |
| `default-jre` | `2:1.25-77` | resolute | main |
| `default-jre-headless` | `2:1.25-77` | resolute | main |
| `default-libmysqlclient-dev` | `1.1.1ubuntu2` | resolute | main |
| `designer-qt6` | `6.10.2-1` | resolute | universe |
| `desktop-file-utils` | `0.28-1build1` | resolute | main |
| `dhcpcd-base` | `1:10.3.0-7` | resolute | main |
| `dictionaries-common` | `1.31.4` | resolute | main |
| `distro-info` | `1.15` | resolute | main |
| `dkms` | `3.2.2-1ubuntu1` | resolute | main |
| `dmeventd` | `2:1.02.205-2ubuntu3` | resolute | main |
| `dmsetup` | `2:1.02.205-2ubuntu3` | resolute | main |
| `dns-root-data` | `2025080400build1` | resolute | main |
| `docbook-xml` | `4.5-13build1` | resolute | main |
| `docbook-xsl` | `1.79.2+dfsg-8` | resolute | universe |
| `docutils-common` | `0.22.4+dfsg-1` | resolute | main |
| `dolphin` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `dolphin-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `dolphin-doc` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `dolphin-plugins` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `dosfstools` | `4.2-1.2build1` | resolute | main |
| `dpkg` | `1.23.7ubuntu1` | resolute | main |
| `dpkg-dev` | `1.23.7ubuntu1` | resolute | main |
| `e2fsprogs` | `1.47.2-3ubuntu4` | resolute | main |
| `ed` | `1.22.4-1` | resolute | main |
| `edid-decode` | `0.1~git20220315.cb74358c2896-1.1build1` | resolute | universe |
| `efibootmgr` | `18-4ubuntu1` | resolute | main |
| `elfutils` | `0.194-4` | resolute | main |
| `elisa` | `25.12.3-0ubuntu1` | resolute | universe |
| `emacsen-common` | `3.0.8build1` | resolute | main |
| `enchant-2` | `2.8.2+dfsg1-3build1` | resolute | main |
| `espeak-ng-data` | `1.52.0+dfsg-5build1` | resolute | main |
| `ethtool` | `1:6.19-1` | resolute | main |
| `evolution-data-server-common` | `3.56.2-8` | resolute | main |
| `exfatprogs` | `1.3.2-1` | resolute | main |
| `fakeroot` | `1.37.2-1` | resolute | main |
| `fastfetch` | `2.57.1+dfsg-1ubuntu1` | resolute | universe |
| `ffmpeg` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `ffmpegthumbs` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `fig2dev` | `1:3.2.9a-5` | resolute | universe |
| `file` | `1:5.46-5build2` | resolute | main |
| `filelight` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `findutils` | `4.10.0-3build2` | resolute | main |
| `firmware-sof-signed` | `2025.12.2-1` | resolute | main |
| `flatpak` | `1.16.6-1` | resolute | universe |
| `fontconfig` | `2.17.1-3ubuntu1` | resolute | main |
| `fontconfig-config` | `2.17.1-3ubuntu1` | resolute | main |
| `fonts-dejavu-core` | `2.37-8build1` | resolute | main |
| `fonts-dejavu-extra` | `2.37-8build1` | resolute | main |
| `fonts-dejavu-mono` | `2.37-8build1` | resolute | main |
| `fonts-droid-fallback` | `1:8.1.0r7-1~1.gbp36536bbuild1` | resolute | main |
| `fonts-font-awesome` | `5.0.10+really4.7.0~dfsg-4.1build1` | resolute | main |
| `fonts-freefont-ttf` | `20211204+svn4273-4build1` | resolute | main |
| `fonts-hack` | `3.003-4` | resolute | universe |
| `fonts-ibm-plex` | `6.1.1-1` | resolute | multiverse |
| `fonts-katex` | `0.16.10+~cs6.1.0-5ubuntu1` | resolute | universe |
| `fonts-lato` | `2.015-1build1` | resolute | main |
| `fonts-liberation` | `1:2.1.5-3build1` | resolute | main |
| `fonts-liberation-sans-narrow` | `1:1.07.6-4build1` | resolute | main |
| `fonts-lyx` | `2.5.0-1` | resolute | universe |
| `fonts-noto-cjk` | `1:20240730+repack1-1build1` | resolute | main |
| `fonts-noto-color-emoji` | `2.051-1build1` | resolute | main |
| `fonts-noto-core` | `20201225-2build1` | resolute | main |
| `fonts-noto-hinted` | `20201225-2build1` | resolute | universe |
| `fonts-noto-mono` | `20201225-2build1` | resolute | main |
| `fonts-noto-ui-core` | `20201225-2build1` | resolute | main |
| `fonts-noto-unhinted` | `20201225-2build1` | resolute | universe |
| `fonts-tuffy` | `20120614-3` | resolute | universe |
| `fonts-ubuntu` | `0.869+git20240321-0ubuntu2` | resolute | main |
| `fonts-urw-base35` | `20200910-8build1` | resolute | main |
| `foomatic-db-compressed-ppds` | `20250819-1build1` | resolute | main |
| `fprintd` | `1.94.5-4` | resolute | main |
| `frameworkintegration6` | `6.24.0-0ubuntu1` | resolute | universe |
| `freeglut3-dev` | `3.4.0-6` | resolute | universe |
| `frei0r-plugins` | `2.5.5-1ubuntu1` | resolute | universe |
| `friendly-recovery` | `0.2.42build1` | resolute | main |
| `ftp` | `20260211-1` | resolute | main |
| `fuse-overlayfs` | `1.14-1build2` | resolute | universe |
| `fuse3` | `3.18.2-1` | resolute | main |
| `fwupd-signed` | `1.55+1.7-1` | resolute | main |
| `fzf` | `0.67.0-1` | resolute | universe |
| `g++` | `4:15.2.0-5ubuntu1` | resolute | main |
| `g++-15` | `15.2.0-16ubuntu1` | resolute | main |
| `g++-15-x86-64-linux-gnu` | `15.2.0-16ubuntu1` | resolute | main |
| `g++-x86-64-linux-gnu` | `4:15.2.0-5ubuntu1` | resolute | main |
| `gcc` | `4:15.2.0-5ubuntu1` | resolute | main |
| `gcc-15` | `15.2.0-16ubuntu1` | resolute | main |
| `gcc-15-base` | `15.2.0-16ubuntu1` | resolute | main |
| `gcc-15-x86-64-linux-gnu` | `15.2.0-16ubuntu1` | resolute | main |
| `gcc-16` | `16-20260322-1ubuntu1` | resolute | universe |
| `gcc-16-base` | `16-20260322-1ubuntu1` | resolute | main |
| `gcc-16-x86-64-linux-gnu` | `16-20260322-1ubuntu1` | resolute | universe |
| `gcc-x86-64-linux-gnu` | `4:15.2.0-5ubuntu1` | resolute | main |
| `gdal-bin` | `3.12.2+dfsg-1build2` | resolute | universe |
| `gdal-data` | `3.12.2+dfsg-1build2` | resolute | universe |
| `gdal-plugins` | `3.12.2+dfsg-1build2` | resolute | universe |
| `gdb` | `17.1-2ubuntu1` | resolute | main |
| `genisoimage` | `9:1.1.11-5` | resolute | main |
| `geoclue-2.0` | `2.7.2-2ubuntu3` | resolute | main |
| `gettext-base` | `0.23.2-1` | resolute | main |
| `gfortran` | `4:15.2.0-5ubuntu1` | resolute | main |
| `gfortran-15` | `15.2.0-16ubuntu1` | resolute | main |
| `gfortran-15-x86-64-linux-gnu` | `15.2.0-16ubuntu1` | resolute | main |
| `gfortran-16` | `16-20260322-1ubuntu1` | resolute | universe |
| `gfortran-16-x86-64-linux-gnu` | `16-20260322-1ubuntu1` | resolute | universe |
| `gfortran-x86-64-linux-gnu` | `4:15.2.0-5ubuntu1` | resolute | main |
| `ghostwriter` | `25.12.3-0ubuntu1` | resolute | universe |
| `ghp-import` | `2.1.0-3build1` | resolute | universe |
| `gimp-help-common` | `3.0.2-2` | resolute | universe |
| `gimp-help-en` | `3.0.2-2` | resolute | universe |
| `gir1.2-babl-0.1` | `1:0.1.124-1` | resolute | universe |
| `gir1.2-freedesktop` | `1.86.0-6build1` | resolute | main |
| `gir1.2-gdkpixbuf-2.0` | `2.44.5+dfsg-4ubuntu1` | resolute | main |
| `gir1.2-gegl-0.4` | `1:0.4.70-1` | resolute | universe |
| `gir1.2-gexiv2-0.10` | `0.14.6-2` | resolute | main |
| `gir1.2-gstreamer-1.0` | `1.28.2-1` | resolute | main |
| `gir1.2-gtk-3.0` | `3.24.52-0ubuntu1` | resolute | main |
| `gir1.2-gudev-1.0` | `1:238-7build1` | resolute | main |
| `gir1.2-harfbuzz-0.0` | `12.3.2-2` | resolute | main |
| `gir1.2-ibus-1.0` | `1.5.34~rc2-1` | resolute | main |
| `gir1.2-notify-0.7` | `0.8.8-1` | resolute | main |
| `gir1.2-pango-1.0` | `1.57.0-1` | resolute | main |
| `gir1.2-secret-1` | `0.21.7-2build1` | resolute | main |
| `gir1.2-vte-2.91` | `0.84.0-2` | resolute | main |
| `gir1.2-wnck-3.0` | `43.3-1build1` | resolute | main |
| `gir1.2-xapp-1.0` | `3.2.2-1` | resolute | universe |
| `git` | `1:2.53.0-1ubuntu1` | resolute | main |
| `git-man` | `1:2.53.0-1ubuntu1` | resolute | main |
| `glib-networking` | `2.80.1-1build2` | resolute | main |
| `glib-networking-common` | `2.80.1-1build2` | resolute | main |
| `glib-networking-services` | `2.80.1-1build2` | resolute | main |
| `glslang-dev` | `16.2.0-2` | resolute | universe |
| `glslc` | `2026.1-1` | resolute | universe |
| `gnome-themes-extra-data` | `3.28-5` | resolute | main |
| `gnustep-base-common` | `1.31.1-4ubuntu2` | resolute | universe |
| `gnustep-base-runtime` | `1.31.1-4ubuntu2` | resolute | universe |
| `gnustep-common` | `2.9.3-7` | resolute | universe |
| `gnustep-multiarch` | `2.9.3-7` | resolute | universe |
| `go-mtpfs` | `1.0.0+git20200111.42254b1-1build3` | resolute | universe |
| `gocryptfs` | `2.6.1-1` | resolute | universe |
| `golang-github-containers-common` | `0.66.0+ds2-3` | resolute | universe |
| `golang-github-containers-image` | `5.38.0+ds2-2` | resolute | universe |
| `googletest` | `1.17.0-1build1` | resolute | universe |
| `gradle` | `4.4.1-22ubuntu1` | resolute | universe |
| `graphviz` | `14.1.2-1ubuntu1` | resolute | universe |
| `grep` | `3.12-1` | resolute | main |
| `groff-base` | `1.23.0-10` | resolute | main |
| `groovy` | `2.4.21-10build1` | resolute | universe |
| `grub-efi-amd64-bin` | `2.14-2ubuntu1` | resolute | main |
| `grub-efi-amd64-signed` | `1.215+2.14-2ubuntu1` | resolute | main |
| `grub-efi-amd64-unsigned` | `2.14-2ubuntu1` | resolute | main |
| `grub-gfxpayload-lists` | `0.7build3` | resolute | main |
| `grub-theme-breeze` | `6.6.4-0ubuntu1` | resolute | universe |
| `gsettings-desktop-schemas` | `50.0-1ubuntu2` | resolute | main |
| `gstreamer1.0-libav` | `1.28.2-1` | resolute | universe |
| `gwenview` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `gwenview-doc` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `haruna` | `1.7.1-1ubuntu3` | resolute | universe |
| `hdf5-helpers` | `1.14.6+repack-2` | resolute | universe |
| `hdparm` | `9.65+ds-1.1build1` | resolute | main |
| `hicolor-icon-theme` | `0.18-2build1` | resolute | main |
| `hostname` | `3.25build1` | resolute | main |
| `htop` | `3.4.1-5build2` | resolute | main |
| `hunspell-en-us` | `1:2020.12.07-4build1` | resolute | main |
| `hwdata` | `0.394-1build1` | resolute | main |
| `hyphen-en-ca` | `0.10ubuntu3` | resolute | main |
| `hyphen-fi` | `0.10ubuntu3` | resolute | main |
| `hyphen-ga` | `0.10ubuntu3` | resolute | main |
| `hyphen-id` | `1:25.2.3-1build1` | resolute | main |
| `i965-va-driver` | `2.4.1+dfsg1-2build1` | resolute | universe |
| `ibus-data` | `1.5.34~rc2-1` | resolute | main |
| `ibus-gtk3` | `1.5.34~rc2-1` | resolute | main |
| `ibus-gtk4` | `1.5.34~rc2-1` | resolute | main |
| `ibverbs-providers` | `61.0-2ubuntu3` | resolute | main |
| `icu-devtools` | `78.2-2ubuntu1` | resolute | main |
| `ieee-data` | `20240722build1` | resolute | main |
| `iio-sensor-proxy` | `3.8-1` | resolute | main |
| `im-config` | `0.62` | resolute | main |
| `imagemagick` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `imagemagick-7-common` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `imagemagick-7.q16` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `info` | `7.2-5ubuntu2` | resolute | main |
| `init` | `1.69` | resolute | main |
| `init-system-helpers` | `1.69` | resolute | main |
| `initramfs-tools` | `0.151ubuntu1` | resolute | main |
| `initramfs-tools-bin` | `0.151ubuntu1` | resolute | main |
| `initramfs-tools-core` | `0.151ubuntu1` | resolute | main |
| `inkscape` | `1.4.3-0ubuntu2` | resolute | universe |
| `inputattach` | `1:1.8.1-2build2` | resolute | main |
| `install-info` | `7.2-5ubuntu2` | resolute | main |
| `intel-media-va-driver` | `26.1.2+dfsg1-1` | resolute | universe |
| `intel-microcode` | `3.20260210.1ubuntu2` | resolute | main |
| `inxi` | `3.3.40-1-1` | resolute | universe |
| `ipp-usb` | `0.9.31-1` | resolute | main |
| `iptables` | `1.8.11-2ubuntu3` | resolute | main |
| `iputils-ping` | `3:20250605-1ubuntu1` | resolute | main |
| `iputils-tracepath` | `3:20250605-1ubuntu1` | resolute | main |
| `isa-support` | `27ubuntu2` | resolute | main |
| `iso-codes` | `4.20.1-1` | resolute | main |
| `isoimagewriter` | `25.12.3-0ubuntu1` | resolute | universe |
| `isympy-common` | `1.14.0-2` | resolute | universe |
| `isympy3` | `1.14.0-2` | resolute | universe |
| `iucode-tool` | `2.3.1-3build2` | resolute | main |
| `ivy` | `2.5.3-1` | resolute | universe |
| `iw` | `6.17-1` | resolute | main |
| `java-common` | `0.77` | resolute | main |
| `java-wrappers` | `0.5build1` | resolute | universe |
| `javascript-common` | `12+nmu1build1` | resolute | main |
| `jfsutils` | `1.1.15-7` | resolute | main |
| `junit4` | `4.13.2-5ubuntu1` | resolute | universe |
| `kaccounts-providers` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kaddressbook` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kaddressbook-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kalendarac` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kamera` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kate` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kate-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kbd` | `2.7.1-2ubuntu2` | resolute | main |
| `kcalc` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kcharselect` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kde-cli-tools` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kde-cli-tools-data` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kde-config-gtk-style` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kde-config-gtk-style-preview` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kde-config-plymouth` | `6.6.4-0ubuntu1` | resolute | universe |
| `kde-config-sddm` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kde-config-tablet` | `6.6.4-0ubuntu1` | resolute | universe |
| `kde-inotify-survey` | `25.12.3-0ubuntu1` | resolute | universe |
| `kded5` | `5.116.0-1ubuntu1` | resolute | universe |
| `kded6` | `6.24.0-0ubuntu1` | resolute | universe |
| `kdegames-card-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdegames-mahjongg-data-kf6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdegraphics-thumbnailers` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdenetwork-filesharing` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdepim-addons` | `25.12.3-0ubuntu1` | resolute | universe |
| `kdepim-runtime` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdepim-themeeditors` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdialog` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kdoctools6` | `6.24.0-0ubuntu1` | resolute | universe |
| `keditbookmarks` | `25.12.3-0ubuntu1` | resolute | universe |
| `keyutils` | `1.6.3-6ubuntu3` | resolute | main |
| `kf6-breeze-icon-theme` | `6.24.0-0ubuntu1` | resolute | universe |
| `kfind` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kgamma` | `6.6.4-0ubuntu1` | resolute | universe |
| `khelpcenter` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `khelpcenter-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kimageformat6-plugins` | `6.24.0-0ubuntu1` | resolute | universe |
| `kio` | `5.116.0-2` | resolute | universe |
| `kio-admin` | `25.12.3-0ubuntu1` | resolute | universe |
| `kio-audiocd` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kio-extras` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kio-extras-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kio-fuse` | `5.1.1-1` | resolute | universe |
| `kio-ldap` | `25.12.3-0ubuntu1` | resolute | universe |
| `kio6` | `6.24.0-0ubuntu1` | resolute | universe |
| `kirigami-addons-data` | `1.11.0-2ubuntu2` | resolute | universe |
| `klibc-utils` | `2.0.14-1ubuntu2` | resolute | main |
| `kmahjongg` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kmail` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kmailtransport-plugins` | `25.12.3-0ubuntu1` | resolute | universe |
| `kmenuedit` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kmines` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kmod` | `34.2-2ubuntu2` | resolute | main |
| `kmymoney` | `5.2.2-1` | resolute | universe |
| `kmymoney-common` | `5.2.2-1` | resolute | universe |
| `kolourpaint` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `konqueror` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `konqueror-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `konqueror-doc` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `konsole` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `konsole-kpart` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kontact` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `korganizer` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kpackagelauncherqml` | `5.116.0-1ubuntu1` | resolute | universe |
| `kpackagetool5` | `5.116.0-1ubuntu1` | resolute | universe |
| `kpackagetool6` | `6.24.0-0ubuntu1` | resolute | universe |
| `kpat` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `ksshaskpass` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `ksudoku` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `ksystemlog` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kubuntu-notification-helper` | `26.04ubuntu6` | resolute | universe |
| `kubuntu-settings-desktop` | `1:26.04.13` | resolute | universe |
| `kubuntu-wallpapers` | `26.04.3` | resolute | universe |
| `kunifiedpush` | `25.12.3-0ubuntu1` | resolute | universe |
| `kup-backup` | `0.10.0-1ubuntu2` | resolute | universe |
| `kwallet6` | `6.24.0-0ubuntu1` | resolute | universe |
| `kwalletmanager` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `kwayland-integration` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kwayland5-data` | `4:5.116.0-0ubuntu7` | resolute | universe |
| `kwayland6-data` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `kwrited` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `lame` | `3.101~svn6525+dfsg-2` | resolute | universe |
| `language-selector-common` | `0.228build1` | resolute | main |
| `laptop-detect` | `0.16+nmu1build1` | resolute | main |
| `layer-shell-qt` | `6.6.4-0ubuntu1` | resolute | universe |
| `less` | `668-1build1` | resolute | main |
| `lib2geom1.4.0` | `1.4-5` | resolute | universe |
| `libaa1` | `1.4p5-51.1build1` | resolute | main |
| `libaacs0` | `0.11.1-4build1` | resolute | universe |
| `libabsl20260107` | `20260107.0-4` | resolute | main |
| `libabw-0.1-1` | `0.1.3-1build6` | resolute | main |
| `libaccounts-glib0` | `1.27-3` | resolute | universe |
| `libaccounts-qt6-1` | `1.17-4ubuntu2` | resolute | universe |
| `libacl1` | `2.3.2-2` | resolute | main |
| `libacl1-dev` | `2.3.2-2` | resolute | main |
| `libadios2-mpi-auxiliary-2.11` | `2.11.0+dfsg1-6build1` | resolute | universe |
| `libadios2-mpi-c++-2.11` | `2.11.0+dfsg1-6build1` | resolute | universe |
| `libadios2-mpi-c-2.11` | `2.11.0+dfsg1-6build1` | resolute | universe |
| `libadios2-mpi-core-2.11` | `2.11.0+dfsg1-6build1` | resolute | universe |
| `libadios2-mpi-plugins` | `2.11.0+dfsg1-6build1` | resolute | universe |
| `libaec-dev` | `1.1.5-1` | resolute | universe |
| `libaec0` | `1.1.5-1` | resolute | universe |
| `libaio1t64` | `0.3.113-8build1` | resolute | main |
| `libakonadi-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libakonadicalendar-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libakonadisearch-bin` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libakonadisearch-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libakonadisearch-plugins` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libalgorithm-diff-perl` | `1.201-1` | resolute | main |
| `libalgorithm-diff-xs-perl` | `0.04-9` | resolute | main |
| `libalgorithm-merge-perl` | `0.08-5` | resolute | main |
| `libalkimia6-8` | `8.2.1-1` | resolute | universe |
| `libamd-comgr3` | `7.1.1+dfsg-0ubuntu1` | resolute | universe |
| `libamd3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libamdhip64-7` | `7.1.0-0ubuntu2` | resolute | universe |
| `libantlr-java` | `2.7.7+dfsg-14build2` | resolute | universe |
| `libao-common` | `1.2.2+20180113-1.2ubuntu2` | resolute | main |
| `libao4` | `1.2.2+20180113-1.2ubuntu2` | resolute | main |
| `libaopalliance-java` | `20070526-7` | resolute | universe |
| `libapache-pom-java` | `33-2build1` | resolute | universe |
| `libappimage1.0abi1t64` | `1.0.4-5-7build1` | resolute | universe |
| `libappmenu-gtk3-parser0` | `25.04-1build1` | resolute | universe |
| `libappstream5` | `1.1.2-1` | resolute | main |
| `libappstreamqt3` | `1.1.2-1` | resolute | universe |
| `libapr1t64` | `1.7.6-3` | resolute | main |
| `libapt-pkg7.0` | `3.2.0` | resolute | main |
| `libaqbanking-data` | `6.9.1-1` | resolute | universe |
| `libaqbanking44` | `6.9.1-1` | resolute | universe |
| `libargon2-1` | `0~20190702+dfsg-5` | resolute | main |
| `libaribb24-0t64` | `1.0.3-3` | resolute | universe |
| `libarmadillo-dev` | `1:15.2.1+dfsg-2` | resolute | universe |
| `libarmadillo15` | `1:15.2.1+dfsg-2` | resolute | universe |
| `libarpack2-dev` | `3.9.1-6build1` | resolute | universe |
| `libarpack2t64` | `3.9.1-6build1` | resolute | universe |
| `libasan8` | `16-20260322-1ubuntu1` | resolute | main |
| `libasm-java` | `9.9.1-1` | resolute | universe |
| `libasm1t64` | `0.194-4` | resolute | main |
| `libasound2-plugins` | `1.2.12-2build1` | resolute | universe |
| `libaspell15` | `0.60.8.2-3` | resolute | main |
| `libass9` | `1:0.17.4-2` | resolute | universe |
| `libassimp-dev` | `6.0.4+ds-1build1` | resolute | universe |
| `libassimp6` | `6.0.4+ds-1build1` | resolute | universe |
| `libassuan-dev` | `3.0.2-2build1` | resolute | main |
| `libassuan9` | `3.0.2-2build1` | resolute | main |
| `libastro1` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libasyncns0` | `0.8-7` | resolute | main |
| `libatasmart4` | `0.19-6` | resolute | main |
| `libatinject-jsr330-api-java` | `1.0+ds1-6build1` | resolute | universe |
| `libatk-wrapper-java` | `0.44.0-1` | resolute | main |
| `libatk-wrapper-java-jni` | `0.44.0-1` | resolute | main |
| `libatkmm-1.6-1v5` | `2.28.4-2` | resolute | main |
| `libatomic1` | `16-20260322-1ubuntu1` | resolute | main |
| `libaudcore5t64` | `4.5.1-1` | resolute | universe |
| `libaudgui6` | `4.5.1-1` | resolute | universe |
| `libaudqt3` | `4.5.1-1` | resolute | universe |
| `libaudtag3t64` | `4.5.1-1` | resolute | universe |
| `libavc1394-0` | `0.5.4-5build4` | resolute | main |
| `libavcodec-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavcodec62` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavdevice-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavdevice62` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavfilter-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavfilter11` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavformat-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavformat62` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavif-dev` | `1.3.0-1ubuntu4` | resolute | universe |
| `libavif16` | `1.3.0-1ubuntu4` | resolute | universe |
| `libavtp0` | `0.2.0-2build1` | resolute | universe |
| `libavutil-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libavutil60` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libayatana-appindicator3-1` | `0.5.94-1build1` | resolute | main |
| `libayatana-ido3-0.4-0` | `0.10.4-1build1` | resolute | main |
| `libayatana-indicator3-7` | `0.9.4-2` | resolute | main |
| `libb2-1` | `0.98.1-1.1build2` | resolute | universe |
| `libbabeltrace1` | `1.5.11-5build1` | resolute | main |
| `libbabeltrace2-0` | `2.1.2-1build2` | resolute | universe |
| `libbabeltrace2-python-plugin-provider` | `2.1.2-1build2` | resolute | universe |
| `libbabl-0.1-0` | `1:0.1.124-1` | resolute | universe |
| `libbaloowidgets-bin` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libbcel-java` | `6.12.0-0ubuntu1` | resolute | universe |
| `libbcpg-java` | `1.80-3` | resolute | universe |
| `libbcprov-java` | `1.80-3` | resolute | universe |
| `libbdplus0` | `0.2.0-4build1` | resolute | universe |
| `libbenchmark-dev` | `1.9.1-1build1` | resolute | universe |
| `libbenchmark1.9.1` | `1.9.1-1build1` | resolute | universe |
| `libbindex-java` | `2.2+svn101-4build1` | resolute | universe |
| `libbinutils` | `2.46-3ubuntu2` | resolute | main |
| `libblas-dev` | `3.12.1-7ubuntu1` | resolute | main |
| `libblas3` | `3.12.1-7ubuntu1` | resolute | main |
| `libblockdev-crypto3` | `3.4.0-1` | resolute | main |
| `libblockdev-fs3` | `3.4.0-1` | resolute | main |
| `libblockdev-loop3` | `3.4.0-1` | resolute | main |
| `libblockdev-mdraid3` | `3.4.0-1` | resolute | main |
| `libblockdev-nvme3` | `3.4.0-1` | resolute | main |
| `libblockdev-part3` | `3.4.0-1` | resolute | main |
| `libblockdev-smart3` | `3.4.0-1` | resolute | main |
| `libblockdev-swap3` | `3.4.0-1` | resolute | main |
| `libblockdev-utils3` | `3.4.0-1` | resolute | main |
| `libblockdev3` | `3.4.0-1` | resolute | main |
| `libblosc-dev` | `1.21.5+ds-2` | resolute | universe |
| `libblosc1` | `1.21.5+ds-2` | resolute | universe |
| `libblosc2-7` | `2.23.0+ds-1` | resolute | universe |
| `libbluray3` | `1:1.4.1-1` | resolute | universe |
| `libboost-all-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-atomic-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-atomic1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-atomic1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-charconv1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-charconv1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-chrono-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-chrono1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-chrono1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-container-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-container1.90-dev` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-container1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-context-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-context1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-context1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-coroutine-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-coroutine1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-coroutine1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-date-time-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-date-time1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-date-time1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-dev` | `1.90.0.1ubuntu3` | resolute | main |
| `libboost-exception-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-exception1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-fiber-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-fiber1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-fiber1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-filesystem-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-filesystem1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-filesystem1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-graph-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-graph-parallel-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-graph-parallel1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-graph-parallel1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-graph1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-graph1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-iostreams-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-iostreams1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-iostreams1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-json-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-json1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-json1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-locale-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-locale1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-locale1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-log-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-log1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-log1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-math-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-math1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-math1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-mpi-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-mpi-python-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-mpi-python1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-mpi-python1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-mpi1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-mpi1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-nowide-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-nowide1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-nowide1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-numpy-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-numpy1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-numpy1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-process-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-process1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-process1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-program-options-dev` | `1.90.0.1ubuntu3` | resolute | main |
| `libboost-program-options1.90-dev` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-program-options1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-python-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-python1.83.0` | `1.83.0-5ubuntu5` | resolute | universe |
| `libboost-python1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-python1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-random-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-random1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-random1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-regex-dev` | `1.90.0.1ubuntu3` | resolute | main |
| `libboost-regex1.90-dev` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-regex1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-serialization-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-serialization1.88.0` | `1.88.0-1.4ubuntu4` | resolute | universe |
| `libboost-serialization1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-serialization1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-stacktrace-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-stacktrace1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-stacktrace1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-test-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-test1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-test1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-thread-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-thread1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-thread1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-timer-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-timer1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-timer1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-tools-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-type-erasure-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-type-erasure1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-type-erasure1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-url-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-url1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-url1.90.0` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost-wave-dev` | `1.90.0.1ubuntu3` | resolute | universe |
| `libboost-wave1.90-dev` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost-wave1.90.0` | `1.90.0-6ubuntu1` | resolute | universe |
| `libboost1.90-dev` | `1.90.0-6ubuntu1` | resolute | main |
| `libboost1.90-tools-dev` | `1.90.0-6ubuntu1` | resolute | main |
| `libbpf1` | `1:1.6.3-1ubuntu1` | resolute | main |
| `libbpfcc` | `0.35.0+ds-1ubuntu2` | resolute | main |
| `libbrlapi0.8` | `6.7-1ubuntu6` | resolute | main |
| `libbrotli-dev` | `1.2.0-3build1` | resolute | main |
| `libbrotli1` | `1.2.0-3build1` | resolute | main |
| `libbs2b0` | `3.1.0+dfsg-8build1` | resolute | universe |
| `libbsd-dev` | `0.12.2-2build2` | resolute | main |
| `libbsd0` | `0.12.2-2build2` | resolute | main |
| `libbsf-java` | `1:2.4.0-8build1` | resolute | universe |
| `libbsh-java` | `2.0b4-20build1` | resolute | universe |
| `libbtf2` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libbullet-dev` | `3.24+dfsg-5` | resolute | universe |
| `libbullet3.24t64` | `3.24+dfsg-5` | resolute | universe |
| `libburn4t64` | `1.5.6-1.2build1` | resolute | main |
| `libbytesize-common` | `2.12-1` | resolute | main |
| `libbytesize1` | `2.12-1` | resolute | main |
| `libcaf-openmpi-3t64` | `2.10.3-4` | resolute | universe |
| `libcairo-gobject-perl` | `1.005-4build4` | resolute | main |
| `libcairo-gobject2` | `1.18.4-3` | resolute | main |
| `libcairo-perl` | `1.109-5build1` | resolute | main |
| `libcairo-script-interpreter2` | `1.18.4-3` | resolute | main |
| `libcairo2` | `1.18.4-3` | resolute | main |
| `libcairomm-1.0-1v5` | `1.14.5-3` | resolute | main |
| `libcalendarsupport-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libcamd3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libcamel-1.2-64t64` | `3.56.2-8` | resolute | main |
| `libcanberra-pulse` | `0.30-18ubuntu3` | resolute | main |
| `libcanberra0` | `0.30-18ubuntu3` | resolute | main |
| `libcap-dev` | `1:2.75-10ubuntu2` | resolute | main |
| `libcap-ng0` | `0.8.5-4build5` | resolute | main |
| `libcap2` | `1:2.75-10ubuntu2` | resolute | main |
| `libcap2-bin` | `1:2.75-10ubuntu2` | resolute | main |
| `libcapi20-3t64` | `1:3.27-3.2build1` | resolute | universe |
| `libcbor0.10` | `0.10.2-2ubuntu3` | resolute | main |
| `libcc1-0` | `16-20260322-1ubuntu1` | resolute | main |
| `libccd-dev` | `2.1-3` | resolute | universe |
| `libccd2` | `2.1-3` | resolute | universe |
| `libccolamd3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libcddb2` | `1.3.2-7.1fakesync1build1` | resolute | universe |
| `libcdi-api-java` | `1.2-4build1` | resolute | universe |
| `libcdio-cdda2t64` | `10.2+2.0.2-2` | resolute | main |
| `libcdio-paranoia2t64` | `10.2+2.0.2-2` | resolute | main |
| `libcdio19t64` | `2.2.0-4build1` | resolute | main |
| `libcdparanoia0` | `3.10.2+debian-14ubuntu2` | resolute | main |
| `libcdr-0.1-1` | `0.1.7-1build4` | resolute | main |
| `libcdt6` | `14.1.2-1ubuntu1` | resolute | universe |
| `libceres-dev` | `2.2.0+dfsg-4.1ubuntu3` | resolute | universe |
| `libceres4t64` | `2.2.0+dfsg-4.1ubuntu3` | resolute | universe |
| `libcfitsio-dev` | `4.6.3-1` | resolute | universe |
| `libcfitsio-doc` | `4.6.3-1` | resolute | universe |
| `libcfitsio10t64` | `4.6.3-1` | resolute | universe |
| `libcgraph8` | `14.1.2-1ubuntu1` | resolute | universe |
| `libcharls2` | `2.4.2-2build3` | resolute | universe |
| `libchm1` | `2:0.40a-9` | resolute | universe |
| `libcholmod5` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libchromaprint1` | `1.6.0-2build1` | resolute | universe |
| `libcjson1` | `1.7.19-2` | resolute | universe |
| `libclang-cpp21` | `1:21.1.8-6ubuntu1` | resolute | main |
| `libclang1-21` | `1:21.1.8-6ubuntu1` | resolute | main |
| `libcli11-dev` | `2.6.1+ds-1` | resolute | universe |
| `libclone-perl` | `0.47-1` | resolute | main |
| `libclucene-contribs1t64` | `2.3.3.4+dfsg-1.3` | resolute | main |
| `libclucene-core1t64` | `2.3.3.4+dfsg-1.3` | resolute | main |
| `libcmark-gfm-extensions0.29.0.gfm.13` | `0.29.0.gfm.13-7` | resolute | universe |
| `libcmark-gfm0.29.0.gfm.13` | `0.29.0.gfm.13-7` | resolute | universe |
| `libcmark0.30.2` | `0.30.2-6build2` | resolute | universe |
| `libcoarrays-dev` | `2.10.3-4` | resolute | universe |
| `libcoarrays-openmpi-dev` | `2.10.3-4` | resolute | universe |
| `libcodec2-1.2` | `1.2.0-4` | resolute | universe |
| `libcolamd3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | main |
| `libcolord2` | `1.4.8-3` | resolute | main |
| `libcolorhug2` | `1.4.8-3` | resolute | main |
| `libcom-err2` | `1.47.2-3ubuntu4` | resolute | main |
| `libcommon-sense-perl` | `3.75-3build5` | resolute | main |
| `libcommons-cli-java` | `1.6.0-1` | resolute | universe |
| `libcommons-codec-java` | `1.18.0-1` | resolute | universe |
| `libcommons-collections3-java` | `3.2.2-3` | resolute | universe |
| `libcommons-compress-java` | `1.27.1-2` | resolute | universe |
| `libcommons-io-java` | `2.19.0-1` | resolute | universe |
| `libcommons-lang-java` | `2.6-12` | resolute | universe |
| `libcommons-lang3-java` | `3.17.0-2` | resolute | universe |
| `libcommons-logging-java` | `1.3.0-1ubuntu1` | resolute | universe |
| `libcommons-parent-java` | `56-1build1` | resolute | universe |
| `libcompel1` | `4.2-1ubuntu2` | resolute | universe |
| `libcomposefs1` | `1.0.8-3` | resolute | universe |
| `libconsole-bridge-dev` | `1.0.1+dfsg2-4` | resolute | universe |
| `libconsole-bridge1.0` | `1.0.1+dfsg2-4` | resolute | universe |
| `libcpuinfo0` | `0.0~git20250905.877328f-1` | resolute | universe |
| `libcrack2` | `2.9.6-5.2build3` | resolute | main |
| `libcriu2` | `4.2-1ubuntu2` | resolute | universe |
| `libcrypt-dev` | `1:4.5.1-1` | resolute | main |
| `libcrypt-urandom-perl` | `0.55-1` | resolute | main |
| `libcrypt1` | `1:4.5.1-1` | resolute | main |
| `libcrypto++8t64` | `8.9.0-2build1` | resolute | universe |
| `libcryptsetup12` | `2:2.8.4-1ubuntu4` | resolute | main |
| `libctf-nobfd0` | `2.46-3ubuntu2` | resolute | main |
| `libctf0` | `2.46-3ubuntu2` | resolute | main |
| `libcue2` | `2.2.1-4.2` | resolute | main |
| `libcupsfilters2-common` | `2.1.1-0ubuntu5` | resolute | main |
| `libcupsfilters2t64` | `2.1.1-0ubuntu5` | resolute | main |
| `libcwidget4` | `0.5.18-6build2` | resolute | universe |
| `libcxsparse4` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libdaemon0` | `0.14-7.1ubuntu5` | resolute | main |
| `libdata-dump-perl` | `1.25-1` | resolute | main |
| `libdatrie1` | `0.2.14-1` | resolute | main |
| `libdav1d-dev` | `1.5.3-1` | resolute | universe |
| `libdav1d7` | `1.5.3-1` | resolute | universe |
| `libdb5.3t64` | `5.3.28+dfsg2-10ubuntu1` | resolute | main |
| `libdbus-1-3` | `1.16.2-2ubuntu4` | resolute | main |
| `libdbus-1-dev` | `1.16.2-2ubuntu4` | resolute | main |
| `libdbusmenu-glib4` | `18.10.20180917~bzr492+repack1-4build1` | resolute | main |
| `libdbusmenu-gtk3-4` | `18.10.20180917~bzr492+repack1-4build1` | resolute | main |
| `libdbusmenu-qt5-2` | `0.9.3+16.04.20160218-5` | resolute | universe |
| `libdc1394-25` | `2.2.6-6` | resolute | universe |
| `libdc1394-dev` | `2.2.6-6` | resolute | universe |
| `libdca0` | `0.0.7-2build2` | resolute | universe |
| `libdconf1` | `0.49.0-4` | resolute | main |
| `libdd-plist-java` | `1.20-1.1build1` | resolute | universe |
| `libddcutil5` | `2.2.5-1` | resolute | universe |
| `libde265-0` | `1.0.16-1build1` | resolute | universe |
| `libdebconf-kde1` | `1.2.0-2ubuntu1` | resolute | universe |
| `libdebconfclient0` | `0.280ubuntu1` | resolute | main |
| `libdebuginfod-common` | `0.194-4` | resolute | main |
| `libdebuginfod1t64` | `0.194-4` | resolute | main |
| `libdecor-0-0` | `0.2.5-1` | resolute | main |
| `libdecor-0-dev` | `0.2.5-1` | resolute | main |
| `libdecor-0-plugin-1-gtk` | `0.2.5-1` | resolute | main |
| `libdeflate-dev` | `1.23-2ubuntu1` | resolute | main |
| `libdeflate0` | `1.23-2ubuntu1` | resolute | main |
| `libdevmapper-event1.02.1` | `2:1.02.205-2ubuntu3` | resolute | main |
| `libdevmapper1.02.1` | `2:1.02.205-2ubuntu3` | resolute | main |
| `libdisplay-info-bin` | `0.3.0-1` | resolute | universe |
| `libdisplay-info3` | `0.3.0-1` | resolute | main |
| `libdjvulibre-text` | `3.5.29-1` | resolute | main |
| `libdjvulibre21` | `3.5.29-1` | resolute | main |
| `libdmtx0t64` | `0.7.8-1` | resolute | universe |
| `libdnnl3.6` | `3.9.1+ds-2` | resolute | universe |
| `libdolphinvcs6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libdom4j-java` | `2.1.4-1build1` | resolute | universe |
| `libdotconf0` | `1.4.1-1build1` | resolute | main |
| `libdouble-conversion-dev` | `3.4.0-1` | resolute | universe |
| `libdouble-conversion3` | `3.4.0-1` | resolute | universe |
| `libdpkg-perl` | `1.23.7ubuntu1` | resolute | main |
| `libdraco9` | `1.5.7+dfsg-2` | resolute | universe |
| `libdrm-amdgpu1` | `2.4.131-1` | resolute | main |
| `libdrm-common` | `2.4.131-1` | resolute | main |
| `libdrm-dev` | `2.4.131-1` | resolute | main |
| `libdrm-intel1` | `2.4.131-1` | resolute | main |
| `libdrm-nouveau2` | `2.4.131-1` | resolute | main |
| `libdrm-radeon1` | `2.4.131-1` | resolute | main |
| `libdrm2` | `2.4.131-1` | resolute | main |
| `libduktape207` | `2.7.0+tests-0ubuntu4` | resolute | main |
| `libdv4t64` | `1.0.0-17.1build2` | resolute | main |
| `libdvbpsi10` | `1.3.3-1build2` | resolute | universe |
| `libdvdnav4` | `7.0.0-2` | resolute | universe |
| `libdvdread8t64` | `7.0.1-1` | resolute | universe |
| `libdw-dev` | `0.194-4` | resolute | main |
| `libdw1t64` | `0.194-4` | resolute | main |
| `libdwarf-dev` | `1:0.11.1-1build1` | resolute | universe |
| `libdwarf1` | `1:0.11.1-1build1` | resolute | universe |
| `libe-book-0.1-1` | `0.1.3-2build9` | resolute | main |
| `libe131-1` | `1.4.0+repack-1build1` | resolute | universe |
| `libebackend-1.2-11t64` | `3.56.2-8` | resolute | main |
| `libebml5` | `1.4.5-2` | resolute | universe |
| `libebook-1.2-21t64` | `3.56.2-8` | resolute | main |
| `libebook-contacts-1.2-4t64` | `3.56.2-8` | resolute | main |
| `libebur128-1` | `1.2.6-2` | resolute | universe |
| `libeclipse-jdt-annotation-java` | `2.2.700+eclipse4.29-2build1` | resolute | universe |
| `libedata-book-1.2-27t64` | `3.56.2-8` | resolute | main |
| `libedataserver-1.2-27t64` | `3.56.2-8` | resolute | main |
| `libedit2` | `3.1-20251016-1` | resolute | main |
| `libefiboot1t64` | `39-2` | resolute | main |
| `libefivar1t64` | `39-2` | resolute | main |
| `libegl-dev` | `1.7.0-3` | resolute | main |
| `libegl1` | `1.7.0-3` | resolute | main |
| `libei1` | `1.5.0-3` | resolute | main |
| `libeigen3-dev` | `3.4.0-5` | resolute | universe |
| `libeis1` | `1.5.0-3` | resolute | main |
| `libel-api-java` | `3.0.0-3build1` | resolute | universe |
| `libelf-dev` | `0.194-4` | resolute | main |
| `libelf1t64` | `0.194-4` | resolute | main |
| `libenchant-2-2` | `2.8.2+dfsg1-3build1` | resolute | main |
| `libencode-locale-perl` | `1.05-3` | resolute | main |
| `libeot0` | `0.01-5build4` | resolute | main |
| `libepoxy0` | `1.5.10-2build1` | resolute | main |
| `libepub0` | `0.2.2-8` | resolute | universe |
| `libepubgen-0.1-1` | `0.1.1-1ubuntu8` | resolute | main |
| `liberror-perl` | `0.17030-1` | resolute | main |
| `liberror-prone-java` | `2.18.0-1build1` | resolute | universe |
| `libespeak-ng1` | `1.52.0+dfsg-5build1` | resolute | main |
| `libestr0` | `0.1.11-2build1` | resolute | main |
| `libetonyek-0.1-1` | `0.1.13-2` | resolute | main |
| `libev-dev` | `1:4.33-2.1build2` | resolute | universe |
| `libev4t64` | `1:4.33-2.1build2` | resolute | universe |
| `libevdev-dev` | `1.13.6+dfsg-1` | resolute | main |
| `libevdev2` | `1.13.6+dfsg-1` | resolute | main |
| `libeventviews-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libexiv2-28` | `0.28.8+dfsg-1` | resolute | main |
| `libexiv2-data` | `0.28.8+dfsg-1` | resolute | main |
| `libexiv2-dev` | `0.28.8+dfsg-1` | resolute | main |
| `libexprtk-dev` | `0.0.3-4` | resolute | universe |
| `libext2fs-dev` | `1.47.2-3ubuntu4` | resolute | main |
| `libext2fs2t64` | `1.47.2-3ubuntu4` | resolute | main |
| `libexttextcat-2.0-0` | `3.4.7-2` | resolute | main |
| `libexttextcat-data` | `3.4.7-2` | resolute | main |
| `libextutils-depends-perl` | `0.8002-1` | resolute | main |
| `libfaad2` | `2.11.2-1build1` | resolute | universe |
| `libfabric1` | `2.1.0-1.1build1` | resolute | universe |
| `libfakeroot` | `1.37.2-1` | resolute | main |
| `libfarmhash0` | `0~git20190513.0d859a8-4` | resolute | universe |
| `libfastjson4` | `1.2304.0-2build1` | resolute | main |
| `libfcl-dev` | `0.7.0-3ubuntu1` | resolute | universe |
| `libfcl0.7` | `0.7.0-3ubuntu1` | resolute | universe |
| `libfelix-framework-java` | `4.6.1-3build1` | resolute | universe |
| `libfelix-gogo-runtime-java` | `0.16.2-2build1` | resolute | universe |
| `libfelix-osgi-obr-java` | `1.0.2-5fakesync1build1` | resolute | universe |
| `libfelix-resolver-java` | `1.16.0-1build1` | resolute | universe |
| `libffi-dev` | `3.5.2-4` | resolute | main |
| `libffi8` | `3.5.2-4` | resolute | main |
| `libfftw3-double3` | `3.3.10-2fakesync1build3` | resolute | main |
| `libfftw3-single3` | `3.3.10-2fakesync1build3` | resolute | main |
| `libfido2-1` | `1.16.0-2build1` | resolute | main |
| `libfile-basedir-perl` | `0.09-2` | resolute | main |
| `libfile-desktopentry-perl` | `0.23-1` | resolute | main |
| `libfile-fcntllock-perl` | `0.22-4ubuntu6` | resolute | main |
| `libfile-listing-perl` | `6.16-1` | resolute | main |
| `libfile-mimeinfo-perl` | `0.36-2` | resolute | main |
| `libfindbugs-java` | `3.1.0~preview2-5` | resolute | universe |
| `libflac++11` | `1.5.0+ds-5` | resolute | main |
| `libflac14` | `1.5.0+ds-5` | resolute | main |
| `libflann-dev` | `1.9.2+dfsg-7` | resolute | universe |
| `libflann1.9` | `1.9.2+dfsg-7` | resolute | universe |
| `libflite1` | `2.2-7build1` | resolute | universe |
| `libfluidsynth3` | `2.4.8+dfsg-1` | resolute | universe |
| `libfmt-dev` | `10.1.1+ds1-4build1` | resolute | universe |
| `libfmt10` | `10.1.1+ds1-4build1` | resolute | universe |
| `libfont-afm-perl` | `1.20-4` | resolute | main |
| `libfontconfig-dev` | `2.17.1-3ubuntu1` | resolute | main |
| `libfontconfig1` | `2.17.1-3ubuntu1` | resolute | main |
| `libfontenc1` | `1:1.1.8-1build2` | resolute | main |
| `libfreeaptx0` | `0.2.2-1build1` | resolute | main |
| `libfreecell-solver0` | `5.0.0-4` | resolute | universe |
| `libfreehand-0.1-1` | `0.1.2-3build4` | resolute | main |
| `libfreeimage-dev` | `3.18.0+ds2-11build1` | resolute | universe |
| `libfreeimage3` | `3.18.0+ds2-11build1` | resolute | universe |
| `libfreexl-dev` | `2.0.0-1build3` | resolute | universe |
| `libfreexl1` | `2.0.0-1build3` | resolute | universe |
| `libfribidi0` | `1.0.16-5` | resolute | main |
| `libftdi1-2` | `1.6~rc1-1build1` | resolute | main |
| `libfuse2t64` | `2.9.9-9build1` | resolute | universe |
| `libfuse3-4` | `3.18.2-1` | resolute | main |
| `libfyaml0` | `0.9.4-1` | resolute | main |
| `libfyba-dev` | `4.1.1-11build2` | resolute | universe |
| `libfyba0t64` | `4.1.1-11build2` | resolute | universe |
| `libgav1-2` | `0.20.0-2build1` | resolute | universe |
| `libgavl3` | `2.0.1-1` | resolute | universe |
| `libgc1` | `1:8.2.12-1` | resolute | main |
| `libgcc-15-dev` | `15.2.0-16ubuntu1` | resolute | main |
| `libgcc-16-dev` | `16-20260322-1ubuntu1` | resolute | universe |
| `libgcc-s1` | `16-20260322-1ubuntu1` | resolute | main |
| `libgd3` | `2.3.3-13ubuntu2` | resolute | main |
| `libgdal-dev` | `3.12.2+dfsg-1build2` | resolute | universe |
| `libgdal38` | `3.12.2+dfsg-1build2` | resolute | universe |
| `libgdbm-compat4t64` | `1.26-1build1` | resolute | main |
| `libgdbm6t64` | `1.26-1build1` | resolute | main |
| `libgdcm-dev` | `3.0.24-9ubuntu1` | resolute | universe |
| `libgdcm3.0t64` | `3.0.24-9ubuntu1` | resolute | universe |
| `libgdk-pixbuf-2.0-0` | `2.44.5+dfsg-4ubuntu1` | resolute | main |
| `libgdk-pixbuf2.0-common` | `2.44.5+dfsg-4ubuntu1` | resolute | main |
| `libgegl-0.4-0t64` | `1:0.4.70-1` | resolute | universe |
| `libgegl-common` | `1:0.4.70-1` | resolute | universe |
| `libgeoclue-2-0` | `2.7.2-2ubuntu3` | resolute | main |
| `libgeos-c1t64` | `3.14.1-2` | resolute | universe |
| `libgeos-dev` | `3.14.1-2` | resolute | universe |
| `libgeos3.14.1` | `3.14.1-2` | resolute | universe |
| `libgeotiff-dev` | `1.7.4-1build1` | resolute | universe |
| `libgeotiff5` | `1.7.4-1build1` | resolute | universe |
| `libgeronimo-annotation-1.3-spec-java` | `1.3-1build1` | resolute | universe |
| `libgeronimo-interceptor-3.0-spec-java` | `1.0.1-5fakesyncbuild1` | resolute | universe |
| `libgexiv2-2` | `0.14.6-2` | resolute | main |
| `libgflags-dev` | `2.2.2-3` | resolute | universe |
| `libgflags2.2` | `2.2.2-3` | resolute | universe |
| `libgfortran-15-dev` | `15.2.0-16ubuntu1` | resolute | main |
| `libgfortran-16-dev` | `16-20260322-1ubuntu1` | resolute | universe |
| `libgfortran5` | `16-20260322-1ubuntu1` | resolute | main |
| `libgirepository-1.0-1` | `1.86.0-6build1` | resolute | main |
| `libgl-dev` | `1.7.0-3` | resolute | main |
| `libgl1` | `1.7.0-3` | resolute | main |
| `libgl2ps-dev` | `1.4.2+dfsg1-4` | resolute | universe |
| `libgl2ps1.4` | `1.4.2+dfsg1-4` | resolute | universe |
| `libgles-dev` | `1.7.0-3` | resolute | main |
| `libgles1` | `1.7.0-3` | resolute | main |
| `libgles2` | `1.7.0-3` | resolute | main |
| `libglew-dev` | `2.2.0-4build2` | resolute | universe |
| `libglew2.2` | `2.2.0-4build2` | resolute | universe |
| `libglfw3` | `3.4-4` | resolute | universe |
| `libglfw3-dev` | `3.4-4` | resolute | universe |
| `libglib-object-introspection-perl` | `0.052-1` | resolute | main |
| `libglib-perl` | `3:1.329.4-1` | resolute | main |
| `libglibmm-2.4-1t64` | `2.66.8-3` | resolute | main |
| `libglu1-mesa` | `9.0.2-1.1build2` | resolute | universe |
| `libglu1-mesa-dev` | `9.0.2-1.1build2` | resolute | universe |
| `libglut-dev` | `3.4.0-6` | resolute | universe |
| `libglut3.12` | `3.4.0-6` | resolute | universe |
| `libglvnd-core-dev` | `1.7.0-3` | resolute | main |
| `libglvnd-dev` | `1.7.0-3` | resolute | main |
| `libglvnd0` | `1.7.0-3` | resolute | main |
| `libglx-dev` | `1.7.0-3` | resolute | main |
| `libglx0` | `1.7.0-3` | resolute | main |
| `libgme0` | `0.6.4-1` | resolute | universe |
| `libgmock-dev` | `1.17.0-1build1` | resolute | universe |
| `libgmp-dev` | `2:6.3.0+dfsg-5ubuntu2` | resolute | main |
| `libgmp10` | `2:6.3.0+dfsg-5ubuntu2` | resolute | main |
| `libgmpxx4ldbl` | `2:6.3.0+dfsg-5ubuntu2` | resolute | main |
| `libgnomekbd-common` | `3.28.1-3build1` | resolute | universe |
| `libgnomekbd8` | `3.28.1-3build1` | resolute | universe |
| `libgnustep-base1.31` | `1.31.1-4ubuntu2` | resolute | universe |
| `libgomp1` | `16-20260322-1ubuntu1` | resolute | main |
| `libgoogle-glog-dev` | `0.6.0-3` | resolute | universe |
| `libgoogle-glog0v6t64` | `0.6.0-3` | resolute | universe |
| `libgoogle-gson-java` | `2.10.1-1` | resolute | universe |
| `libgpars-groovy-java` | `1.2.1-11` | resolute | universe |
| `libgpg-error-dev` | `1.58-2` | resolute | main |
| `libgpg-error-l10n` | `1.58-2` | resolute | main |
| `libgpg-error0` | `1.58-2` | resolute | main |
| `libgpgme-dev` | `2.0.1-2build1` | resolute | main |
| `libgpgme45` | `2.0.1-2build1` | resolute | main |
| `libgpgmepp-dev` | `2.0.0-2` | resolute | main |
| `libgpgmepp-doc` | `2.0.0-3` | resolute | main |
| `libgpgmepp7` | `2.0.0-2` | resolute | main |
| `libgpm2` | `1.20.7-12build1` | resolute | main |
| `libgprofng0` | `2.46-3ubuntu2` | resolute | main |
| `libgps32` | `3.27.5-0.1` | resolute | main |
| `libgradle-core-java` | `4.4.1-22ubuntu1` | resolute | universe |
| `libgradle-plugins-java` | `4.4.1-22ubuntu1` | resolute | universe |
| `libgrantleetheme-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libgrantleetheme-plugins` | `25.12.3-0ubuntu1` | resolute | universe |
| `libgraphblas-dev` | `7.4.0+dfsg-2build1` | resolute | universe |
| `libgraphblas7` | `7.4.0+dfsg-2build1` | resolute | universe |
| `libgraphene-1.0-0` | `1.10.8-5build1` | resolute | main |
| `libgravatar-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libgsl28` | `2.8+dfsg-6` | resolute | universe |
| `libgslcblas0` | `2.8+dfsg-6` | resolute | universe |
| `libgsm1` | `1.0.23-2` | resolute | universe |
| `libgspell-1-3` | `1.14.2-2` | resolute | universe |
| `libgspell-1-common` | `1.14.2-2` | resolute | universe |
| `libgssdp-1.6-0` | `1.6.4-5` | resolute | main |
| `libgstreamer1.0-0` | `1.28.2-1` | resolute | main |
| `libgtest-dev` | `1.17.0-1build1` | resolute | universe |
| `libgtk-3-0t64` | `3.24.52-0ubuntu1` | resolute | main |
| `libgtk-3-bin` | `3.24.52-0ubuntu1` | resolute | main |
| `libgtk-3-common` | `3.24.52-0ubuntu1` | resolute | main |
| `libgtk3-perl` | `0.038-3` | resolute | main |
| `libgtkmm-3.0-1t64` | `3.24.10-2` | resolute | main |
| `libgtksourceview-4-0` | `4.8.4-9` | resolute | universe |
| `libgtksourceview-4-common` | `4.8.4-9` | resolute | universe |
| `libgts-0.7-5t64` | `0.7.6+darcs121130-5.2build2` | resolute | universe |
| `libgts-bin` | `0.7.6+darcs121130-5.2build2` | resolute | universe |
| `libguava-java` | `32.0.1-1build1` | resolute | universe |
| `libgudev-1.0-0` | `1:238-7build1` | resolute | main |
| `libgudev-1.0-dev` | `1:238-7build1` | resolute | main |
| `libguice-java` | `5.1.0-1build1` | resolute | universe |
| `libgupnp-1.6-0` | `1.6.9-4` | resolute | main |
| `libgupnp-igd-1.6-0` | `1.6.0-5` | resolute | universe |
| `libgusb2a` | `0.4.9-7` | resolute | main |
| `libgutenprint-common` | `5.3.4.20220624T01008808d602-4ubuntu2` | resolute | main |
| `libgutenprint9` | `5.3.4.20220624T01008808d602-4ubuntu2` | resolute | main |
| `libgvc7` | `14.1.2-1ubuntu1` | resolute | universe |
| `libgvplugin-gd8` | `14.1.2-1ubuntu1` | resolute | universe |
| `libgvplugin-neato-layout8` | `14.1.2-1ubuntu1` | resolute | universe |
| `libgvplugin-pango8` | `14.1.2-1ubuntu1` | resolute | universe |
| `libgvpr2` | `14.1.2-1ubuntu1` | resolute | universe |
| `libgwengui-qt6-79` | `5.14.1-2` | resolute | universe |
| `libgwenhywfar-data` | `5.14.1-2` | resolute | universe |
| `libgwenhywfar79t64` | `5.14.1-2` | resolute | universe |
| `libhamcrest-java` | `2.2-2` | resolute | universe |
| `libharfbuzz-gobject0` | `12.3.2-2` | resolute | main |
| `libharfbuzz-icu0` | `12.3.2-2` | resolute | main |
| `libharfbuzz-subset0` | `12.3.2-2` | resolute | main |
| `libharfbuzz0b` | `12.3.2-2` | resolute | main |
| `libhawtjni-runtime-java` | `1.18-1build1` | resolute | universe |
| `libhdf4-0` | `4.3.1-2` | resolute | universe |
| `libhdf4-dev` | `4.3.1-2` | resolute | universe |
| `libhdf5-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-cpp-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-dev` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-fortran-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-hl-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-hl-cpp-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-hl-fortran-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-mpi-dev` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-cpp-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-dev` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-fortran-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-hl-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-hl-cpp-310` | `1.14.6+repack-2` | resolute | universe |
| `libhdf5-openmpi-hl-fortran-310` | `1.14.6+repack-2` | resolute | universe |
| `libhfstospell11` | `0.5.4-1build5` | resolute | main |
| `libhidapi-hidraw0` | `0.15.0-2` | resolute | universe |
| `libhogweed6t64` | `3.10.2-1` | resolute | main |
| `libhsa-runtime64-1` | `7.1.0+dfsg-0ubuntu9` | resolute | universe |
| `libhsakmt1` | `7.1.0+dfsg-0ubuntu9` | resolute | universe |
| `libhtml-form-perl` | `6.13-1build1` | resolute | main |
| `libhtml-format-perl` | `2.16-2` | resolute | main |
| `libhtml-tagset-perl` | `3.24-1` | resolute | main |
| `libhtml-tree-perl` | `5.07-3` | resolute | main |
| `libhttp-cookies-perl` | `6.11-1` | resolute | main |
| `libhttp-message-perl` | `7.01-1ubuntu1` | resolute | main |
| `libhttp-negotiate-perl` | `6.01-2` | resolute | main |
| `libhttpclient-java` | `4.5.14-1build1` | resolute | universe |
| `libhttpcore-java` | `4.4.16-1build1` | resolute | universe |
| `libhueplusplus1` | `1.2.0+ds-2build1` | resolute | universe |
| `libhunspell-1.7-0` | `1.7.2+really1.7.2-11` | resolute | main |
| `libhwasan0` | `16-20260322-1ubuntu1` | resolute | main |
| `libhwloc-dev` | `2.13.0-2` | resolute | universe |
| `libhwloc-plugins` | `2.13.0-2` | resolute | universe |
| `libhwloc15` | `2.13.0-2` | resolute | universe |
| `libhwy-dev` | `1.3.0-2` | resolute | main |
| `libhwy1t64` | `1.3.0-2` | resolute | main |
| `libhyphen0` | `2.8.8-7build4` | resolute | main |
| `libibmad5` | `61.0-2ubuntu3` | resolute | main |
| `libibumad3` | `61.0-2ubuntu3` | resolute | main |
| `libibus-1.0-5` | `1.5.34~rc2-1` | resolute | main |
| `libibus-1.0-dev` | `1.5.34~rc2-1` | resolute | main |
| `libibverbs-dev` | `61.0-2ubuntu3` | resolute | main |
| `libibverbs1` | `61.0-2ubuntu3` | resolute | main |
| `libical3t64` | `3.0.20-2build1` | resolute | main |
| `libice-dev` | `2:1.1.1-1build1` | resolute | main |
| `libice6` | `2:1.1.1-1build1` | resolute | main |
| `libicu-dev` | `78.2-2ubuntu1` | resolute | main |
| `libicu78` | `78.2-2ubuntu1` | resolute | main |
| `libid3tag0` | `0.16.3-4` | resolute | universe |
| `libidn2-0` | `2.3.8-4build1` | resolute | main |
| `libidn2-dev` | `2.3.8-4build1` | resolute | main |
| `libiec61883-0` | `1.2.0-8` | resolute | main |
| `libieee1284-3t64` | `0.2.11-14.1build2` | resolute | main |
| `libigdgmm12` | `22.9.0+ds1-1` | resolute | universe |
| `libijs-0.35` | `0.35-16` | resolute | main |
| `libimage-magick-perl` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `libimage-magick-q16-perl` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `libimagequant0` | `4.4.1-1` | resolute | main |
| `libimath-3-1-29t64` | `3.1.12-1ubuntu5` | resolute | universe |
| `libimath-dev` | `3.1.12-1ubuntu5` | resolute | universe |
| `libimobiledevice-1.0-6` | `1.4.0-1build1` | resolute | main |
| `libimobiledevice-glue-1.0-0` | `1.3.2-2build1` | resolute | main |
| `libincidenceeditor-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libinih1` | `61-1ubuntu1` | resolute | main |
| `libinireader0` | `61-1ubuntu1` | resolute | main |
| `libinstpatch-1.0-2` | `1.1.7-1.1` | resolute | universe |
| `libio-html-perl` | `1.004-3` | resolute | main |
| `libio-socket-ssl-perl` | `2.098-1` | resolute | main |
| `libio-stringy-perl` | `2.113-2` | resolute | main |
| `libip4tc2` | `1.8.11-2ubuntu3` | resolute | main |
| `libip6tc2` | `1.8.11-2ubuntu3` | resolute | main |
| `libipc-system-simple-perl` | `1.30-2` | resolute | main |
| `libipt2` | `2.1.2-3` | resolute | main |
| `libisl23` | `0.27-1build1` | resolute | main |
| `libisoburn1t64` | `1:1.5.6-1.1ubuntu4` | resolute | main |
| `libisofs6t64` | `1.5.6.pl01-1.1ubuntu3` | resolute | main |
| `libitm1` | `16-20260322-1ubuntu1` | resolute | main |
| `libixml11t64` | `1:1.14.25-1ubuntu1` | resolute | universe |
| `libjack-jackd2-0` | `1.9.22~dfsg-5build1` | resolute | main |
| `libjansi-java` | `2.4.2-1` | resolute | universe |
| `libjansi-native-java` | `1.8-2build1` | resolute | universe |
| `libjansi1-java` | `1.18-3.1build1` | resolute | universe |
| `libjansson4` | `2.14-2build4` | resolute | main |
| `libjarjar-java` | `1.4+svn142-12build1` | resolute | universe |
| `libjatl-java` | `0.2.3-2build1` | resolute | universe |
| `libjavaewah-java` | `1.2.3-2` | resolute | universe |
| `libjaxen-java` | `1.2.0-1` | resolute | universe |
| `libjbig-dev` | `2.1-6.1ubuntu3` | resolute | main |
| `libjbig0` | `2.1-6.1ubuntu3` | resolute | main |
| `libjcat1` | `0.2.5-1build1` | resolute | main |
| `libjcifs-java` | `1.3.19+dfsg-1build1` | resolute | universe |
| `libjcip-annotations-java` | `20060626-6` | resolute | universe |
| `libjcommander-java` | `1.71-4build1` | resolute | universe |
| `libjcsp-java` | `1.1-rc4-3build1` | resolute | universe |
| `libjemalloc2` | `5.3.0-4` | resolute | main |
| `libjetty9-java` | `9.4.58-1` | resolute | universe |
| `libjformatstring-java` | `0.10~20131207-3build1` | resolute | universe |
| `libjgit-java` | `6.7.0-2build1` | resolute | universe |
| `libjline2-java` | `2.14.6-6` | resolute | universe |
| `libjna-java` | `5.15.0-1build1` | resolute | universe |
| `libjna-jni` | `5.15.0-1build1` | resolute | universe |
| `libjpeg-dev` | `8c-2ubuntu12` | resolute | main |
| `libjpeg-turbo-progs` | `2.1.5-4ubuntu4` | resolute | universe |
| `libjpeg-turbo8` | `2.1.5-4ubuntu4` | resolute | main |
| `libjpeg-turbo8-dev` | `2.1.5-4ubuntu4` | resolute | main |
| `libjpeg8` | `8c-2ubuntu12` | resolute | main |
| `libjpeg8-dev` | `8c-2ubuntu12` | resolute | main |
| `libjs-bootstrap4` | `4.6.2+dfsg-2` | resolute | universe |
| `libjs-bootstrap5` | `5.3.8+dfsg-2` | resolute | universe |
| `libjs-jquery` | `3.7.1+dfsg+~3.5.33-1build1` | resolute | main |
| `libjs-jquery-hotkeys` | `0.2.0-1` | resolute | universe |
| `libjs-jquery-isonscreen` | `1.2.0-2` | resolute | universe |
| `libjs-jquery-metadata` | `12-4build1` | resolute | universe |
| `libjs-jquery-tablesorter` | `1:2.31.3+dfsg1-5` | resolute | universe |
| `libjs-jquery-throttle-debounce` | `1.1+dfsg.1-2build1` | resolute | universe |
| `libjs-jquery-ui` | `1.13.2+dfsg-1build1` | resolute | universe |
| `libjs-katex` | `0.16.10+~cs6.1.0-5ubuntu1` | resolute | universe |
| `libjs-lunr` | `2.3.9~dfsg-2` | resolute | universe |
| `libjs-popper.js` | `1.16.1+ds-7` | resolute | universe |
| `libjs-sizzle` | `2.3.10+ds+~2.3.6-1build1` | resolute | universe |
| `libjs-sphinxdoc` | `8.2.3-12` | resolute | main |
| `libjs-underscore` | `1.13.8~dfsg+~1.13.0-1` | resolute | main |
| `libjsch-java` | `0.2.19-1build1` | resolute | universe |
| `libjson-c-dev` | `0.18+ds-3` | resolute | main |
| `libjson-c5` | `0.18+ds-3` | resolute | main |
| `libjson-glib-1.0-0` | `1.10.8+ds-2` | resolute | main |
| `libjson-glib-1.0-common` | `1.10.8+ds-2` | resolute | main |
| `libjson-perl` | `4.10000-1` | resolute | main |
| `libjson-xs-perl` | `4.040-1` | resolute | main |
| `libjsoncpp-dev` | `1.9.6-5` | resolute | main |
| `libjsoncpp26` | `1.9.6-5` | resolute | main |
| `libjsoup-java` | `1.15.3-1build1` | resolute | universe |
| `libjsp-api-java` | `2.3.4-3build1` | resolute | universe |
| `libjsr166y-java` | `1.7.0-3` | resolute | universe |
| `libjsr305-java` | `0.1~+svn49-12` | resolute | universe |
| `libjunixsocket-java` | `2.6.1-1build2` | resolute | universe |
| `libjunixsocket-jni` | `2.6.1-1build2` | resolute | universe |
| `libjxr-tools` | `1.2~git20170615.f752187-5.3build1` | resolute | universe |
| `libjxr0t64` | `1.2~git20170615.f752187-5.3build1` | resolute | universe |
| `libjzlib-java` | `1.1.3-3build1` | resolute | universe |
| `libkaccounts6-2` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkate1` | `0.4.1-12` | resolute | universe |
| `libkcalendarutils-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkcddb6-5` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkchart-l10n` | `3.0.1-4ubuntu2` | resolute | universe |
| `libkchart6-3` | `3.0.1-4ubuntu2` | resolute | universe |
| `libkcolorpicker-qt6-0` | `0.3.1-3` | resolute | universe |
| `libkcompactdisc6-5` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkdcrawqt6-5` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkddockwidgets-qt6-3` | `2.4.0+ds-2ubuntu1` | resolute | universe |
| `libkdecorations3-6` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkdecorations3private2` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkdegames6-6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkdegames6-i18n` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkdepim-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkdepim-plugins` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkdsingleapplication-qt6-1.0` | `1.2.0-1` | resolute | universe |
| `libkdsoap-qt6-2` | `2.2.0+dfsg-4ubuntu1` | resolute | universe |
| `libkdsoapwsdiscoveryclient0` | `0.4.0-2ubuntu2` | resolute | universe |
| `libkexiv2qt6-0` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkeyutils1` | `1.6.3-6ubuntu3` | resolute | main |
| `libkf5archive-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5archive5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5auth-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5authcore5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5bookmarks-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5bookmarks5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5codecs-data` | `5.116.0-2` | resolute | universe |
| `libkf5codecs5` | `5.116.0-2` | resolute | universe |
| `libkf5completion-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5completion5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5config-bin` | `5.116.0-2` | resolute | universe |
| `libkf5config-data` | `5.116.0-2` | resolute | universe |
| `libkf5configcore5` | `5.116.0-2` | resolute | universe |
| `libkf5configgui5` | `5.116.0-2` | resolute | universe |
| `libkf5configwidgets-data` | `5.116.0-2` | resolute | universe |
| `libkf5configwidgets5` | `5.116.0-2` | resolute | universe |
| `libkf5coreaddons-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5coreaddons5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5crash5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5dbusaddons-bin` | `5.116.0-2` | resolute | universe |
| `libkf5dbusaddons-data` | `5.116.0-2` | resolute | universe |
| `libkf5dbusaddons5` | `5.116.0-2` | resolute | universe |
| `libkf5declarative-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5declarative5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5doctools5` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5globalaccel-bin` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5globalaccel-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5globalaccel5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5globalaccelprivate5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5guiaddons-bin` | `5.116.0-2ubuntu1` | resolute | universe |
| `libkf5guiaddons-data` | `5.116.0-2ubuntu1` | resolute | universe |
| `libkf5guiaddons5` | `5.116.0-2ubuntu1` | resolute | universe |
| `libkf5i18n-data` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5i18n5` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5iconthemes-bin` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5iconthemes-data` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5iconthemes5` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5itemviews-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5itemviews5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5jobwidgets-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5jobwidgets5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5kiocore5` | `5.116.0-2` | resolute | universe |
| `libkf5kiofilewidgets5` | `5.116.0-2` | resolute | universe |
| `libkf5kiogui5` | `5.116.0-2` | resolute | universe |
| `libkf5kiontlm5` | `5.116.0-2` | resolute | universe |
| `libkf5kiowidgets5` | `5.116.0-2` | resolute | universe |
| `libkf5kirigami2-5` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5notifications-data` | `5.116.0-2` | resolute | universe |
| `libkf5notifications5` | `5.116.0-2` | resolute | universe |
| `libkf5package-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5package5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5quickaddons5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5service-bin` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5service-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5service5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5solid5` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5solid5-data` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5sonnet5-data` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5sonnetcore5` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5sonnetui5` | `5.116.0-1ubuntu2` | resolute | universe |
| `libkf5style5` | `5.116.0-3` | resolute | universe |
| `libkf5textwidgets-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5textwidgets5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5wallet-bin` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5wallet-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5wallet5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5waylandclient5` | `4:5.116.0-0ubuntu7` | resolute | universe |
| `libkf5widgetsaddons-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5widgetsaddons5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5windowsystem-data` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5windowsystem5` | `5.116.0-1ubuntu1` | resolute | universe |
| `libkf5xmlgui-bin` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5xmlgui-data` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf5xmlgui5` | `5.116.0-1ubuntu4` | resolute | universe |
| `libkf6archive-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6archive6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6attica6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6auth-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6authcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6baloo6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6balooengine6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6baloowidgets6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkf6bluezqt-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6bluezqt6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6bookmarks-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6bookmarks6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6bookmarkswidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6breezeicons6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6calendarcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6calendarevents6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6codecs-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6codecs6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6colorscheme-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6colorscheme6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6completion-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6completion6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6config-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6config-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6configcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6configgui6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6configqml6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6configwidgets-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6configwidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6contacts-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6contacts6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6crash6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dav-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dav6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dbusaddons-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dbusaddons-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dbusaddons6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6declarative-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dnssd-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6dnssd6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6doctools6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6filemetadata-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6filemetadata-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6filemetadata3` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6globalaccel-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6globalaccel6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6holidays-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6holidays6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6i18n-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6i18n6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6i18nlocaledata6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6i18nqml6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6iconthemes-bin` | `6.24.0-0ubuntu2` | resolute | universe |
| `libkf6iconthemes-data` | `6.24.0-0ubuntu2` | resolute | universe |
| `libkf6iconthemes6` | `6.24.0-0ubuntu2` | resolute | universe |
| `libkf6iconwidgets6` | `6.24.0-0ubuntu2` | resolute | universe |
| `libkf6idletime6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6itemmodels6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6itemviews-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6itemviews6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6jobwidgets-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6jobwidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kcmutils-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kcmutils-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kcmutils6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kcmutilscore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kcmutilsquick6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kiocore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kiofilewidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kiogui6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6kiowidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6konq7` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkf6konqsettings7` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkf6modemmanagerqt6` | `6.23.0-0ubuntu1` | resolute | universe |
| `libkf6networkmanagerqt6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6newstuff-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6newstuffcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6newstuffwidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6notifications-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6notifications6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6notifyconfig-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6notifyconfig6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6package-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6package6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6parts-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6parts6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6prison6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6prisonscanner6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6pty-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6pty6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6pulseaudioqt5` | `1.7.0-1build1` | resolute | universe |
| `libkf6purpose-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6purpose-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6purpose6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6purposewidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6qqc2desktopstyle-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6runner6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6screen8` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkf6screendpms8` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkf6service-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6service-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6service6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6solid-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6solid6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6sonnet-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6sonnetcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6sonnetui6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6statusnotifieritem-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6statusnotifieritem6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6style6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6su-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6su-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6su6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6svg6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6syndication6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6syntaxhighlighting-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6syntaxhighlighting6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6textaddonswidgets1` | `1.9.1-3` | resolute | universe |
| `libkf6textautocorrectioncore1` | `1.9.1-3` | resolute | universe |
| `libkf6textautocorrectionwidgets1` | `1.9.1-3` | resolute | universe |
| `libkf6textautogeneratetext1` | `1.9.1-3` | resolute | universe |
| `libkf6textcustomeditor1` | `1.9.1-3` | resolute | universe |
| `libkf6texteditor-bin` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6texteditor-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6texteditor-katepart` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6texteditor6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6textedittexttospeech1` | `1.9.1-3` | resolute | universe |
| `libkf6textemoticonscore1` | `1.9.1-3` | resolute | universe |
| `libkf6textemoticonswidgets1` | `1.9.1-3` | resolute | universe |
| `libkf6textgrammarcheck1` | `1.9.1-3` | resolute | universe |
| `libkf6texttemplate6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6texttranslator1` | `1.9.1-3` | resolute | universe |
| `libkf6textutils1` | `1.9.1-3` | resolute | universe |
| `libkf6textwidgets-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6textwidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6threadweaver6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6unitconversion-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6unitconversion6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6userfeedback-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6userfeedback-doc` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6userfeedbackcore6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6userfeedbackwidgets6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6wallet-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6wallet6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6walletbackend6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6widgetsaddons-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6widgetsaddons6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6windowsystem-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6windowsystem6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6xmlgui-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkf6xmlgui6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkgantt-l10n` | `3.0.1-4ubuntu2` | resolute | universe |
| `libkgantt6-3` | `3.0.1-4ubuntu2` | resolute | universe |
| `libkgapi-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkimageannotator-common` | `0.7.2-2` | resolute | universe |
| `libkimageannotator-qt6-0` | `0.7.2-2` | resolute | universe |
| `libkimap-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkirigami-data` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigami6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamiaddonsstatefulapp6` | `1.11.0-2ubuntu2` | resolute | universe |
| `libkirigamiapp6` | `1.11.0-2ubuntu2` | resolute | universe |
| `libkirigamicontrols6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamidelegates6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamidialogs6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamilayouts6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamilayoutsprivate6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamiplatform6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamipolyfill6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamiprimitives6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamiprivate6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkirigamitemplates6` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkitinerary-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkldap-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkleo-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libklibc` | `2.0.14-1ubuntu2` | resolute | main |
| `libklu2` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libkmahjongg6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkmailtransport-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkmime-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkml-dev` | `1.3.0-13` | resolute | universe |
| `libkmlbase1t64` | `1.3.0-13` | resolute | universe |
| `libkmlconvenience1t64` | `1.3.0-13` | resolute | universe |
| `libkmldom1t64` | `1.3.0-13` | resolute | universe |
| `libkmlengine1t64` | `1.3.0-13` | resolute | universe |
| `libkmlregionator1t64` | `1.3.0-13` | resolute | universe |
| `libkmlxsd1t64` | `1.3.0-13` | resolute | universe |
| `libkmod2` | `34.2-2ubuntu2` | resolute | main |
| `libkontactinterface-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6addressbookimportexport6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadiagentbase6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadiagentwidgetbase6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadicalendar6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadicalendarcore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadicontactcore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadicontactwidgets6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadicore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadimime6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadiprivate6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadisearchcore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadisearchdebug6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadisearchpim6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadisearchxapian6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6akonadiwidgets6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6calendarsupport6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6calendarutils6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6eventviews6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6gapicalendar6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6gapicore6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6gapipeople6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6gapitasks6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6grantleetheme6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6gravatar6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6identitymanagementcore6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6identitymanagementwidgets6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6imap6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6importwizard6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6incidenceeditor6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6itinerary6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6kmanagesieve6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6kontactinterface6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6ksieve6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6ksievecore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6ksieveui6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6ldapcore6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6ldapwidgets6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6libkdepim6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6libkleo6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mailcommon6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mailimporter6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mailimporterakonadi6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mailtransport6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mbox6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6messagecomposer6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6messagecore6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6messagelist6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6messageviewer6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mime6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6mimetreeparser6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6pimcommon6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6pimcommonactivities6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6pimcommonakonadi6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6pkpass6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6smtp6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6templateparser6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6textedit6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6tnef6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpim6webengineviewer6` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkpimtextedit-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkpipewire-data` | `6.6.4-0ubuntu1` | resolute | universe |
| `libkpipewire6` | `6.6.4-0ubuntu1` | resolute | universe |
| `libkpipewiredmabuf6` | `6.6.4-0ubuntu1` | resolute | universe |
| `libkpipewirerecord6` | `6.6.4-0ubuntu1` | resolute | universe |
| `libkpmcore13` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkquickcontrolsprivate0` | `6.24.0-0ubuntu1` | resolute | universe |
| `libkryo-java` | `2.20-8` | resolute | universe |
| `libksane-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libksanecore6-1` | `25.12.3-0ubuntu1` | resolute | universe |
| `libksanewidgets6-6` | `25.12.3-0ubuntu1` | resolute | universe |
| `libksba8` | `1.6.7-2build1` | resolute | main |
| `libkscreen-bin` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkscreen-data` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libksieve-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libksmtp-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libktextaddons-data` | `1.9.1-3` | resolute | universe |
| `libktnef-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libkubuntu1` | `26.04ubuntu1` | resolute | universe |
| `libkunifiedpush-data` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkunifiedpush1` | `25.12.3-0ubuntu1` | resolute | universe |
| `libkwaylandclient6` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libkxml2-java` | `2.3.0+ds1-3build1` | resolute | universe |
| `liblangtag-common` | `0.6.8-2` | resolute | main |
| `liblangtag1` | `0.6.8-2` | resolute | main |
| `liblapack-dev` | `3.12.1-7ubuntu1` | resolute | main |
| `liblapack3` | `3.12.1-7ubuntu1` | resolute | main |
| `liblayershellqtinterface6` | `6.6.4-0ubuntu1` | resolute | universe |
| `liblc3-1` | `1.1.3+dfsg-1build1` | resolute | main |
| `libldacbt-abr2` | `2.0.2.3+git20200429+ed310a0-5build1` | resolute | main |
| `libldacbt-enc2` | `2.0.2.3+git20200429+ed310a0-5build1` | resolute | main |
| `libldap-common` | `2.6.10+dfsg-1ubuntu5` | resolute | main |
| `libldap-dev` | `2.6.10+dfsg-1ubuntu5` | resolute | main |
| `libldap2` | `2.6.10+dfsg-1ubuntu5` | resolute | main |
| `libldl3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libleptonica6` | `1.86.0-1` | resolute | universe |
| `liblerc-dev` | `4.0.0+ds-5ubuntu2` | resolute | main |
| `liblerc4` | `4.0.0+ds-5ubuntu2` | resolute | main |
| `liblightcouch-java` | `0.2.0-1build1` | resolute | universe |
| `liblilv-0-0` | `0.26.2-1` | resolute | universe |
| `liblirc-client0t64` | `0.10.2-0.10ubuntu1` | resolute | main |
| `libllvm21` | `1:21.1.8-6ubuntu1` | resolute | main |
| `liblmdb0` | `0.9.31-1build2` | resolute | main |
| `liblocale-gettext-perl` | `1.07-8` | resolute | main |
| `liblog4j2-java` | `2.19.0-2build1` | resolute | universe |
| `liblogback-java` | `1:1.2.11-6build1` | resolute | universe |
| `liblouis-data` | `3.36.0-1` | resolute | main |
| `liblouis20` | `3.36.0-1` | resolute | main |
| `liblouisutdml-bin` | `2.12.0-8build1` | resolute | main |
| `liblouisutdml-data` | `2.12.0-8build1` | resolute | main |
| `liblouisutdml9t64` | `2.12.0-8build1` | resolute | main |
| `liblqr-1-0` | `0.4.2-2.2` | resolute | universe |
| `liblrdf0` | `0.6.1-5` | resolute | universe |
| `liblsan0` | `16-20260322-1ubuntu1` | resolute | main |
| `liblsof0` | `4.99.4+dfsg-2build2` | resolute | main |
| `libltc11` | `1.3.2-1build2` | resolute | universe |
| `libltdl-dev` | `2.5.4-9` | resolute | main |
| `libltdl7` | `2.5.4-9` | resolute | main |
| `liblttng-ctl0t64` | `2.14.1-1build1` | resolute | universe |
| `liblttng-ust-common1t64` | `2.14.0-1.1` | resolute | main |
| `liblttng-ust-ctl6` | `2.14.0-1.1` | resolute | main |
| `liblttng-ust-dev` | `2.14.0-1.1` | resolute | main |
| `liblttng-ust-python-agent1t64` | `2.14.0-1.1` | resolute | main |
| `liblttng-ust1t64` | `2.14.0-1.1` | resolute | main |
| `liblua5.2-0` | `5.2.4-4` | resolute | universe |
| `liblua5.4-0` | `5.4.8-1build1` | resolute | main |
| `liblvm2cmd2.03` | `2.03.31-2ubuntu3` | resolute | main |
| `liblwp-mediatypes-perl` | `6.04-2` | resolute | main |
| `liblwp-protocol-https-perl` | `6.14-1` | resolute | main |
| `liblz4-1` | `1.10.0-8` | resolute | main |
| `liblz4-dev` | `1.10.0-8` | resolute | main |
| `liblzf1` | `3.6-4build1` | resolute | universe |
| `liblzma-dev` | `5.8.3-1` | resolute | main |
| `liblzma5` | `5.8.3-1` | resolute | main |
| `liblzo2-2` | `2.10-3build2` | resolute | main |
| `libmad0` | `0.16.4-2ubuntu1` | resolute | universe |
| `libmagic-mgc` | `1:5.46-5build2` | resolute | main |
| `libmagic1t64` | `1:5.46-5build2` | resolute | main |
| `libmagickcore-7.q16-10` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `libmagickcore-7.q16-10-extra` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `libmagickwand-7.q16-10` | `8:7.1.2.18+dfsg1-1` | resolute | universe |
| `libmailcommon-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libmailimporter-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libmailtools-perl` | `2.22-1` | resolute | main |
| `libmarblewidget-qt6-28` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libmarkdown2` | `2.2.7-2.1build1` | resolute | main |
| `libmatroska7` | `1.7.1-2` | resolute | universe |
| `libmaven-parent-java` | `43-2build1` | resolute | universe |
| `libmaven-resolver-java` | `1.9.25-1` | resolute | universe |
| `libmaven-shared-utils-java` | `3.4.2-1build1` | resolute | universe |
| `libmaven3-core-java` | `3.9.12-1` | resolute | universe |
| `libmaxminddb0` | `1.12.2-1build2` | resolute | main |
| `libmbedcrypto16` | `3.6.5-0.1ubuntu2` | resolute | universe |
| `libmbedtls21` | `3.6.5-0.1ubuntu2` | resolute | universe |
| `libmbedx509-7` | `3.6.5-0.1ubuntu2` | resolute | universe |
| `libmbim-glib4` | `1.32.0-2ubuntu1` | resolute | main |
| `libmbim-proxy` | `1.32.0-2ubuntu1` | resolute | main |
| `libmd-dev` | `1.1.0-2build4` | resolute | main |
| `libmd0` | `1.1.0-2build4` | resolute | main |
| `libmd4c0` | `0.5.2-2build1` | resolute | universe |
| `libmediainfo0v5` | `26.01+dfsg-1` | resolute | universe |
| `libmhash2` | `0.9.9.9-11` | resolute | main |
| `libminlog-java` | `1.3.1-1` | resolute | universe |
| `libmjpegutils-2.2-0` | `1:2.2.1-3` | resolute | universe |
| `libmm-glib0` | `1.25.95-1ubuntu1` | resolute | main |
| `libmms0` | `0.6.4-3build2` | resolute | universe |
| `libmng2` | `2.0.3+dfsg-5` | resolute | universe |
| `libmnl0` | `1.0.5-3build1` | resolute | main |
| `libmodplug1` | `1:0.8.9.0-3build2` | resolute | universe |
| `libmongodb-java` | `3.6.3-2.1` | resolute | universe |
| `libmosquitto1` | `2.0.22-5build1` | resolute | universe |
| `libmovit8` | `1.7.2-1` | resolute | universe |
| `libmp3lame0` | `3.101~svn6525+dfsg-2` | resolute | main |
| `libmpc3` | `1.3.1-3` | resolute | main |
| `libmpcdec6` | `2:0.1~r495-3build1` | resolute | universe |
| `libmpeg2encpp-2.2-0` | `1:2.2.1-3` | resolute | universe |
| `libmpfr6` | `4.2.2-3` | resolute | main |
| `libmpg123-0t64` | `1.33.3-2` | resolute | main |
| `libmplex2-2.2-0` | `1:2.2.1-3` | resolute | universe |
| `libmpv2` | `0.41.0-2ubuntu4` | resolute | universe |
| `libmpvqt2` | `1.1.1-2` | resolute | universe |
| `libmspack0t64` | `0.11-1.1build2` | resolute | main |
| `libmspub-0.1-1` | `0.1.4-4build1` | resolute | main |
| `libmtdev-dev` | `1.1.7-1build1` | resolute | main |
| `libmtdev1t64` | `1.1.7-1build1` | resolute | main |
| `libmtp-common` | `1.1.22-1ubuntu1` | resolute | main |
| `libmtp-runtime` | `1.1.22-1ubuntu1` | resolute | main |
| `libmtp9t64` | `1.1.22-1ubuntu1` | resolute | main |
| `libmujs3` | `1.3.8-2` | resolute | universe |
| `libmultiverse-core-java` | `0.7.0-6build1` | resolute | universe |
| `libmunge2` | `0.5.16-1.1` | resolute | universe |
| `libmuparser-dev` | `2.3.4-2` | resolute | universe |
| `libmuparser2v5` | `2.3.4-2` | resolute | universe |
| `libmusicbrainz5cc2v5` | `5.1.0+git20150707-12` | resolute | universe |
| `libmwaw-0.3-3` | `0.3.22-2` | resolute | main |
| `libmypaint-1.5-1` | `1.6.0-4build1` | resolute | universe |
| `libmypaint-common` | `1.6.0-4build1` | resolute | universe |
| `libmysofa1` | `1.3.3+dfsg-1ubuntu2` | resolute | universe |
| `libmythes-1.2-0` | `2:1.2.5-2build1` | resolute | main |
| `libnative-platform-java` | `0.14-6build1` | resolute | universe |
| `libnative-platform-jni` | `0.14-6build1` | resolute | universe |
| `libncurses6` | `6.6+20251231-1` | resolute | main |
| `libncursesw6` | `6.6+20251231-1` | resolute | main |
| `libndp0` | `1.9-1build1` | resolute | main |
| `libnekohtml-java` | `1.9.22.noko2-1` | resolute | universe |
| `libneon27t64` | `0.36.0-1` | resolute | universe |
| `libneon27t64-gnutls` | `0.36.0-1` | resolute | universe |
| `libnet-dbus-perl` | `1.2.0-2build4` | resolute | main |
| `libnet-http-perl` | `6.24-1build1` | resolute | main |
| `libnet-smtp-ssl-perl` | `1.04-2` | resolute | main |
| `libnet-ssleay-perl` | `1.94-3` | resolute | main |
| `libnet9` | `1.3+dfsg-3` | resolute | main |
| `libnetcdf-dev` | `1:4.9.3-1build2` | resolute | universe |
| `libnetcdf22` | `1:4.9.3-1build2` | resolute | universe |
| `libnetfilter-conntrack3` | `1.1.1-1` | resolute | main |
| `libnetpbm11t64` | `2:11.10.02-1build1` | resolute | universe |
| `libnettle8t64` | `3.10.2-1` | resolute | main |
| `libnewt0.52` | `0.52.25-1ubuntu3` | resolute | main |
| `libnfnetlink0` | `1.0.2-3build1` | resolute | main |
| `libnftables1` | `1.1.6-1` | resolute | main |
| `libnftnl11` | `1.3.1-1` | resolute | main |
| `libnice10` | `0.1.23-2` | resolute | universe |
| `libnl-3-200` | `3.12.0-2` | resolute | main |
| `libnl-3-dev` | `3.12.0-2` | resolute | main |
| `libnl-genl-3-200` | `3.12.0-2` | resolute | main |
| `libnl-route-3-200` | `3.12.0-2` | resolute | main |
| `libnl-route-3-dev` | `3.12.0-2` | resolute | main |
| `libnorm-dev` | `1.5.9+dfsg-4` | resolute | universe |
| `libnorm1t64` | `1.5.9+dfsg-4` | resolute | universe |
| `libnotify-bin` | `0.8.8-1` | resolute | main |
| `libnotify4` | `0.8.8-1` | resolute | main |
| `libnpth0t64` | `1.8-3build1` | resolute | main |
| `libnspr4` | `2:4.38.2-1ubuntu1` | resolute | main |
| `libnspr4-dev` | `2:4.38.2-1ubuntu1` | resolute | main |
| `libnss-mdns` | `0.15.1-5` | resolute | main |
| `libnuma-dev` | `2.0.19-1build1` | resolute | main |
| `libnuma1` | `2.0.19-1build1` | resolute | main |
| `libnvidia-egl-wayland1` | `1:1.1.21-1` | resolute | main |
| `libnvme1t64` | `1.16.1-4` | resolute | main |
| `libobjc4` | `16-20260322-1ubuntu1` | resolute | universe |
| `libobjenesis-java` | `3.5-1` | resolute | universe |
| `liboctomap-dev` | `1.10.0+dfsg-3` | resolute | universe |
| `liboctomap1.10` | `1.10.0+dfsg-3` | resolute | universe |
| `libodbc2` | `2.3.14-1` | resolute | main |
| `libodbccr2` | `2.3.14-1` | resolute | main |
| `libodbcinst2` | `2.3.14-1` | resolute | main |
| `libode-dev` | `2:0.16.6-3` | resolute | universe |
| `libode8t64` | `2:0.16.6-3` | resolute | universe |
| `libodfgen-0.1-1` | `0.1.8-3build1` | resolute | main |
| `liboeffis1` | `1.5.0-3` | resolute | main |
| `libofx7t64` | `1:0.10.9-1.1build3` | resolute | universe |
| `libogg-dev` | `1.3.6-2` | resolute | main |
| `libogg0` | `1.3.6-2` | resolute | main |
| `libogre-1.9-dev` | `1.9.0+dfsg1-14.1build5` | resolute | universe |
| `libogre-1.9.0t64` | `1.9.0+dfsg1-14.1build5` | resolute | universe |
| `libokular6core4` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libolm3` | `3.2.16+dfsg-5` | resolute | universe |
| `libonig5` | `6.9.10-1build1` | resolute | main |
| `libonnx1t64` | `1.20.0-1` | resolute | universe |
| `libonnxruntime-providers` | `1.23.2+dfsg-6ubuntu1` | resolute | universe |
| `libonnxruntime1.23` | `1.23.2+dfsg-6ubuntu1` | resolute | universe |
| `libopenal-data` | `1:1.25.1-2` | resolute | universe |
| `libopenal1` | `1:1.25.1-2` | resolute | universe |
| `libopenblas0` | `0.3.32+ds-5` | resolute | universe |
| `libopenblas0-pthread` | `0.3.32+ds-5` | resolute | universe |
| `libopenconnect5` | `9.12-3.3` | resolute | universe |
| `libopencore-amrnb0` | `0.1.6-1build2` | resolute | universe |
| `libopencore-amrwb0` | `0.1.6-1build2` | resolute | universe |
| `libopencv-calib3d-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-calib3d410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-contrib-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-contrib410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-core-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-core410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-dnn-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-dnn410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-features2d-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-features2d410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-flann-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-flann410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-highgui-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-highgui410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-imgcodecs-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-imgcodecs410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-imgproc-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-imgproc410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-java` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-ml-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-ml410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-objdetect-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-objdetect410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-photo-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-photo410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-shape-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-shape410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-stitching-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-stitching410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-superres-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-superres410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-video-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-video410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-videoio-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-videoio410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-videostab-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-videostab410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-viz-dev` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv-viz410` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopencv410-jni` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `libopenexr-3-1-30` | `3.1.13-2build1` | resolute | universe |
| `libopenexr-dev` | `3.1.13-2build1` | resolute | universe |
| `libopengl-dev` | `1.7.0-3` | resolute | main |
| `libopengl0` | `1.7.0-3` | resolute | main |
| `libopenh264-8` | `2.6.0+dfsg-2build1` | resolute | universe |
| `libopenmpi-dev` | `5.0.10-1` | resolute | universe |
| `libopenmpi40` | `5.0.10-1` | resolute | universe |
| `libopenmpt-modplug1` | `0.8.9.0-openmpt1-2build3` | resolute | universe |
| `libopenmpt0t64` | `0.8.4-1` | resolute | universe |
| `libopenni-dev` | `1.5.4.0+dfsg-8build1` | resolute | universe |
| `libopenni-sensor-pointclouds0` | `5.1.0.41.11-1build3` | resolute | universe |
| `libopenni0t64` | `1.5.4.0+dfsg-8build1` | resolute | universe |
| `libopenni2-0` | `2.2.0.33+dfsg-19` | resolute | universe |
| `libopenni2-dev` | `2.2.0.33+dfsg-19` | resolute | universe |
| `libopentimelineio0` | `0.18.1-1fakesync1` | resolute | universe |
| `libopus0` | `1.6.1-1` | resolute | main |
| `libopusfile0` | `0.12-4build4` | resolute | universe |
| `liborc-0.4-0t64` | `1:0.4.42-2` | resolute | main |
| `liborcus-0.21-0` | `0.21.0-4` | resolute | main |
| `liborcus-parser-0.21-0` | `0.21.0-4` | resolute | main |
| `liborocos-kdl-dev` | `1.5.2-1` | resolute | universe |
| `liborocos-kdl1.5` | `1.5.2-1` | resolute | universe |
| `libosgi-annotation-java` | `8.1.0-1build1` | resolute | universe |
| `libosgi-compendium-java` | `7.0.0-1build1` | resolute | universe |
| `libosgi-core-java` | `8.0.0-2build1` | resolute | universe |
| `libosp5` | `1.5.2-15.2ubuntu2` | resolute | universe |
| `libostree-1-1` | `2025.7-3build1` | resolute | universe |
| `libp11-kit-dev` | `0.26.2-2` | resolute | main |
| `libp11-kit0` | `0.26.2-2` | resolute | main |
| `libpackagekitqt6-2` | `1.1.4-1` | resolute | universe |
| `libpagemaker-0.0-0` | `0.0.4-1build5` | resolute | main |
| `libpam-cap` | `1:2.75-10ubuntu2` | resolute | main |
| `libpam-fprintd` | `1.94.5-4` | resolute | main |
| `libpam-kwallet-common` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libpam-kwallet5` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libpango-1.0-0` | `1.57.0-1` | resolute | main |
| `libpangocairo-1.0-0` | `1.57.0-1` | resolute | main |
| `libpangoft2-1.0-0` | `1.57.0-1` | resolute | main |
| `libpangomm-1.4-1v5` | `2.46.4-2` | resolute | main |
| `libpangoxft-1.0-0` | `1.57.0-1` | resolute | main |
| `libpaper-utils` | `2.2.5-0.3maysync1` | resolute | main |
| `libpaper2` | `2.2.5-0.3maysync1` | resolute | main |
| `libparted2t64` | `3.6-6` | resolute | main |
| `libparu1` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libpathplan4` | `14.1.2-1ubuntu1` | resolute | universe |
| `libpcaudio0` | `1.3-1build1` | resolute | main |
| `libpci3` | `1:3.14.0-1build2` | resolute | main |
| `libpcl-apps1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-common1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-dev` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-features1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-filters1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-io1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-kdtree1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-keypoints1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-ml1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-octree1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-outofcore1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-people1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-recognition1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-registration1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-sample-consensus1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-search1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-segmentation1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-stereo1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-surface1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-tracking1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcl-visualization1.15` | `1.15.1+dfsg-2` | resolute | universe |
| `libpcre2-16-0` | `10.46-1build1` | resolute | main |
| `libpcre2-32-0` | `10.46-1build1` | resolute | main |
| `libpcre2-8-0` | `10.46-1build1` | resolute | main |
| `libpcre2-dev` | `10.46-1build1` | resolute | main |
| `libpcre2-posix3` | `10.46-1build1` | resolute | main |
| `libpcsclite1` | `2.4.1-1` | resolute | main |
| `libpgm-5.3-0t64` | `5.3.128~dfsg-2.1build2` | resolute | universe |
| `libpgm-dev` | `5.3.128~dfsg-2.1build2` | resolute | universe |
| `libphonenumber8` | `8.13.51+ds-5` | resolute | main |
| `libphonon-l10n` | `4:4.12.0-7` | resolute | universe |
| `libphonon4qt6-4t64` | `4:4.12.0-7` | resolute | universe |
| `libpimcommon-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libpipeline1` | `1.5.8-2` | resolute | main |
| `libpixman-1-0` | `0.46.4-1` | resolute | main |
| `libpkcs11-helper1t64` | `1.31.0-1` | resolute | main |
| `libpkgconf7` | `2.5.1-4` | resolute | main |
| `libplacebo360` | `7.360.0-3` | resolute | universe |
| `libplasma-geolocation-interface6` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libplasma5support-data` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libplasma5support6` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libplasmaactivities-data` | `6.6.4-0ubuntu1` | resolute | universe |
| `libplasmaactivities7` | `6.6.4-0ubuntu1` | resolute | universe |
| `libplasmaactivitiesstats1` | `6.6.4-0ubuntu1` | resolute | universe |
| `libplexus-cipher-java` | `2.0-1build1` | resolute | universe |
| `libplexus-classworlds-java` | `2.7.0-1build1` | resolute | universe |
| `libplexus-component-annotations-java` | `2.1.1-1build1` | resolute | universe |
| `libplexus-container-default-java` | `2.1.1-1build1` | resolute | universe |
| `libplexus-interpolation-java` | `1.27-1build1` | resolute | universe |
| `libplexus-sec-dispatcher-java` | `2.0-3build1` | resolute | universe |
| `libplexus-utils2-java` | `3.4.2-1build1` | resolute | universe |
| `libplist-2.0-4` | `2.7.0+git20250820-1build1` | resolute | main |
| `libplymouth5` | `24.004.60+git20250831.4a3c171d-0ubuntu8` | resolute | main |
| `libpmix-dev` | `6.0.0+really5.0.9-3build1` | resolute | universe |
| `libpmix2t64` | `6.0.0+really5.0.9-3build1` | resolute | universe |
| `libpng-dev` | `1.6.57-1` | resolute | main |
| `libpng-tools` | `1.6.57-1` | resolute | main |
| `libpng16-16t64` | `1.6.57-1` | resolute | main |
| `libpoco-dev` | `1.14.2-3` | resolute | universe |
| `libpocoactiverecord112` | `1.14.2-3` | resolute | universe |
| `libpococrypto112` | `1.14.2-3` | resolute | universe |
| `libpocodata112` | `1.14.2-3` | resolute | universe |
| `libpocodatamysql112` | `1.14.2-3` | resolute | universe |
| `libpocodataodbc112` | `1.14.2-3` | resolute | universe |
| `libpocodatapostgresql112` | `1.14.2-3` | resolute | universe |
| `libpocodatasqlite112` | `1.14.2-3` | resolute | universe |
| `libpocoencodings112` | `1.14.2-3` | resolute | universe |
| `libpocofoundation112` | `1.14.2-3` | resolute | universe |
| `libpocojson112` | `1.14.2-3` | resolute | universe |
| `libpocojwt112` | `1.14.2-3` | resolute | universe |
| `libpocomongodb112` | `1.14.2-3` | resolute | universe |
| `libpoconet112` | `1.14.2-3` | resolute | universe |
| `libpoconetssl112` | `1.14.2-3` | resolute | universe |
| `libpocoprometheus112` | `1.14.2-3` | resolute | universe |
| `libpocoredis112` | `1.14.2-3` | resolute | universe |
| `libpocoutil112` | `1.14.2-3` | resolute | universe |
| `libpocoxml112` | `1.14.2-3` | resolute | universe |
| `libpocozip112` | `1.14.2-3` | resolute | universe |
| `libpolkit-qt5-1-1` | `0.200.0-4ubuntu1` | resolute | universe |
| `libpolkit-qt6-1-1` | `0.200.0-4ubuntu1` | resolute | universe |
| `libpolyglot-maven-java` | `0.8~tobrien+git20120905-10build1` | resolute | universe |
| `libpopt0` | `1.19+dfsg-2build1` | resolute | main |
| `libportaudio2` | `19.7.0+git20260206.e1b70d33-0ubuntu1` | resolute | universe |
| `libportmidi2` | `2:2.0.8-1` | resolute | universe |
| `libportsmf0t64` | `0.1~svn20101010-7build2` | resolute | universe |
| `libpotrace0` | `1.16-2build2` | resolute | universe |
| `libppd2` | `2:2.1.1-0ubuntu2` | resolute | main |
| `libppd2-common` | `2:2.1.1-0ubuntu2` | resolute | main |
| `libproc2-0` | `2:4.0.4-9ubuntu1` | resolute | main |
| `libproj-dev` | `9.7.1-1` | resolute | universe |
| `libproj25` | `9.7.1-1` | resolute | universe |
| `libprotobuf-c1` | `1.5.1-1ubuntu2` | resolute | universe |
| `libprotobuf-dev` | `3.21.12-15ubuntu1` | resolute | main |
| `libprotobuf-lite32t64` | `3.21.12-15ubuntu1` | resolute | main |
| `libprotobuf32t64` | `3.21.12-15ubuntu1` | resolute | main |
| `libprotoc-dev` | `3.21.12-15ubuntu1` | resolute | main |
| `libprotoc32t64` | `3.21.12-15ubuntu1` | resolute | main |
| `libproxy-tools` | `0.5.12-1` | resolute | universe |
| `libproxy1v5` | `0.5.12-1` | resolute | main |
| `libprrte-bin` | `3.0.13-2` | resolute | universe |
| `libprrte-dev` | `3.0.13-2` | resolute | universe |
| `libprrte3` | `3.0.13-2` | resolute | universe |
| `libpskc0t64` | `2.6.14-1` | resolute | main |
| `libpsl-dev` | `0.21.2-1.1build2` | resolute | main |
| `libpsl5t64` | `0.21.2-1.1build2` | resolute | main |
| `libpsm2-2` | `11.2.185-2.1build1` | resolute | universe |
| `libpthreadpool0` | `0.0~git20251020.0e6ca13-1` | resolute | universe |
| `libpugixml-dev` | `1.14-2build1` | resolute | universe |
| `libpugixml1v5` | `1.14-2build1` | resolute | universe |
| `libpulse-dev` | `1:17.0+dfsg1-2ubuntu4` | resolute | main |
| `libpulse-mainloop-glib0` | `1:17.0+dfsg1-2ubuntu4` | resolute | main |
| `libpulse0` | `1:17.0+dfsg1-2ubuntu4` | resolute | main |
| `libpulsedsp` | `1:17.0+dfsg1-2ubuntu4` | resolute | universe |
| `libpwquality-common` | `1.4.5-5build1` | resolute | main |
| `libpwquality1` | `1.4.5-5build1` | resolute | main |
| `libpyside6-dev` | `6.10.2-6ubuntu1` | resolute | universe |
| `libpyside6-py3-6.10` | `6.10.2-6ubuntu1` | resolute | universe |
| `libpython3-dev` | `3.14.3-0ubuntu2` | resolute | main |
| `libpython3-stdlib` | `3.14.3-0ubuntu2` | resolute | main |
| `libqaccessibilityclient-qt6-0` | `0.6.0-4ubuntu1` | resolute | universe |
| `libqalculate-data` | `5.9.0-1` | resolute | universe |
| `libqalculate23` | `5.9.0-1` | resolute | universe |
| `libqca-qt6-2` | `2.3.10-2` | resolute | universe |
| `libqca-qt6-plugins` | `2.3.10-2` | resolute | universe |
| `libqcoro6core0t64` | `0.13.0-1ubuntu2` | resolute | universe |
| `libqcoro6dbus0t64` | `0.13.0-1ubuntu2` | resolute | universe |
| `libqcoro6network0t64` | `0.13.0-1ubuntu2` | resolute | universe |
| `libqdox-java` | `1.12.1-4build1` | resolute | universe |
| `libqgpgmeqt6-15` | `2.0.0-3` | resolute | universe |
| `libqhull-dev` | `2020.2-8` | resolute | universe |
| `libqhull-r8.0` | `2020.2-8` | resolute | universe |
| `libqhull8.0` | `2020.2-8` | resolute | universe |
| `libqhullcpp8.0` | `2020.2-8` | resolute | universe |
| `libqmi-glib5` | `1.38.0-1` | resolute | main |
| `libqmi-proxy` | `1.38.0-1` | resolute | main |
| `libqmobipocket6-3` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `libqpdf30` | `12.3.2-1` | resolute | main |
| `libqrencode4` | `4.1.1-2build1` | resolute | universe |
| `libqrtr-glib0` | `1.2.2-2ubuntu1` | resolute | main |
| `libqt5core5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5dbus5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5designer5` | `5.15.18-1` | resolute | universe |
| `libqt5gui5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5help5` | `5.15.18-1` | resolute | universe |
| `libqt5network5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5opengl5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5printsupport5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5qml5` | `5.15.18+dfsg-2` | resolute | universe |
| `libqt5qmlmodels5` | `5.15.18+dfsg-2` | resolute | universe |
| `libqt5qmlworkerscript5` | `5.15.18+dfsg-2` | resolute | universe |
| `libqt5quick5` | `5.15.18+dfsg-2` | resolute | universe |
| `libqt5quickcontrols2-5` | `5.15.18+dfsg-1` | resolute | universe |
| `libqt5quicktemplates2-5` | `5.15.18+dfsg-1` | resolute | universe |
| `libqt5sql5-sqlite` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5sql5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5svg5` | `5.15.18-1` | resolute | universe |
| `libqt5test5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5texttospeech5` | `5.15.18-1` | resolute | universe |
| `libqt5waylandclient5` | `5.15.18-1` | resolute | universe |
| `libqt5waylandcompositor5` | `5.15.18-1` | resolute | universe |
| `libqt5widgets5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt5x11extras5` | `5.15.18-1` | resolute | universe |
| `libqt5xml5t64` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `libqt6charts6` | `6.10.2-1` | resolute | universe |
| `libqt6concurrent6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6core5compat6` | `6.10.2-1` | resolute | universe |
| `libqt6core6t64` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6dbus6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6designer6` | `6.10.2-1` | resolute | universe |
| `libqt6designercomponents6` | `6.10.2-1` | resolute | universe |
| `libqt6gui6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6help6` | `6.10.2-1` | resolute | universe |
| `libqt6keychain1` | `0.15.0-2` | resolute | universe |
| `libqt6labsplatform6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6labssynchronizer6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6location6` | `6.10.2-1` | resolute | universe |
| `libqt6multimedia6` | `6.10.2-2` | resolute | universe |
| `libqt6multimediawidgets6` | `6.10.2-2` | resolute | universe |
| `libqt6network6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6networkauth6` | `6.10.2-1` | resolute | universe |
| `libqt6opengl6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6openglwidgets6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6pdf6` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6positioning6` | `6.10.2-1` | resolute | universe |
| `libqt6positioning6-plugins` | `6.10.2-1` | resolute | universe |
| `libqt6positioningquick6` | `6.10.2-1` | resolute | universe |
| `libqt6printsupport6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6qml6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6qmlcompiler6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6qmlmeta6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6qmlmodels6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6qmlnetwork6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6qmlworkerscript6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quick3d6` | `6.10.2-1` | resolute | universe |
| `libqt6quick3druntimerender6` | `6.10.2-1` | resolute | universe |
| `libqt6quick3dutils6` | `6.10.2-1` | resolute | universe |
| `libqt6quick6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickcontrols2-6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickshapes6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickshapesdesignhelpers6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quicktemplates2-6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quicktest6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickvectorimage6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickvectorimagegenerator6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickvectorimagehelpers6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6quickwidgets6` | `6.10.2+dfsg-3` | resolute | universe |
| `libqt6serialport6` | `6.10.2-1` | resolute | universe |
| `libqt6shadertools6` | `6.10.2-1` | resolute | universe |
| `libqt6spatialaudio6` | `6.10.2-2` | resolute | universe |
| `libqt6sql6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6sql6-sqlite` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6svg6` | `6.10.2-2` | resolute | universe |
| `libqt6svgwidgets6` | `6.10.2-2` | resolute | universe |
| `libqt6test6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6texttospeech6` | `6.10.2-1` | resolute | universe |
| `libqt6uitools6` | `6.10.2-1` | resolute | universe |
| `libqt6virtualkeyboard6` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6waylandclient6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6waylandcompositor6` | `6.10.2-4` | resolute | universe |
| `libqt6webchannel6` | `6.10.2-1` | resolute | universe |
| `libqt6webchannelquick6` | `6.10.2-1` | resolute | universe |
| `libqt6webengine6-data` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6webenginecore6` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6webenginecore6-bin` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6webenginequick6` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6webenginewidgets6` | `6.10.2+dfsg-1` | resolute | universe |
| `libqt6websockets6` | `6.10.2-1` | resolute | universe |
| `libqt6webview6` | `6.10.2-1` | resolute | universe |
| `libqt6widgets6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6wlshellintegration6` | `6.10.2+dfsg-7` | resolute | universe |
| `libqt6xml6` | `6.10.2+dfsg-7` | resolute | universe |
| `libquadmath0` | `16-20260322-1ubuntu1` | resolute | main |
| `libquickcharts1` | `6.24.0-0ubuntu1` | resolute | universe |
| `libquickchartscontrols1` | `6.24.0-0ubuntu1` | resolute | universe |
| `libquotientqt6-0.9` | `0.9.6.1-1ubuntu1` | resolute | universe |
| `libraptor2-0` | `2.0.16-6build1` | resolute | main |
| `libraqm0` | `0.10.4-1` | resolute | main |
| `librasqal3t64` | `0.9.33-3` | resolute | main |
| `librav1e0.8` | `0.8.1-7` | resolute | universe |
| `libraw1394-11` | `2.1.2-2build4` | resolute | main |
| `libraw1394-dev` | `2.1.2-2build4` | resolute | main |
| `libraw1394-tools` | `2.1.2-2build4` | resolute | main |
| `librbio4` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `librdf0t64` | `1.0.17-8` | resolute | main |
| `librdmacm1t64` | `61.0-2ubuntu3` | resolute | main |
| `libre2-11` | `20250805-1build3` | resolute | main |
| `libreadline8t64` | `8.3-4` | resolute | main |
| `libreflectasm-java` | `1.11.9+dfsg-4` | resolute | universe |
| `libreflectasm-java-doc` | `1.11.9+dfsg-4` | resolute | universe |
| `libresid-builder0c2a` | `2.1.1-16build1` | resolute | universe |
| `librevenge-0.0-0` | `0.0.5-3build2` | resolute | main |
| `librhash1` | `1.4.6-1.1` | resolute | main |
| `librhino-java` | `1.7.15-1build1` | resolute | universe |
| `librist4` | `0.2.11+dfsg-1build1` | resolute | universe |
| `librsvg2-2` | `2.61.3+dfsg-3` | resolute | main |
| `librsvg2-common` | `2.61.3+dfsg-3` | resolute | main |
| `librtaudio7` | `6.0.1~ds-2build1` | resolute | universe |
| `librtmp-dev` | `2.4+20151223.gitfa8646d.1-3` | resolute | main |
| `librtmp1` | `2.4+20151223.gitfa8646d.1-3` | resolute | main |
| `librttopo-dev` | `1.1.0-4build1` | resolute | universe |
| `librttopo1` | `1.1.0-4build1` | resolute | universe |
| `librubberband3` | `4.0.0+dfsg-2ubuntu1` | resolute | universe |
| `libruby` | `1:3.3build1` | resolute | main |
| `libsamplerate0` | `0.2.2-4build2` | resolute | main |
| `libsamplerate0-dev` | `0.2.2-4build2` | resolute | main |
| `libsane-common` | `1.4.0-1ubuntu1` | resolute | main |
| `libsane1` | `1.4.0-1ubuntu1` | resolute | main |
| `libsasl2-2` | `2.1.28+dfsg1-9ubuntu3` | resolute | main |
| `libsasl2-modules` | `2.1.28+dfsg1-9ubuntu3` | resolute | main |
| `libsasl2-modules-db` | `2.1.28+dfsg1-9ubuntu3` | resolute | main |
| `libsasl2-modules-kdexoauth2` | `25.12.3-0ubuntu1` | resolute | universe |
| `libsbc1` | `2.1-1build1` | resolute | main |
| `libsbsms10` | `2.3.0-1build2` | resolute | universe |
| `libscim8v5` | `1.4.18+git20211204-0.5` | resolute | universe |
| `libsdl2-2.0-0` | `2.32.10+dfsg-6` | resolute | main |
| `libsdl2-classic` | `2.32.10+dfsg-6` | resolute | main |
| `libsdl2-dev` | `2.32.10+dfsg-6` | resolute | universe |
| `libsdl3-0` | `3.4.2+ds-1ubuntu1` | resolute | universe |
| `libseccomp2` | `2.6.0-2ubuntu5` | resolute | main |
| `libsecret-1-0` | `0.21.7-2build1` | resolute | main |
| `libsecret-common` | `0.21.7-2build1` | resolute | main |
| `libselinux-dev` | `3.9-4build1` | resolute | main |
| `libselinux1` | `3.9-4build1` | resolute | main |
| `libsemanage-common` | `3.9-1build1` | resolute | main |
| `libsemanage2` | `3.9-1build1` | resolute | main |
| `libsensors-config` | `1:3.6.2-2build1` | resolute | main |
| `libsensors5` | `1:3.6.2-2build1` | resolute | main |
| `libsepol-dev` | `3.9-2` | resolute | main |
| `libsepol2` | `3.9-2` | resolute | main |
| `libserd-0-0` | `0.32.6-1` | resolute | universe |
| `libserf-1-1` | `1.3.10-3ubuntu2` | resolute | universe |
| `libservlet-api-java` | `4.0.1-2build1` | resolute | universe |
| `libsfcgal2` | `2.2.0-1` | resolute | universe |
| `libsframe3` | `2.46-3ubuntu2` | resolute | main |
| `libshaderc-dev` | `2026.1-1` | resolute | universe |
| `libshaderc1` | `2026.1-1` | resolute | universe |
| `libsharpyuv-dev` | `1.5.0-0.1build1` | resolute | main |
| `libsharpyuv0` | `1.5.0-0.1build1` | resolute | main |
| `libshiboken6-dev` | `6.10.2-6ubuntu1` | resolute | universe |
| `libshiboken6-py3-6.10` | `6.10.2-6ubuntu1` | resolute | universe |
| `libshine3` | `3.1.1-3build1` | resolute | universe |
| `libshout3` | `2.4.6-1build3` | resolute | main |
| `libshp4` | `1.6.2-1` | resolute | universe |
| `libsidplay2` | `2.1.1-16build1` | resolute | universe |
| `libsidplayfp6` | `2.16.0-1` | resolute | universe |
| `libsigc++-2.0-0v5` | `2.12.1-4build1` | resolute | main |
| `libsignon-extension1` | `8.61+git20231015.c8ad982-8` | resolute | universe |
| `libsignon-plugins-common1` | `8.61+git20231015.c8ad982-8` | resolute | universe |
| `libsignon-qt6-1` | `8.61+git20231015.c8ad982-8` | resolute | universe |
| `libsimdutf31` | `8.0.0-1` | resolute | main |
| `libsimple-http-java` | `4.1.21-2fakesync1` | resolute | universe |
| `libsisu-inject-java` | `0.3.5-1build1` | resolute | universe |
| `libsisu-plexus-java` | `0.3.5-1build1` | resolute | universe |
| `libsixel1` | `1.10.5-1build1` | resolute | universe |
| `libslang2` | `2.3.3-5build1` | resolute | main |
| `libslf4j-java` | `1.7.32-2` | resolute | universe |
| `libsm-dev` | `2:1.2.6-1build1` | resolute | main |
| `libsm6` | `2:1.2.6-1build1` | resolute | main |
| `libsnapd-glib-2-1` | `1.72-0ubuntu3` | resolute | main |
| `libsnapd-qt-2-1` | `1.72-0ubuntu3` | resolute | universe |
| `libsnappy1v5` | `1.2.2-2` | resolute | main |
| `libsndfile1` | `1.2.2-4` | resolute | main |
| `libsndio-dev` | `1.10.0-0.2` | resolute | universe |
| `libsndio7.0` | `1.10.0-0.2` | resolute | universe |
| `libsnmp-base` | `5.9.4+dfsg-2ubuntu3` | resolute | main |
| `libsnmp40t64` | `5.9.4+dfsg-2ubuntu3` | resolute | main |
| `libsocket++1` | `1.12.13+git20131030.5d039ba-2` | resolute | universe |
| `libsodium-dev` | `1.0.18-2` | resolute | main |
| `libsodium23` | `1.0.18-2` | resolute | main |
| `libsonic0` | `0.2.0-13build2` | resolute | main |
| `libsord-0-0` | `0.16.20-1` | resolute | universe |
| `libsoundtouch1` | `2.4.0+ds-1build1` | resolute | universe |
| `libsoup-3.0-0` | `3.6.6-1` | resolute | main |
| `libsoup-3.0-common` | `3.6.6-1` | resolute | main |
| `libsource-highlight-common` | `3.1.9-4.3build2` | resolute | main |
| `libsource-highlight4t64` | `3.1.9-4.3build2` | resolute | main |
| `libsox-fmt-alsa` | `14.7.0.9+ds1-1` | resolute | universe |
| `libsox-fmt-base` | `14.7.0.9+ds1-1` | resolute | universe |
| `libsox-ng3` | `14.7.0.9+ds1-1` | resolute | universe |
| `libsoxr0` | `0.1.3-4.1` | resolute | universe |
| `libspandsp2t64` | `0.0.6+dfsg-2.2build2` | resolute | universe |
| `libspatialaudio0t64` | `0.3.0+git20180730+dfsg1-3` | resolute | universe |
| `libspatialite-dev` | `5.1.0-3ubuntu2` | resolute | universe |
| `libspatialite8t64` | `5.1.0-3ubuntu2` | resolute | universe |
| `libspdlog-dev` | `1:1.15.3+ds-1build1` | resolute | universe |
| `libspdlog1.15` | `1:1.15.3+ds-1build1` | resolute | universe |
| `libspectre1` | `0.2.12-2` | resolute | universe |
| `libspeechd-module0` | `0.12.1-2ubuntu1` | resolute | main |
| `libspeechd2` | `0.12.1-2ubuntu1` | resolute | main |
| `libspeex1` | `1.2.1-3build1` | resolute | main |
| `libspeexdsp1` | `1.2.1-3build1` | resolute | main |
| `libspex3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libspqr4` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libsqlcipher2` | `4.13.0-1` | resolute | universe |
| `libsquashfuse0` | `0.5.2-0.3` | resolute | universe |
| `libsratom-0-0` | `0.6.20-1` | resolute | universe |
| `libsrt1.5-gnutls` | `1.5.4-3` | resolute | universe |
| `libsrtp2-1` | `2.7.0-3build1` | resolute | universe |
| `libss2` | `1.47.2-3ubuntu4` | resolute | main |
| `libstartup-notification0` | `0.12-8build1` | resolute | main |
| `libstdc++-15-dev` | `15.2.0-16ubuntu1` | resolute | main |
| `libstdc++6` | `16-20260322-1ubuntu1` | resolute | main |
| `libstemmer0d` | `3.0.1-1` | resolute | main |
| `libstoken1t64` | `0.93-1` | resolute | universe |
| `libsubid5` | `1:4.17.4-2ubuntu3` | resolute | main |
| `libsuil-0-0` | `0.10.24-1` | resolute | universe |
| `libsuitesparse-dev` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libsuitesparse-mongoose3` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libsuitesparseconfig7` | `1:7.12.2+dfsg-1ubuntu1` | resolute | main |
| `libsuperlu-dev` | `7.0.1+dfsg1-2build1` | resolute | universe |
| `libsuperlu7` | `7.0.1+dfsg1-2build1` | resolute | universe |
| `libsvn1` | `1.14.5-6build1` | resolute | universe |
| `libsvtav1enc2` | `2.3.0+dfsg-1build1` | resolute | universe |
| `libswresample-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libswresample6` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libswscale-dev` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libswscale9` | `7:8.0.1-3ubuntu2` | resolute | universe |
| `libsysprof-capture-4-dev` | `50.0-1` | resolute | main |
| `libsz2` | `1.1.5-1` | resolute | universe |
| `libtag2` | `2.2.1-3` | resolute | main |
| `libtasn1-6` | `4.21.0-2` | resolute | main |
| `libtasn1-6-dev` | `4.21.0-2` | resolute | main |
| `libtasn1-doc` | `4.21.0-2` | resolute | main |
| `libtbb-dev` | `2022.3.0-2` | resolute | universe |
| `libtbb12` | `2022.3.0-2` | resolute | universe |
| `libtbbbind-2-5` | `2022.3.0-2` | resolute | universe |
| `libtbbmalloc2` | `2022.3.0-2` | resolute | universe |
| `libtcl8.6` | `8.6.17+dfsg-1build1` | resolute | main |
| `libteamdctl0` | `1.31-1build4` | resolute | main |
| `libtensorflow-lite2.14.1` | `2.14.1+dfsg-3build1` | resolute | universe |
| `libtesseract5` | `5.5.0-1build1` | resolute | universe |
| `libtext-charwidth-perl` | `0.04-11build4` | resolute | main |
| `libtext-csv-perl` | `2.06-1` | resolute | universe |
| `libtext-csv-xs-perl` | `1.61-1` | resolute | universe |
| `libtext-iconv-perl` | `1.7-8.1` | resolute | main |
| `libtext-wrapi18n-perl` | `0.06-10` | resolute | main |
| `libtextutils-cmark-rc-copy0` | `1.9.1-3` | resolute | universe |
| `libthai-data` | `0.1.30-1` | resolute | main |
| `libthai0` | `0.1.30-1` | resolute | main |
| `libtheora-dev` | `1.2.0+dfsg-6` | resolute | main |
| `libtheora1` | `1.2.0+dfsg-6` | resolute | main |
| `libtheoradec2` | `1.2.0+dfsg-6` | resolute | main |
| `libtheoraenc2` | `1.2.0+dfsg-6` | resolute | main |
| `libtie-ixhash-perl` | `1.23-4` | resolute | main |
| `libtimedate-perl` | `2.3300-2` | resolute | main |
| `libtinfo6` | `6.6+20251231-1` | resolute | main |
| `libtinyxml2-11` | `11.0.0+dfsg-1build1` | resolute | universe |
| `libtinyxml2-dev` | `11.0.0+dfsg-1build1` | resolute | universe |
| `libtinyxml2.6.2v5` | `2.6.2-7build1` | resolute | universe |
| `libtirpc-common` | `1.3.7-0.1` | resolute | main |
| `libtirpc3t64` | `1.3.7-0.1` | resolute | main |
| `libtk8.6` | `8.6.17-1build1` | resolute | main |
| `libtomcrypt1` | `1.18.2+dfsg-7build2` | resolute | universe |
| `libtommath1` | `1.3.0-1build1` | resolute | universe |
| `libtool` | `2.5.4-9` | resolute | main |
| `libtraceevent1` | `1:1.8.7-1` | resolute | main |
| `libtraceevent1-plugin` | `1:1.8.7-1` | resolute | main |
| `libtracefs1` | `1.8.2-1ubuntu1` | resolute | main |
| `libtry-tiny-perl` | `0.32-1` | resolute | main |
| `libts0t64` | `1.22-1.1build2` | resolute | universe |
| `libtsan2` | `16-20260322-1ubuntu1` | resolute | main |
| `libtss2-esys-3.0.2-0t64` | `4.1.3-6` | resolute | main |
| `libtss2-mu-4.0.1-0t64` | `4.1.3-6` | resolute | main |
| `libtss2-sys1t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-cmd0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-device0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-libtpms0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-mssim0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-spi-helper0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tcti-swtpm0t64` | `4.1.3-6` | resolute | main |
| `libtss2-tctildr0t64` | `4.1.3-6` | resolute | main |
| `libturbojpeg0` | `1:2.1.5-4ubuntu4` | resolute | universe |
| `libtwolame0` | `0.4.0-2build4` | resolute | main |
| `libtypes-serialiser-perl` | `1.01-1` | resolute | main |
| `libubsan1` | `16-20260322-1ubuntu1` | resolute | main |
| `libucc1` | `1.7.0~rc1-1` | resolute | universe |
| `libuchardet0` | `0.0.8-2` | resolute | main |
| `libucx0` | `1.20.0+ds-4ubuntu2` | resolute | universe |
| `libudfread3` | `1.2.0-2` | resolute | universe |
| `libumfpack6` | `1:7.12.2+dfsg-1ubuntu1` | resolute | universe |
| `libunibreak6` | `6.1-3build1` | resolute | universe |
| `libuniconf4.6t64` | `4.6.1-19` | resolute | universe |
| `libunistring5` | `1.3-2build1` | resolute | main |
| `libunwind-dev` | `1.8.3-0ubuntu1` | resolute | main |
| `libunwind8` | `1.8.3-0ubuntu1` | resolute | main |
| `libupnp17t64` | `1:1.14.25-1ubuntu1` | resolute | universe |
| `libupower-glib3` | `1.91.1-1` | resolute | main |
| `liburcu-dev` | `0.15.6-1` | resolute | main |
| `liburcu8t64` | `0.15.6-1` | resolute | main |
| `liburdfdom-dev` | `5.1.0-1` | resolute | universe |
| `liburdfdom-headers-dev` | `2.1.0-1` | resolute | universe |
| `liburdfdom-model5` | `5.1.0-1` | resolute | universe |
| `liburdfdom-sensor5` | `5.1.0-1` | resolute | universe |
| `liburdfdom-world5` | `5.1.0-1` | resolute | universe |
| `liburi-perl` | `5.34-2build1` | resolute | main |
| `liburing2` | `2.14-1` | resolute | main |
| `liburiparser-dev` | `0.9.8+dfsg-2build1` | resolute | universe |
| `liburiparser1` | `0.9.8+dfsg-2build1` | resolute | universe |
| `libusb-0.1-4` | `2:0.1.12-35build2` | resolute | main |
| `libusb-1.0-0` | `2:1.0.29-2build1` | resolute | main |
| `libusb-1.0-0-dev` | `2:1.0.29-2build1` | resolute | main |
| `libusb-1.0-doc` | `2:1.0.29-2build1` | resolute | main |
| `libusbmuxd-2.0-7` | `2.1.1-1` | resolute | main |
| `libutempter0` | `1.2.1-4build1` | resolute | main |
| `libutf8proc3` | `2.10.0-2` | resolute | universe |
| `libutfcpp-dev` | `4.0.9-1` | resolute | universe |
| `libuv1-dev` | `1.51.0-2ubuntu1` | resolute | main |
| `libuv1t64` | `1.51.0-2ubuntu1` | resolute | main |
| `libv4l-0t64` | `1.32.0-2ubuntu1` | resolute | main |
| `libv4lconvert0t64` | `1.32.0-2ubuntu1` | resolute | main |
| `libva-drm2` | `2.23.0-1ubuntu1` | resolute | main |
| `libva-glx2` | `2.23.0-1ubuntu1` | resolute | universe |
| `libva-wayland2` | `2.23.0-1ubuntu1` | resolute | universe |
| `libva-x11-2` | `2.23.0-1ubuntu1` | resolute | universe |
| `libva2` | `2.23.0-1ubuntu1` | resolute | main |
| `libvamp-hostsdk3t64` | `2.10.0-5build1` | resolute | universe |
| `libvdpau1` | `1.5-4` | resolute | main |
| `libvidstab1.1` | `1.1.0-2.1` | resolute | universe |
| `libvisio-0.1-1` | `0.1.10-1build1` | resolute | main |
| `libvisual-0.4-0` | `0.4.2-4` | resolute | main |
| `libvlc-bin` | `3.0.23-1` | resolute | universe |
| `libvlc5` | `3.0.23-1` | resolute | universe |
| `libvlccore9` | `3.0.23-1` | resolute | universe |
| `libvo-aacenc0` | `0.1.3-3build1` | resolute | universe |
| `libvo-amrwbenc0` | `0.1.3-2build2` | resolute | universe |
| `libvoikko1` | `4.3.3-1` | resolute | main |
| `libvolume-key1` | `0.3.12-10build2` | resolute | main |
| `libvorbis0a` | `1.3.7-3build2` | resolute | main |
| `libvorbisenc2` | `1.3.7-3build2` | resolute | main |
| `libvorbisfile3` | `1.3.7-3build2` | resolute | main |
| `libvpl2` | `1:2.16.0-1` | resolute | universe |
| `libvpx12` | `1.16.0-3` | resolute | main |
| `libvte-2.91-0` | `0.84.0-2` | resolute | main |
| `libvte-2.91-common` | `0.84.0-2` | resolute | main |
| `libvtk9-dev` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `libvtk9-java` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `libvtk9-qt-dev` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `libvtk9.5` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `libvtk9.5-qt` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `libvulkan-dev` | `1.4.341.0-1` | resolute | main |
| `libvulkan1` | `1.4.341.0-1` | resolute | main |
| `libwacom-common` | `2.18.0-1` | resolute | main |
| `libwacom-dev` | `2.18.0-1` | resolute | main |
| `libwacom9` | `2.18.0-1` | resolute | main |
| `libwagon-file-java` | `3.5.3-2` | resolute | universe |
| `libwagon-http-java` | `3.5.3-2` | resolute | universe |
| `libwagon-provider-api-java` | `3.5.3-2` | resolute | universe |
| `libwavpack1` | `5.9.0-1` | resolute | main |
| `libwayland-bin` | `1.24.0-2` | resolute | main |
| `libwayland-client0` | `1.24.0-2` | resolute | main |
| `libwayland-cursor0` | `1.24.0-2` | resolute | main |
| `libwayland-dev` | `1.24.0-2` | resolute | main |
| `libwayland-egl1` | `1.24.0-2` | resolute | main |
| `libwayland-server0` | `1.24.0-2` | resolute | main |
| `libweather-ion7` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `libwebp-dev` | `1.5.0-0.1build1` | resolute | main |
| `libwebp7` | `1.5.0-0.1build1` | resolute | main |
| `libwebpdecoder3` | `1.5.0-0.1build1` | resolute | main |
| `libwebpdemux2` | `1.5.0-0.1build1` | resolute | main |
| `libwebpmux3` | `1.5.0-0.1build1` | resolute | main |
| `libwebrtc-audio-processing-1-3` | `1.3-3build2` | resolute | main |
| `libwebsocket-api-java` | `1.1-2build1` | resolute | universe |
| `libwhoopsie0` | `0.2.82ubuntu` | resolute | main |
| `libwildmidi2` | `0.4.6-1` | resolute | universe |
| `libwine` | `10.0~repack-12ubuntu1` | resolute | universe |
| `libwireplumber-0.5-0` | `0.5.13-1ubuntu1` | resolute | main |
| `libwmf-0.2-7` | `0.2.14-1` | resolute | main |
| `libwmf-bin` | `0.2.14-1` | resolute | universe |
| `libwmflite-0.2-7` | `0.2.14-1` | resolute | main |
| `libwnck-3-0` | `43.3-1build1` | resolute | main |
| `libwnck-3-common` | `43.3-1build1` | resolute | main |
| `libwpd-0.10-10` | `0.10.3-2build3` | resolute | main |
| `libwpg-0.3-3` | `0.3.4-3build2` | resolute | main |
| `libwps-0.4-4` | `0.4.14-2build2` | resolute | main |
| `libwrap0` | `7.6.q-36build2` | resolute | main |
| `libwvstreams4.6t64-base` | `4.6.1-19` | resolute | universe |
| `libwvstreams4.6t64-extras` | `4.6.1-19` | resolute | universe |
| `libwww-robotrules-perl` | `6.02-1build1` | resolute | main |
| `libwxbase3.2-1t64` | `3.2.9+dfsg-1` | resolute | universe |
| `libwxgtk3.2-1t64` | `3.2.9+dfsg-1` | resolute | universe |
| `libx11-6` | `2:1.8.13-1` | resolute | main |
| `libx11-data` | `2:1.8.13-1` | resolute | main |
| `libx11-dev` | `2:1.8.13-1` | resolute | main |
| `libx11-protocol-perl` | `0.56-9` | resolute | main |
| `libx11-xcb-dev` | `2:1.8.13-1` | resolute | main |
| `libx11-xcb1` | `2:1.8.13-1` | resolute | main |
| `libx264-165` | `2:0.165.3222+gitb35605ac-3build1` | resolute | universe |
| `libx265-215` | `4.1-4` | resolute | universe |
| `libxapian30` | `1.4.31-2` | resolute | universe |
| `libxapp-gtk3-module` | `3.2.2-1` | resolute | universe |
| `libxapp1` | `3.2.2-1` | resolute | universe |
| `libxau-dev` | `1:1.0.11-1build2` | resolute | main |
| `libxau6` | `1:1.0.11-1build2` | resolute | main |
| `libxaw7` | `2:1.0.16-1build1` | resolute | main |
| `libxaw7-dev` | `2:1.0.16-1build1` | resolute | main |
| `libxbean-reflect-java` | `4.5-9` | resolute | universe |
| `libxcb-composite0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-cursor-dev` | `0.1.6-1` | resolute | universe |
| `libxcb-cursor0` | `0.1.6-1` | resolute | universe |
| `libxcb-damage0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-dpms0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-dri2-0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-dri3-0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-glx0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-icccm4` | `0.4.2-1build1` | resolute | universe |
| `libxcb-image0` | `0.4.0-2build2` | resolute | universe |
| `libxcb-image0-dev` | `0.4.0-2build2` | resolute | universe |
| `libxcb-keysyms1` | `0.4.1-1build1` | resolute | universe |
| `libxcb-present0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-randr0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-randr0-dev` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-record0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-render-util0` | `0.3.10-1build1` | resolute | universe |
| `libxcb-render-util0-dev` | `0.3.10-1build1` | resolute | universe |
| `libxcb-render0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-render0-dev` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-res0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-shape0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-shm0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-shm0-dev` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-sync1` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-util1` | `0.4.1-1build1` | resolute | main |
| `libxcb-xfixes0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-xinerama0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-xinput0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-xkb1` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb-xv0` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb1` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcb1-dev` | `1.17.0-2ubuntu1` | resolute | main |
| `libxcomposite1` | `1:0.4.6-1build1` | resolute | main |
| `libxcursor-dev` | `1:1.2.3-1build1` | resolute | main |
| `libxcursor1` | `1:1.2.3-1build1` | resolute | main |
| `libxcvt0` | `0.1.3-1build1` | resolute | main |
| `libxdamage1` | `1:1.1.7-1` | resolute | main |
| `libxdgutilsbasedir1.0.1` | `1.0.1-3.2` | resolute | universe |
| `libxdgutilsdesktopentry1.0.1` | `1.0.1-3.2` | resolute | universe |
| `libxdmcp-dev` | `1:1.1.5-2` | resolute | main |
| `libxdmcp6` | `1:1.1.5-2` | resolute | main |
| `libxdot4` | `14.1.2-1ubuntu1` | resolute | universe |
| `libxerces-c-dev` | `3.2.4+debian-1.3build2` | resolute | universe |
| `libxerces-c3.2t64` | `3.2.4+debian-1.3build2` | resolute | universe |
| `libxerces2-java` | `2.12.2-1` | resolute | universe |
| `libxext-dev` | `2:1.3.4-1build3` | resolute | main |
| `libxext6` | `2:1.3.4-1build3` | resolute | main |
| `libxfixes-dev` | `1:6.0.0-2build2` | resolute | main |
| `libxfixes3` | `1:6.0.0-2build2` | resolute | main |
| `libxft-dev` | `2.3.6-1build2` | resolute | main |
| `libxft2` | `2.3.6-1build2` | resolute | main |
| `libxi-dev` | `2:1.8.2-2` | resolute | main |
| `libxi6` | `2:1.8.2-2` | resolute | main |
| `libxinerama-dev` | `2:1.1.4-3build2` | resolute | main |
| `libxinerama1` | `2:1.1.4-3build2` | resolute | main |
| `libxkbcommon-dev` | `1.13.1-1` | resolute | main |
| `libxkbcommon-x11-0` | `1.13.1-1` | resolute | main |
| `libxkbcommon0` | `1.13.1-1` | resolute | main |
| `libxkbfile1` | `1:1.1.0-1build5` | resolute | main |
| `libxkbregistry0` | `1.13.1-1` | resolute | main |
| `libxklavier16` | `5.4-6build1` | resolute | main |
| `libxml-commons-external-java` | `1.4.01-6build1` | resolute | universe |
| `libxml-commons-resolver1.1-java` | `1.2-11` | resolute | universe |
| `libxml-parser-perl` | `2.47-1ubuntu1` | resolute | main |
| `libxml-twig-perl` | `1:3.54-1build1` | resolute | main |
| `libxml-xpathengine-perl` | `0.14-2` | resolute | main |
| `libxmlb2` | `0.3.24-2` | resolute | main |
| `libxmlsec1-1` | `1.3.9-1` | resolute | main |
| `libxmlsec1-nss1` | `1.3.9-1` | resolute | main |
| `libxmlsec1-openssl1` | `1.3.9-1` | resolute | main |
| `libxmu-dev` | `2:1.1.3-4` | resolute | main |
| `libxmu-headers` | `2:1.1.3-4` | resolute | main |
| `libxmu6` | `2:1.1.3-4` | resolute | main |
| `libxmuu1` | `2:1.1.3-4` | resolute | main |
| `libxnnpack0.20241108` | `0.0~git20241108.4ea82e5-2build1` | resolute | universe |
| `libxnvctrl0` | `510.47.03-0ubuntu7` | resolute | main |
| `libxpp3-java` | `1.1.4c-4` | resolute | universe |
| `libxpresent1` | `1.0.1-1build1` | resolute | universe |
| `libxrandr-dev` | `2:1.5.4-1build1` | resolute | main |
| `libxrandr2` | `2:1.5.4-1build1` | resolute | main |
| `libxrender-dev` | `1:0.9.12-1build1` | resolute | main |
| `libxrender1` | `1:0.9.12-1build1` | resolute | main |
| `libxres1` | `2:1.2.1-1build2` | resolute | main |
| `libxshmfence1` | `1.3.3-1build1` | resolute | main |
| `libxslt1.1` | `1.1.45-0.1` | resolute | main |
| `libxss-dev` | `1:1.2.3-1build4` | resolute | main |
| `libxss1` | `1:1.2.3-1build4` | resolute | main |
| `libxstream-java` | `1.4.21-1` | resolute | universe |
| `libxt-dev` | `1:1.2.1-1.3build1` | resolute | main |
| `libxt6t64` | `1:1.2.1-1.3build1` | resolute | main |
| `libxtables12` | `1.8.11-2ubuntu3` | resolute | main |
| `libxtst6` | `2:1.2.5-1build1` | resolute | main |
| `libxv-dev` | `2:1.0.13-1` | resolute | main |
| `libxv1` | `2:1.0.13-1` | resolute | main |
| `libxvidcore4` | `2:1.3.7-3` | resolute | universe |
| `libxxf86dga1` | `2:1.1.5-1build2` | resolute | main |
| `libxxf86vm-dev` | `1:1.1.4-2` | resolute | main |
| `libxxf86vm1` | `1:1.1.4-2` | resolute | main |
| `libxxhash-dev` | `0.8.3-2build1` | resolute | main |
| `libxxhash0` | `0.8.3-2build1` | resolute | main |
| `libxz-java` | `1.11+repack-1` | resolute | universe |
| `libyajl2` | `2.1.0-5.1` | resolute | main |
| `libyaml-0-2` | `0.2.5-2build3` | resolute | main |
| `libyaml-cpp-dev` | `0.8.0+dfsg-9` | resolute | main |
| `libyaml-cpp0.8` | `0.8.0+dfsg-9` | resolute | main |
| `libyaml-dev` | `0.2.5-2build3` | resolute | main |
| `libyaml-snake-java` | `2.5+ds-1` | resolute | universe |
| `libyuv-dev` | `0.0.1922.20260106-1` | resolute | main |
| `libyuv0` | `0.0.1922.20260106-1` | resolute | main |
| `libyyjson0` | `0.12.0+ds-1` | resolute | universe |
| `libz-mingw-w64` | `1.3.1+dfsg-2` | resolute | universe |
| `libzbar0t64` | `0.23.93-9ubuntu1` | resolute | universe |
| `libze1` | `1.28.2-2` | resolute | universe |
| `libzen0t64` | `0.4.41-4` | resolute | universe |
| `libzfp1t64` | `1.0.1-4build5` | resolute | universe |
| `libzimg2` | `3.0.6+ds1-1` | resolute | universe |
| `libzip-dev` | `1.11.4-2` | resolute | universe |
| `libzip5` | `1.11.4-2` | resolute | universe |
| `libzix-0-0` | `0.8.0-1` | resolute | universe |
| `libzmq3-dev` | `4.3.5-1build3` | resolute | universe |
| `libzmq5` | `4.3.5-1build3` | resolute | universe |
| `libzopfli1` | `1.0.3-3build1` | resolute | universe |
| `libzstd-dev` | `1.5.7+dfsg-3` | resolute | main |
| `libzstd1` | `1.5.7+dfsg-3` | resolute | main |
| `libzvbi-common` | `0.2.44-1ubuntu2` | resolute | universe |
| `libzvbi0t64` | `0.2.44-1ubuntu2` | resolute | universe |
| `libzxing3` | `2.3.0-5` | resolute | universe |
| `libzzip-0-13t64` | `0.13.78+dfsg.1-0.2` | resolute | universe |
| `libzzip-dev` | `0.13.78+dfsg.1-0.2` | resolute | universe |
| `linguist-qt6` | `6.10.2-1` | resolute | universe |
| `linux-base` | `4.15ubuntu5` | resolute | main |
| `linux-firmware` | `20260319.git217ca6e4.1ubuntu` | resolute | main |
| `linux-sound-base` | `1.0.25+dfsg-0ubuntu9` | resolute | main |
| `linux-sysctl-defaults` | `4.15ubuntu5` | resolute | main |
| `lm-sensors` | `1:3.6.2-2build1` | resolute | universe |
| `login.defs` | `1:4.17.4-2ubuntu3` | resolute | main |
| `logrotate` | `3.22.0-1build1` | resolute | main |
| `logsave` | `1.47.2-3ubuntu4` | resolute | main |
| `lsb-release` | `12.1-2build1` | resolute | main |
| `lshw` | `02.19.git.2021.06.19.996aaad9c7-2.1ubuntu3` | resolute | main |
| `lsof` | `4.99.4+dfsg-2build2` | resolute | main |
| `lto-disabled-list` | `79` | resolute | main |
| `lttng-tools` | `2.14.1-1build1` | resolute | universe |
| `luit` | `2.0.20250912-1` | resolute | main |
| `lvm2` | `2.03.31-2ubuntu3` | resolute | main |
| `lz4` | `1.10.0-8` | resolute | universe |
| `m4` | `1.4.21-1` | resolute | main |
| `make` | `4.4.1-3` | resolute | main |
| `man-db` | `2.13.1-1build1` | resolute | main |
| `manpages` | `6.17-1` | resolute | main |
| `manpages-dev` | `6.17-1` | resolute | main |
| `marble-plugins` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `marble-qt` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `marble-qt-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `mawk` | `1.3.4.20260129-1` | resolute | main |
| `mbox-importer` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `media-player-info` | `26-1build1` | resolute | main |
| `media-types` | `14.0.0build1` | resolute | main |
| `mediainfo` | `26.01-1` | resolute | universe |
| `memtest86+` | `8.00-3` | resolute | main |
| `mercurial` | `7.2-3build1` | resolute | universe |
| `mercurial-common` | `7.2-3build1` | resolute | universe |
| `mesa-utils` | `9.0.0-2build1` | resolute | universe |
| `mesa-utils-bin` | `9.0.0-2build1` | resolute | universe |
| `messagelib-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `milou` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `mintstick` | `1.6.6-1` | resolute | universe |
| `mkdocs` | `1.6.1+dfsg1-2` | resolute | universe |
| `mkdocs-get-deps` | `0.2.0-2` | resolute | universe |
| `mobile-broadband-provider-info` | `20251101-1build1` | resolute | main |
| `mokutil` | `0.7.2-2` | resolute | main |
| `mpi-default-bin` | `1.20` | resolute | universe |
| `mpi-default-dev` | `1.20` | resolute | universe |
| `mscompress` | `0.4-10build2` | resolute | main |
| `mtr-tiny` | `0.95-1.1ubuntu2` | resolute | main |
| `mysql-common` | `5.8+1.1.1ubuntu2` | resolute | main |
| `native-architecture` | `0.2.6build1` | resolute | main |
| `ncurses-base` | `6.6+20251231-1` | resolute | main |
| `ncurses-bin` | `6.6+20251231-1` | resolute | main |
| `neochat` | `25.12.3-0ubuntu1` | resolute | universe |
| `netavark` | `1.16.1-3.1` | resolute | universe |
| `netbase` | `6.5build1` | resolute | main |
| `netcat-openbsd` | `1.234-1` | resolute | main |
| `netpbm` | `2:11.10.02-1build1` | resolute | universe |
| `nettle-dev` | `3.10.2-1` | resolute | main |
| `network-manager-openconnect` | `1.2.10-4.1` | resolute | universe |
| `network-manager-openvpn` | `1.12.5-1` | resolute | main |
| `network-manager-pptp` | `1.2.12-6` | resolute | main |
| `networkd-dispatcher` | `2.2.4-1.1ubuntu1` | resolute | main |
| `nftables` | `1.1.6-1` | resolute | main |
| `ninja-build` | `1.13.2-1` | resolute | universe |
| `nlohmann-json3-dev` | `3.12.0.really.3.12.0.really.3.11.3-3build1` | resolute | main |
| `node-jquery` | `3.7.1+dfsg+~3.5.33-1build1` | resolute | universe |
| `node-popper2` | `2.11.2-9` | resolute | universe |
| `numactl` | `2.0.19-1build1` | resolute | main |
| `nvidia-prime` | `0.8.17.2build1` | resolute | main |
| `nvidia-settings` | `510.47.03-0ubuntu7` | resolute | main |
| `ocean-sound-theme` | `6.6.4-0ubuntu1` | resolute | universe |
| `ocl-icd-libopencl1` | `2.3.4-1` | resolute | main |
| `okular` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `okular-data` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `okular-doc` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `okular-extra-backends` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `openconnect` | `9.12-3.3` | resolute | universe |
| `opencv-data` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `openmpi-bin` | `5.0.10-1` | resolute | universe |
| `openmpi-common` | `5.0.10-1` | resolute | universe |
| `openni-utils` | `1.5.4.0+dfsg-8build1` | resolute | universe |
| `openoffice.org-hyphenation` | `0.10ubuntu3` | resolute | universe |
| `openprinting-ppds` | `20250819-1build1` | resolute | main |
| `openrgb` | `0.9+git20251009+ds-1` | resolute | universe |
| `optipng` | `7.9.1+ds-2build1` | resolute | main |
| `os-prober` | `1.84ubuntu1` | resolute | main |
| `oxygen-sounds` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `p11-kit` | `0.26.2-2` | resolute | main |
| `p11-kit-modules` | `0.26.2-2` | resolute | main |
| `par2` | `1.1.1-1` | resolute | universe |
| `parted` | `3.6-6` | resolute | main |
| `partitionmanager` | `25.12.3-0ubuntu1` | resolute | universe |
| `passt` | `0.0~git20260120.386b5f5-1` | resolute | universe |
| `passwd` | `1:4.17.4-2ubuntu3` | resolute | main |
| `pastebinit` | `1.8.0-1` | resolute | main |
| `patch` | `2.8-2build1` | resolute | main |
| `pci.ids` | `0.0~2026.02.12-1` | resolute | main |
| `pciutils` | `1:3.14.0-1build2` | resolute | main |
| `pcmciautils` | `018-19` | resolute | main |
| `pdfarranger` | `1.13.0-1` | resolute | universe |
| `perl-openssl-defaults` | `7build4` | resolute | main |
| `phonon-backend-vlc-common` | `0.12.0-3build5` | resolute | universe |
| `phonon4qt6` | `4:4.12.0-7` | resolute | universe |
| `phonon4qt6-backend-vlc` | `0.12.0-3build5` | resolute | universe |
| `phonon4settings` | `4:4.12.0-7` | resolute | universe |
| `photocollage` | `1.4.8-0.1build1` | resolute | universe |
| `pim-data-exporter` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `pim-sieve-editor` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `pinentry-qt` | `1.3.2-3ubuntu1` | resolute | universe |
| `pipx` | `1.8.0-1` | resolute | universe |
| `pkg-config` | `2.5.1-4` | resolute | main |
| `pkgconf` | `2.5.1-4` | resolute | main |
| `pkgconf-bin` | `2.5.1-4` | resolute | main |
| `plasma-activities-bin` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-browser-integration` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-disks` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-distro-release-notifier` | `20241226-0ubuntu8` | resolute | universe |
| `plasma-firewall` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-thunderbolt` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-vault` | `6.6.4-0ubuntu1` | resolute | universe |
| `plasma-workspace-wallpapers` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `plocate` | `1.1.23-1ubuntu3` | resolute | universe |
| `plymouth` | `24.004.60+git20250831.4a3c171d-0ubuntu8` | resolute | main |
| `plymouth-label` | `24.004.60+git20250831.4a3c171d-0ubuntu8` | resolute | main |
| `plymouth-theme-breeze` | `6.6.4-0ubuntu1` | resolute | universe |
| `plymouth-theme-kubuntu-logo` | `1:26.04.13` | resolute | universe |
| `plymouth-theme-kubuntu-text` | `1:26.04.13` | resolute | universe |
| `plymouth-theme-spinner` | `24.004.60+git20250831.4a3c171d-0ubuntu8` | resolute | main |
| `plymouth-theme-ubuntu-text` | `24.004.60+git20250831.4a3c171d-0ubuntu8` | resolute | main |
| `pnp.ids` | `0.394-1build1` | resolute | main |
| `podman` | `5.7.0+ds2-3build1` | resolute | universe |
| `policykit-desktop-privileges` | `0.22build1` | resolute | main |
| `polkit-kde-agent-1` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `poppler-data` | `0.4.12-1build1` | resolute | main |
| `postgis` | `3.6.2+dfsg-1` | resolute | universe |
| `postgresql` | `18+290ubuntu1` | resolute | main |
| `postgresql-18-postgis-3` | `3.6.2+dfsg-1` | resolute | universe |
| `postgresql-18-postgis-3-scripts` | `3.6.2+dfsg-1` | resolute | universe |
| `postgresql-client-common` | `290ubuntu1` | resolute | main |
| `postgresql-common` | `290ubuntu1` | resolute | main |
| `postgresql-postgis` | `3.6.2+dfsg-1` | resolute | universe |
| `postgresql-postgis-scripts` | `3.6.2+dfsg-1` | resolute | universe |
| `power-profiles-daemon` | `0.30-2` | resolute | main |
| `powermgmt-base` | `1.38ubuntu2` | resolute | main |
| `ppa-purge` | `0.2.8+bzr63-0ubuntu4` | resolute | universe |
| `ppp` | `2.5.2-1+1.2` | resolute | main |
| `pptp-linux` | `1.10.0-2build1` | resolute | main |
| `printer-driver-brlaser` | `6.2.8-1` | resolute | main |
| `printer-driver-c2esp` | `27-11ubuntu8` | resolute | main |
| `printer-driver-foo2zjs` | `20200505dfsg0-3ubuntu1` | resolute | main |
| `printer-driver-foo2zjs-common` | `20200505dfsg0-3ubuntu1` | resolute | main |
| `printer-driver-gutenprint` | `5.3.4.20220624T01008808d602-4ubuntu2` | resolute | main |
| `printer-driver-m2300w` | `0.51-15build3` | resolute | main |
| `printer-driver-min12xxw` | `0.0.9-11build4` | resolute | main |
| `printer-driver-pnm2ppa` | `1.13+nondbs-0ubuntu11` | resolute | main |
| `printer-driver-ptouch` | `1.7.1-1build1` | resolute | main |
| `printer-driver-pxljr` | `1.4+repack0-6build3` | resolute | main |
| `printer-driver-sag-gdi` | `0.1-8build1` | resolute | main |
| `printer-driver-splix` | `2.0.1-2` | resolute | main |
| `procps` | `2:4.0.4-9ubuntu1` | resolute | main |
| `proj-bin` | `9.7.1-1` | resolute | universe |
| `proj-data` | `9.7.1-1` | resolute | universe |
| `protobuf-compiler` | `3.21.12-15ubuntu1` | resolute | universe |
| `psmisc` | `23.7-2ubuntu2` | resolute | main |
| `publicsuffix` | `20260129.1928-1` | resolute | main |
| `pulseaudio-utils` | `1:17.0+dfsg1-2ubuntu4` | resolute | universe |
| `pybind11-dev` | `3.0.1-3` | resolute | universe |
| `pydocstyle` | `6.3.0-3` | resolute | universe |
| `pyflakes3` | `3.4.0-1` | resolute | universe |
| `pyqt6-dev` | `6.10.2-2build5` | resolute | universe |
| `pyqt6-dev-tools` | `6.10.2-2build5` | resolute | universe |
| `python-babel-localedata` | `2.17.0-2` | resolute | main |
| `python-matplotlib-data` | `3.10.7+dfsg1-2build1` | resolute | universe |
| `python-tinycss2-common` | `1.5.1-1` | resolute | universe |
| `python3` | `3.14.3-0ubuntu2` | resolute | main |
| `python3-annotated-types` | `0.7.0-1` | resolute | universe |
| `python3-apsw` | `3.46.0.1-1build4` | resolute | universe |
| `python3-argcomplete` | `3.6.3-1` | resolute | universe |
| `python3-asn1crypto` | `1.5.1-3build1` | resolute | universe |
| `python3-astroid` | `4.1.1-1` | resolute | universe |
| `python3-asttokens` | `3.0.1-2` | resolute | universe |
| `python3-attr` | `25.4.0-1build1` | resolute | main |
| `python3-autocommand` | `2.2.2-4` | resolute | main |
| `python3-babel` | `2.17.0-2` | resolute | main |
| `python3-bcj` | `1.0.7+ds-2build1` | resolute | universe |
| `python3-bcrypt` | `5.0.0-3build1` | resolute | main |
| `python3-blinker` | `1.9.0-2build1` | resolute | main |
| `python3-bpfcc` | `0.35.0+ds-1ubuntu2` | resolute | main |
| `python3-breezy` | `3.3.21-1build1` | resolute | universe |
| `python3-brlapi` | `6.7-1ubuntu6` | resolute | main |
| `python3-brotli` | `1.2.0-3build1` | resolute | universe |
| `python3-brotlicffi` | `1.2.0.0+ds-2` | resolute | universe |
| `python3-bs4` | `4.14.3-2build1` | resolute | main |
| `python3-bt2` | `2.1.2-1build2` | resolute | universe |
| `python3-cachecontrol` | `0.14.3-1` | resolute | universe |
| `python3-cairo` | `1.27.0-2build2` | resolute | main |
| `python3-certifi` | `2026.1.4+ds-1` | resolute | main |
| `python3-cffi-backend` | `2.0.0-3build1` | resolute | main |
| `python3-chardet` | `5.2.0+dfsg-2build1` | resolute | main |
| `python3-chm` | `0.8.6+ds-7build1` | resolute | universe |
| `python3-click` | `8.2.0+0.really.8.1.8-1build1` | resolute | main |
| `python3-commandnotfound` | `23.04.0build1` | resolute | main |
| `python3-configobj` | `5.0.9-1build1` | resolute | main |
| `python3-contourpy` | `1.3.3-1build1` | resolute | universe |
| `python3-coverage` | `7.13.5+dfsg1-0ubuntu1` | resolute | universe |
| `python3-css-parser` | `1.0.10-1build1` | resolute | universe |
| `python3-cssselect` | `1.4.0-1` | resolute | main |
| `python3-cups` | `2.0.4-3build1` | resolute | main |
| `python3-cupshelpers` | `1.5.18-4ubuntu2` | resolute | main |
| `python3-cycler` | `0.12.1-2` | resolute | universe |
| `python3-dasbus` | `1.7-2build1` | resolute | main |
| `python3-dateutil` | `2.9.0-4build1` | resolute | main |
| `python3-dbus` | `1.4.0-1build2` | resolute | main |
| `python3-dbus.mainloop.pyqt6` | `6.10.2-2build5` | resolute | universe |
| `python3-debconf` | `1.5.92` | resolute | main |
| `python3-debian` | `1.0.1ubuntu2` | resolute | main |
| `python3-decorator` | `5.2.1-2` | resolute | main |
| `python3-deprecated` | `1.3.1-1` | resolute | universe |
| `python3-dev` | `3.14.3-0ubuntu2` | resolute | main |
| `python3-distlib` | `0.4.0-1` | resolute | universe |
| `python3-distro` | `1.9.0-1build1` | resolute | main |
| `python3-distro-info` | `1.15` | resolute | main |
| `python3-dnspython` | `2.8.0-1ubuntu1` | resolute | main |
| `python3-docutils` | `0.22.4+dfsg-1` | resolute | main |
| `python3-dulwich` | `1.1.0-3` | resolute | universe |
| `python3-email-validator` | `2.2.0-1` | resolute | universe |
| `python3-empy` | `4.2.1-1` | resolute | universe |
| `python3-executing` | `2.2.1-0.1` | resolute | universe |
| `python3-fastbencode` | `0.3.8-1build1` | resolute | universe |
| `python3-fastimport` | `0.9.14-2.1build1` | resolute | universe |
| `python3-feedparser` | `6.0.12-1` | resolute | universe |
| `python3-flake8` | `7.3.0-1` | resolute | universe |
| `python3-flake8-blind-except` | `0.2.1-1build1` | resolute | universe |
| `python3-flake8-builtins` | `3.1.0-1` | resolute | universe |
| `python3-flake8-class-newline` | `1.6.0-6build1` | resolute | universe |
| `python3-flake8-comprehensions` | `3.17.0-1` | resolute | universe |
| `python3-flake8-deprecated` | `2.3.0-1` | resolute | universe |
| `python3-flake8-import-order` | `0.19.2-1` | resolute | universe |
| `python3-flake8-quotes` | `3.4.0-4build1` | resolute | universe |
| `python3-fonttools` | `4.61.1-3build1` | resolute | universe |
| `python3-gdal` | `3.12.2+dfsg-1build2` | resolute | universe |
| `python3-gdbm` | `3.14.3-0ubuntu2` | resolute | main |
| `python3-gi` | `3.56.2-1` | resolute | main |
| `python3-gi-cairo` | `3.56.2-1` | resolute | main |
| `python3-github` | `2.6.1-1` | resolute | universe |
| `python3-gnupg` | `0.5.4-1` | resolute | universe |
| `python3-gpg` | `2.0.0-2build1` | resolute | main |
| `python3-html2text` | `2025.4.15-1` | resolute | universe |
| `python3-html5-parser` | `0.4.12+ds-8build1` | resolute | universe |
| `python3-html5lib` | `1.2-3` | resolute | main |
| `python3-ifaddr` | `0.2.0-2` | resolute | universe |
| `python3-img2pdf` | `0.6.2-1` | resolute | universe |
| `python3-inflate64` | `1.0.4+ds-2build1` | resolute | universe |
| `python3-inflect` | `7.5.0-1build1` | resolute | main |
| `python3-iniconfig` | `2.1.0-2` | resolute | universe |
| `python3-ipython` | `9.11.0-1` | resolute | universe |
| `python3-ipython-pygments-lexers` | `1.1.1-2` | resolute | universe |
| `python3-jaraco.context` | `6.0.1-2` | resolute | main |
| `python3-jaraco.functools` | `4.1.0-1build1` | resolute | main |
| `python3-jaraco.text` | `4.0.0-1build1` | resolute | main |
| `python3-jedi` | `0.19.1+ds1-1build1` | resolute | universe |
| `python3-jeepney` | `0.9.0-2` | resolute | universe |
| `python3-jinja2` | `3.1.6-1build1` | resolute | main |
| `python3-joblib` | `1.5.2-1` | resolute | universe |
| `python3-kiwisolver` | `1.4.10~rc0-1build1` | resolute | universe |
| `python3-lark` | `1.3.1-1` | resolute | universe |
| `python3-launchpadlib` | `2.1.0-1build1` | resolute | main |
| `python3-lazr.restfulclient` | `0.14.6-3build1` | resolute | main |
| `python3-lazr.uri` | `1.0.6-7build1` | resolute | main |
| `python3-legacy-cgi` | `2.6.4-2` | resolute | main |
| `python3-librt` | `0.7.3-1build1` | resolute | universe |
| `python3-linkify-it` | `2.0.3-1ubuntu3` | resolute | main |
| `python3-livereload` | `2.7.1-0.1` | resolute | universe |
| `python3-louis` | `3.36.0-1` | resolute | main |
| `python3-lunr` | `0.8.0-1` | resolute | universe |
| `python3-lxml` | `6.0.2-1build1` | resolute | main |
| `python3-lxml-html-clean` | `0.4.4-1` | resolute | universe |
| `python3-lz4` | `4.4.5+dfsg-1build1` | resolute | universe |
| `python3-markdown` | `3.10.2-1` | resolute | main |
| `python3-markdown-it` | `3.0.0-3build1` | resolute | main |
| `python3-markupsafe` | `3.0.3-1build1` | resolute | main |
| `python3-matplotlib` | `3.10.7+dfsg1-2build1` | resolute | universe |
| `python3-matplotlib-inline` | `0.2.1-1` | resolute | universe |
| `python3-mccabe` | `0.7.0-1build1` | resolute | universe |
| `python3-mdurl` | `0.1.2-1build1` | resolute | main |
| `python3-mechanize` | `1:0.4.10+ds-7` | resolute | universe |
| `python3-merge3` | `0.0.8-1build1` | resolute | universe |
| `python3-mergedeep` | `1.3.4-4build1` | resolute | universe |
| `python3-minimal` | `3.14.3-0ubuntu2` | resolute | main |
| `python3-more-itertools` | `10.8.0-1build1` | resolute | main |
| `python3-mpi4py` | `4.1.1-1ubuntu2` | resolute | universe |
| `python3-mpmath` | `1.3.0-2` | resolute | universe |
| `python3-msgpack` | `1.1.2-2build1` | resolute | main |
| `python3-multivolumefile` | `0.2.3-6` | resolute | universe |
| `python3-munkres` | `1.1.4-3build1` | resolute | universe |
| `python3-mutagen` | `1.47.0-1build1` | resolute | universe |
| `python3-mypy` | `1.19.1-5build1` | resolute | universe |
| `python3-mypy-extensions` | `1.1.0-1` | resolute | universe |
| `python3-nacl` | `1.5.0-8` | resolute | main |
| `python3-netaddr` | `1.3.0-1build1` | resolute | main |
| `python3-netifaces` | `0.11.0-2build7` | resolute | main |
| `python3-nltk` | `3.9.2-1` | resolute | universe |
| `python3-notify2` | `0.3.1-2` | resolute | universe |
| `python3-numpy` | `1:2.3.5+ds-3ubuntu1` | resolute | main |
| `python3-numpy-dev` | `1:2.3.5+ds-3ubuntu1` | resolute | main |
| `python3-oauthlib` | `3.3.1-1build1` | resolute | main |
| `python3-olefile` | `0.47-1build1` | resolute | main |
| `python3-opencv` | `4.10.0+dfsg-7ubuntu5` | resolute | universe |
| `python3-orjson` | `3.11.5-1build1` | resolute | universe |
| `python3-packaging` | `26.0-1` | resolute | main |
| `python3-parso` | `0.8.5-1` | resolute | universe |
| `python3-parted` | `3.13.0-1build4` | resolute | universe |
| `python3-pathspec` | `1.0.4-1` | resolute | universe |
| `python3-patiencediff` | `0.2.13-1build6` | resolute | universe |
| `python3-pexpect` | `4.9-4` | resolute | main |
| `python3-pikepdf` | `10.3.0+dfsg-1build1` | resolute | universe |
| `python3-pip` | `25.1.1+dfsg-1ubuntu2` | resolute | universe |
| `python3-pip-whl` | `25.1.1+dfsg-1ubuntu2` | resolute | universe |
| `python3-pkg-resources` | `78.1.1-0.1build1` | resolute | main |
| `python3-platformdirs` | `4.9.4-1` | resolute | main |
| `python3-pluggy` | `1.6.0-2` | resolute | universe |
| `python3-ply` | `3.11-10` | resolute | main |
| `python3-prompt-toolkit` | `3.0.52-2` | resolute | universe |
| `python3-protobuf` | `3.21.12-15ubuntu1` | resolute | universe |
| `python3-psutil` | `7.1.0-1ubuntu1` | resolute | main |
| `python3-ptyprocess` | `0.7.0-6build1` | resolute | main |
| `python3-pure-eval` | `0.2.3-1` | resolute | universe |
| `python3-py7zr` | `1.1.2+dfsg-1` | resolute | universe |
| `python3-pyasyncore` | `1.0.2-3build1` | resolute | main |
| `python3-pycodestyle` | `2.14.0-1` | resolute | universe |
| `python3-pycriu` | `4.2-1ubuntu2` | resolute | universe |
| `python3-pycryptodome` | `3.20.0+dfsg-3build1` | resolute | universe |
| `python3-pydantic` | `2.12.5-2` | resolute | universe |
| `python3-pydantic-core` | `2.41.5-2build1` | resolute | universe |
| `python3-pydocstyle` | `6.3.0-3` | resolute | universe |
| `python3-pydot` | `4.0.1-1` | resolute | universe |
| `python3-pyflakes` | `3.4.0-1` | resolute | universe |
| `python3-pygments` | `2.19.2+dfsg-1` | resolute | main |
| `python3-pygraphviz` | `1.14-5build1` | resolute | universe |
| `python3-pyinotify` | `0.9.6-5build1` | resolute | main |
| `python3-pykdl` | `1.5.2-1` | resolute | universe |
| `python3-pylibacl` | `0.7.2-1build2` | resolute | main |
| `python3-pyparsing` | `3.3.2-2` | resolute | main |
| `python3-pyppmd` | `1.3.1+ds-2build1` | resolute | universe |
| `python3-pyqt5` | `5.15.11+dfsg-3build3` | resolute | universe |
| `python3-pyqt5.sip` | `12.17.2-1build1` | resolute | universe |
| `python3-pyqt6` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtmultimedia` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtqml` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtquick` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtsvg` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qttexttospeech` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtwebchannel` | `6.10.2-2build5` | resolute | universe |
| `python3-pyqt6.qtwebengine` | `6.10.0-1` | resolute | universe |
| `python3-pyqt6.sip` | `13.11.0-1build1` | resolute | universe |
| `python3-pyqtbuild` | `1.19.0+dfsg-1` | resolute | universe |
| `python3-pyside6.qtcore` | `6.10.2-6ubuntu1` | resolute | universe |
| `python3-pyside6.qtgui` | `6.10.2-6ubuntu1` | resolute | universe |
| `python3-pyside6.qtsvg` | `6.10.2-6ubuntu1` | resolute | universe |
| `python3-pyside6.qtwidgets` | `6.10.2-6ubuntu1` | resolute | universe |
| `python3-pystache` | `0.6.8-2` | resolute | universe |
| `python3-pytest` | `9.0.2-4` | resolute | universe |
| `python3-pytest-cov` | `5.0.0-1` | resolute | universe |
| `python3-pyxattr` | `0.8.1-1build6` | resolute | main |
| `python3-pyyaml-env-tag` | `1.1-1` | resolute | universe |
| `python3-regex` | `0.1.20250918-1build1` | resolute | universe |
| `python3-repoze.lru` | `0.7-3build1` | resolute | main |
| `python3-requests-toolbelt` | `1.0.0-4` | resolute | universe |
| `python3-rich` | `13.9.4-1.2` | resolute | main |
| `python3-roman-numerals` | `4.1.0-1` | resolute | main |
| `python3-routes` | `2.5.1-7build1` | resolute | main |
| `python3-scour` | `0.38.2-6` | resolute | universe |
| `python3-sentry-sdk` | `2.22.0-1` | resolute | universe |
| `python3-serial` | `3.5-2build1` | resolute | main |
| `python3-setproctitle` | `1.3.7-2build1` | resolute | main |
| `python3-setuptools` | `78.1.1-0.1build1` | resolute | main |
| `python3-setuptools-whl` | `78.1.1-0.1build1` | resolute | universe |
| `python3-sgmllib3k` | `1.0.0-5build1` | resolute | universe |
| `python3-sipbuild` | `6.15.1-1` | resolute | universe |
| `python3-six` | `1.17.0-2build1` | resolute | main |
| `python3-snowballstemmer` | `3.0.1-1` | resolute | main |
| `python3-soupsieve` | `2.8.3-1` | resolute | main |
| `python3-speechd` | `0.12.1-2ubuntu1` | resolute | main |
| `python3-sshsig` | `0.2.2-2` | resolute | universe |
| `python3-stack-data` | `0.6.3-3` | resolute | universe |
| `python3-sympy` | `1.14.0-2` | resolute | universe |
| `python3-systemd` | `235-1build9` | resolute | main |
| `python3-texttable` | `1.7.0-1build1` | resolute | universe |
| `python3-tinycss2` | `1.5.1-1` | resolute | universe |
| `python3-tk` | `3.14.3-0ubuntu2` | resolute | universe |
| `python3-tomli-w` | `1.2.0-2` | resolute | universe |
| `python3-tqdm` | `4.67.3-1build1` | resolute | universe |
| `python3-traitlets` | `5.14.3+really5.14.3-3` | resolute | universe |
| `python3-typeguard` | `4.4.4-2` | resolute | main |
| `python3-typeshed` | `0.0~git20260204.516eed0-1` | resolute | universe |
| `python3-typing-extensions` | `4.15.0-2` | resolute | main |
| `python3-typing-inspection` | `0.4.2-1` | resolute | universe |
| `python3-tzlocal` | `5.3.1-2` | resolute | universe |
| `python3-uc-micro` | `1.0.3-1build1` | resolute | main |
| `python3-ufolib2` | `0.18.1+dfsg1-1` | resolute | universe |
| `python3-unicodedata2` | `16.0.0+ds-1build2` | resolute | universe |
| `python3-unidecode` | `1.4.0-1` | resolute | universe |
| `python3-update-manager` | `1:26.04.5` | resolute | main |
| `python3-userpath` | `1.9.2-2` | resolute | universe |
| `python3-venv` | `3.14.3-0ubuntu2` | resolute | universe |
| `python3-vtk9` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `python3-wadllib` | `2.0.0-3` | resolute | main |
| `python3-watchdog` | `6.0.0-4` | resolute | universe |
| `python3-wcwidth` | `0.2.14+dfsg1-1build1` | resolute | main |
| `python3-webencodings` | `0.5.1-5build1` | resolute | main |
| `python3-websockets` | `15.0.1-1build2` | resolute | universe |
| `python3-wheel` | `0.46.3-2` | resolute | universe |
| `python3-wrapt` | `2.1.1-1` | resolute | main |
| `python3-xdg` | `0.28-3` | resolute | main |
| `python3-xkit` | `0.5.0ubuntu8` | resolute | main |
| `python3-xxhash` | `3.2.0-1build7` | resolute | universe |
| `python3-yaml` | `6.0.3-1build1` | resolute | main |
| `python3-zeroconf` | `0.148.0-2` | resolute | universe |
| `python3-zipp` | `3.23.0-1build1` | resolute | main |
| `python3-zopfli` | `0.4.1-1` | resolute | universe |
| `python3-zstandard` | `0.25.0-1build1` | resolute | universe |
| `qdbus-qt6` | `6.10.2-1` | resolute | universe |
| `qdoc-qt6` | `6.10.2-1` | resolute | universe |
| `qmake6` | `6.10.2+dfsg-7` | resolute | universe |
| `qmake6-bin` | `6.10.2+dfsg-7` | resolute | universe |
| `qml-module-org-kde-kirigami2` | `5.116.0-1ubuntu4` | resolute | universe |
| `qml-module-org-kde-kquickcontrolsaddons` | `5.116.0-1ubuntu1` | resolute | universe |
| `qml-module-org-kde-qqc2desktopstyle` | `5.116.1-2` | resolute | universe |
| `qml-module-org-kde-sonnet` | `5.116.0-1ubuntu2` | resolute | universe |
| `qml-module-qtgraphicaleffects` | `5.15.18-1` | resolute | universe |
| `qml-module-qtqml-models2` | `5.15.18+dfsg-2` | resolute | universe |
| `qml-module-qtquick-controls2` | `5.15.18+dfsg-1` | resolute | universe |
| `qml-module-qtquick-layouts` | `5.15.18+dfsg-2` | resolute | universe |
| `qml-module-qtquick-templates2` | `5.15.18+dfsg-1` | resolute | universe |
| `qml-module-qtquick-window2` | `5.15.18+dfsg-2` | resolute | universe |
| `qml-module-qtquick2` | `5.15.18+dfsg-2` | resolute | universe |
| `qml6-module-org-kde-activities` | `6.6.4-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-baloo` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-bluezqt` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-config` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-desktop` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-draganddrop` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-graphicaleffects` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-iconthemes` | `6.24.0-0ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kcmutils` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kholidays` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kirigami` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-components` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-datetime` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-delegates` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-formcard` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-labs-components` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-settings` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-statefulapp` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-tableview` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kirigamiaddons-treeview` | `1.11.0-2ubuntu2` | resolute | universe |
| `qml6-module-org-kde-kitemmodels` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kquickcontrols` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kquickcontrolsaddons` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-ksvg` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-kwindowsystem` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-layershell` | `6.6.4-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-networkmanager` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-newstuff` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-notifications` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-pipewire` | `6.6.4-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-plasma-plasma5support` | `4:6.6.4-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-prison` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-purpose` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-quickcharts` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-sonnet` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-syntaxhighlighting` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-org-kde-userfeedback` | `6.24.0-0ubuntu1` | resolute | universe |
| `qml6-module-qml` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qmltime` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-animation` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-assetdownloader` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-folderlistmodel` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-platform` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-qmlmodels` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-settings` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-sharedimage` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-synchronizer` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt-labs-wavefrontmesh` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qt5compat-graphicaleffects` | `6.10.2-1` | resolute | universe |
| `qml6-module-qtcharts` | `6.10.2-1` | resolute | universe |
| `qml6-module-qtcore` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtlocation` | `6.10.2-1` | resolute | universe |
| `qml6-module-qtmultimedia` | `6.10.2-2` | resolute | universe |
| `qml6-module-qtnetwork` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtpositioning` | `6.10.2-1` | resolute | universe |
| `qml6-module-qtqml` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtqml-models` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtqml-workerscript` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtqml-xmllistmodel` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-controls` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-dialogs` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-effects` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-layouts` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-localstorage` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-particles` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-shapes` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-shapes-designhelpers` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-templates` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-tooling` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-vectorimage` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-vectorimage-helpers` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick-virtualkeyboard` | `6.10.2+dfsg-1` | resolute | universe |
| `qml6-module-qtquick-window` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtquick3d` | `6.10.2-1` | resolute | universe |
| `qml6-module-qttest` | `6.10.2+dfsg-3` | resolute | universe |
| `qml6-module-qtwebchannel` | `6.10.2-1` | resolute | universe |
| `qml6-module-qtwebengine` | `6.10.2+dfsg-1` | resolute | universe |
| `qml6-module-qtwebengine-controlsdelegates` | `6.10.2+dfsg-1` | resolute | universe |
| `qml6-module-qtwebview` | `6.10.2-1` | resolute | universe |
| `qml6-module-sso-onlineaccounts` | `0.7+git20231028.05e79eb-7` | resolute | universe |
| `qrca` | `25.12.3-0ubuntu1` | resolute | universe |
| `qt5-gtk-platformtheme` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `qt5-qmake` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `qt5-qmake-bin` | `5.15.18+dfsg-1ubuntu1` | resolute | universe |
| `qt6-5compat-dev` | `6.10.2-1` | resolute | universe |
| `qt6-base-dev` | `6.10.2+dfsg-7` | resolute | universe |
| `qt6-base-dev-tools` | `6.10.2+dfsg-7` | resolute | universe |
| `qt6-base-private-dev` | `6.10.2+dfsg-7` | resolute | universe |
| `qt6-declarative-dev` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-declarative-dev-tools` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-declarative-private-dev` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-documentation-tools` | `6.10.2-1` | resolute | universe |
| `qt6-gtk-platformtheme` | `6.10.2+dfsg-7` | resolute | universe |
| `qt6-image-formats-plugins` | `6.10.2-1` | resolute | universe |
| `qt6-l10n-tools` | `6.10.2-1` | resolute | universe |
| `qt6-location-plugins` | `6.10.2-1` | resolute | universe |
| `qt6-qmllint-plugins` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-qmlls-plugins` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-qmltooling-plugins` | `6.10.2+dfsg-3` | resolute | universe |
| `qt6-qpa-plugins` | `6.10.2+dfsg-7` | resolute | universe |
| `qt6-speech-flite-plugin` | `6.10.2-1` | resolute | universe |
| `qt6-svg-dev` | `6.10.2-2` | resolute | universe |
| `qt6-svg-plugins` | `6.10.2-2` | resolute | universe |
| `qt6-tools-dev-tools` | `6.10.2-1` | resolute | universe |
| `qt6-translations-l10n` | `6.10.2-1` | resolute | universe |
| `qt6-virtualkeyboard-plugin` | `6.10.2+dfsg-1` | resolute | universe |
| `qt6-wayland` | `6.10.2-4` | resolute | universe |
| `qtchooser` | `66-2build3` | resolute | universe |
| `qtspeech5-speechd-plugin` | `5.15.18-1` | resolute | universe |
| `qttranslations5-l10n` | `5.15.18-1` | resolute | universe |
| `qtwayland5` | `5.15.18-1` | resolute | universe |
| `rake` | `13.3.1-1` | resolute | main |
| `rapidjson-dev` | `1.1.0+dfsg2-7.6ubuntu1` | resolute | universe |
| `readline-common` | `8.3-4` | resolute | main |
| `redis-server` | `5:8.0.5-1` | resolute | universe |
| `redis-tools` | `5:8.0.5-1` | resolute | universe |
| `restic` | `0.18.1-3ubuntu1` | resolute | main |
| `rpcsvc-proto` | `1.4.3-1build1` | resolute | main |
| `rpi-imager` | `1.8.5+noembed-0ubuntu6` | resolute | universe |
| `rtkit` | `0.14-1` | resolute | main |
| `ruby` | `1:3.3build1` | resolute | main |
| `ruby-csv` | `3.3.5-1` | resolute | main |
| `ruby-did-you-mean` | `2.0.0-1` | resolute | main |
| `ruby-net-telnet` | `0.2.0-1build1` | resolute | main |
| `ruby-ruby2-keywords` | `0.0.5-1build1` | resolute | main |
| `ruby-rubygems` | `3.6.7-2ubuntu2` | resolute | main |
| `ruby-sdbm` | `1.0.0-5build6` | resolute | main |
| `ruby-webrick` | `1.9.2-1` | resolute | main |
| `ruby-xmlrpc` | `0.3.3-2build1` | resolute | main |
| `rubygems-integration` | `1.19build1` | resolute | main |
| `sane-airscan` | `0.99.36-2ubuntu1` | resolute | main |
| `sane-utils` | `1.4.0-1ubuntu1` | resolute | main |
| `sbsigntool` | `0.9.4-3.1ubuntu9` | resolute | main |
| `screen` | `4.9.1-3ubuntu2` | resolute | main |
| `screen-resolution-extra` | `0.18.5build1` | resolute | main |
| `sddm` | `0.21.0+git20250502.4fe234b-2ubuntu3` | resolute | universe |
| `secureboot-db` | `1.9build2` | resolute | main |
| `sensible-utils` | `0.0.26build1` | resolute | main |
| `sgml-base` | `1.31+nmu1build1` | resolute | main |
| `sgml-data` | `2.0.11+nmu1build1` | resolute | main |
| `shared-mime-info` | `2.4-5build3` | resolute | main |
| `shiboken6` | `6.10.2-6ubuntu1` | resolute | universe |
| `shim-signed` | `1.59+15.8-0ubuntu2` | resolute | main |
| `signon-kwallet-extension` | `4:25.12.3-0ubuntu1` | resolute | universe |
| `signon-plugin-oauth2` | `0.25+git20231015.fab69886-3build1` | resolute | universe |
| `signon-ui-qt` | `0.17+git20231016.eef943f-3build1` | resolute | universe |
| `signon-ui-service` | `0.17+git20231016.eef943f-3build1` | resolute | universe |
| `skanpage` | `25.12.3-0ubuntu1` | resolute | universe |
| `slirp4netns` | `1.3.3-1` | resolute | universe |
| `smartmontools` | `7.5-2` | resolute | main |
| `sonnet-plugins` | `5.116.0-1ubuntu2` | resolute | universe |
| `sonnet6-plugins` | `6.24.0-0ubuntu1` | resolute | universe |
| `sound-icons` | `0.1-8build1` | resolute | main |
| `sound-theme-freedesktop` | `0.8-7build1` | resolute | main |
| `speech-dispatcher` | `0.12.1-2ubuntu1` | resolute | main |
| `speech-dispatcher-audio-plugins` | `0.12.1-2ubuntu1` | resolute | main |
| `speech-dispatcher-espeak-ng` | `0.12.1-2ubuntu1` | resolute | main |
| `sphinx-rtd-theme-common` | `3.1.0+dfsg-1` | resolute | main |
| `spirv-headers` | `1.6.1+1.4.341.0-1` | resolute | universe |
| `spirv-tools-dev` | `2026.1-1` | resolute | universe |
| `spirv-tools-headers` | `2026.1-1` | resolute | universe |
| `squashfs-tools` | `1:4.7.5-1` | resolute | main |
| `sse3-support` | `27ubuntu2` | resolute | universe |
| `sshpass` | `1.10-0.1build1` | resolute | universe |
| `ssl-cert` | `1.1.3ubuntu2` | resolute | main |
| `steam-libs` | `1:1.0.0.85~ds-2build1` | resolute | universe |
| `strace` | `6.19+ds-0ubuntu5` | resolute | main |
| `subversion` | `1.14.5-6build1` | resolute | universe |
| `sudo-common` | `1.2ubuntu` | resolute | main |
| `swh-plugins` | `0.4.17-3build2` | resolute | universe |
| `switcheroo-control` | `3.0-2` | resolute | main |
| `synaptic` | `0.91.7build1` | resolute | universe |
| `sysstat` | `12.7.7-0ubuntu2` | resolute | main |
| `system-config-printer-common` | `1.5.18-4ubuntu2` | resolute | main |
| `system-config-printer-udev` | `1.5.18-4ubuntu2` | resolute | main |
| `systemd-hwe-hwdb` | `259.5.3ubuntu` | resolute | main |
| `sysvinit-utils` | `3.15-5ubuntu1` | resolute | main |
| `tango-icon-theme` | `0.9.0-1build1` | resolute | universe |
| `tcl` | `8.6.16build1` | resolute | main |
| `tcl8.6` | `8.6.17+dfsg-1build1` | resolute | main |
| `tcpdump` | `4.99.6-1` | resolute | main |
| `tesseract-ocr` | `5.5.0-1build1` | resolute | universe |
| `tesseract-ocr-eng` | `1:4.1.0-2build1` | resolute | universe |
| `tesseract-ocr-osd` | `1:4.1.0-2build1` | resolute | universe |
| `testng` | `6.9.12-5` | resolute | universe |
| `thin-provisioning-tools` | `1.1.0-4ubuntu2` | resolute | main |
| `time` | `1.9-0.4` | resolute | main |
| `timgm6mb-soundfont` | `1.3-5build1` | resolute | universe |
| `tnftp` | `20260211-1` | resolute | main |
| `tokodon` | `25.12.3-0ubuntu1` | resolute | universe |
| `tpm-udev` | `4.1.3-6` | resolute | main |
| `trace-cmd` | `3.3.3-1ubuntu2` | resolute | main |
| `tree` | `2.3.1-1` | resolute | universe |
| `ubuntu-drivers-common` | `1:0.10.9` | resolute | main |
| `ubuntu-keyring` | `2023.11.28.1build1` | resolute | main |
| `ucf` | `3.0052ubuntu1` | resolute | main |
| `ufw` | `0.36.2-9build1` | resolute | main |
| `uidmap` | `1:4.17.4-2ubuntu3` | resolute | main |
| `unar` | `1.10.8+ds1-9build1` | resolute | universe |
| `unattended-upgrades` | `2.12ubuntu9` | resolute | main |
| `uncrustify` | `0.78.1+dfsg1-1build1` | resolute | universe |
| `unicode-data` | `16.0.0-1build1` | resolute | universe |
| `unixodbc-common` | `2.3.14-1` | resolute | main |
| `unixodbc-dev` | `2.3.14-1` | resolute | main |
| `unzip` | `6.0-29ubuntu1` | resolute | main |
| `update-inetd` | `4.54build1` | resolute | main |
| `update-manager-core` | `1:26.04.5` | resolute | main |
| `upower` | `1.91.1-1` | resolute | main |
| `usb-creator-common` | `0.4.1build1` | resolute | main |
| `usb-creator-kde` | `0.4.1build1` | resolute | universe |
| `usb-modeswitch` | `2.6.2-1ubuntu1` | resolute | main |
| `usb-modeswitch-data` | `20191128-7build1` | resolute | main |
| `usb.ids` | `2025.12.13-1` | resolute | main |
| `usbmuxd` | `1.1.1-7` | resolute | main |
| `usbutils` | `1:019-1` | resolute | main |
| `user-session-migration` | `0.5.1` | resolute | main |
| `va-driver-all` | `2.23.0-1ubuntu1` | resolute | universe |
| `vlc` | `3.0.23-1` | resolute | universe |
| `vlc-bin` | `3.0.23-1` | resolute | universe |
| `vlc-data` | `3.0.23-1` | resolute | universe |
| `vlc-l10n` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-access-extra` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-base` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-notify` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-qt` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-samba` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-skins2` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-video-output` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-video-splitter` | `3.0.23-1` | resolute | universe |
| `vlc-plugin-visualization` | `3.0.23-1` | resolute | universe |
| `vpnc-scripts` | `0.1~git20220510-1.1` | resolute | universe |
| `vtk9` | `9.5.2+dfsg4-3ubuntu1` | resolute | universe |
| `vulkan-tools` | `1.4.341.0+dfsg1-1` | resolute | universe |
| `wamerican` | `2020.12.07-4build1` | resolute | main |
| `wayland-utils` | `1.3.0-1` | resolute | universe |
| `wbritish` | `2020.12.07-4build1` | resolute | main |
| `webp` | `1.5.0-0.1build1` | resolute | universe |
| `whiptail` | `0.52.25-1ubuntu3` | resolute | main |
| `whoopsie` | `0.2.82ubuntu` | resolute | main |
| `wine` | `10.0~repack-12ubuntu1` | resolute | universe |
| `wine-common` | `10.0~repack-12ubuntu1` | resolute | universe |
| `wine64` | `10.0~repack-12ubuntu1` | resolute | universe |
| `wireplumber` | `0.5.13-1ubuntu1` | resolute | main |
| `wpasupplicant` | `2:2.11-0ubuntu5` | resolute | main |
| `wvdial` | `1.61-8build1` | resolute | universe |
| `x11-common` | `1:7.7+26ubuntu1` | resolute | main |
| `x11-utils` | `7.7+7build1` | resolute | main |
| `x11-xkb-utils` | `7.7+9build1` | resolute | main |
| `x11-xserver-utils` | `7.7+11build1` | resolute | main |
| `x11proto-dev` | `2025.1-1` | resolute | main |
| `xapp-sn-watcher` | `3.2.2-1` | resolute | universe |
| `xapp-symbolic-icons` | `1.0.9-2` | resolute | universe |
| `xapps-common` | `3.2.2-1` | resolute | universe |
| `xauth` | `1:1.1.2-1.1build1` | resolute | main |
| `xbitmaps` | `1.1.1-2.2build1` | resolute | universe |
| `xbrlapi` | `6.7-1ubuntu6` | resolute | main |
| `xcvt` | `0.1.3-1build1` | resolute | main |
| `xdg-dbus-proxy` | `0.1.7-1` | resolute | main |
| `xdg-desktop-portal-gtk` | `1.15.3-2ubuntu1` | resolute | main |
| `xdg-user-dirs` | `0.19-1` | resolute | main |
| `xdg-utils` | `1.2.1-2ubuntu2` | resolute | main |
| `xfonts-base` | `1:1.0.5+nmu1build1` | resolute | main |
| `xfonts-encodings` | `1:1.0.5-0ubuntu3` | resolute | main |
| `xfonts-utils` | `1:7.7+7build1` | resolute | main |
| `xfsprogs` | `6.18.0-3` | resolute | main |
| `xkb-data` | `2.46-2` | resolute | main |
| `xml-core` | `0.19build1` | resolute | main |
| `xorg-sgml-doctools` | `1:1.11-1.1build1` | resolute | main |
| `xorriso` | `1:1.5.6-1.1ubuntu4` | resolute | main |
| `xsettingsd` | `1.0.2-1build2` | resolute | universe |
| `xterm` | `407-1ubuntu1` | resolute | universe |
| `xtrans-dev` | `1.6.0-1build1` | resolute | main |
| `xwayland` | `2:24.1.10-1` | resolute | main |
| `xz-utils` | `5.8.3-1` | resolute | main |
| `zenity` | `4.2.1-1` | resolute | main |
| `zenity-common` | `4.2.1-1` | resolute | main |
| `zip` | `3.0-15ubuntu3` | resolute | main |
| `zipcmp` | `1.11.4-2` | resolute | universe |
| `zipmerge` | `1.11.4-2` | resolute | universe |
| `ziptool` | `1.11.4-2` | resolute | universe |
| `zstd` | `1.5.7+dfsg-3` | resolute | main |
| `zsync` | `0.6.2-9` | resolute | universe |

</details>

### Not in any apt index (locally built, or source removed) — 3 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 3</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `crossover` | `25.1.0-1` | — | — |
| `dbeaver-ce` | `26.1.5` | — | — |
| `obsidian` | `1.13.4` | — | — |

</details>

### Third-party: cli.github.com/packages — 1 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `gh` | `2.102.0` | stable | main |

</details>

### Third-party: deb.nodesource.com/node/24.x — 1 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `nodejs` | `24.21.0-1nodesource1` | nodistro | main |

</details>

### Third-party: dl.google.com/linux/chrome-stable/deb — 1 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `google-chrome-stable` | `154.0.8037.92-1` | stable | main |

</details>

### Third-party: download.vscodium.com/debs — 1 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `codium` | `1.135.06055` | vscodium | main |

</details>

### Third-party: nvidia.github.io/libnvidia-container/stable/deb/amd64 — 4 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 4</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `libnvidia-container-tools` | `1.20.1-1` | — | — |
| `libnvidia-container1` | `1.20.1-1` | — | — |
| `nvidia-container-toolkit` | `1.20.1-1` | — | — |
| `nvidia-container-toolkit-base` | `1.20.1-1` | — | — |

</details>

### Third-party: packages.microsoft.com/repos/edge-stable — 1 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 1</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `microsoft-edge-stable` ⚠️ | `154.0.4258.48-1` | stable | main |

</details>

### Third-party: packages.ros.org/ros2/ubuntu — 351 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 351</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `python3-bloom` | `0.14.4+upstream-1` | resolute | main |
| `python3-catkin-pkg` | `1.1.1-100` | resolute | main |
| `python3-catkin-pkg-modules` | `1.1.1-1` | resolute | main |
| `python3-colcon-argcomplete` | `0.3.3+upstream-1` | resolute | main |
| `python3-colcon-bash` | `0.5.0-100` | resolute | main |
| `python3-colcon-cd` | `0.2.1-1build1` | resolute | main |
| `python3-colcon-cmake` | `0.2.30+upstream-1` | resolute | main |
| `python3-colcon-common-extensions` | `0.3.0-100` | resolute | main |
| `python3-colcon-core` | `0.21.3+upstream-1` | resolute | main |
| `python3-colcon-defaults` | `0.2.9+upstream-1` | resolute | main |
| `python3-colcon-devtools` | `0.3.0-1build1` | resolute | main |
| `python3-colcon-installed-package-information` | `0.2.1-1` | resolute | main |
| `python3-colcon-library-path` | `0.2.1-100` | resolute | main |
| `python3-colcon-metadata` | `0.3.1+upstream-1` | resolute | main |
| `python3-colcon-mixin` | `0.3.2+upstream-1` | resolute | main |
| `python3-colcon-notification` | `0.3.3+upstream-1` | resolute | main |
| `python3-colcon-output` | `0.2.14+upstream-1` | resolute | main |
| `python3-colcon-override-check` | `0.0.1-100` | resolute | main |
| `python3-colcon-package-information` | `0.4.1+upstream-1` | resolute | main |
| `python3-colcon-package-selection` | `0.2.10-100` | resolute | main |
| `python3-colcon-parallel-executor` | `0.4.0-1` | resolute | main |
| `python3-colcon-pkg-config` | `0.1.0-100` | resolute | main |
| `python3-colcon-powershell` | `0.5.0+upstream-1` | resolute | main |
| `python3-colcon-python-setup-py` | `0.2.9-2` | resolute | main |
| `python3-colcon-recursive-crawl` | `0.2.3-100` | resolute | main |
| `python3-colcon-ros` | `0.5.0+upstream-1` | resolute | main |
| `python3-colcon-test-result` | `0.3.8-100` | resolute | main |
| `python3-colcon-zsh` | `0.5.0-100` | resolute | main |
| `python3-osrf-pycommon` | `2.1.7-1` | resolute | main |
| `python3-rosdep` | `0.27.0-1` | resolute | main |
| `python3-rosdep-modules` | `0.27.0-1` | resolute | main |
| `python3-rosdistro` | `1.1.0-100` | resolute | main |
| `python3-rosdistro-modules` | `1.1.0-1` | resolute | main |
| `python3-rospkg-modules` | `1.6.3-1` | resolute | main |
| `python3-vcstool` | `0.3.0-1` | resolute | main |
| `python3-vcstools` | `0.1.42-1` | resolute | main |
| `ros-build-essential` | `1.0.3` | resolute | main |
| `ros-dev-tools` | `1.0.3` | resolute | main |
| `ros-lyrical-action-msgs` | `2.4.5-1resolute.20260915.041037` | resolute | main |
| `ros-lyrical-action-tutorials-cpp` | `0.37.9-1resolute.20260915.071207` | resolute | main |
| `ros-lyrical-action-tutorials-py` | `0.37.9-1resolute.20260915.071209` | resolute | main |
| `ros-lyrical-actuator-msgs` | `0.0.1-5resolute.20260915.044428` | resolute | main |
| `ros-lyrical-ament-cmake` | `2.8.8-1resolute.20260728.175713` | resolute | main |
| `ros-lyrical-ament-cmake-auto` | `2.8.8-1resolute.20260728.210738` | resolute | main |
| `ros-lyrical-ament-cmake-copyright` | `0.20.6-1resolute.20260728.204014` | resolute | main |
| `ros-lyrical-ament-cmake-core` | `2.8.8-1resolute.20260728.162608` | resolute | main |
| `ros-lyrical-ament-cmake-cppcheck` | `0.20.6-1resolute.20260728.204151` | resolute | main |
| `ros-lyrical-ament-cmake-cpplint` | `0.20.6-1resolute.20260728.204159` | resolute | main |
| `ros-lyrical-ament-cmake-export-definitions` | `2.8.8-1resolute.20260728.173325` | resolute | main |
| `ros-lyrical-ament-cmake-export-dependencies` | `2.8.8-1resolute.20260728.173500` | resolute | main |
| `ros-lyrical-ament-cmake-export-include-directories` | `2.8.8-1resolute.20260728.172444` | resolute | main |
| `ros-lyrical-ament-cmake-export-libraries` | `2.8.8-1resolute.20260728.173328` | resolute | main |
| `ros-lyrical-ament-cmake-export-link-flags` | `2.8.8-1resolute.20260728.173334` | resolute | main |
| `ros-lyrical-ament-cmake-export-targets` | `2.8.8-1resolute.20260728.173432` | resolute | main |
| `ros-lyrical-ament-cmake-flake8` | `0.20.6-1resolute.20260728.204007` | resolute | main |
| `ros-lyrical-ament-cmake-gen-version-h` | `2.8.8-1resolute.20260728.173325` | resolute | main |
| `ros-lyrical-ament-cmake-gmock` | `2.8.8-1resolute.20260728.175747` | resolute | main |
| `ros-lyrical-ament-cmake-gtest` | `2.8.8-1resolute.20260728.175609` | resolute | main |
| `ros-lyrical-ament-cmake-include-directories` | `2.8.8-1resolute.20260728.173227` | resolute | main |
| `ros-lyrical-ament-cmake-libraries` | `2.8.8-1resolute.20260728.173352` | resolute | main |
| `ros-lyrical-ament-cmake-lint-cmake` | `0.20.6-1resolute.20260728.204241` | resolute | main |
| `ros-lyrical-ament-cmake-mypy` | `0.20.6-1resolute.20260728.204152` | resolute | main |
| `ros-lyrical-ament-cmake-pep257` | `0.20.6-1resolute.20260728.204012` | resolute | main |
| `ros-lyrical-ament-cmake-pytest` | `2.8.8-1resolute.20260728.175653` | resolute | main |
| `ros-lyrical-ament-cmake-python` | `2.8.8-1resolute.20260728.173021` | resolute | main |
| `ros-lyrical-ament-cmake-ros` | `0.15.8-1resolute.20260915.054806` | resolute | main |
| `ros-lyrical-ament-cmake-ros-core` | `0.15.8-1resolute.20260728.173607` | resolute | main |
| `ros-lyrical-ament-cmake-target-dependencies` | `2.8.8-1resolute.20260728.173503` | resolute | main |
| `ros-lyrical-ament-cmake-test` | `2.8.8-1resolute.20260728.175319` | resolute | main |
| `ros-lyrical-ament-cmake-uncrustify` | `0.20.6-1resolute.20260728.210813` | resolute | main |
| `ros-lyrical-ament-cmake-version` | `2.8.8-1resolute.20260728.173013` | resolute | main |
| `ros-lyrical-ament-cmake-xmllint` | `0.20.6-1resolute.20260728.204019` | resolute | main |
| `ros-lyrical-ament-copyright` | `0.20.6-1resolute.20260728.172704` | resolute | main |
| `ros-lyrical-ament-cppcheck` | `0.20.6-1resolute.20260728.173125` | resolute | main |
| `ros-lyrical-ament-cpplint` | `0.20.6-1resolute.20260728.173508` | resolute | main |
| `ros-lyrical-ament-flake8` | `0.20.6-1resolute.20260728.172702` | resolute | main |
| `ros-lyrical-ament-index-cpp` | `1.13.3-3resolute.20260728.204744` | resolute | main |
| `ros-lyrical-ament-index-python` | `1.13.3-3resolute.20260728.172618` | resolute | main |
| `ros-lyrical-ament-lint` | `0.20.6-1resolute.20260728.172451` | resolute | main |
| `ros-lyrical-ament-lint-auto` | `0.20.6-1resolute.20260728.204247` | resolute | main |
| `ros-lyrical-ament-lint-cmake` | `0.20.6-1resolute.20260728.173508` | resolute | main |
| `ros-lyrical-ament-lint-common` | `0.20.6-1resolute.20260728.211054` | resolute | main |
| `ros-lyrical-ament-mypy` | `0.20.6-1resolute.20260728.173532` | resolute | main |
| `ros-lyrical-ament-package` | `0.18.3-3resolute.20260430.010336` | resolute | main |
| `ros-lyrical-ament-pep257` | `0.20.6-1resolute.20260728.172706` | resolute | main |
| `ros-lyrical-ament-uncrustify` | `0.20.6-1resolute.20260728.210701` | resolute | main |
| `ros-lyrical-ament-xmllint` | `0.20.6-1resolute.20260728.172708` | resolute | main |
| `ros-lyrical-angles` | `1.16.1-3resolute.20260728.204755` | resolute | main |
| `ros-lyrical-builtin-interfaces` | `2.4.5-1resolute.20260915.031157` | resolute | main |
| `ros-lyrical-class-loader` | `2.9.4-3resolute.20260831.171005` | resolute | main |
| `ros-lyrical-common-interfaces` | `5.9.3-1resolute.20260915.053335` | resolute | main |
| `ros-lyrical-composition` | `0.37.9-1resolute.20260915.071707` | resolute | main |
| `ros-lyrical-composition-interfaces` | `2.4.5-1resolute.20260915.050451` | resolute | main |
| `ros-lyrical-compressed-depth-image-transport` | `6.2.6-1resolute.20260915.074341` | resolute | main |
| `ros-lyrical-compressed-image-transport` | `6.2.6-1resolute.20260915.081411` | resolute | main |
| `ros-lyrical-console-bridge-vendor` | `1.9.1-3resolute.20260728.205113` | resolute | main |
| `ros-lyrical-cv-bridge` | `4.1.0-3resolute.20260915.073513` | resolute | main |
| `ros-lyrical-demo-nodes-cpp` | `0.37.9-1resolute.20260915.065629` | resolute | main |
| `ros-lyrical-demo-nodes-cpp-native` | `0.37.9-1resolute.20260915.065404` | resolute | main |
| `ros-lyrical-demo-nodes-py` | `0.37.9-1resolute.20260915.064940` | resolute | main |
| `ros-lyrical-depthimage-to-laserscan` | `2.5.1-4resolute.20260915.073230` | resolute | main |
| `ros-lyrical-diagnostic-msgs` | `5.9.3-1resolute.20260915.051854` | resolute | main |
| `ros-lyrical-dummy-map-server` | `0.37.9-1resolute.20260915.073006` | resolute | main |
| `ros-lyrical-dummy-sensors` | `0.37.9-1resolute.20260915.073544` | resolute | main |
| `ros-lyrical-eigen3-cmake-module` | `0.5.1-3resolute.20260728.205221` | resolute | main |
| `ros-lyrical-example-interfaces` | `0.14.1-3resolute.20260915.044603` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-action-client` | `0.21.5-3resolute.20260915.071204` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-action-server` | `0.21.5-3resolute.20260915.071634` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-client` | `0.21.5-3resolute.20260915.071506` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-composition` | `0.21.5-3resolute.20260915.065729` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-publisher` | `0.21.5-3resolute.20260915.070525` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-service` | `0.21.5-3resolute.20260915.071541` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-subscriber` | `0.21.5-3resolute.20260915.065717` | resolute | main |
| `ros-lyrical-examples-rclcpp-minimal-timer` | `0.21.5-3resolute.20260915.080503` | resolute | main |
| `ros-lyrical-examples-rclcpp-multithreaded-executor` | `0.21.5-3resolute.20260915.070546` | resolute | main |
| `ros-lyrical-examples-rclpy-executors` | `0.21.5-3resolute.20260915.065049` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-action-client` | `0.21.5-3resolute.20260915.064346` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-action-server` | `0.21.5-3resolute.20260915.071355` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-client` | `0.21.5-3resolute.20260915.065050` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-publisher` | `0.21.5-3resolute.20260915.065102` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-service` | `0.21.5-3resolute.20260915.065131` | resolute | main |
| `ros-lyrical-examples-rclpy-minimal-subscriber` | `0.21.5-3resolute.20260915.065219` | resolute | main |
| `ros-lyrical-fastcdr` | `2.3.6-1resolute.20260728.172850` | resolute | main |
| `ros-lyrical-fastdds` | `3.6.2-1resolute.20260728.174239` | resolute | main |
| `ros-lyrical-foonathan-memory-vendor` | `1.4.1-1resolute.20260728.173726` | resolute | main |
| `ros-lyrical-geometry-msgs` | `5.9.3-1resolute.20260915.045122` | resolute | main |
| `ros-lyrical-geometry2` | `0.45.10-1resolute.20260915.143444` | resolute | main |
| `ros-lyrical-gps-msgs` | `3.1.1-1resolute.20260915.045135` | resolute | main |
| `ros-lyrical-gz-cmake-vendor` | `0.4.5-1resolute.20260728.204248` | resolute | main |
| `ros-lyrical-gz-common-vendor` | `0.3.8-1resolute.20260827.143639` | resolute | main |
| `ros-lyrical-gz-dartsim-vendor` | `0.1.3-3resolute.20260728.205412` | resolute | main |
| `ros-lyrical-gz-gui-vendor` | `0.3.2-1resolute.20260914.180039` | resolute | main |
| `ros-lyrical-gz-math-vendor` | `0.4.5-1resolute.20260827.141333` | resolute | main |
| `ros-lyrical-gz-msgs-vendor` | `0.3.4-2resolute.20260827.150529` | resolute | main |
| `ros-lyrical-gz-ogre-next-vendor` | `0.2.1-1resolute.20260728.205418` | resolute | main |
| `ros-lyrical-gz-physics-vendor` | `0.4.7-1resolute.20260901.221631` | resolute | main |
| `ros-lyrical-gz-plugin-vendor` | `0.3.1-3resolute.20260820.133841` | resolute | main |
| `ros-lyrical-gz-rendering-vendor` | `0.4.4-1resolute.20260827.145029` | resolute | main |
| `ros-lyrical-gz-sensors-vendor` | `0.3.5-1resolute.20260914.175731` | resolute | main |
| `ros-lyrical-gz-tools-vendor` | `0.2.2-1resolute.20260820.132934` | resolute | main |
| `ros-lyrical-gz-transport-vendor` | `0.3.5-1resolute.20260914.175014` | resolute | main |
| `ros-lyrical-gz-utils-vendor` | `0.4.1-3resolute.20260728.210531` | resolute | main |
| `ros-lyrical-image-geometry` | `4.1.0-3resolute.20260915.055055` | resolute | main |
| `ros-lyrical-image-tools` | `0.37.9-1resolute.20260915.065834` | resolute | main |
| `ros-lyrical-image-transport` | `6.4.10-1resolute.20260915.073117` | resolute | main |
| `ros-lyrical-image-transport-plugins` | `6.2.6-1resolute.20260915.082409` | resolute | main |
| `ros-lyrical-interactive-markers` | `2.8.4-1resolute.20260915.144429` | resolute | main |
| `ros-lyrical-intra-process-demo` | `0.37.9-1resolute.20260915.072041` | resolute | main |
| `ros-lyrical-joy` | `3.3.0-4resolute.20260915.073318` | resolute | main |
| `ros-lyrical-kdl-parser` | `3.0.1-3resolute.20260915.060157` | resolute | main |
| `ros-lyrical-keyboard-handler` | `0.5.1-1resolute.20260728.205547` | resolute | main |
| `ros-lyrical-laser-geometry` | `2.11.3-6resolute.20260915.135129` | resolute | main |
| `ros-lyrical-launch` | `3.9.8-1resolute.20260728.172811` | resolute | main |
| `ros-lyrical-launch-ros` | `0.29.9-1resolute.20260915.064616` | resolute | main |
| `ros-lyrical-launch-testing` | `3.9.8-1resolute.20260728.175423` | resolute | main |
| `ros-lyrical-launch-testing-ament-cmake` | `3.9.8-1resolute.20260728.205136` | resolute | main |
| `ros-lyrical-launch-testing-ros` | `0.29.9-1resolute.20260915.073741` | resolute | main |
| `ros-lyrical-launch-xml` | `3.9.8-1resolute.20260728.175211` | resolute | main |
| `ros-lyrical-launch-yaml` | `3.9.8-1resolute.20260728.172929` | resolute | main |
| `ros-lyrical-libstatistics-collector` | `2.1.2-1resolute.20260915.061028` | resolute | main |
| `ros-lyrical-libyaml-vendor` | `1.8.1-3resolute.20260728.205613` | resolute | main |
| `ros-lyrical-lifecycle` | `0.37.9-1resolute.20260915.065201` | resolute | main |
| `ros-lyrical-lifecycle-msgs` | `2.4.5-1resolute.20260915.045218` | resolute | main |
| `ros-lyrical-logging-demo` | `0.37.9-1resolute.20260915.065459` | resolute | main |
| `ros-lyrical-lz4-cmake-module` | `0.33.3-1resolute.20260728.205656` | resolute | main |
| `ros-lyrical-map-msgs` | `2.6.1-1resolute.20260915.052834` | resolute | main |
| `ros-lyrical-marine-acoustic-msgs` | `2.1.0-3resolute.20260915.050509` | resolute | main |
| `ros-lyrical-mcap-vendor` | `0.33.3-1resolute.20260728.210724` | resolute | main |
| `ros-lyrical-message-filters` | `7.4.2-1resolute.20260915.064044` | resolute | main |
| `ros-lyrical-nav-msgs` | `5.9.3-1resolute.20260915.051911` | resolute | main |
| `ros-lyrical-pcl-conversions` | `2.10.0-1resolute.20260915.065230` | resolute | main |
| `ros-lyrical-pcl-msgs` | `1.0.0-10resolute.20260915.052856` | resolute | main |
| `ros-lyrical-pendulum-control` | `0.37.9-1resolute.20260915.071220` | resolute | main |
| `ros-lyrical-pendulum-msgs` | `0.37.9-1resolute.20260915.045347` | resolute | main |
| `ros-lyrical-pluginlib` | `5.8.5-1resolute.20260831.172534` | resolute | main |
| `ros-lyrical-point-cloud-transport` | `5.4.3-1resolute.20260915.073223` | resolute | main |
| `ros-lyrical-python-qt-binding` | `2.5.5-1resolute.20260728.205956` | resolute | main |
| `ros-lyrical-qt-dotgraph` | `2.11.1-1resolute.20260728.210436` | resolute | main |
| `ros-lyrical-qt-gui` | `2.11.1-1resolute.20260728.210439` | resolute | main |
| `ros-lyrical-qt-gui-cpp` | `2.11.1-1resolute.20260831.173352` | resolute | main |
| `ros-lyrical-qt-gui-py-common` | `2.11.1-1resolute.20260728.210443` | resolute | main |
| `ros-lyrical-quality-of-service-demo-cpp` | `0.37.9-1resolute.20260915.071341` | resolute | main |
| `ros-lyrical-quality-of-service-demo-py` | `0.37.9-1resolute.20260915.071433` | resolute | main |
| `ros-lyrical-rcl` | `10.4.5-1resolute.20260915.060844` | resolute | main |
| `ros-lyrical-rcl-action` | `10.4.5-1resolute.20260915.061100` | resolute | main |
| `ros-lyrical-rcl-interfaces` | `2.4.5-1resolute.20260915.045418` | resolute | main |
| `ros-lyrical-rcl-lifecycle` | `10.4.5-1resolute.20260915.061109` | resolute | main |
| `ros-lyrical-rcl-logging-implementation` | `3.4.1-3resolute.20260915.055807` | resolute | main |
| `ros-lyrical-rcl-logging-interface` | `3.4.1-3resolute.20260915.055121` | resolute | main |
| `ros-lyrical-rcl-logging-spdlog` | `3.4.1-3resolute.20260915.055418` | resolute | main |
| `ros-lyrical-rcl-yaml-param-parser` | `10.4.5-1resolute.20260915.055121` | resolute | main |
| `ros-lyrical-rclcpp` | `32.0.3-1resolute.20260915.061505` | resolute | main |
| `ros-lyrical-rclcpp-action` | `32.0.3-1resolute.20260915.064317` | resolute | main |
| `ros-lyrical-rclcpp-components` | `32.0.3-1resolute.20260915.065011` | resolute | main |
| `ros-lyrical-rclcpp-lifecycle` | `32.0.3-1resolute.20260915.064713` | resolute | main |
| `ros-lyrical-rclpy` | `10.0.11-1resolute.20260915.061807` | resolute | main |
| `ros-lyrical-rcpputils` | `2.14.5-1resolute.20260831.170316` | resolute | main |
| `ros-lyrical-rcutils` | `7.1.3-1resolute.20260831.165446` | resolute | main |
| `ros-lyrical-resource-retriever-interfaces` | `0.0.3-1resolute.20260915.045531` | resolute | main |
| `ros-lyrical-rmw` | `7.10.2-3resolute.20260901.091148` | resolute | main |
| `ros-lyrical-rmw-dds-common` | `6.0.0-3resolute.20260915.045630` | resolute | main |
| `ros-lyrical-rmw-fastrtps-cpp` | `9.4.10-1resolute.20260915.053043` | resolute | main |
| `ros-lyrical-rmw-fastrtps-shared-cpp` | `9.4.10-1resolute.20260915.051845` | resolute | main |
| `ros-lyrical-rmw-implementation` | `3.1.6-1resolute.20260915.053750` | resolute | main |
| `ros-lyrical-rmw-implementation-cmake` | `7.10.2-3resolute.20260901.091219` | resolute | main |
| `ros-lyrical-rmw-security-common` | `7.10.2-3resolute.20260901.091646` | resolute | main |
| `ros-lyrical-rmw-test-fixture` | `0.15.8-1resolute.20260901.092020` | resolute | main |
| `ros-lyrical-rmw-test-fixture-implementation` | `0.15.8-1resolute.20260915.054330` | resolute | main |
| `ros-lyrical-robot-state-publisher` | `3.5.6-1resolute.20260915.141620` | resolute | main |
| `ros-lyrical-ros-base` | `0.13.0-3resolute.20260915.154859` | resolute | main |
| `ros-lyrical-ros-core` | `0.13.0-3resolute.20260915.090714` | resolute | main |
| `ros-lyrical-ros-environment` | `4.5.1-1resolute.20260728.172811` | resolute | main |
| `ros-lyrical-ros-gz-bridge` | `3.0.10-1resolute.20260915.142616` | resolute | main |
| `ros-lyrical-ros-gz-image` | `3.0.10-1resolute.20260915.152414` | resolute | main |
| `ros-lyrical-ros-gz-interfaces` | `3.0.10-1resolute.20260915.051849` | resolute | main |
| `ros-lyrical-ros-workspace` | `1.0.3-9resolute.20260728.162902` | resolute | main |
| `ros-lyrical-ros2action` | `0.40.9-1resolute.20260915.075756` | resolute | main |
| `ros-lyrical-ros2bag` | `0.33.3-1resolute.20260915.110720` | resolute | main |
| `ros-lyrical-ros2cli` | `0.40.9-1resolute.20260915.075638` | resolute | main |
| `ros-lyrical-ros2cli-common-extensions` | `0.5.2-3resolute.20260915.090532` | resolute | main |
| `ros-lyrical-ros2component` | `0.40.9-1resolute.20260915.082453` | resolute | main |
| `ros-lyrical-ros2doctor` | `0.40.9-1resolute.20260915.075912` | resolute | main |
| `ros-lyrical-ros2interface` | `0.40.9-1resolute.20260915.082233` | resolute | main |
| `ros-lyrical-ros2launch` | `0.29.9-1resolute.20260915.085616` | resolute | main |
| `ros-lyrical-ros2lifecycle` | `0.40.9-1resolute.20260915.080451` | resolute | main |
| `ros-lyrical-ros2multicast` | `0.40.9-1resolute.20260915.082157` | resolute | main |
| `ros-lyrical-ros2node` | `0.40.9-1resolute.20260915.080017` | resolute | main |
| `ros-lyrical-ros2param` | `0.40.9-1resolute.20260915.080636` | resolute | main |
| `ros-lyrical-ros2pkg` | `0.40.9-1resolute.20260915.082312` | resolute | main |
| `ros-lyrical-ros2plugin` | `5.8.5-1resolute.20260915.085453` | resolute | main |
| `ros-lyrical-ros2run` | `0.40.9-1resolute.20260915.090402` | resolute | main |
| `ros-lyrical-ros2service` | `0.40.9-1resolute.20260915.080006` | resolute | main |
| `ros-lyrical-ros2topic` | `0.40.9-1resolute.20260915.080326` | resolute | main |
| `ros-lyrical-rosbag2` | `0.33.3-1resolute.20260915.111344` | resolute | main |
| `ros-lyrical-rosbag2-compression` | `0.33.3-1resolute.20260915.090557` | resolute | main |
| `ros-lyrical-rosbag2-compression-zstd` | `0.33.3-1resolute.20260915.110400` | resolute | main |
| `ros-lyrical-rosbag2-cpp` | `0.33.3-1resolute.20260915.080852` | resolute | main |
| `ros-lyrical-rosbag2-interfaces` | `0.33.3-1resolute.20260915.050641` | resolute | main |
| `ros-lyrical-rosbag2-py` | `0.33.3-1resolute.20260915.092025` | resolute | main |
| `ros-lyrical-rosbag2-storage` | `0.33.3-1resolute.20260915.080404` | resolute | main |
| `ros-lyrical-rosbag2-storage-default-plugins` | `0.33.3-1resolute.20260915.110336` | resolute | main |
| `ros-lyrical-rosbag2-storage-mcap` | `0.33.3-1resolute.20260915.090607` | resolute | main |
| `ros-lyrical-rosbag2-storage-sqlite3` | `0.33.3-1resolute.20260915.090614` | resolute | main |
| `ros-lyrical-rosbag2-transport` | `0.33.3-1resolute.20260915.091021` | resolute | main |
| `ros-lyrical-rosgraph-msgs` | `2.4.5-1resolute.20260915.050401` | resolute | main |
| `ros-lyrical-rosidl-adapter` | `5.2.1-1resolute.20260728.204010` | resolute | main |
| `ros-lyrical-rosidl-buffer` | `5.2.1-1resolute.20260728.210115` | resolute | main |
| `ros-lyrical-rosidl-buffer-backend` | `5.2.1-1resolute.20260901.091711` | resolute | main |
| `ros-lyrical-rosidl-buffer-backend-registry` | `5.2.1-1resolute.20260901.091931` | resolute | main |
| `ros-lyrical-rosidl-buffer-py` | `5.2.1-1resolute.20260728.210209` | resolute | main |
| `ros-lyrical-rosidl-cli` | `5.2.1-1resolute.20260728.173046` | resolute | main |
| `ros-lyrical-rosidl-cmake` | `5.2.1-1resolute.20260728.210427` | resolute | main |
| `ros-lyrical-rosidl-core-generators` | `0.4.3-3resolute.20260915.030113` | resolute | main |
| `ros-lyrical-rosidl-core-runtime` | `0.4.3-3resolute.20260915.030238` | resolute | main |
| `ros-lyrical-rosidl-default-generators` | `1.8.1-3resolute.20260915.042236` | resolute | main |
| `ros-lyrical-rosidl-default-runtime` | `1.8.1-3resolute.20260915.042259` | resolute | main |
| `ros-lyrical-rosidl-dynamic-typesupport` | `0.4.1-3resolute.20260831.170948` | resolute | main |
| `ros-lyrical-rosidl-dynamic-typesupport-fastrtps` | `0.5.1-3resolute.20260831.171643` | resolute | main |
| `ros-lyrical-rosidl-generator-c` | `5.2.1-1resolute.20260831.170131` | resolute | main |
| `ros-lyrical-rosidl-generator-cpp` | `5.2.1-1resolute.20260831.171349` | resolute | main |
| `ros-lyrical-rosidl-generator-py` | `0.27.2-3resolute.20260901.091938` | resolute | main |
| `ros-lyrical-rosidl-generator-rs` | `0.5.0-2resolute.20260831.171630` | resolute | main |
| `ros-lyrical-rosidl-generator-type-description` | `5.2.1-1resolute.20260728.210206` | resolute | main |
| `ros-lyrical-rosidl-parser` | `5.2.1-1resolute.20260728.210114` | resolute | main |
| `ros-lyrical-rosidl-pycommon` | `5.2.1-1resolute.20260728.210228` | resolute | main |
| `ros-lyrical-rosidl-runtime-c` | `5.2.1-1resolute.20260831.170154` | resolute | main |
| `ros-lyrical-rosidl-runtime-cpp` | `5.2.1-1resolute.20260831.170544` | resolute | main |
| `ros-lyrical-rosidl-runtime-py` | `0.15.2-3resolute.20260728.210536` | resolute | main |
| `ros-lyrical-rosidl-typesupport-c` | `3.4.2-3resolute.20260831.171238` | resolute | main |
| `ros-lyrical-rosidl-typesupport-cpp` | `3.4.2-3resolute.20260831.173017` | resolute | main |
| `ros-lyrical-rosidl-typesupport-fastrtps-c` | `3.9.7-1resolute.20260915.025611` | resolute | main |
| `ros-lyrical-rosidl-typesupport-fastrtps-cpp` | `3.9.7-1resolute.20260915.025317` | resolute | main |
| `ros-lyrical-rosidl-typesupport-interface` | `5.2.1-1resolute.20260728.210128` | resolute | main |
| `ros-lyrical-rosidl-typesupport-introspection-c` | `5.2.1-1resolute.20260831.170823` | resolute | main |
| `ros-lyrical-rosidl-typesupport-introspection-cpp` | `5.2.1-1resolute.20260831.172258` | resolute | main |
| `ros-lyrical-rosx-introspection` | `2.3.0-3resolute.20260915.081751` | resolute | main |
| `ros-lyrical-rpyutils` | `0.7.2-3resolute.20260728.174949` | resolute | main |
| `ros-lyrical-rqt-action` | `2.5.0-1resolute.20260915.082422` | resolute | main |
| `ros-lyrical-rqt-bag` | `2.2.5-1resolute.20260915.092813` | resolute | main |
| `ros-lyrical-rqt-bag-plugins` | `2.2.5-1resolute.20260915.111558` | resolute | main |
| `ros-lyrical-rqt-common-plugins` | `1.2.0-5resolute.20260915.111731` | resolute | main |
| `ros-lyrical-rqt-console` | `2.4.4-1resolute.20260915.080734` | resolute | main |
| `ros-lyrical-rqt-graph` | `1.8.5-1resolute.20260915.081018` | resolute | main |
| `ros-lyrical-rqt-gui` | `1.10.6-1resolute.20260915.075649` | resolute | main |
| `ros-lyrical-rqt-gui-cpp` | `1.10.6-1resolute.20260915.080659` | resolute | main |
| `ros-lyrical-rqt-gui-py` | `1.10.6-1resolute.20260915.080446` | resolute | main |
| `ros-lyrical-rqt-image-view` | `2.0.5-3resolute.20260915.081629` | resolute | main |
| `ros-lyrical-rqt-msg` | `1.7.4-1resolute.20260915.080956` | resolute | main |
| `ros-lyrical-rqt-plot` | `1.7.6-1resolute.20260915.080820` | resolute | main |
| `ros-lyrical-rqt-publisher` | `1.10.4-1resolute.20260915.081013` | resolute | main |
| `ros-lyrical-rqt-py-common` | `1.10.6-1resolute.20260915.075702` | resolute | main |
| `ros-lyrical-rqt-py-console` | `1.5.3-1resolute.20260915.081032` | resolute | main |
| `ros-lyrical-rqt-reconfigure` | `1.8.6-1resolute.20260915.081005` | resolute | main |
| `ros-lyrical-rqt-service-caller` | `1.5.4-1resolute.20260915.090453` | resolute | main |
| `ros-lyrical-rqt-shell` | `1.4.2-1resolute.20260915.090500` | resolute | main |
| `ros-lyrical-rqt-srv` | `1.4.1-3resolute.20260915.090410` | resolute | main |
| `ros-lyrical-rqt-topic` | `2.1.2-1resolute.20260915.080918` | resolute | main |
| `ros-lyrical-rttest` | `0.20.1-1resolute.20260728.210200` | resolute | main |
| `ros-lyrical-rviz-ogre-vendor` | `15.2.6-1resolute.20260908.121206` | resolute | main |
| `ros-lyrical-sdformat-urdf` | `2.1.1-1resolute.20260915.060201` | resolute | main |
| `ros-lyrical-sdformat-vendor` | `0.3.4-1resolute.20260827.143900` | resolute | main |
| `ros-lyrical-sdl2-vendor` | `3.3.0-4resolute.20260728.210149` | resolute | main |
| `ros-lyrical-sensor-msgs` | `5.9.3-1resolute.20260915.051912` | resolute | main |
| `ros-lyrical-sensor-msgs-py` | `5.9.3-1resolute.20260915.052909` | resolute | main |
| `ros-lyrical-service-msgs` | `2.4.5-1resolute.20260915.032658` | resolute | main |
| `ros-lyrical-shape-msgs` | `5.9.3-1resolute.20260915.050607` | resolute | main |
| `ros-lyrical-simulation-interfaces` | `2.1.0-3resolute.20260915.051917` | resolute | main |
| `ros-lyrical-spdlog-vendor` | `1.8.0-3resolute.20260728.210243` | resolute | main |
| `ros-lyrical-sros2` | `0.16.6-1resolute.20260915.080327` | resolute | main |
| `ros-lyrical-sros2-cmake` | `0.16.6-1resolute.20260915.082359` | resolute | main |
| `ros-lyrical-statistics-msgs` | `2.4.5-1resolute.20260915.043006` | resolute | main |
| `ros-lyrical-std-msgs` | `5.9.3-1resolute.20260915.043001` | resolute | main |
| `ros-lyrical-std-srvs` | `5.9.3-1resolute.20260915.045802` | resolute | main |
| `ros-lyrical-stereo-msgs` | `5.9.3-1resolute.20260915.052917` | resolute | main |
| `ros-lyrical-tango-icons-vendor` | `0.5.1-3resolute.20260728.210308` | resolute | main |
| `ros-lyrical-teleop-twist-joy` | `2.6.5-3resolute.20260915.074000` | resolute | main |
| `ros-lyrical-teleop-twist-keyboard` | `2.4.1-3resolute.20260915.064957` | resolute | main |
| `ros-lyrical-tf2` | `0.45.10-1resolute.20260915.134323` | resolute | main |
| `ros-lyrical-tf2-bullet` | `0.45.10-1resolute.20260915.142835` | resolute | main |
| `ros-lyrical-tf2-eigen` | `0.45.10-1resolute.20260915.143039` | resolute | main |
| `ros-lyrical-tf2-eigen-kdl` | `0.45.10-1resolute.20260915.135157` | resolute | main |
| `ros-lyrical-tf2-geometry-msgs` | `0.45.10-1resolute.20260915.143024` | resolute | main |
| `ros-lyrical-tf2-kdl` | `0.45.10-1resolute.20260915.143027` | resolute | main |
| `ros-lyrical-tf2-msgs` | `0.45.10-1resolute.20260915.134604` | resolute | main |
| `ros-lyrical-tf2-py` | `0.45.10-1resolute.20260915.135155` | resolute | main |
| `ros-lyrical-tf2-ros` | `0.45.10-1resolute.20260915.140307` | resolute | main |
| `ros-lyrical-tf2-ros-py` | `0.45.10-1resolute.20260915.135515` | resolute | main |
| `ros-lyrical-tf2-sensor-msgs` | `0.45.10-1resolute.20260915.143046` | resolute | main |
| `ros-lyrical-tf2-tools` | `0.45.10-1resolute.20260915.135840` | resolute | main |
| `ros-lyrical-theora-image-transport` | `6.2.6-1resolute.20260915.074331` | resolute | main |
| `ros-lyrical-tlsf` | `0.11.1-3resolute.20260728.210355` | resolute | main |
| `ros-lyrical-tlsf-cpp` | `0.20.1-1resolute.20260915.070715` | resolute | main |
| `ros-lyrical-topic-monitor` | `0.37.9-1resolute.20260915.065226` | resolute | main |
| `ros-lyrical-tracetools` | `8.10.2-1resolute.20260728.204752` | resolute | main |
| `ros-lyrical-trajectory-msgs` | `5.9.3-1resolute.20260915.051919` | resolute | main |
| `ros-lyrical-turtlesim` | `1.10.9-1resolute.20260915.064816` | resolute | main |
| `ros-lyrical-turtlesim-msgs` | `1.10.9-1resolute.20260915.043057` | resolute | main |
| `ros-lyrical-type-description-interfaces` | `2.4.5-1resolute.20260915.033102` | resolute | main |
| `ros-lyrical-uncrustify-vendor` | `3.2.0-3resolute.20260728.210418` | resolute | main |
| `ros-lyrical-unique-identifier-msgs` | `2.8.1-3resolute.20260915.030702` | resolute | main |
| `ros-lyrical-urdf` | `2.13.2-3resolute.20260915.055458` | resolute | main |
| `ros-lyrical-urdf-parser-plugin` | `2.13.2-3resolute.20260915.055127` | resolute | main |
| `ros-lyrical-urdfdom` | `6.0.0-3resolute.20260728.205537` | resolute | main |
| `ros-lyrical-urdfdom-headers` | `3.0.0-3resolute.20260728.173048` | resolute | main |
| `ros-lyrical-vision-msgs` | `4.2.0-3resolute.20260915.050641` | resolute | main |
| `ros-lyrical-visualization-msgs` | `5.9.3-1resolute.20260915.052651` | resolute | main |
| `ros-lyrical-xacro` | `2.1.1-3resolute.20260728.204820` | resolute | main |
| `ros-lyrical-yaml-cpp-vendor` | `9.2.1-3resolute.20260728.210605` | resolute | main |
| `ros-lyrical-zenoh-cpp-vendor` | `0.10.6-1resolute.20260914.173008` | resolute | main |
| `ros-lyrical-zstd-cmake-module` | `0.33.3-1resolute.20260728.210616` | resolute | main |
| `ros-lyrical-zstd-image-transport` | `6.2.6-1resolute.20260915.081707` | resolute | main |

</details>

### Third-party: repo.steampowered.com/steam — 3 packages

*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*

<details><summary>Show all 3</summary>

| Package | Version | Suite | Component |
|---|---|---|---|
| `steam-launcher` | `1:1.0.0.87` | stable | steam |
| `steam-libs-amd64` | `1:1.0.0.87` | stable | steam |
| `steam-libs-i386` | `1:1.0.0.87` | stable | steam |

</details>

### Behind `Candidate`

| Package | Installed |
|---|---|
| `alsa-ucm-conf` | `1.2.15.3-1ubuntu1.5` |
| `drkonqi` | `6.6.4-0ubuntu1` |
| `gstreamer1.0-plugins-good` | `1.28.2-2ubuntu0.3` |
| `microsoft-edge-stable` | `154.0.4258.48-1` |

## Desktop applications

`319` entries, enumerated from `/usr/share/applications` and
`~/.local/share/applications`. A hand-picked list of "the main ones" omits
most of what is installed; this is the exhaustive set.

<details><summary>Show all</summary>

| Application | Desktop id | Provided by |
|---|---|---|
| Report a problem... | `apport-kde-mime` | `apport` `2.34.1-0ubuntu0.1` |
| Report a problem... | `apport-kde` | `apport` `2.34.1-0ubuntu0.1` |
| Audacious | `audacious` | — |
| Audacity | `audacity` | — |
| Bookmarks | `bookmarks` | — |
| Breeze Widget Style | `breezestyleconfig` | — |
| E-book editor | `calibre-ebook-edit` | — |
| E-book viewer | `calibre-ebook-viewer` | — |
| calibre | `calibre-gui` | — |
| LRF viewer | `calibre-lrfviewer` | — |
| ClamTk | `clamtk` | — |
| VSCodium - URL Handler | `codium-url-handler` | — |
| VSCodium | `codium` | — |
| PDF Arranger | `com.github.jeromerobert.pdfarranger` | — |
| Google Chrome | `com.google.Chrome` | — |
| Microsoft Edge | `com.microsoft.Edge` | — |
| ConvertAll | `convertall` | — |
| CrossOver (Restore) | `cxassoc-cxoffice-0:application_x-crossover-cxarchive::restore` | — |
| CrossOver (Install) | `cxassoc-cxoffice-0:application_x-crossover-exe::install` | — |
| CrossOver (Run) | `cxassoc-cxoffice-0:application_x-crossover-exe::run` | — |
| CrossOver (Run) | `cxassoc-cxoffice-0:application_x-crossover-lnk::run` | — |
| CrossOver (Install) | `cxassoc-cxoffice-0:application_x-crossover-msi::install` | — |
| CrossOver (Install) | `cxassoc-cxoffice-1:application_x-crossover-c4p::install` | — |
| CrossOver (Install) | `cxassoc-cxoffice-1:application_x-crossover-tie::install` | — |
| CrossOver | `cxmenu-cxoffice-0-29ra4ke-CrossOver` | — |
| dbeaver-ce | `dbeaver-ce` | — |
| UXTerm | `debian-uxterm` | — |
| XTerm | `debian-xterm` | — |
| ImageMagick (color depth=q16) | `display-im7.q16` | — |
| Geoclue Demo agent | `geoclue-demo-agent` | — |
| GNU Image Manipulation Program | `gimp` | — |
| Google Chrome | `google-chrome` | — |
| Google Maps | `google-maps-geo-handler` | — |
| Groovy Console | `groovyConsole` | — |
| Reactivate HP LaserJet 1018/1020 after reloading paper | `hplj1020` | — |
| Htop | `htop` | — |
| Input Method | `im-config` | `im-config` `0.62` |
| TeXInfo | `info` | — |
| Snapd User Session Agent | `io.snapcraft.SessionAgent` | — |
| Accessibility | `kaccess` | — |
| KAddressbook import file | `kaddressbook-importer` | — |
| KAddressBook View | `kaddressbook-view` | — |
| About this System | `kcm_about-distro` | — |
| Accessibility | `kcm_access` | — |
| Activities | `kcm_activities` | — |
| Animations | `kcm_animations` | — |
| Audio CDs | `kcm_audiocd` | — |
| Autostart | `kcm_autostart` | — |
| File Search | `kcm_baloofile` | — |
| Bluetooth | `kcm_bluetooth` | — |
| Thunderbolt | `kcm_bolt` | — |
| Bookmarks | `kcm_bookmarks` | — |
| Breeze Window Decoration | `kcm_breezedecoration` | — |
| Cellular Network | `kcm_cellular_network` | — |
| Date & Time | `kcm_clock` | — |
| Colors | `kcm_colors` | — |
| Default Applications | `kcm_componentchooser` | — |
| Cursors | `kcm_cursortheme` | — |
| Locations | `kcm_desktoppaths` | — |
| Plasma Style | `kcm_desktoptheme` | — |
| SMART Status | `kcm_disks` | — |
| Energy | `kcm_energyinfo` | — |
| User Feedback | `kcm_feedback` | — |
| File Associations | `kcm_filetypes` | — |
| Firewall | `kcm_firewall` | — |
| Font Management | `kcm_fontinst` | — |
| Fonts | `kcm_fonts` | — |
| Game Controller | `kcm_gamecontroller` | — |
| Icons | `kcm_icons` | — |
| Digital Camera | `kcm_kamera` | — |
| Background Services | `kcm_kded` | — |
| Keyboard | `kcm_keyboard` | — |
| Shortcuts | `kcm_keys` | — |
| Gamma | `kcm_kgamma` | — |
| KRunner Settings | `kcm_krunnersettings` | — |
| Display Configuration | `kcm_kscreen` | — |
| Backups | `kcm_kup` | — |
| Desktop Effects | `kcm_kwin_effects` | — |
| KWin Scripts | `kcm_kwin_scripts` | — |
| Virtual Desktops | `kcm_kwin_virtualdesktops` | — |
| Window Decorations | `kcm_kwindecoration` | — |
| Window Behavior | `kcm_kwinoptions` | — |
| Window Rules | `kcm_kwinrules` | — |
| Task Switcher | `kcm_kwintabbox` | — |
| Legacy X11 App Support | `kcm_kwinxwayland` | — |
| Quick Settings | `kcm_landingpage` | — |
| Global Theme | `kcm_lookandfeel` | — |
| Hotspot | `kcm_mobile_hotspot` | — |
| Energy | `kcm_mobile_power` | — |
| Wi-Fi | `kcm_mobile_wifi` | — |
| Wired Network | `kcm_mobile_wired` | — |
| Mouse | `kcm_mouse` | — |
| Connection Preferences | `kcm_netpref` | — |
| Wi-Fi & Networking | `kcm_networkmanagement` | — |
| Night Light | `kcm_nightlight` | — |
| Day-Night Cycle | `kcm_nighttime` | — |
| Other Notifications | `kcm_notificationhelper` | — |
| Notifications | `kcm_notifications` | — |
| Oxygen Window Decoration | `kcm_oxygendecoration` | — |
| On-Screen Keyboard | `kcm_plasmakeyboard` | — |
| Plasma Search | `kcm_plasmasearch` | — |
| Boot Splash Screen | `kcm_plymouth` | — |
| Power Management | `kcm_powerdevilprofilesconfig` | — |
| Printers | `kcm_printer_manager` | — |
| Proxy | `kcm_proxy` | — |
| Sound | `kcm_pulseaudio` | — |
| Push Notifications | `kcm_push_notifications` | — |
| Plasma Renderer | `kcm_qtquicksettings` | — |
| Recent Files | `kcm_recentFiles` | — |
| Region & Language | `kcm_regionandlang` | — |
| Screen Locking | `kcm_screenlocker` | — |
| Login Screen (SDDM) | `kcm_sddm` | — |
| Desktop Session | `kcm_smserver` | — |
| Device Actions | `kcm_solid_actions` | — |
| System Sounds | `kcm_soundtheme` | — |
| Splash Screen | `kcm_splashscreen` | — |
| Application Style | `kcm_style` | — |
| Drawing Tablet | `kcm_tablet` | — |
| Touchpad | `kcm_touchpad` | — |
| Touchscreen | `kcm_touchscreen` | — |
| Trash | `kcm_trash` | — |
| Software Update | `kcm_updates` | — |
| Users | `kcm_users` | — |
| Virtual Keyboard | `kcm_virtualkeyboard` | — |
| Graphic Tablet | `kcm_wacomtablet` | — |
| Wallpaper | `kcm_wallpaper` | — |
| Web Search Keywords | `kcm_webshortcuts` | — |
| General Behavior | `kcm_workspace` | — |
| Spell Check | `kcmspellchecking` | — |
| Wacom Tablet finder | `kde_wacom_tabletfinder` | — |
| KDE System Settings | `kdesystemsettings` | — |
| Konqueror | `kfmclient` | — |
| Konqueror | `kfmclient_dir` | — |
| Konqueror | `kfmclient_html` | — |
| Konqueror | `kfmclient_war` | — |
| KMail view | `kmail_view` | — |
| Konqueror | `konqbrowser` | — |
| KOrganizer | `korganizer-import` | — |
| KOrganizer View | `korganizer-view` | — |
| KTelnetService | `ktelnetservice5` | — |
| KTelnetService | `ktelnetservice6` | — |
| KWalletManager | `kwalletmanager5-kwalletd` | — |
| LibreOffice Calc | `libreoffice-calc` | — |
| LibreOffice Draw | `libreoffice-draw` | — |
| LibreOffice Impress | `libreoffice-impress` | — |
| LibreOffice Math | `libreoffice-math` | — |
| LibreOffice | `libreoffice-startcenter` | — |
| LibreOffice Writer | `libreoffice-writer` | — |
| LibreOffice XSLT based filters | `libreoffice-xsltfilter` | — |
| Microsoft Edge | `microsoft-edge` | — |
| USB Stick Formatter | `mintstick-format-kde` | — |
| USB Stick Formatter | `mintstick-format` | — |
| USB Image Writer | `mintstick-kde` | — |
| USB Image Writer | `mintstick` | — |
| NVIDIA X Server Settings | `nvidia-settings` | — |
| Obsidian | `obsidian` | — |
| Okular | `okularApplication_comicbook` | — |
| Okular | `okularApplication_djvu` | — |
| Okular | `okularApplication_dvi` | — |
| Okular | `okularApplication_epub` | — |
| Okular | `okularApplication_fax` | — |
| Okular | `okularApplication_fb` | — |
| Okular | `okularApplication_ghostview` | — |
| Okular | `okularApplication_kimgio` | — |
| Okular | `okularApplication_md` | — |
| Okular | `okularApplication_mobi` | — |
| Okular | `okularApplication_pdf` | — |
| Okular | `okularApplication_tiff` | — |
| Okular | `okularApplication_txt` | — |
| Okular | `okularApplication_xps` | — |
| OpenJDK Java 25 Runtime | `openjdk-25-java` | — |
| OpenStreetMap | `openstreetmap-geo-handler` | — |
| Orca | `orca` | `orca` `50.2-0ubuntu0.1` |
| Xwayland | `org.freedesktop.Xwayland` | — |
| Portal | `org.freedesktop.impl.portal.desktop.kde` | — |
| Zenity | `org.gnome.Zenity` | `zenity` `4.2.1-1` |
| Pinentry | `org.gnupg.pinentry-qt` | — |
| Inkscape | `org.inkscape.Inkscape` | — |
| Configure Printer | `org.kde.ConfigurePrinter` | — |
| Print Queue | `org.kde.PrintQueue` | — |
| Account Wizard | `org.kde.accountwizard` | — |
| Agent Configuration Dialog | `org.kde.akonadi.configdialog` | — |
| Personal Contacts | `org.kde.akonadi_contacts_resource` | — |
| DAV Groupware | `org.kde.akonadi_davgroupware_resource` | — |
| Microsoft Exchange Server (EWS) | `org.kde.akonadi_ews_resource` | — |
| Google Groupware | `org.kde.akonadi_google_resource` | — |
| Emails | `org.kde.akonadi_imap_resource` | — |
| Open-Xchange Groupware Server | `org.kde.akonadi_openxchange_resource` | — |
| vCard File | `org.kde.akonadi_vcard_resource` | — |
| vCard Directory | `org.kde.akonadi_vcarddir_resource` | — |
| Akregator | `org.kde.akregator` | — |
| Ark | `org.kde.ark` | — |
| File Search | `org.kde.baloorunner` | — |
| Bluetooth File Transfer | `org.kde.bluedevilsendfile` | — |
| Add Bluetooth Device | `org.kde.bluedevilwizard` | — |
| Contact Print Theme Editor | `org.kde.contactprintthemeeditor` | — |
| Contact Theme Editor | `org.kde.contactthemeeditor` | — |
| Discover | `org.kde.discover.apt.urlhandler` | — |
| Discover | `org.kde.discover` | — |
| Discover | `org.kde.discover.notifier` | — |
| Discover | `org.kde.discover.snap` | — |
| Discover | `org.kde.discover.urlhandler` | — |
| Dolphin | `org.kde.dolphin` | — |
| Crashed Processes Viewer | `org.kde.drkonqi.coredump.gui` | — |
| Dr Konqi | `org.kde.drkonqi` | — |
| Elisa | `org.kde.elisa` | — |
| Filelight | `org.kde.filelight` | — |
| ghostwriter | `org.kde.ghostwriter` | — |
| Gwenview | `org.kde.gwenview` | — |
| Gwenview Importer | `org.kde.gwenview_importer` | — |
| Haruna | `org.kde.haruna` | — |
| KMail Header Theme Editor | `org.kde.headerthemeeditor` | — |
| ISO Image Writer | `org.kde.isoimagewriter` | — |
| KAddressBook | `org.kde.kaddressbook` | — |
| Kate | `org.kde.kate` | — |
| KCalc | `org.kde.kcalc` | — |
| KCharSelect | `org.kde.kcharselect` | — |
| KColorSchemeEditor | `org.kde.kcolorschemeeditor` | — |
| KDED | `org.kde.kded5` | — |
| KDED | `org.kde.kded6` | — |
| Kdenlive | `org.kde.kdenlive` | — |
| KDialog | `org.kde.kdialog` | — |
| Bookmark Editor | `org.kde.keditbookmarks` | — |
| File Type Editor | `org.kde.keditfiletype` | — |
| KFind | `org.kde.kfind` | — |
| KFontInst | `org.kde.kfontinst` | — |
| KFontView | `org.kde.kfontview` | — |
| Help Center | `org.kde.khelpcenter` | — |
| Info Center | `org.kde.kinfocenter` | — |
| KIO | `org.kde.kiod6` | — |
| Klipper | `org.kde.klipper` | — |
| KMahjongg | `org.kde.kmahjongg` | — |
| KMail Refresh Settings | `org.kde.kmail-refresh-settings` | — |
| KMail | `org.kde.kmail2` | — |
| Menu Editor | `org.kde.kmenuedit` | — |
| KMines | `org.kde.kmines` | — |
| KMyMoney | `org.kde.kmymoney` | — |
| KNetAttach | `org.kde.knetattach` | — |
| Night Time Service | `org.kde.knighttimed` | — |
| KolourPaint | `org.kde.kolourpaint` | — |
| Konqueror | `org.kde.konqueror` | — |
| Konsole | `org.kde.konsole` | — |
| Kontact | `org.kde.kontact` | — |
| KOrganizer | `org.kde.korganizer` | — |
| KPatience | `org.kde.kpat` | — |
| KDE Wallet Service | `org.kde.ksecretd` | — |
| SSH Credentials | `org.kde.ksshaskpass` | — |
| KSudoku | `org.kde.ksudoku` | — |
| KSystemLog | `org.kde.ksystemlog` | — |
| KTnef | `org.kde.ktnef` | — |
| KWalletManager | `org.kde.kwalletmanager` | — |
| KWin Kill Helper | `org.kde.kwin.killer` | — |
| Marble | `org.kde.marble-qt` | — |
| MBoxImporter | `org.kde.mboximporter` | — |
| Reader | `org.kde.mobile.okular_djvu` | — |
| Reader | `org.kde.mobile.okular_epub` | — |
| Reader | `org.kde.mobile.okular_md` | — |
| Reader | `org.kde.mobile.okular_tiff` | — |
| NeoChat | `org.kde.neochat` | — |
| Okular | `org.kde.okular` | — |
| Online Quotes Editor | `org.kde.onlinequoteseditor6` | — |
| KDE Partition Manager | `org.kde.partitionmanager` | — |
| PIM Data Exporter | `org.kde.pimdataexporter` | — |
| Plasma Session Save | `org.kde.plasma-fallback-session-save` | — |
| Desktop Shell Scripting Console | `org.kde.plasma-interactiveconsole` | — |
| System Monitor | `org.kde.plasma-systemmonitor` | — |
| Welcome Center | `org.kde.plasma-welcome` | — |
| Plasma Browser Integration Host | `org.kde.plasma.browser_integration.host` | — |
| Emoji Selector | `org.kde.plasma.emojier` | — |
| Plasma Keyboard | `org.kde.plasma.keyboard` | — |
| Open System Settings | `org.kde.plasma.settings.open` | — |
| Plasma Desktop Workspace | `org.kde.plasmashell` | — |
| Plasma Windowed | `org.kde.plasmawindowed` | — |
| PolicyKit Authentication Agent | `org.kde.polkit-kde-authentication-agent-1` | — |
| Qrca | `org.kde.qrca` | — |
| Qrca Wifi scanner | `org.kde.qrca.wifi` | — |
| Secret Prompter | `org.kde.secretprompter` | — |
| Sieve Editor | `org.kde.sieveeditor` | — |
| Skanpage | `org.kde.skanpage` | — |
| Spectacle | `org.kde.spectacle` | — |
| Tokodon | `org.kde.tokodon` | — |
| VPN Importer | `org.kde.vpnimport` | — |
| HOW-TO Guides | `org.kfocus.web.howtos` | — |
| Driver Manager | `org.kubuntu.driver-manager` | — |
| Manage Software | `org.kubuntu.manage-software` | — |
| Restore desktop links | `org.kubuntu.restore-desktop-links` | — |
| Kubuntu Website | `org.kubuntu.web.home` | — |
| OpenRGB | `org.openrgb.OpenRGB` | — |
| Imager | `org.raspberrypi.rpi-imager` | — |
| Remmina Connect | `org.remmina.Remmina-file` | — |
| Remmina | `org.remmina.Remmina` | — |
| PhotoCollage | `photocollage` | — |
| Python (v3.14) | `python3.14` | — |
| remmina-gnome | `remmina-gnome` | — |
| Account authentication | `signon-ui` | `signon-ui` `` |
| Handler for snap:// URIs | `snap-handle-link` | — |
| Additional Drivers | `software-properties-drivers-lxqt` | `software-properties` `` |
| Software Sources | `software-properties-lxqt` | `software-properties` `` |
| Software Sources | `software-properties-qt` | `software-properties` `` |
| Steam | `steam` | — |
| Synaptic Package Manager | `synaptic` | `synaptic` `0.91.7build1` |
| System Settings | `systemsettings` | — |
| Startup Disk Creator | `usb-creator-kde` | `usbcreator` `` |
| Vim | `vim` | — |
| VLC media player | `vlc` | — |
| wheelmap.org | `wheelmap-geo-handler` | — |
| Portal | `xdg-desktop-portal-gtk` | — |
| pCloud | `appimagekit-pcloud` | — |
| Google Chrome | `com.google.Chrome` | — |
| Google Chrome | `google-chrome` | — |
| LM Studio | `lmstudio` | — |
| nPerf | `nPerf` | — |
| Sleep diagnostics capture | `net.local.sleep-diagnostics-hotkey` | — |
| pCloud | `pcloud` | — |
| Podman Desktop | `podman-desktop` | — |
| QGroundControl | `qgroundcontrol` | — |
| Reticulum MeshChatX | `reticulum-meshchatx-port18000` | — |
| Reticulum MeshChatX | `reticulum-meshchatx` | — |
| STEAM BOTTLES | `steam-bottles` | — |

</details>

## Applications with no package manager

Invisible to any apt, snap, or flatpak inventory. Several are load-bearing
for this project. **Nothing here updates itself** — each is a manual
re-download, and a stale one is invisible until it fails.

| Kind | Name | Path | Update source |
|---|---|---|---|
| AppImage | `QGroundControl-x86_64.AppImage` | `/home/scottw/Applications/QGroundControl-x86_64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `ReticulumMeshChatX-v4.8.5-linux-x86_64.AppImage` | `/home/scottw/Applications/ReticulumMeshChatX-v4.8.5-linux-x86_64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `ReticulumMeshChatX-v4.9.1-linux-x86_64.AppImage` | `/home/scottw/Applications/ReticulumMeshChatX-v4.9.1-linux-x86_64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `nPerf-latest-x86_64.AppImage` | `/home/scottw/Applications/nPerf-latest-x86_64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `LM-Studio-0.4.20-1-x64.AppImage` | `/home/scottw/Documents/APP IMAGES/LM-Studio-0.4.20-1-x64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `QGroundControl-x86_64.AppImage` | `/home/scottw/Documents/APP IMAGES/QGroundControl-x86_64.AppImage` | MANUAL re-download; no package manager |
| AppImage | `pCloud.AppImage` | `/home/scottw/Documents/APP IMAGES/pCloud.AppImage` | MANUAL re-download; no package manager |
| AppImage | `nPerf.AppImage` | `/home/scottw/.local/bin/nPerf.AppImage` | MANUAL re-download; no package manager |
| /opt tree | `Obsidian` | `/opt/Obsidian` | MANUAL; installed under /opt, not apt |
| /opt tree | `cxoffice` | `/opt/cxoffice` | MANUAL; installed under /opt, not apt |
| /opt tree | `google` | `/opt/google` | MANUAL; installed under /opt, not apt |
| /opt tree | `microsoft` | `/opt/microsoft` | MANUAL; installed under /opt, not apt |
| /opt tree | `ros` | `/opt/ros` | MANUAL; installed under /opt, not apt |
| /usr/local/bin | `cloudflared` | `/usr/local/bin/cloudflared` | MANUAL; built or dropped locally |
| /usr/local/bin | `docker-compose` | `/usr/local/bin/docker-compose` | MANUAL; built or dropped locally |

## Executables in `~/.local/bin`

| Name | Likely source |
|---|---|
| `ao-font-cache-gate.sh` | local script or project tool |
| `ao-fontconfig-watch.sh` | local script or project tool |
| `ao-lmstudio-stop` | python entry point or local tool |
| `ao-lmstudio-supervisor` | python entry point or local tool |
| `ao-podman-gui` | python entry point or local tool |
| `bun` | third-party tool installed to ~/.local/bin |
| `bunx` | third-party tool installed to ~/.local/bin |
| `cffi-gen-src` | python entry point or local tool |
| `cline` | third-party tool installed to ~/.local/bin |
| `dotenv` | python entry point or local tool |
| `esp_rfc2217_server` | python entry point or local tool |
| `esp_rfc2217_server.py` | local script or project tool |
| `espefuse` | local script or project tool |
| `espefuse.py` | local script or project tool |
| `espsecure` | local script or project tool |
| `espsecure.py` | local script or project tool |
| `esptool` | local script or project tool |
| `esptool.py` | local script or project tool |
| `gh` | third-party tool installed to ~/.local/bin |
| `git-remote-rns` | python entry point or local tool |
| `google-chrome` | third-party tool installed to ~/.local/bin |
| `google-chrome-stable` | third-party tool installed to ~/.local/bin |
| `httpx` | python entry point or local tool |
| `httpx2` | python entry point or local tool |
| `idna` | python entry point or local tool |
| `inv` | python entry point or local tool |
| `invoke` | python entry point or local tool |
| `jsonschema` | python entry point or local tool |
| `kwin-mcp` | python entry point or local tool |
| `kwin-mcp-cli` | python entry point or local tool |
| `lmstudio-memory-policy.py` | local script or project tool |
| `lmstudio-protected-launch` | python entry point or local tool |
| `magfit.py` | local script or project tool |
| `magfit_WMM.py` | local script or project tool |
| `magfit_delta.py` | local script or project tool |
| `magfit_gps.py` | local script or project tool |
| `magfit_motors.py` | local script or project tool |
| `mastodon-openclaw-bridge.py` | local script or project tool |
| `mastodon-openclaw-bridge.py.bak.20261001T062710Z` | python entry point or local tool |
| `mavextract.py` | local script or project tool |
| `mavfft.py` | local script or project tool |
| `mavfft_isb.py` | local script or project tool |
| `mavflightmodes.py` | local script or project tool |
| `mavflighttime.py` | local script or project tool |
| `mavgen.py` | local script or project tool |
| `mavgpslock.py` | local script or project tool |
| `mavgraph.py` | local script or project tool |
| `mavkml.py` | local script or project tool |
| `mavlink_bitmask_decoder.py` | local script or project tool |
| `mavlogdump.py` | local script or project tool |
| `mavloss.py` | local script or project tool |
| `mavmission.py` | local script or project tool |
| `mavparmdiff.py` | local script or project tool |
| `mavparms.py` | local script or project tool |
| `mavplayback.py` | local script or project tool |
| `mavsearch.py` | local script or project tool |
| `mavsigloss.py` | local script or project tool |
| `mavsummarize.py` | local script or project tool |
| `mavtogpx.py` | local script or project tool |
| `mavtomfile.py` | local script or project tool |
| `mcp` | third-party tool installed to ~/.local/bin |
| `meshchatx-register-tray` | python entry point or local tool |
| `meshchatx-watchdog` | python entry point or local tool |
| `meshchatx-watchdog-port18000` | python entry point or local tool |
| `nPerf.AppImage` | third-party tool installed to ~/.local/bin |
| `obsidian` | third-party tool installed to ~/.local/bin |
| `openclaw-kwallet-secret` | python entry point or local tool |
| `openclaw-lmstudio-mcp-direct.js` | local script or project tool |
| `openclaw-lmstudio-mcp-direct.js.bak-direct-runtime-20260925` | python entry point or local tool |
| `openclaw-lmstudio-mcp.js` | local script or project tool |
| `pcloud` | third-party tool installed to ~/.local/bin |
| `rncp` | local script or project tool |
| `rngcs` | local script or project tool |
| `rngit` | local script or project tool |
| `rnid` | local script or project tool |
| `rnir` | local script or project tool |
| `rnodeconf` | local script or project tool |
| `rnpath` | local script or project tool |
| `rnpkg` | local script or project tool |
| `rnprobe` | local script or project tool |
| `rnsd` | local script or project tool |
| `rnsh` | local script or project tool |
| `rnstatus` | local script or project tool |
| `rnx` | local script or project tool |
| `sleep-capture-notify` | python entry point or local tool |
| `sleep-diagnostics` | python entry point or local tool |
| `start-meshchatx-firefox` | python entry point or local tool |
| `uvicorn` | python entry point or local tool |

## pip / pipx / npm global

| Ecosystem | Package | Version | Update source |
|---|---|---|---|
| pip --user | `anyio` | `4.14.2` | PyPI; manual, no upgrade timer |
| pip --user | `asyncssh` | `2.24.0` | PyPI; manual, no upgrade timer |
| pip --user | `cffi` | `2.1.1` | PyPI; manual, no upgrade timer |
| pip --user | `cryptography` | `50.0.1` | PyPI; manual, no upgrade timer |
| pip --user | `fastcrc` | `0.3.6` | PyPI; manual, no upgrade timer |
| pip --user | `h11` | `0.16.0` | PyPI; manual, no upgrade timer |
| pip --user | `httpcore` | `1.0.9` | PyPI; manual, no upgrade timer |
| pip --user | `httpcore2` | `2.9.1` | PyPI; manual, no upgrade timer |
| pip --user | `httpx` | `0.28.1` | PyPI; manual, no upgrade timer |
| pip --user | `httpx-sse` | `0.4.3` | PyPI; manual, no upgrade timer |
| pip --user | `httpx2` | `2.9.1` | PyPI; manual, no upgrade timer |
| pip --user | `idna` | `3.18` | PyPI; manual, no upgrade timer |
| pip --user | `invoke` | `3.0.3` | PyPI; manual, no upgrade timer |
| pip --user | `jsonschema` | `4.26.0` | PyPI; manual, no upgrade timer |
| pip --user | `jsonschema-specifications` | `2025.9.1` | PyPI; manual, no upgrade timer |
| pip --user | `kwin-mcp` | `0.7.0` | PyPI; manual, no upgrade timer |
| pip --user | `mcp` | `1.30.0` | PyPI; manual, no upgrade timer |
| pip --user | `mcp-types` | `2.0.0` | PyPI; manual, no upgrade timer |
| pip --user | `opentelemetry-api` | `1.44.0` | PyPI; manual, no upgrade timer |
| pip --user | `paramiko` | `5.0.0` | PyPI; manual, no upgrade timer |
| pip --user | `piexif` | `1.1.3` | PyPI; manual, no upgrade timer |
| pip --user | `pycparser` | `3.0` | PyPI; manual, no upgrade timer |
| pip --user | `pydantic-settings` | `2.15.0` | PyPI; manual, no upgrade timer |
| pip --user | `pymavlink` | `2.4.49` | PyPI; manual, no upgrade timer |
| pip --user | `pynmeagps` | `1.1.7` | PyPI; manual, no upgrade timer |
| pip --user | `python-dotenv` | `1.2.3` | PyPI; manual, no upgrade timer |
| pip --user | `python-multipart` | `0.0.32` | PyPI; manual, no upgrade timer |
| pip --user | `referencing` | `0.37.0` | PyPI; manual, no upgrade timer |
| pip --user | `rpds-py` | `2026.6.3` | PyPI; manual, no upgrade timer |
| pip --user | `sse-starlette` | `3.4.6` | PyPI; manual, no upgrade timer |
| pip --user | `starlette` | `1.3.1` | PyPI; manual, no upgrade timer |
| pip --user | `truststore` | `0.10.4` | PyPI; manual, no upgrade timer |
| pip --user | `uvicorn` | `0.52.1` | PyPI; manual, no upgrade timer |
| pipx | `esptool` | `5.4.0` | PyPI; pipx upgrade, manual |
| pipx | `rns` | `1.4.2` | PyPI; pipx upgrade, manual |
| npm -g | `cline` | `3.0.60` | npm registry; manual |
| npm -g | `corepack` | `0.36.0` | npm registry; manual |
| npm -g | `kanban` | `0.1.70` | npm registry; manual |
| npm -g | `npm` | `11.19.0` | npm registry; manual |

## Snap, Flatpak, and containers

| Package | Version | Channel / branch | Update source |
|---|---|---|---|
| snap:`bare` | `1.0` (rev 5) | latest/stable | snap store; UNATTENDED |
| snap:`brave` | `1.96.60` (rev 688) | latest/stable | snap store; UNATTENDED |
| snap:`core20` | `20260901` (rev 2922) | latest/stable | snap store; UNATTENDED |
| snap:`core22` | `20260824` (rev 2955) | latest/stable | snap store; UNATTENDED |
| snap:`core24` | `20260824` (rev 2124) | latest/stable | snap store; UNATTENDED |
| snap:`core26` | `20260629` (rev 462) | latest/stable | snap store; UNATTENDED |
| snap:`cups` | `2.4.19-6` (rev 1262) | latest/stable | snap store; UNATTENDED |
| snap:`dbeaver-ce` | `26.2.1.202609210342` (rev 557) | latest/stable | snap store; UNATTENDED |
| snap:`firefox` | `157.0-1` (rev 8995) | latest/stable/… | snap store; UNATTENDED |
| snap:`gnome-42-2204` | `0+git.4982e7b-sdk0+git.69b626a` (rev 263) | latest/stable | snap store; UNATTENDED |
| snap:`gnome-46-2404` | `0+git.b31ceab-sdk0+git.f80dd8b` (rev 168) | latest/stable/… | snap store; UNATTENDED |
| snap:`gtk-common-themes` | `0.1-81-g442e511` (rev 1535) | latest/stable/… | snap store; UNATTENDED |
| snap:`gtk-theme-breeze` | `1.5` (rev 8) | latest/stable/… | snap store; UNATTENDED |
| snap:`icon-theme-breeze` | `1.3` (rev 5) | latest/stable/… | snap store; UNATTENDED |
| snap:`mesa-2404` | `25.2.8-snap288` (rev 1839) | latest/stable/… | snap store; UNATTENDED |
| snap:`orcaslicer` | `2.4.2` (rev 9) | latest/stable | snap store; UNATTENDED |
| snap:`snapd` | `2.76.3` (rev 27738) | latest/stable | snap store; UNATTENDED |
| flatpak:`com.usebottles.bottles` | `66.7` | stable (flathub) | flathub; manual, no timer installed |
| container:`ao-build-update` | — | build-update | container registry; manual promote |
| container:`ao-fabrication-db` | — | fabrication | container registry; manual promote |
| container:`ao-nodeodm` | — | mapping | container registry; manual promote |
| container:`ao-webodm-broker` | — | mapping | container registry; manual promote |
| container:`ao-webodm-db` | — | mapping | container registry; manual promote |
| container:`ao-webodm-web` | — | mapping | container registry; manual promote |
| container:`ao-webodm-worker` | — | mapping | container registry; manual promote |
| container:`ao-grafana` | — | operations | container registry; manual promote |
| container:`ao-metabase` | — | operations | container registry; manual promote |
| container:`ao-node-exporter` | — | operations | container registry; manual promote |
| container:`ao-prometheus` | — | operations | container registry; manual promote |
| container:`ao-ingress-payment` | — | payment | container registry; manual promote |
| container:`ao-mastodon-db` | — | sales | container registry; manual promote |
| container:`ao-mastodon-redis` | — | sales | container registry; manual promote |
| container:`ao-mastodon-sidekiq` | — | sales | container registry; manual promote |
| container:`ao-mastodon-streaming` | — | sales | container registry; manual promote |
| container:`ao-mastodon-web` | — | sales | container registry; manual promote |
| container:`ao-sales-db` | — | sales | container registry; manual promote |
| container:`ao-sim-fabrication-gui-gz` | — | sim-fabrication | container registry; manual promote |
| container:`ao-sim-fabrication-gz` | — | sim-fabrication | container registry; manual promote |
| container:`ao-ardupilot-sitl` | — | sim-vehicle | container registry; manual promote |

