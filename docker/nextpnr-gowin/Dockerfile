# nextpnr-himbaechel (Gowin) + chipdb + gowin_pack for PyFPGA Openflow.
#
# Build: docker build -t pyfpga/nextpnr-gowin:sid -f docker/nextpnr-gowin/Dockerfile .
# SPDX-License-Identifier: GPL-3.0-or-later

FROM debian:sid-slim

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nextpnr-himbaechel-gowin \
      nextpnr-himbaechel-gowin-chipdb \
      python3-apycula \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && ln -sf nextpnr-himbaechel-gowin /usr/bin/nextpnr-himbaechel
