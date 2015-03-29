(import re)
(import [StringIO [StringIO]])
(import [Tkinter [*]])
(import urllib2)
(import [threading [Thread]])
(import json)

(import ImageTk)
(import [PIL [Image]])

(defclass BaseWindow [object]
  [[--init--
    (fn [self]
        (setv self.top (Toplevel))
        (.createWidgets self)
        None)]
   [destroy
     (fn [self]
         (.destroy self.top)
         None)]
   [mainloop
     (fn [self]
         (.mainloop self.top)
         None)]])


(defn button [label root command &optional [side "left"]]
  (setv button (kwapply (Button root)
                        {"text" label
                         "fg" "red"
                         "command" command}))
  (kwapply (button.pack) {"side" side})
  button)


(defclass Response [BaseWindow]
  [[createWidgets
    (fn [self]
      (button "quit" self.top self.destroy)
        (setv image (ImageTk.PhotoImage (Image.open (.get_img self))))
        (setv label (kwapply (Label self.top) {"image" image}))
        (setv label.image image)
        (kwapply (label.pack) {"side" "left"
                               "fill" "both"
                               "expand" True})
        )]
    [get_img
      (fn [self]
        (setv page (.read (urllib2.urlopen "http://anon.fm/feedback")))
        (setv img_url (re.findall "<img src=\"(.*?)\">" page))
        (setv img_url (img_url.__getitem__ 0))
        (setv img (.read (urllib2.urlopen (+ "http://anon.fm" img_url))))
        (StringIO img))]])

 (defclass Application [Frame]
   [[--init--
     (fn [self master]
       (.__init__ Frame self master)
       (.pack self)
       (.createWidgets self))]

    [createWidgets
     (fn [self]
       (button "quit" self self.destroy)
       (button "update" self self.perd "right")
       (setv self.list (Listbox self.master))
       (kwapply (self.list.pack) {"side" "left"
                                 "fill" "both"
                                 "expand" True})
       (self.list.bind "<<ListboxSelect>>" self.perd)
       (setv pusher (kwapply (Thread) {"target" self.push
                                       "args" []}))
       (.start pusher))]

    [perd
     (fn [self event]
       (if (hasattr self "r")
         (do (.destroy self.r)
             (del self.r))
         (print "peass"))
       (if (hasattr self "r")
         (print "pess")
         (do (setv self.r (Response))
             (.mainloop self.r)))
       )]
    [push
     (fn [self]
       (self.list.delete 0 END)
       (setv data (.read (urllib2.urlopen "http://anon.fm/answers.js")))
       (setv data (json.loads data))
       (setv i 0)
       (for (row data)
         (do (self.list.insert i (+ (row.__getitem__ 2)
                                    (row.__getitem__ 5)))
             (setv i (+ i 1))))
       )]
])



(setv root (Tk))
(setv app (kwapply (Application) {"master" root}))
(app.master.title "QOOQAREQ")
(app.master.minsize 500 500)
(.mainloop app)
