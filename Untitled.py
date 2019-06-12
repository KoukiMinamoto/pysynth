#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding:utf-8 -*-
import pygame
from pygame.locals import *  #pygemeの使用を簡単にする
import sys


def main():
    pygame.init()                                   # Pygameの初期化
    screen = pygame.display.set_mode((400, 300))    # 大きさ400*300の画面を生成
    pygame.display.set_caption("Test")              # タイトルバーに表示する文字(題名)

    while (1):
        screen.fill((0,0,0))        # 画面を黒色(#000000)に塗りつぶし
        pygame.display.update()     # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 閉じるボタンが押されたら終了
                print("aaaa")
                pygame.quit()
                
                break # Pygameの終了(画面閉じられる)
                         #pygame.quit()だけでもいいが正常に終了するために書く


if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:




