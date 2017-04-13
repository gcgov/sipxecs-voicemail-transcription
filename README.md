# sipxecs-voicemail-transcription

This project extends sipxcom voicemail email notifications to include a voice to text transcription. Requirements:
- sipxcom
- Python3
- Credentials for the Google CLOUD SPEECH API (https://cloud.google.com/speech/)

## Installing with install.sh
 1. Download entire package into a local directory
 2. cd into that directory and run install.sh
 3. Sign up for Google Cloud Speech API
 	 1. Generate the app credentials JSON file. Save the json credentials as `./credentials/SipxecsVoicemailtoText.json`
	 2. Set Environment variable `GOOGLE_APPLICATION_CREDENTIALS = ./credentials/SipxecsVoicemailtoText.json` CentOS6: Run command: `export GOOGLE_APPLICATION_CREDENTIALS=/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json`

## Manual Install for CentOS 6
 1. Install Python3 and pip

 2. Create the directories:
	 `/usr/voicemailtranscription`
	 `/usr/voicemailtranscription/voicemail`
	 `/usr/voicemailtranscription/credentials`

 3. Sign up for Google Cloud Speech API
 	 1. Generate the app credentials JSON file. Save the json credentials as `./credentials/SipxecsVoicemailtoText.json`
	 2. Set Environment variable `GOOGLE_APPLICATION_CREDENTIALS = ./credentials/SipxecsVoicemailtoText.json` CentOS6: Run command: `export GOOGLE_APPLICATION_CREDENTIALS=/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json`

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
	3. Run command `sh /etc/init.d/voicemailtranscription start` to make the transcription service right now

## Testing without running as service
Follow instructions 1-6 of the manual install. Run command: `python3 vrmilter.py`. All output is dumpped to the terminal. If results are satisfactory, follow step 7 to run the milter as a service so that it is always transcribing voicemails.

## Logging
All output of the voicemailtranscription service is logged to `/var/log/voicemailtranscription.log`. Once you have the milter running as a service, to verify the service is working or to watch for any errors, `tail -f /var/log/voicemailtranscription.log`
