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
from oscillator import PulseWave, TriangleWave
from FX import Lowpass
from amplifier import SimpleAmp
from controller import *

from beatplayer import BeatPlayer


# In[2]:


# その他設定
bundle = './content/attention_rnn.mag'
device_id = 0
sess_flag = False
s_qpm = 100
in_flag = False
start_time = time.time()
input_sequence = []

# 歌用シンセの設定
tb = Series()
tb_if = tb.stack(SingNoteSequence())
tb_osc = tb.stack(TriangleWave(interval=12))
tb_amp = tb.stack(SimpleAmp(volume=0.07))

tbe_amp = Envelope(A=0.01, D=0.2, S=1.0, R=0.1)
tbe_amp.assign(tb_amp.amp)

tb.implement(tbe_amp)
tb.completed()

# 鳴声用シンセの設定
peep = Series()
peep_if = peep.stack(SingNoteSequence())
peep_osc = peep.stack(TriangleWave(interval=24))
peep_amp = peep.stack(SimpleAmp(volume=0.07))

penv_amp = Envelope(A=0.01, D=0.5, S=1.0, R=0.2)
penv_amp.assign(peep_amp.amp)
peep.implement(penv_amp)
peep.completed()


# インスタンスたち
mk = MIDIKeyboard()
ac = AutoComposition(bundle, 'attention_rnn')
ac.initialize()
bp = BeatPlayer("./beat/beat100.wav", s_qpm, 8)
bp.setVolume(0.5)

# スレッド
bp_thread = threading.Thread(target=bp.play_beat)
#tb_thread = threading.Thread(target=tb.play)

# ノートシーケンスの設定
# 少し声を出す(嬉しそうに)
chirp_ns = music_pb2.NoteSequence()
chirp_ns.notes.add(pitch=60, start_time=0., end_time=1., velocity=80)
chirp_ns.total_time = 1.0
chirp_ns.tempos.add(qpm=60)


# In[ ]:


# 開始
# 周りの様子を疑う

bp_thread.start()

while True:
    while True:
        if bp.state == 1:
            input_sequence, in_flag = mk.wait_for_bar(bar=8, qpm=s_qpm)
            break

    # ２小節入力がなかったら
    if in_flag == False:
        while True:
            if bp.state == 1:
                peep_if.set_note_sequence(chirp_ns)
                peep.play()
            if bp.state == 5:
                peep_if.set_note_sequence(chirp_ns)
                peep.play()
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


# In[ ]:





# In[ ]:




