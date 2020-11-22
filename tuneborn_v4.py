#!/usr/bin/env python
# coding: utf-8

# # Tune-born v4
# ## 一通りのインタラクションの実装
# - ビートを最初から再生
# - 人がいないときは顔を少し出す
# - 人がいるときは顔をだして声を出す
# - 鍵盤からの入力があるとそれに他するメロディを生成
# ### 問題点    
# - 各工程が同期的
#    
# ## 不確定さ
# - 身体の傾きとピッチのみ
# 
# ## 改良しなきゃいけないこと
# - 「人がいないときモード」などを非同期にする(入力があったら中断する)
# - カラの開閉とカットオフの対応
# - 天候などから作用される要素の追加

# In[1]:


from autocomposition import AutoComposition


# In[2]:


import cv2
import time
import threading
from midikeyboard import MIDIKeyboard
import serial
import note_seq
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2

from synth import Series
from interface import SingNoteSequence
from oscillator import PulseWave
from FX import Lowpass
from amplifier import SimpleAmp
from controller import *

from beatplayer import BeatPlayer


# In[3]:


def face_detection(cascade, cap):
    end_flag, c_frame = cap.read()
    # 画像の取得と顔の検出
    img = c_frame
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = cascade.detectMultiScale(img_gray, minSize=(100, 100))

    # 検出した顔の数
    if face_list != ():
        face_num = len(face_list)
    else:
        face_num = 0

    return face_num


# In[4]:


# その他設定
port = '/dev/cu.usbmodem141301'
bundle = './content/attention_rnn.mag'
cascade_file = "./haar/haarcascade_frontalface_alt.xml"
device_id = 0
sess_flag = False
s_qpm = 100
inflag = False


# 歌用シンセの設定
tb = Series()
tb_if = tb.stack(SingNoteSequence(port=port))
tb_osc = tb.stack(PulseWave(interval=24))
#tb_LPC = LPC(a=a)
tb_lp = tb.stack(Lowpass(fs=1000, fp=10000))
tb_amp = tb.stack(SimpleAmp(volume=0.7))

tbe_amp = Envelope(A=0.01, D=0.2, S=0.6, R=0.5)
tbe_amp.assign(tb_amp.amp)
tbe_amp.assign(tb_lp.ws, 0.2)
tbe_cont = ArduinoController(com=port, baudrate=9600)
tbe_cont.assign(tb_osc.fine, 100.)

tb.implement(tbe_amp)
tb.implement(tbe_cont)
tb.completed()

# 鳴声用シンセの設定
peep = Series()
peep_if = peep.stack(SingNoteSequence())
peep_osc = peep.stack(PulseWave(interval=24))
peep_lp = peep.stack(Lowpass(fs=1000, fp=10000))
peep_amp = peep.stack(SimpleAmp(volume=0.9))

penv_amp = Envelope(A=0.01, D=0.5, S=0.6, R=0.2)
penv_amp.assign(peep_amp.amp)
penv_amp.assign(peep_osc.fine, -50.)

peep.implement(penv_amp)
peep.completed()


# インスタンスたち
cascade = cv2.CascadeClassifier(cascade_file)
cap = cv2.VideoCapture(device_id)
mk = MIDIKeyboard()
ac = AutoComposition(bundle, 'attention_rnn')
ac.initialize()
bp = BeatPlayer("./beat/beat100.wav", s_qpm, 8)
bp.setVolume(0.4)
bp_thread = threading.Thread(target=bp.play_beat)


# ノートシーケンスの設定
# 少し声を出す(嬉しそうに)
chirp_ns = music_pb2.NoteSequence()
chirp_ns.notes.add(pitch=60, start_time=0., end_time=1., velocity=80)
chirp_ns.total_time = 1.0
chirp_ns.tempos.add(qpm=60)
# 喜びの声
happy_ns = music_pb2.NoteSequence()
happy_ns.notes.add(pitch=64, start_time=0., end_time=1., velocity=100)
happy_ns.notes.add(pitch=64, start_time=1., end_time=2., velocity=100)
happy_ns.notes.add(pitch=64, start_time=2., end_time=3., velocity=100)
happy_ns.total_time = 2.5
happy_ns.tempos.add(qpm=120)


# 開始
bp_thread.start()
with serial.Serial(port, 9600,timeout=1) as ser:
    flag=bytes('0','utf-8')
    ser.write(flag)
    
i = 0
while True: 
    
    # 人がいるか
    face = face_detection(cascade, cap)
    # 鍵盤入力待機
    input_sequence = mk.wait(timeout=1.0, in_timeout=5.0) 
    if input_sequence != []:
        inflag = True
        qpm, note_sequence = mk.make_note_sequence(input_sequence)
    else: 
        inflag = False
    
    # 人おるけど鍵盤入力なし
    if face > 0 and inflag == False:
        # 声を出す(嬉しそうに)
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('4','utf-8')
            ser.write(flag)
        peep_if.set_note_sequence(chirp_ns)
        peep.play()
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('0','utf-8')
            ser.write(flag)
    
    # 鍵盤の入力なし且、人いない
    elif inflag == False:
        # 顔を出して周り見る
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('2','utf-8')
            ser.write(flag)
            time.sleep(2.0)
            flag=bytes('0','utf-8')
            ser.write(flag)
    
    # 鍵盤入力あり
    elif inflag == True:
        out_sequence = ac.generate(note_sequence)
        #for j in range(len(note_sequence.notes)):
            #out_sequence.notes.pop(0)
        out_sequence.tempos[0].qpm = s_qpm
        tb_if.set_note_sequence(out_sequence)
        while True:
            if bp.state == 1:
                tb.play()
                break
                
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('0','utf-8')
            ser.write(flag)
        
        i = i + 1
    
    if i == 10:
        mk.quit()
        break

# インタラクション終了
while True:
    if bp.state == 1:
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('5','utf-8')
            ser.write(flag)
        peep_if.set_note_sequence(happy_ns)
        peep.play() 
        break
        
with serial.Serial(port, 9600,timeout=1) as ser:
    flag=bytes('0','utf-8')
    ser.write(flag)


# In[ ]:





# In[ ]:




