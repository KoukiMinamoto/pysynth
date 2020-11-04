#!/usr/bin/env python
# coding: utf-8

# In[2]:


import note_seq
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2
import AutoComposition

from synth import Series
from interface import 


# # TODO
# - [x] 顔検出
# - [x] 自動作曲
#     - [x] とりあえず動かす
#     - [ ] LookbackやAttentionも試してみる
#     - [ ] 長さの調節
#     - [ ] 童謡で学習させてみる
# - [x] MIDIkeyからの入力
# - [x] Note Sequence形式での再生
#     - [ ] テンポを可変にする
# - [x] LowPass 
#     - [x] カットオフ周波数を可変に。
#     - [x] リリースまでかかるようにする
# - [ ] ビートをつける
# - [ ] 気温と湿度の取得
# - [ ] ハードと対応させる
#     - [ ] カラの開閉とカットオフ

# In[ ]:


# その他設定
port = '/dev/cu.usbmodem141101'
bundle = './content/basic_rnn.mag'
cascade_file = "./haar/haarcascade_frontalface_alt.xml"
device_id = 0
sess_flag = False
inflag = False


#シンセの設定
tb = Series()
tb_if = SingSong()
tb_osc = PulseWave()
tb_LPC = LPC(a=a)
tb_lowp = LowPass()
tb_amp = SimpleAmp(volume=1.0)

tbe_amp = Envelope(A=0.01, D=0.2, S=0.6, R=0.01)
tbe_amp.assign(tb_amp.amp)
tbe_cont = ArduinoController()
tbe_cont.assign()

tb.implement(tbe_amp)
tb.implement(tbe_cont)
tb.completed()


# インスタンスたち
cascade = cv2.CascadeClassifier(cascade_file)
cap = cv2.VideoCapture(device_id)
midikey = MIDIKey()
ac = AutoComposition(bundle, 'basic_rnn')
ac.initialize()


# ノートシーケンスの設定
# 少し声を出す(嬉しそうに)
chirp_ns = music_pb2.NoteSequence()
chirp_ns.notes.add(pitch=72, start_time=0., end_time=1., velocity=80)
chirp_ns.total_time = 1.0
chirp_ns.tempo.add(qpm=60)
# 喜びの声
happy_ns = music_pb2.NoteSequence()
happy_ns.note.add(pitch=72, start_time=0., end_time=0.5, velocity=100)
happy_ns.note.add(pitch=72, start_time=1., end_time=1.5, velocity=100)
happy_ns.note.add(pitch=72, start_time=2., end_time=2.5, velocity=100)
happy_ns.total_time = 2.5
happy_ns.tempo.add(qpm=60)


# 開始
while True:
    # 人がいるか
    face = face_detection(cascade, cap)
    # 鍵盤入力待機
    input_sequence, inflag = midikey.wait(timeout=5.0)
    
    # 鍵盤の入力なし且、人おる
    if face > 0 and inflag == False:
        # 声を出す(嬉しそうに)
        tb_if.set_notesequence(chirp_ns)
        tb.play() 
        
    # 鍵盤の入力なし且、人いない
    elif inflag == False:
        # 顔を出して周り見る
        with serial.Serial(port,9600,timeout=1) as ser:
            flag=bytes('s','utf-8')
            ser.write(flag)      
            
    # 鍵盤の入力があった場合
    elif inflag == True:
        sess_flag = True
        out_sequence = ac.generate(in_sequence)
        tb_if.set_notesequence(out_sequence)
        tb.play()
        
    # セッション終了
    elif inflag == False and sess_flag == True:
        tb_if.set_notesequence(happy_ns)
        tb.play()
        sess_flag == False
        


# In[ ]:


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

