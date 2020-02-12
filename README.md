# sipxecs-voicemail-transcription

Install this on your Ezuce unitme server to add voicemail transcriptions to voicemail emails utilizing Google's Cloud Speech-to-Text API.

![Alt text](screenshot/sample.PNG?raw=true "Voicemail email with transcription")

 - Requirements:
	 - Python3
	 - Google Cloud Project
	 	 - Project needs access to the Google Cloud Storage API (https://cloud.google.com/storage/) and the Google Cloud Speech API (https://cloud.google.com/speech/)
	 	 - In the Google Cloud Console, create and download Application Service Credentials as a JSON file

## Installing with install.sh
 1. Download entire package into a local directory
 2. cd into that directory and run install.sh
 3. Save Google Cloud Application Credentials JSON file as `/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json`

## Manual Install for CentOS 7
 1. Install Python3 by running command `sudo yum install python3`
 
 2. Install google speech libraries for Python3 `pip3 install google-cloud-speech`

 2. Create directories:
	 `/usr/voicemailtranscription`
	 `/usr/voicemailtranscription/voicemail`
	 `/usr/voicemailtranscription/credentials`

 3. Copy code base into /usr/voicemailtranscription. Run `chmod 777` on all files and directories (there is likely a more precise permission model to use but this works for us, for now.

 4. Modify SendMail configuration
	 1. Append the following lines to */etc/mail/sendmail.mc*
		```
		dnl #Mail filter
		INPUT_MAIL_FILTER(`vrfilter', `S=inet:5000@localhost, T=C:5m;R:5m')dnl
		define(`confINPUT_MAIL_FILTERS', `vrfilter')dnl
		dnl#
		```
	 2. Run command: m4 /etc/mail/sendmail.mc > /etc/mail/sendmail.cf
	 3. Run command: service sendmail restart

 6. Copy `vrmilter.py` and `libmilter.py` into `/usr/voicemailtranscription/`
 7. Copy `voicemailtranscriptionservice.sh` to have the file name and path `/etc/init.d/voicemailtranscription`
 	1. Run command `chmod 777 /etc/init.d/voicemailtranscription`
	2. Run command `chkconfig voicemailtranscription on` to make the transcription service start on bootup


## Manage Service
To start service: `service voicemailtranscription start`
To stop service: `service voicemailstranscription stop`
To restart service: `service voicemailstranscription restart`

## Logging
All output of the voicemailtranscription service is logged to `/var/log/voicemailtranscription.log`. Once you have the milter running as a service, to verify the service is working or to watch for any errors, `tail -f /var/log/voicemailtranscription.log`
