#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pyaudio
import struct
import cv2
import threading
import matplotlib.pyplot as plt
import time

RATE=44100        
bufsize = 512

#鍵盤のGUI作成
ksx = 800
ksy = 200
keyboard = np.zeros([ksy,ksx,3])
keyboard[:,:,:] = 255
for i in range(15):
    cv2.rectangle(keyboard, (int(ksx/15*i), 0), (int(ksx/15*(i+1)),ksy), (0, 0, 0), 5)
for i in range(15):
    if i in {0,1,3,4,5,7,8,10,11,12}:
        cv2.rectangle(keyboard, (int(ksx/15*i + ksx/27 ), 0), (int(ksx/15*(i+1) + ksx/33),int(ksy/2)), (0, 0, 0), -1)

cv2.imshow("keyboard", keyboard) 


#各種パラメータ用スライダーの設定
sl=np.array([0,150,150,255,0,0,0,0])
slName = np.array(['Wave_type',
                   'Attack',
                   'Release',
                   'Lowpass_freq',
                   'FM_amp',
                   'FM_freq',
                   'Delay_time',
                   'Delay_feedback'])

def changeBar(val):
    global sl
    for i in range(8):
        sl[i] = cv2.getTrackbarPos(slName[i], "keyboard")
cv2.namedWindow("keyboard", cv2.WINDOW_NORMAL)
cv2.createTrackbar(slName[0], "keyboard", 0, 4, changeBar)
cv2.createTrackbar(slName[1], "keyboard", 0, 255, changeBar)
cv2.createTrackbar(slName[2], "keyboard", 0, 255, changeBar)
cv2.createTrackbar(slName[3], "keyboard", 0, 255, changeBar) 
cv2.createTrackbar(slName[4], "keyboard", 0, 255, changeBar) 
cv2.createTrackbar(slName[5], "keyboard", 0, 11, changeBar)
cv2.createTrackbar(slName[6], "keyboard", 0, 255, changeBar) 
cv2.createTrackbar(slName[7], "keyboard", 0, 255, changeBar)  
for i in range(8):
    cv2.setTrackbarPos(slName[i], "keyboard", sl[i])

#マウス位置による鍵盤選択
keyon = 0
pre_keyon = 0
pitch = 440
velosity = 0.0
highkeys = np.array([0,1,1,3,3,4,5,6,6,8,8,10,10,11, 12,13,13,15,15,16,17,18,18,20,20,22,22,23, 24,24])
lowkeys = np.array([0,2,4,5,7,9,11, 12,14,16,17,19,21,23, 24])
def mouse_event(event, x, y, flags, param):
    global keyon,pre_keyon,pitch,velosity
    if event == cv2.EVENT_LBUTTONDOWN:
        keyon = 1
        if y >= ksy/2:
            note = lowkeys[int(15.0*x/ksx)]
        elif y < ksy/2:
            note = highkeys[int(30.0*x/ksx)]
        pitch = 440*(np.power(2,(note-9)/12))
    elif event == cv2.EVENT_LBUTTONUP :
        keyon = 0
    if pre_keyon ==0 and keyon ==1:
        velosity = 0.0
    pre_keyon = keyon
cv2.setMouseCallback("keyboard", mouse_event)


#ローパスフィルター
lpfbuf=np.zeros(4)
outwave=np.zeros(bufsize)
def lowpass(wave):
    global lpfbuf,outwave
    w0 = 2.0*np.pi*(200+(sl[3]/255.0)**2*20000)/RATE;
    Q = 1.0
    alpha = np.sin(w0)/(2.0*Q)
    a0 =   (1 + alpha)
    a1 =  -2*np.cos(w0)/a0
    a2 =   (1 - alpha)/a0
    b0 =  (1 - np.cos(w0))/2/a0
    b1 =   (1 - np.cos(w0))/a0
    b2 =  (1 - np.cos(w0))/2/a0
    for i in range(bufsize):
        outwave[i] = b0*wave[i]+b1*lpfbuf[1]+b2*lpfbuf[0]-a1*lpfbuf[3]-a2*lpfbuf[2]
        lpfbuf[0] = lpfbuf[1]
        lpfbuf[1] = wave[i]
        lpfbuf[2] = lpfbuf[3]
        lpfbuf[3] = outwave[i]
    return outwave

#ディレイ
ringbuf = np.zeros(50000)#最大ディレイタイムは50000/RATE秒
def delay(wave):
    global ringbuf
    delaytime = sl[6]/255.0 * 1.0
    feedback = sl[7]/255.0 * 0.7
    dryandwet = feedback/2.0
    writepoint = int(delaytime*RATE)
    ringbuf = np.roll(ringbuf,-bufsize)
    ringbuf[writepoint:writepoint+bufsize] = wave + feedback * ringbuf[:bufsize]
    outwave = (1-dryandwet) * wave + dryandwet * ringbuf[:bufsize]
    return outwave


