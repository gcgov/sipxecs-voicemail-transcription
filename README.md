# sipxecs-voicemail-translation

This project extends sipxcom/sipexcs voicemail emails to include a voice to text transcription. Requirements:
- Python3
- Credentials for the Google CLOUD SPEECH API (https://cloud.google.com/speech/)

## Installing
 1. Install Python3
 
 2. Create the directories:
	 `/usr/voicemailtranscription`
	 `/usr/voicemailtranscription/voicemail`
	 `/usr/voicemailtranscription/credentials`
	 
 3. Sign up for Google Cloud Speech API
 	 1. Generate the app credentials JSON file. Save the json credentials as `./credentials/SipxecsVoicemailtoText.json`
	 2. Set Environment variable `GOOGLE_APPLICATION_CREDENTIALS = ./credentials/SipXecsVoicemailToText.json`

 4. Modify SendMail configuration
	 1. Append the following lines to */etc/mail/sendmail.mc*
```
dnl #Mail filter
INPUT_MAIL_FILTER(`vrfilter', `S=inet:5000@localhost, T=C:5m;R:5m')dnl
define(`confINPUT_MAIL_FILTERS', `vrfilter')dnl
dnl#
```
	 2. Run command: `m4 /etc/mail/sendmail.mc > /etc/mail/sendmail.cf`
	 3. Run command: `service sendmail restart`

 6. Copy `vrmilter.py` and `libmilter.py` into `/usr/voicemailtranscription/`
