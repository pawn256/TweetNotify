#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import traceback
import datetime
import glob
import time
import wavplay
import threading
from multiprocessing import Process, Queue
import textwrap
import Tkinter as tk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException


reload(sys)
sys.setdefaultencoding('utf-8')

class getTweet():
    def __init__(self,strUrl,bBrowser=0):
        self.strUrl = strUrl
        self.strTweetText = ''
        self.bBrowser = bBrowser
        self.drv = None
        if self.bBrowser == 0:
            pass
        elif self.bBrowser == 1: # phantomjs
            USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"
            cap = dict(DesiredCapabilities.PHANTOMJS)
            cap['phantomjs.page.settings.userAgent'] = (USER_AGENT)
            cap["phantomjs.page.settings.javascriptEnabled"] = True
            self.drv = webdriver.PhantomJS(desired_capabilities=cap)
            self.drv.implicitly_wait(15)
            self.drv.get(strUrl)
        elif self.bBrowser == 2: # chrome
            options=Options()
            options.add_argument('--headless')
            drv_path=os.environ['CHROME_DRIVER'] # envirionment variable
            self.drv=webdriver.Chrome(drv_path,options=options)
            self.drv.set_window_size(1920,1080)
            self.drv.implicitly_wait(15)
            self.drv.get(strUrl)

    def __del__(self,):
        self.drv.close()

    def getScreenShot(self,fname):
        self.drv.save_screenshot(fname)

    def getTweetText(self,):
        if self.bBrowser != 0:
            return self.getTweetTextEx3()
        else:
            return self.getTweetTextEx2()
    
    def getTweetTextEx(self,):
        objReq = requests.get(self.strUrl)
        
        objHtml = BeautifulSoup(objReq.text,'lxml')
        
        objTweetTag = objHtml.find_all(attrs={"class":"tweet"})
        
        objTweetText = objTweetTag[0].find(attrs={"class":"js-tweet-text-container"})
        
        strTweetText = objTweetText.text.encode('utf-8')
        return strTweetText
    
    def getTweetTextEx2(self,):
        objReq = requests.get(self.strUrl)
        
        objHtml = BeautifulSoup(objReq.text,'lxml')
        
        objTweetTag = objHtml.find_all(attrs={"class":"tweet"})
        
        objTweetText = objTweetTag[0].find(attrs={"class":"pinned"})
        strTweetText = ''
        if objTweetText == None:
            objTweetText = objTweetTag[0].find(attrs={"class":"js-tweet-text-container"})
            strTweetText = objTweetText.text.encode('utf-8')
        else:
            objTweetText = objTweetTag[1].find(attrs={"class":"js-tweet-text-container"})
            strTweetText = objTweetText.text.encode('utf-8')

        return strTweetText
    
    # add in 06022020
    def getTweetTextEx3(self,):
        strTweetText = ''
        drv = self.drv

        # retry processing. because there was timeout exception before.
        # 3 times for now
        for i in range(3):
            try:
                drv.refresh()
            except:
                drv.refresh()
            else:
                break

        arcs=drv.find_elements_by_tag_name('article')
        try:
            objTitleTag = arcs[0].find_element_by_css_selector('[class="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"]')
            aryObjTweetTextTag = []
            print "objTitleTag = ", objTitleTag.text.encode('utf-8')
            TweetTextTagCssSelector='[class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-1mi0q7o"] > div + div > div' # 12062020 this is used.
            try:
                # if span tag is null
                objTitleTag.find_element_by_tag_name('span')
                aryObjTweetTextTag = arcs[0].find_elements_by_css_selector(TweetTextTagCssSelector)
            except NoSuchElementException:
                # if span tag is not null
                aryObjTweetTextTag = arcs[1].find_elements_by_css_selector(TweetTextTagCssSelector)
                t,v,tb = sys.exc_info()
                log_txt=''.join(traceback.format_exception(t,v,tb))
                print log_txt
            aryObjTweetTextTag = aryObjTweetTextTag[:len(aryObjTweetTextTag)-1] # remove the end of element, because this element is follow,retweet,like...
            for idx in range(len(aryObjTweetTextTag)):
                if len(aryObjTweetTextTag[idx].find_elements_by_tag_name('video')) < 1: # ignore a video tag
                    strTweetText += aryObjTweetTextTag[idx].text.encode('utf-8')
        except:
            t,v,tb = sys.exc_info()
            log_txt=''.join(traceback.format_exception(t,v,tb))
            print log_txt
            self.getScreenShot('testpy.png')
            pass
        
        if strTweetText == '':
            return self.strTweetText
        else:
            self.strTweetText = strTweetText
            return strTweetText