#波形生成
x=np.arange(bufsize)
pos = 0
def synthesize():
    global pos,velosity

    #位相計算
    t = pitch * (x+pos) / RATE
    t = t - np.trunc(t)
    pos += bufsize

    #基本波形選択
    if sl[0]==1:#のこぎり波
        wave = t*2.0-1.0
    elif sl[0]==2:#矩形波
        wave = np.zeros(bufsize);wave[t<=0.5]=-1;wave[t>0.5]=1;
    elif sl[0]==3:#三角波
        wave = np.abs(t*2.0-1.0)*2.0-1.0
    elif sl[0]==4:#FM変調
        wave = np.sin(2.0*np.pi*t + sl[4]/100.0 * np.sin(2.0*np.pi*t*sl[5]))
    else:#サイン波
        wave = np.sin(2.0*np.pi*t)

    #エンベロープ設定
    if keyon == 1:
        vels = velosity + x * ((sl[1]/1000)**3+0.00001)
        vels[vels>0.6] = 0.6
    else:
        vels = velosity - x * ((sl[2]/1000)**3+0.00001)
        vels[vels<0.0] = 0.0
    velosity = vels[-1]    
    wave = vels * wave

    #ローパスフィルター
    wave = lowpass(wave)

    return wave


#波形再生
playing = 1
def audioplay():
    print ("Start Streaming")
    p=pyaudio.PyAudio()
    stream=p.open(format = pyaudio.paInt16,
            channels = 1,
            rate = RATE,
            frames_per_buffer = bufsize,
            output = True)
    while stream.is_active():
        start = time.time()
        buf = synthesize()
        buf = delay(buf)
        buf = (buf * 32768.0).astype(np.int16)#16ビット整数に変換
        buf = struct.pack("h" * len(buf), *buf)
        stream.write(buf)
        if playing == 0:
            break
        print(time.time()-start)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print ("Stop Streaming")



#波形とスペクトル画像生成
def waveformAndSpectrum():
    sampleN = 1024
    t0 = pitch * np.arange(sampleN) / RATE
    t = t0 - np.trunc(t0)
    #基本波形選択
    if sl[0]==1:#のこぎり波
        wave = t*2.0-1.0
    elif sl[0]==2:#矩形波
        wave = np.zeros(bufsize);wave[t<=0.5]=-1;wave[t>0.5]=1;
    elif sl[0]==3:#三角波
        wave = np.abs(t*2.0-1.0)*2.0-1.0
    elif sl[0]==4:#FM変調
        wave = np.sin(2.0*np.pi*t + sl[4]/100.0 * np.sin(2.0*np.pi*t*sl[5]))
    else:#サイン波
        wave = np.sin(2.0*np.pi*t)

    if sl[3] < 250:#ローパスフィルター
        outwave=np.zeros(sampleN)
        w0 = 2.0*np.pi*(200+(sl[3]/255.0)**2*20000)/RATE;
        Q = 1.0
        alpha = np.sin(w0)/(2.0*Q)
        a0 =   (1 + alpha)
        a1 =  -2*np.cos(w0)/a0
        a2 =   (1 - alpha)/a0
        b0 =  (1 - np.cos(w0))/2/a0
        b1 =   (1 - np.cos(w0))/a0
        b2 =  (1 - np.cos(w0))/2/a0
        lpfbuf2=np.zeros(4)
        for i in range(sampleN):
            outwave[i] = b0*wave[i]+b1*lpfbuf2[1]+b2*lpfbuf2[0]-a1*lpfbuf2[3]-a2*lpfbuf2[2]
            lpfbuf2[0] = lpfbuf2[1]
            lpfbuf2[1] = wave[i]
            lpfbuf2[2] = lpfbuf2[3]
            lpfbuf2[3] = outwave[i]
    else:
        outwave = wave

    Spectrum = abs(np.fft.fft(outwave))
    frq = np.fft.fftfreq(sampleN,1.0 / RATE)

    plt.clf()
    plt.subplot(2,1,1)
    plt.title("Waveform")
    plt.plot(t0,outwave)
    plt.xlim([0,pitch * sampleN / RATE])
    plt.ylim([-1.5, 1.5])
    plt.subplot(2,1,2)
    plt.title("Spectrum")
    plt.yscale("log")
    plt.plot(frq[:int(sampleN/2)],Spectrum[:int(sampleN/2)])
    plt.xlim([0,10000])
    plt.pause(1)

#画面描画
if __name__ == "__main__": 
    thread = threading.Thread(target=audioplay)
    thread.start()
    while (True):
        cv2.imshow("keyboard", keyboard) 
        k = cv2.waitKey(100) & 0xFF
        if k == ord('q'):
            playing = 0
            break
        if k == ord('s'):
            waveformAndSpectrum()

    cv2.destroyAllWindows()


# In[ ]:


a

