#!/usr/bin/env python3

#
# This milter corrects links and tries to convert a WAV file to text.
#

# Standard library.
import base64
import os
import os.path
import io
import subprocess
import sys
import tempfile
import time
import string
import random
import signal
import traceback

import libmilter as lm

from contextlib import contextmanager
from textwrap import dedent

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from pydub import AudioSegment

#=======================================================================
# Global settings
#=======================================================================
GLV_TMP_PATH_TO_SAVE_VOICEMAIL = '/usr/voicemailtranscription/voicemail/'


#=======================================================================
# Recognizer
#=======================================================================
def glog(msg):
    t = time.strftime('%H:%M:%S')
    print('[%s] %s' % (t, msg))
    sys.stdout.flush()
        
def decode_speech(file_name):
    result = "No transcription available"

    try:
        result = subprocess.check_output(['/usr/voicemailtranscription/go/./transcription', file_name], encoding='utf-8')
    except Exception as e:
        result = "Transcription failed"

    print(result)

    return result


#=======================================================================
# Milter capturer & process handler
#=======================================================================
def fn_run_milter():
    """When the script runs, this is the primary entry point.
        It generates a listener for sendmail
    """
    # We can set our milter opts here
    opts = lm.SMFIF_CHGFROM | lm.SMFIF_ADDRCPT | lm.SMFIF_CHGBODY | lm.SMFIF_CHGFROM

    # We initialize the factory we want to use (you can choose from an
    # AsyncFactory, ForkFactory or ThreadFactory.  You must use the
    # appropriate mixin classes for your milter for Thread and Fork)
    f = lm.ForkFactory('inet:127.0.0.1:5000', VRMilter, opts)

    def sigHandler(num, frame):
        f.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigHandler)
    try:
        # run it
        f.run()
    except Exception as e:
        f.close()
        glog('EXCEPTION OCCURED: ' + str(e))
        sys.exit(3)


#=======================================================================
# Helper Functions
#=======================================================================
def split_body_pieces(body):
    """Take the entire body (as a real string) provided by the milter class
       and divide it into it's content type pieces
       return an array of strings
    """
    first_piece = True
    lines = []
    for byteline in body.split("\r\n"):
        line = str(byteline)
        if line.startswith("------=_Part_"):
            if first_piece:
                first_piece = False
            else:
                data = '\n'.join(lines)
                yield data
                del data
                lines = []
        lines.append(line)
    if len(lines) > 0:
        yield '\r\n'.join(lines)


def get_content_type(piece):
    """Provide a body piece (as provided by split_body_pieces) and get the content type header"""
    for line in piece.split("\n"):
        if line.startswith("Content-Type: "):
            glog(line)
            return line[len("Content-Type: "):].strip()
    return "Unknown"


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    """Get a random string of numbers and uppercase letters"""
    return ''.join(random.choice(chars) for _ in range(size))


def fn_extract_wav(piece):
    """Save the base64 encoded wav data in this email piece and
        return the file path and name as a string
    """
    glog('Extracting wav from piece')

    # parse this piece of the email text to merge the
    #  base64 encoded string into one line and then
    #  decode the string into binary data
    capture = False
    lines = []
    index = 0
    for line in piece.split('\n'):
        if line.strip() == "":
            capture = True
        if capture == True:
            lines.append(line.strip())
            index = index + 1

    b64_data = ''.join(lines)
    data = base64.b64decode(b64_data)

    rs_string = random_string(20)

    if not os.path.exists(GLV_TMP_PATH_TO_SAVE_VOICEMAIL):
        os.makedirs(GLV_TMP_PATH_TO_SAVE_VOICEMAIL)

    rs_path = GLV_TMP_PATH_TO_SAVE_VOICEMAIL + rs_string + '.wav'
    glog("save wav file to " + rs_path)
    with open(rs_path, 'wb') as f:
        f.write(data)

    # return temporary file path and name
    return rs_path


def fn_extract_mp3(piece):
    """Save the base64 encoded wav data in this email piece and
        return the file path and name as a string
    """
    glog('Extracting wav from piece')

    # parse this piece of the email text to merge the
    #  base64 encoded string into one line and then
    #  decode the string into binary data
    capture = False
    lines = []
    index = 0
    for line in piece.split('\n'):
        if line.strip() == "":
            capture = True
        if capture == True:
            lines.append(line.strip())
            index = index + 1

    b64_data = ''.join(lines)
    data = base64.b64decode(b64_data)

    rs_string = random_string(20)

    if not os.path.exists(GLV_TMP_PATH_TO_SAVE_VOICEMAIL):
        os.makedirs(GLV_TMP_PATH_TO_SAVE_VOICEMAIL)

    rs_path = GLV_TMP_PATH_TO_SAVE_VOICEMAIL + rs_string + '.mp3'
    glog("save mp3 file to " + rs_path)
    with open(rs_path, 'wb') as f:
        f.write(data)

    wav_path = GLV_TMP_PATH_TO_SAVE_VOICEMAIL + rs_string + '.wav'
    sound = AudioSegment.from_mp3(rs_path)
    sound.export(wav_path, format="wav")

    #delete the mp3
    try:
        os.unlink(rs_path)
    except:
        pass         

    # return temporary file path and name for wav
    return wav_path


