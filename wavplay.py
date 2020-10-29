#coding: utf-8
# 参考 http://aidiary.hatenablog.com/entry/20110515/1305420830
# 準備 sudo port install py27-pyaudio 

import wave
import pyaudio
import sys # argv

def wavplay(fname):
    wf = wave.open(fname, "r")

    # ストリームを開く
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # チャンク単位でストリームに出力し音声を再生
    chunk = 1024
    data = wf.readframes(chunk)
    while data != '':
        stream.write(data)
        data = wf.readframes(chunk)
    stream.close()
    p.terminate()
