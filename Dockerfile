FROM alpine

MAINTAINER Jaka Hudoklin <offlinehacker@users.noreply.github.com>

RUN apk add --no-cache bash hostapd iptables dhcp docker iproute2 iw && \
 apk add --no-cache --update python3 screen && \
 pip3 install --upgrade pip setuptools
RUN pip3 install zeroconf requests tornado
RUN echo "" > /var/lib/dhcp/dhcpd.leases
ADD wlanstart.sh /bin/wlanstart.sh

ADD start_flash.sh /root
COPY scripts /root/scripts
COPY files /root/files

WORKDIR /root
ENTRYPOINT [ "/root/start_flash.sh" ]
