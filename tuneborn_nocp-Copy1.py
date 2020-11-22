#!/usr/bin/env python
# coding: utf-8

# TODO
# - [ ] 二小節ごとにターンチェンジ
# - [ ] 非同期にする
# 
# 余裕があったら
# - [ ] 人がおらん時は鼻歌歌う

# In[1]:


from autocomposition import AutoComposition

import cv2
import time
import threading
import random
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


# In[2]:


# スレッド
# 顔認識
def face_detection():
    global cascade, cap, face_num
    while face_num < 1:
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
        
# 顔出す
def peek():
    global port, flag
    with serial.Serial(port, 9600,timeout=1) as ser:
        flag=bytes('2','utf-8')
        ser.write(flag)
        time.sleep(2.0)
        flag=bytes('0','utf-8')
        ser.write(flag)

# 鍵盤入力まち
def wait_key_input():
    global mk, input_sequence
    input_sequence = mk.wait(timeout=1.0, in_timeout=None)
    
    


# In[3]:


# その他設定
port = '/dev/cu.usbmodem141301'
bundle = './content/attention_rnn.mag'
cascade_file = "./haar/haarcascade_frontalface_alt.xml"
face_num = 0
device_id = 0
sess_flag = False
s_qpm = 100
in_flag = False
start_time = time.time()
input_sequence = []

# 歌用シンセの設定
tb = Series()
tb_if = tb.stack(SingNoteSequence(port=port))
tb_osc = tb.stack(PulseWave(interval=12))
#tb_LPC = LPC(a=a)
tb_lp = tb.stack(Lowpass(fs=1000, fp=10000))
tb_amp = tb.stack(SimpleAmp(volume=0.7))

tbe_amp = Envelope(A=0.01, D=0.2, S=0.6, R=0.5)
tbe_amp.assign(tb_amp.amp)
tbe_amp.assign(tb_lp.ws, 0.2)
#tbe_cont = ArduinoController(com=port, baudrate=9600)
#tbe_cont.assign(tb_osc.fine, 200.)

tb.implement(tbe_amp)
#tb.implement(tbe_cont)
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

# スレッド
fd_thread = threading.Thread(target=face_detection)
bp_thread = threading.Thread(target=bp.play_beat)
#tb_thread = threading.Thread(target=tb.play)

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

with serial.Serial(port, 9600,timeout=1) as ser:
    flag=bytes('0','utf-8')
    ser.write(flag)


# In[ ]:


# 開始
# 顔認識
fd_thread.start()

# 周りの様子を疑う
while True:
    current_time = time.time() - start_time
    # 人がいないとき
    if random.randint(0, 9) == 1 and face_num == 0 and (current_time%0.5) == 0:
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('2','utf-8')
            ser.write(flag)
            time.sleep(2.0)
            flag=bytes('0','utf-8')
            ser.write(flag)
    # 人が来たとき
    elif face_num > 0:
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('4','utf-8')
            ser.write(flag)
        peep_if.set_note_sequence(chirp_ns)
        peep.play()
        # 人がきたらビートスタート
        bp_thread.start()
        with serial.Serial(port, 9600,timeout=1) as ser:
            flag=bytes('0','utf-8')
            ser.write(flag)
        break

while True:
    while True:
        if bp.state == 1:
            input_sequence, in_flag = mk.wait_for_bar(bar=8, qpm=s_qpm)
            break
        

    # ２小節入力がなかったら
    if in_flag == False:
        while True:
            if bp.state == 1:
                with serial.Serial(port, 9600,timeout=1) as ser:
                    flag=bytes('4','utf-8')
                    ser.write(flag)
                peep_if.set_note_sequence(chirp_ns)
                peep.play()
                with serial.Serial(port, 9600,timeout=1) as ser:
                    flag=bytes('0','utf-8')
                    ser.write(flag)
            if bp.state == 5:
                with serial.Serial(port, 9600,timeout=1) as ser:
                    flag=bytes('4','utf-8')
                    ser.write(flag)
                peep_if.set_note_sequence(chirp_ns)
                peep.play()
                with serial.Serial(port, 9600,timeout=1) as ser:
                    flag=bytes('0','utf-8')
                    ser.write(flag)
                break
    # 入力があったら
    else:
        out_sequence = ac.generate(input_sequence)
        out_sequence.tempos[0].qpm = s_qpm
        out_sequence = ac.round_in_bar(out_sequence, 7.5)
        tb_if.set_note_sequence(out_sequence)
        while True:
            if bp.state == 1:
                tb.play()
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




