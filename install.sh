#!/bin/bash

#install python
# Compilers and related tools:
yum groupinstall -y "development tools"
# Libraries needed during compilation to enable all features of Python:
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel
# If you are on a clean "minimal" install of CentOS you also need the wget tool:
yum install -y wget
wget http://python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz
tar xf Python-3.6.0.tar.xz
cd Python-3.6.0
./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
make install

#install pip
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py

#custom email format
cp EmailFormats.properties /etc/sipxpbx/sipxivr/EmailFormats.properties

#python scripts
mkdir -p /usr/voicemailtranscription/voicemail
mkdir -p /usr/voicemailtranscription/credentials
mkdir -p /usr/voicemailtranscription/go
cp go/transcription /usr/voicemailtranscription/go/transcription
cp vrmilter.py /usr/voicemailtranscription/vrmilter.py
cp libmilter.py /usr/voicemailtranscription/libmilter.py
export GOOGLE_APPLICATION_CREDENTIALS=/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json

#google cloud
pip3.6 install --upgrade google-api-python-client
pip3.6 install --upgrade google-cloud-speech

#append to sendmail
echo "dnl #Mail filter" >> /etc/mail/sendmail.mc
echo "INPUT_MAIL_FILTER(\`vrfilter', \`S=inet:5000@localhost, T=C:5m;R:5m')dnl" >> /etc/mail/sendmail.mc
echo "define(\`confINPUT_MAIL_FILTERS', \`vrfilter')dnl" >> /etc/mail/sendmail.mc
echo "dnl#" >> /etc/mail/sendmail.mc

m4 /etc/mail/sendmail.mc > /etc/mail/sendmail.cf

service sendmail restart

#make into a service
cp voicemailtranscriptionservice.sh /etc/init.d/voicemailtranscription
chmod 777 /etc/init.d/voicemailtranscription
chkconfig voicemailtranscription on
sh /etc/init.d/voicemailtranscription start