#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import threading
from StringIO import StringIO
from Tkinter import *
import tkMessageBox
import urllib2
import logging
import json
from PIL import ImageTk, Image


class BaseWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.createWidgets()

    def destroy(self):
        self.top.destroy()

    def mainloop(self):
        self.top.mainloop()


class MessageCaptcha(Label):

    def __init__(self, *args, **kwargs):
        Label.__init__(self, *args, **kwargs)
        self.update_captcha()

    def update_captcha(self):
        img = self.get_img()
        self.configure(image=img)
        self.image = img

    def get_img(self):
        page = urllib2.urlopen('http://anon.fm/feedback').read()
        img_url = re.findall(r'<img\ssrc="(.*?)">', page)[0]
        img = urllib2.urlopen('http://anon.fm' + img_url)
        img = StringIO(img.read())
        return ImageTk.PhotoImage(Image.open(img))


class MessageText(Text):

    _resetting_modified_flag = False

    def __init__(self, *args, **kwargs):
        self.counter = kwargs.pop('counter')

        Text.__init__(self, *args, **kwargs)

        self.bind('<<Modified>>', self.text_click)

    def text_click(self, event=None):
        text = len(self.get(1.0, END)) - 1
        max = 255
        count = (max - text)

        if self._resetting_modified_flag or count <= 1:
            return

        self.counter.configure(text=count)
        print text
        self._resetting_modified_flag = True

        try:
            self.tk.call(self._w, 'edit', 'modified', 0)

        finally:
            self._resetting_modified_flag = False


class MessageSendButton(Button):

    def __init__(self, *args, **kwargs):
        self.textfield = kwargs.pop('textfield')

        kwargs.update({'command': self.send})

        Button.__init__(self, *args, **kwargs)

    def send(self):
        text = self.textfield.get(1.0, END)
        count_chars = len(text)

        if count_chars <= 1:
            tkMessageBox.showerror("SASAI", "You must to put any text")
            return
        if count_chars > 250:
            tkMessageBox.showerror(
                "SASAI", "You must to put less than 250 characters"
            )
            return
        print text, ' has sent'


class MessageWindow(BaseWindow):

    def createWidgets(self):
        self.captcha = MessageCaptcha(self.top)
        self.update = Button(self.top, text="Update captcha",
                             command=self.captcha.update_captcha)
        self.counter = Label(self.top, text='255')
        self.text = MessageText(self.top, width=40, height=5,
                                counter=self.counter)
        self.send = MessageSendButton(self.top, text="Send",
                                      textfield=self.text)

        self.text.grid(row=0, column=0, columnspan=3)
        self.captcha.grid(row=1, column=0, columnspan=3)
        self.update.grid(row=3, column=0)
        self.counter.grid(row=3, column=1)
        self.send.grid(row=3, column=2)


class MessagesList(Listbox):

    def __init__(self, *args, **kwargs):

        Listbox.__init__(self, *args, **kwargs)

        self.bind('<<ListboxSelect>>', self.new_message)

        self.t = threading.Thread(target=self.update_messages, args=())
        self.t.start()

    def update_messages(self):
        self.delete(0, END)
        url = 'http://anon.fm/answers.js'
        try:
            data = json.loads(urllib2.urlopen(url).read())
            i = 0
            for _, who, text, time, uid, answer in data:
                self.insert(i, "%s %s" % (text, answer))
                i += 1
        except ValueError as e:
            tkMessageBox.showerror(
                "SASAI", str(e)
            )

    def new_message(self, event=None):
        try:
            v = self.curselection()
            if not v:
                return
            value = self.get(v[0])

            if hasattr(self, 'r'):
                self.r.destroy()
                del self.r
            if not hasattr(self, 'r'):
                self.r = MessageWindow()
                self.r.mainloop()
        except Exception as e:
            logging.exception(e)
            return


class Application(Frame):

    def createWidgets(self):
        self.list = MessagesList(self.master, height=30, width=40)

        self.write = Button(self.master, text="Write",
                            command=self.list.new_message)
        self.update = Button(self.master, text="Update",
                             command=self.list.update_messages)

    def __init__(self, *arg, **kwargs):
        Frame.__init__(self, *arg, **kwargs)

        self.createWidgets()

        self.master.grid(column=0, row=0, sticky=(N, S, E, W))
        self.grid(column=1, row=0, columnspan=2, rowspan=2,
                  sticky=(N, S, E, W))

        self.update.grid(row=0, column=0, sticky=(N, E, W))
        self.write.grid(row=0, column=1, sticky=(N, E, W))
        self.list.grid(row=1, column=0, columnspan=2, sticky=(N, S, E, W))

        self.master.master.columnconfigure(0, weight=1)
        self.master.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(1, weight=1)


def main():
    root = Tk()
    content = Frame(root)
    app = Application(content, relief="sunken", width=200, height=100)
    root.wm_iconbitmap('anon.ico')
    root.title('KUKAREKALKA')
    #app = Response()
    app.mainloop()

if __name__ == '__main__':
    main()
