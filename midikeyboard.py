#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pygame
import pygame.midi
import note_seq
from note_seq.protobuf import music_pb2
from time import sleep
import time
import copy


# In[7]:


class MIDIKeyboard():
    def __init__(self, buf_size=512, pitch=440, rate=44100):
        self.BUF_SIZE = 512
        self.PITCH = 440
        self.RATE = 44100
        
        pygame.init()
        pygame.midi.init()
        input_id = pygame.midi.get_default_input_id()
        self.midi_in = pygame.midi.Input(input_id, self.BUF_SIZE)
        
    def wait(self, timeout=1.0, in_timeout=3.0):
        end_flag = False
        start_input = False
        still_input = False
        note_sequence = []
        note = {"pitch": -1, "start_time": -1, "end_time": -1, "vel":-1}
        s_time = -1
        e_time = -1
        
        print("Listening your play....")
        while end_flag == False:
            note_on, pitch, vel, timestamp = self._getMIDI()
            # キーボードを押下
            if note_on == 144:
                start_input = True
                still_input = True
                note["pitch"] = pitch
                note["start_time"] = timestamp
                note["vel"] = vel
                note_sequence.append(copy.deepcopy(note))
            # キーボードを離したとき   
            elif note_on == 128:
                still_input = False
                for i in range(len(note_sequence)):
                    if note_sequence[-(i+1)]["pitch"] == pitch:
                        note_sequence[-(i+1)]["end_time"] = timestamp
                        break
            # 入力が終了した時間
            elif note_on == -1 and start_input == True and still_input == False:
                s_time = time.time()
                start_input = False
            
            # 全く入力がない時間
            elif start_input == False and note_sequence == []:
                if e_time == -1:
                    e_time = time.time()
                elif (time.time() - e_time) > in_timeout:
                    break
                
            if (time.time() - s_time) > timeout and s_time != -1:
                break
        
        # オフセット計算
        if note_sequence == []:
            return note_sequence
        else:
            offset = note_sequence[0]["start_time"]
            print("offset: ", offset)
            for i in range(len(note_sequence)):
                note_sequence[i]["start_time"] = note_sequence[i]["start_time"] - offset
                note_sequence[i]["end_time"] = note_sequence[i]["end_time"] - offset
            
        return note_sequence
            
    
    def _getMIDI(self):
        note_num = -1
        vel = -1
        timestamp = -1
        note_on = -1
        if self.midi_in.poll():
            midi_events = self.midi_in.read(self.BUF_SIZE)
            for event in midi_events:
                #print(event)
                note_num = event[0][1]
                note_on = event[0][0]
                vel = event[0][2]
                timestamp = event[1]

        return note_on, note_num, vel, timestamp
    
    
    def make_note_sequence(self, midi_sequence):
        seq_len = len(midi_sequence)
        interval = []
        group = []
        value = []
        
        # 音長計算
        for i in range(seq_len-1):
            info = {}
            info["index"] = i
            info["time"] = midi_sequence[i+1]["start_time"] - midi_sequence[i]["start_time"]
            interval.append(info)
        info = {}
        info["index"] = seq_len-1
        info["time"] = midi_sequence[seq_len-1]["end_time"] - midi_sequence[seq_len-1]["start_time"]
        interval.append(info)
        #print(interval)
        
        # 音長別グループ分け
        temp = copy.deepcopy(interval)
        i = 0
        while temp != []:
            minimum = temp[0]["time"] - temp[0]["time"]/4
            maximum = temp[0]["time"] + temp[0]["time"]/2
            sub_group = [temp.pop(0)]
            j = 0
            while True:
                try:
                    if temp[j]["time"] > minimum and temp[j]["time"] <= maximum:
                        sub_group.append(temp.pop(j))
                    else: 
                        j = j + 1
                except IndexError:
                    break
            #print("sub_group: ", sub_group)
            group.append(sub_group)
        #print("group", group)

        # qpm導出
        bpm_list = []
        for g in group:
            ave = 0
            for gg in g:
                ave = ave + gg["time"]
            ave = ave / len(g)
            bpm = int(60 * 1000 / ave)
            bpm_list.append(bpm)
        print("bpm: ", bpm_list)
        qpm = 0
        n_note = 0
        for i in range(len(bpm_list)):
            n = len(group[i])
            if bpm_list[i] > 50 and bpm_list[i] < 130 and n > n_note:
                qpm = bpm_list[i]
                n_note = len(group[i])
            if qpm == 0:
                qpm = min(bpm_list)
        print("qpm: ", qpm)
        
        # グループ別音価判定
        for i in range(len(bpm_list)):
            v = qpm / bpm_list[i]
            if v >= 1.:
                for g in group[i]:
                    g['value'] = round(v)
            elif v < 1.:
                for g in group[i]:
                    g['value'] = round(v, 1)
        
        #print("group", group)
        
        # note_sequence生成
        note_sequence = music_pb2.NoteSequence()
        for i, ms in enumerate(midi_sequence):
            pitch = ms["pitch"]
            vel = ms["vel"]
            if i != 0:
                start_time = note_sequence.notes[i-1].end_time
            else:
                start_time = 0.
                
            for g in group:
                for gg in g:
                    if gg["index"] == i:
                        end_time = start_time + gg["value"]
                        break
            
            note_sequence.notes.add(pitch=pitch, start_time=start_time, end_time=end_time, velocity=vel)
            
        note_sequence.total_time = note_sequence.notes[-1].end_time
        note_sequence.tempos.add(qpm=qpm)
        #print(note_sequence)
        note_seq.plot_sequence(note_sequence)
    
        return qpm, note_sequence
                
            
    def quit(self):
        self.midi_in.close()
        pygame.midi.quit()
        pygame.quit()
        