class Test(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('410x300')
        self.root.geometry('+880+724')
        self.root.attributes("-topmost",True)

        self.container = tk.Frame(self.root,width=400,height=240)
        self.container.propagate(0)
        self.container.grid(row=0,column=0,padx=10,pady=5)
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.frame2=tk.Frame(self.root,width=400,height=40)
        self.frame2.grid(row=1,column=0,padx=10,pady=5)
        self.frame2.propagate(0)
        self.ary_obj_text=[]
        self.ary_text=[]

    def quit(self):
        self.root.destroy()

    def start(self):
        self.root.mainloop()

    def setButton(self):
        button = tk.Button(self.frame2,
                            text = 'Click and Quit',
                            command=self.quit)
        button.place(relx=1.0,rely=1.0,anchor='se')

    def setTitle(self,str_title):
        self.root.title(str_title)

    def setLabel(self,str_text):
        d='\n'.join(textwrap.wrap(unicode(str_text),30))
        l=tk.Label(self.scrollable_frame,text=d,relief="solid",width='40',height=str(d.count('\n')+3))
        l.pack()

    def UpdateScrollFrame(self):
        self.scrollable_frame.update_idletasks()

    def setText(self,str_text):
        if len(self.ary_obj_text) > 0:
            map(lambda x: x.destroy(),self.ary_obj_text)
            self.ary_text.insert(0,str_text)
        else:
            self.ary_text.insert(0,str_text)
        while len(self.ary_text) > 5:
            self.ary_text.pop()

        for i in range(len(self.ary_text)):
            default_height = 3
            set_height = self.ary_text[i].count('\n')
            if set_height < default_height:
                set_height = default_height
            set_height = str(unicode(set_height))

            self.ary_obj_text.insert(len(self.ary_obj_text),tk.Text(self.scrollable_frame,width='40',height=set_height))
            self.ary_obj_text[-1].insert('1.0',unicode(self.ary_text[i]))
            self.ary_obj_text[-1].pack()



class TweetDialog(Test):
    def __init__(self):
        super(TweetDialog,self).__init__()
        self.running = True

    # override
    def setButton(self):
        button = tk.Button(self.frame2,
                            text = 'Click and Quit',
                            command=self.quit)
        button.place(relx=1.0,rely=1.0,anchor='se')

    def UpdateAfterShowDialog(self,objSubWork):
        print "UpdateAfterShowDialog"
        if self.running:
            strTweetTextFile = objSubWork.readTweetTextFile()
            strTweetText = objSubWork.getStrTweetText()
            if strTweetTextFile != strTweetText:
                objSubWork.writeTweetTextFile(strTweetText)
                objSubWork.playMusic()
                print "checkTweetText"
                self.setText(strTweetText)
                self.UpdateScrollFrame()
            self.root.after(500, self.UpdateAfterShowDialog,objSubWork)
        else:
            self.root.destroy()

    # override
    def quit(self):
        self.running = False

class SubWork():
    def __init__(self,str_url):
        self.running = True
        self.strUrl = str_url
        self.clsGetTweet = getTweet(self.strUrl,2)
        self.strTweetText = ""

        self.strExecFileAbsPath=os.path.abspath(__file__)[:os.path.abspath(__file__).rfind('/')]
        self.strTweetTxtFile = self.strExecFileAbsPath + '/' + self.strUrl[self.strUrl.rfind('/')+1:] + '.txt'
        self.strMusicFile = self.strExecFileAbsPath + '/' + 'content/main.wav'
        
        if len(glob.glob(self.strTweetTxtFile)) != 1:
            f=open(self.strTweetTxtFile,'w')
            f.write("")
            f.close()

        self.checkTweetText() # Get the latest tweets on initialization
        check_tweet_text_thread = threading.Thread(target=self.checkTweetTextLoop,name='check_tweet_text_thread',args=())
        check_tweet_text_thread.setDaemon(True)
        check_tweet_text_thread.start()

    def checkTweetText(self):
        #Compare the string in the file with the string on Twitter.
        d = self.readTweetTextFile()
        self.strTweetText = self.clsGetTweet.getTweetText()
        return d != self.strTweetText

    def checkTweetTextLoop(self):
        while True:
            self.strTweetText = self.clsGetTweet.getTweetText()
            time.sleep(1)

    def getStrTweetText(self):
        return self.strTweetText

    def writeTweetTextFile(self,str_tweet_text):
        f=open(self.strTweetTxtFile,'w')
        f.write(str_tweet_text)
        f.close()

    def readTweetTextFile(self):
        f=open(self.strTweetTxtFile,'r')
        d=f.read()
        f.close()
        return d

    def playMusic(self):
        play_music_thread = threading.Thread(target=wavplay.wavplay,name='play_music_thread',args=(self.strMusicFile,))
        play_music_thread.setDaemon(True)
        play_music_thread.start()


def main():
    strUrl = sys.argv[1]
    objSubWork=SubWork(strUrl)
    while True:
        strTweetTextFile = objSubWork.readTweetTextFile()
        strTweetText = objSubWork.getStrTweetText()
        if strTweetTextFile != strTweetText:
            objSubWork.writeTweetTextFile(strTweetText)
            objSubWork.playMusic()
            objTweetDialog = TweetDialog()
            objTweetDialog.setTitle(strUrl[strUrl.rfind('/')+1:])
            objTweetDialog.setText(strTweetText)
            objTweetDialog.setButton()
            objTweetDialog.root.after(500,objTweetDialog.UpdateAfterShowDialog,objSubWork)
            objTweetDialog.start()

        time.sleep(5)

if __name__ == '__main__':
    main()