def exec_cmd(cmd, **kwds):
    """
    Execute arbitrary commands as sub-processes.
    """
    stdin = kwds.get('stdin', None)
    stdin_flag = None
    if not stdin is None:
        stdin_flag = subprocess.PIPE
    proc = subprocess.Popen(
        cmd,
        stdin=stdin_flag,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(stdin)
    return (proc.returncode, stdout, stderr)


#=======================================================================
# Extend the Milter Class (where the email is captured)
#=======================================================================
class VRMilter(lm.ForkMixin, lm.MilterProtocol):
    def __init__(self, opts=0, protos=0):
        # We must init our parents here
        lm.MilterProtocol.__init__(self, opts, protos)
        lm.ForkMixin.__init__(self)
        # You can initialize more stuff here
        self.ignore = False
        self.body_parts = []
        self.modernEmail = None

    def log(self, msg):
        t = time.strftime('%H:%M:%S')
        print('[%s] %s' % (t, msg))
        sys.stdout.flush()

    @lm.noReply
    def connect(self, hostname, family, ip, port, cmdDict):
        self.log('Connect from %s:%d (%s) with family: %s' % (ip, port,
                                                              hostname, family))
        return lm.CONTINUE

    @lm.noReply
    def helo(self, heloname):
        self.log('HELO: %s' % heloname)
        return lm.CONTINUE

    @lm.noReply
    def mailFrom(self, frAddr, cmdDict):
        self.log('MAIL: %s' % frAddr)
        return lm.CONTINUE

    @lm.noReply
    def rcpt(self, recip, cmdDict):
        self.log('RCPT: %s' % recip)
        return lm.CONTINUE

    @lm.noReply
    def header(self, key, val, cmdDict):
        self.log('%s: %s' % (key, val))
        if key == 'From' and not val.startswith('Voicemail Notification Service'):
            self.log("Not from the voice notification service--skipping this email")
            self.ignore = True
            return lm.ACCEPT
        if key == 'Subject' and 'fax' in val:
            self.log("Fax email--skipping this email")
            self.ignore = True
            return lm.ACCEPT
        return lm.CONTINUE

    @lm.noReply
    def eoh(self, cmdDict):
        self.log('EOH')
        return lm.CONTINUE

    def data(self, cmdDict):
        self.log('DATA')
        return lm.CONTINUE

    @lm.noReply
    def body(self, chunk, cmdDict):
        self.log('Body chunk: ' + str(len(chunk)))
        self.body_parts.append(chunk.decode('UTF-8'))
        # make sure that's a decode, not a cast to string. because, fuck python
        return lm.CONTINUE

    def eob(self, cmdDict):
        self.log('EOB')

        newbody = ''

        if not self.ignore:
            try:
                body = ''.join(self.body_parts)
                self.log("body size: " + str(len(body)))
                new_pieces = []
                
                
                audio_file_name = None
                vr_text = None

                #find wav or mp3 in body
                self.log("Searching for WAV or MP3 ...")
                for __n, piece in enumerate(split_body_pieces(body)):
                    self.log("Processing piece #" + str(__n))
                    ct = get_content_type(piece)
                    self.log("Content-type: " + ct)

                    #wav
                    if ct.startswith("audio/x-wav"):
                        self.log("Extracting WAV ...")
                        try:
                            audio_file_name = fn_extract_wav(piece)
                        except: 
                            pass    

                    #mp3
                    if ct.startswith("audio/mpeg") or  ct.startswith("audio/x-mpeg-3"):
                        self.log("Extracting MP3 ...")
                        try:
                            audio_file_name = fn_extract_mp3(piece)
                        except: 
                            pass   


                #if audio was found, transcribe it and then delete the file
                if audio_file_name is not None:
                    try:
                        self.log("decode speech on "+audio_file_name)
                        vr_text = decode_speech(audio_file_name)
                        self.log("finished speech decoding on "+audio_file_name)
                    except Exception as ex:
                        self.log("decode speech failed")
                        self.log(str(ex))

                    #delete the wav or mp3 file we created if it was created
                    try:
                        os.unlink(audio_file_name)
                    except:
                        pass         

                #append content to email body
                self.log("Assembling message ...")
                for __n, piece in enumerate(split_body_pieces(body)):
                    self.log("Processing piece #" + str(__n))
                    new_piece = str(piece)
                    ct = get_content_type(piece)
                    self.log("Content-type: " + ct)
                    if ct.startswith("text/html"):
                        if vr_text is not None:
                            vr_html = '<p style="font-family:Helvetica,Arial,sans-serif;color:#000000;font-size:16px;margin:0;">Transcription: ' + vr_text + '</p>'
                            new_piece = new_piece.replace(
                                "</body>", vr_html + "</body>")
                    elif ct.startswith("text/plain"):
                        if vr_text is not None:
                            new_piece = new_piece + "\r\n\r\nTranscription: " + vr_text
                    new_pieces.append(new_piece)
                newbody = '\r\n'.join(new_pieces)

            except Exception as ex:
                self.log(str(ex))

            self.replBody(newbody.encode())
        return lm.CONTINUE

    def close(self):
        self.log('Close called. QID: %s' % self._qid)


# RUN ACTION run and enable the milter
def set_exit_handler(func):
    signal.signal(signal.SIGTERM, func)


def on_exit(sig, func=None):
    print("exit handler triggered")
    sys.exit(1)


if __name__ == '__main__':
    fn_run_milter()
