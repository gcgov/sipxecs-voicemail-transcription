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

## Manual Install for CentOS 6
 1. Install Python3 and pip

 2. Create the directories:
	 `/usr/voicemailtranscription`
	 `/usr/voicemailtranscription/voicemail`
	 `/usr/voicemailtranscription/credentials`

 3. Create a Google Cloud Console Project
	 1. Enable Google Cloud Speech API
	 	 1. In the cloud console, generate the app credentials JSON file. Save the json credentials as `/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json`
	 	 2. On your server, Set Environment variable `GOOGLE_APPLICATION_CREDENTIALS = ./credentials/SipxecsVoicemailtoText.json` CentOS6: Run command: `export GOOGLE_APPLICATION_CREDENTIALS=/usr/voicemailtranscription/credentials/SipxecsVoicemailtoText.json`
	 2. Enable Google Cloud Storage
	 	 1. In the cloud console, create a storage bucket in GCS
	 	 2. On your server, create a text file named `/usr/voicemailtranscription/credentials/cloudstoragebucket.txt`. Enter the name of the bucket as the only contents of the file. Do not include any whitespace or blank lines.
	 	 3. On your server, Set Environment variable `GOOGLE_CLOUD_PROJECT = {project_id}` (replace `{project_id}` with your project's id)

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
