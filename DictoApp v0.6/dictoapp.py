# -*- coding: utf-8 -*-
from tempfile import NamedTemporaryFile
import shutil
import os
import csv
import copy
from random import random
from random import shuffle
import webbrowser
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

csv_columns = ['German','English','Type','Attributes']
parts_of_speech = ["Noun","Verb","Adjective","Adverb","Conjunction","Preposition","Phrase"]
umlautBut = ["uUmlautButton","aUmlautButton","oUmlautButton","sUmlautButton"]
umlauts = ["ü","ä","ö","ß"]
pron = ['ich', 'du', 'er/sie/es', 'wir', 'ihr', 'sie/Sie']
genders = ['der', 'die', 'das']
gr_columns = ["Group","Users"]

def setColor(r, g, b):
    return Gdk.Color(red=r * 255, green=g * 255, blue=b * 255)

def to_list(s):
    res = []
    i = 2
    while i < len(s) - 1:
        x = str()
        while i < len(s) - 1 and s[i] != "'":
            x = x + s[i]
            i = i + 1
        i = i + 1
        while i < len(s) - 1 and s[i] != "'":
            i = i + 1
        i = i + 1
        res.append(x)
    return res

# Usage:
# my_groups("kisa")
# print(myGroups)

def my_groups(userName):
    global myGroups
    myGroups = []
    global script_dir
    abs_file_path = os.path.join(script_dir, "system", "groups.csv")
    with open(abs_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if userName in set(to_list(row[gr_columns[1]])):
                myGroups.append(row[gr_columns[0]])

# Usage:
# add_user_to_group("User", "kisa")

def add_user_to_group(groupName, userName):
    f = 0
    global fileName
    my_groups(fileName[:-4])
    global myGroups
    if (len(myGroups) == 3):
        Error("Unfortunately, being in more than 3 groups\n is not currently supported.")
        return 1
    global script_dir
    abs_file_path = os.path.join(script_dir, "system", "groups.csv")
    with open(abs_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row[gr_columns[0]].strip() == groupName:
                f = 1 if (userName in set(to_list(row[gr_columns[1]]))) else 2
    if f == 0:
        Error("No such group!")
        return 1
    elif f == 1:
        Error("User is already in this group!")
        return 1
    else:
        tmp = NamedTemporaryFile(delete=False)
        with open(tmp.name, 'w') as tempfile:
            with open(abs_file_path, 'r') as csvFile:
                csv_reader = csv.DictReader(csvFile)
                csv_writer = csv.DictWriter(tempfile, fieldnames=gr_columns)  
                csv_writer.writeheader()
                for row in csv_reader:
                    if row[gr_columns[0]] == groupName:
                        tmpSet = set(to_list(row[gr_columns[1]]))
                        tmpSet.add(userName)
                        row[gr_columns[1]] = str(tmpSet)
                    csv_writer.writerow(row)
                    
        shutil.move(tempfile.name, abs_file_path)

        column_names = list()
        abs_group_path = os.path.join(script_dir, "groups", groupName + ".csv")
        with open(abs_group_path, "r") as file:
            reader = csv.reader(file)
            column_names = next(reader)
        column_names.append(userName)
        tmp = NamedTemporaryFile(delete=False)
        with open(tmp.name, 'w') as tempfile:
            with open(abs_group_path, 'r') as csvFile:
                csv_reader = csv.DictReader(csvFile)
                csv_writer = csv.DictWriter(tempfile, fieldnames=column_names)  
                csv_writer.writeheader()
                for row in csv_reader:
                    row[userName] = "0/4"
                    csv_writer.writerow(row)
        shutil.move(tempfile.name, abs_group_path)
        return 0

# Usage:
# create_group("User","userName1")

def create_group (groupName, userName):
    f = 0
    global script_dir
    abs_file_path = os.path.join(script_dir, "system", "groups.csv")
    with open(abs_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row[gr_columns[0]] == groupName:
                f = 1
                break
    if f == 1:
        Error("Group exists!")
        return
    with open(abs_file_path, 'a') as csvFile:
        csv_writer = csv.DictWriter(csvFile, fieldnames=gr_columns)
        row = dict()
        row [gr_columns[0]] = groupName
        x = list()
        x.append(userName)
        row [gr_columns[1]] = str(x)
        csv_writer.writerow(row)
    abs_group_path = os.path.join(script_dir, "groups", groupName + ".csv")
    with open(abs_group_path, 'w') as csvFile:
        gr_csv_columns = copy.deepcopy(csv_columns)
        gr_csv_columns.append(userName)
        csv_writer = csv.DictWriter(csvFile, fieldnames=gr_csv_columns)
        csv_writer.writeheader()

def set_default_file(file):
    global script_dir
    abs_file_path = os.path.join(script_dir, "system", "default.csv")
    abs_newfile_path = os.path.join(script_dir, "users", file)
    with open(abs_newfile_path, 'w') as destination:
        with open(abs_file_path, 'r') as origin:
            csv_reader = csv.DictReader(origin)
            csv_writer = csv.DictWriter(destination, fieldnames=csv_columns)  
            csv_writer.writeheader()
            for row in csv_reader:
                csv_writer.writerow(row)

def significant_characters(s):
    l = list()
    i = 0
    for x in s:
        if x != " ":
            l.append(i)
        i = i + 1
    return l

def make_mask(s):
    l = significant_characters(s)
    shuffle(l)
    newS = list(s)
    for i in range(int(2 * len(l) / 3)):
        newS[l[i]] = "*"
    retS = str()
    for x in newS:
        retS = retS + x
    return retS

def conjugate_weak(verb):
    leng = len(verb)
    d = {}

    if verb[leng - 2:] == "en":
        verb = verb[:leng - 2]
        leng = len(verb)
    else:
        verb = verb[:leng - 1]
        leng = len(verb)

    if (verb[leng - 1] == "t" or verb[leng - 1] == "d" 
        or verb[leng - 3:] == "chn" or verb[leng - 3:] == "ffn"
        or verb[leng - 2:] == "dm" or verb[leng - 2:] == "gn"
        or verb[leng - 2:] == "tm"):
        d["ich"] = verb + "e"
        d["du"] = verb + "est"
        d["er/sie/es"] = d["ihr"] = verb + "et"
        d["wir"] = d["sie/Sie"] = verb + "en"
    elif (verb[leng - 1] == "ß" or verb[leng - 1] == "s" or verb[leng - 1] == "z"
        or verb[leng - 2:] == "ss"):
        d["ich"] = verb + "e"
        d["er/sie/es"] = d["ihr"] = d["du"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "en"
    elif verb[leng - 2:] == "er" or verb[leng - 2:] == "el":
        d["ich"] = verb + "e"
        d["du"] = verb + "st"
        d["er/sie/es"] = d["ihr"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "n"
    else:
        d["ich"] = verb + "e"
        d["du"] = verb + "st"
        d["er/sie/es"] = d["ihr"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "en"
    
    return d

def conjugate_strong(verb, option):
    leng = len(verb)
    d = {}

    if verb[leng - 2:] == "en":
        verb = verb[:leng - 2]
        leng = len(verb)
    else:
        verb = verb[:leng - 1]
        leng = len(verb)

    if (verb[leng - 1] == "t" or verb[leng - 1] == "d" 
        or verb[leng - 3:] == "chn" or verb[leng - 3:] == "ffn"
        or verb[leng - 2:] == "dm" or verb[leng - 2:] == "gn"
        or verb[leng - 2:] == "tm"):
        d["ich"] = verb + "e"
        d["du"] = verb + "est"
        d["er/sie/es"] = d["ihr"] = verb + "et"
        d["wir"] = d["sie/Sie"] = verb + "en"
    elif (verb[leng - 1] == "ß" or verb[leng - 1] == "s" or verb[leng - 1] == "z"
        or verb[leng - 2:] == "ss"):
        d["ich"] = verb + "e"
        d["er/sie/es"] = d["ihr"] = d["du"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "en"
    elif verb[leng - 2:] == "er" or verb[leng - 2:] == "el":
        d["ich"] = verb + "e"
        d["du"] = verb + "st"
        d["er/sie/es"] = d["ihr"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "n"
    else:
        d["ich"] = verb + "e"
        d["du"] = verb + "st"
        d["er/sie/es"] = d["ihr"] = verb + "t"
        d["wir"] = d["sie/Sie"] = verb + "en"

    if (verb.find("e") <= 4 or verb.find("a") <= 4 or verb.find("o") <= 4 
        or verb.find("au") <= 4):
        if verb.find("e") != -1:
            d["du"] = d["du"].replace("e", option, 1)
            d["er/sie/es"] = d["er/sie/es"].replace("e", option, 1)
        elif verb.find("a") != -1:
            d["du"] = d["du"].replace("a", "ä", 1)
            d["er/sie/es"] = d["er/sie/es"].replace("a", "ä", 1)
        elif verb.find("o") != -1: 
            d["du"] = d["du"].replace("o", "ö", 1)
            d["er/sie/es"] = d["er/sie/es"].replace("o", "ö", 1)
        elif verb.find("au") != -1:
            d["du"] = d["du"].replace("au", "äu", 1)
            d["er/sie/es"] = d["er/sie/es"].replace("au", "äu", 1)

    return d

def get_size(fileName):
    global fileSize
    fileSize = 0
    global script_dir
    abs_file_path = os.path.join(script_dir, "users", fileName)
    with open(abs_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for _ in csv_reader:
            fileSize = fileSize + 1
    user = fileName[:-4]
    my_groups(user)
    global myGroups
    for group in myGroups:
        abs_group_path = os.path.join(script_dir, "groups", group + '.csv')
        with open(abs_group_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for _ in csv_reader:
                fileSize = fileSize + 1

def change_column (dict, column, containts):
    new_dict = copy.deepcopy(dict)
    new_dict[column] = containts
    return new_dict

def change_in_file(fileName, f, chg, group):
    global fileSize
    global script_dir
    if group:
        abs_file_path = os.path.join(script_dir, "groups", fileName)
    else:
        abs_file_path = os.path.join(script_dir, "users", fileName)
    tmp = NamedTemporaryFile(delete=False)
    with open(abs_file_path, "r") as file:
        reader = csv.reader(file)
        column_names = next(reader)
    with open(tmp.name, 'w') as tempfile:
        with open(abs_file_path, 'r') as csvFile:
            csv_reader = csv.DictReader(csvFile)
            csv_writer = csv.DictWriter(tempfile, fieldnames=column_names)  
            csv_writer.writeheader()
            for row in csv_reader:
                if (f(row) == 0):
                    csv_writer.writerow(row)
                    #don't chg
                elif (f(row) == 1):
                    csv_writer.writerow(chg(row))
                    #chg with func
                else:
                    fileSize = fileSize - 1
    shutil.move(tempfile.name, abs_file_path)

#Usage:
#f = lambda x: 1 if x["Name"] == "Smith" else 0
#change_database(f, "Name", "Mirzoev")

def change_database (f, column, containts):
    global fileName
    t = lambda x: change_column(x, column, containts)
    change_in_file(fileName, f, t, False)
    user = fileName[:-4]
    global myGroups
    for group in myGroups:
        if (column == "Attributes"):
            i = containts.find(" ")
            if i == -1:
                i = len(containts)
            t = lambda x: change_column(x, user, containts[:i])
        else:
            t = lambda x: change_column(x, column, containts)
        change_in_file(group + ".csv", f, t, True)

#Usage:
#overwrite("x.csv", dict_data, 'w')

def overwrite(fileName, dict_data, how):
    try:
        global fileSize
        global script_dir
        abs_file_path = os.path.join(script_dir, "users", fileName)
        fileSize = fileSize + len(dict_data)
        with open(abs_file_path, how) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            if how == 'w':
                writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
                csvfile.flush()
    except IOError:
        Error("I/O error")

def overwrite_gr(fileName, dict_data, how, userName):
    try:
        global script_dir
        abs_file_path = os.path.join(script_dir, "groups", fileName)
        with open(abs_file_path, "r") as file:
            reader = csv.reader(file)
            column_names = next(reader)
        global fileSize
        fileSize = fileSize + len(dict_data)
        with open(abs_file_path, how) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_names)
            if how == 'w':
                writer.writeheader()
            for data in dict_data:
                to_write = dict()
                for i in range(3):
                    to_write [column_names[i]] = data[column_names[i]]
                to_write["Attributes"] = data["Attributes"][4:]
                for i in range(4, len(column_names)):
                    to_write[column_names[i]] = "0/4"
                writer.writerow(to_write)
                csvfile.flush()
    except IOError:
        print("I/O error")

#Usage:
#for x in read_iterative("x.csv"):
#    print ("new")
#    for key in x.keys():
#        print(key, x[key])

def read_iterative(fileNm):
    global script_dir
    abs_file_path = os.path.join(script_dir, "users", fileName)
    with open(abs_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            minidict = dict()
            for key in row.keys():
                minidict[key] = row[key]
            yield minidict
    user = fileNm[:-4]
    my_groups(user)
    global myGroups
    for group in myGroups:
        abs_group_path = os.path.join(script_dir, "groups", group + '.csv')
        with open(abs_group_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                minidict = dict()
                minidict[csv_columns[3]] = row[user] + ' ' + row[csv_columns[3]]
                for i in range(3):
                    minidict[csv_columns[i]] = row[csv_columns[i]]
                yield minidict

def get_quantity_f(f):
    q = 0
    global fileName
    for word in read_iterative(fileName):
        if (f(word)):
            q = q + 1
    return q

#usage:
#change_column(x, "Name", "Mirzoev")

def search_in_buffer(word, key):
    global buffer
    for x in buffer.list:
        if x[key] == word:
            return x
    return {}

#Usage
#t = search("x.csv", "Smith", "Name")
#if t:
#    for key in t.keys():
#        print(key, t[key])
#else:
#    print("Not found")

def search(fileName, word, key):
    ret = search_in_buffer(word, key)
    if ret:
        return ret
    else:
        for x in read_iterative(fileName):
            if x[key] == word:
                return x
        return {}

def unequalRand(word, language):
    global buffer
    x = buffer.list[int(random() * len(buffer.list))]
    while x[language] == word[language]:
        x = buffer.list[int(random() * len(buffer.list))]
    return x[language]

class DictBuffer:
    def __init__(self, bound):
        global fileName
        self.bound = copy.deepcopy(bound)
        i = 0
        self.list = []
        self.file = fileName
        for word in read_iterative(self.file):
            if i >= bound[0] and i < bound[1]:
                self.list.append(word)
            i += 1
        self.bound[0] = min(0, self.bound[0])
        self.bound[1] = self.bound[0] + len(self.list)

class fBuffer:
    def __init__(self, bound, f):
        self.bound = copy.deepcopy(bound)
        i = 0
        self.list = []
        global fileName
        for word in read_iterative(fileName):
            if f(word):
                if i >= bound[0] and i < bound[1]:
                    self.list.append(word)
                i += 1
        self.bound[0] = min(0, self.bound[0])
        self.bound[1] = self.bound[0] + len(self.list)
             
#is redundant
class PartBuffer:
    def __init__(self, bound, part):
        x = fBuffer(bound, lambda x: x["Type"] == part)
        self.bound = x.bound
        self.list = x.list

class VerbConjugation:
    def __init__(self, strongFlag, x, t, buff, dict_data):
        gladeFile = "dict.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
        self.opt = "ie"
        self.word = x

        if strongFlag == 0:
            d = conjugate_weak(self.word["German"])
            self.builder.get_object(pron[0] + "C").set_text(d[pron[0]])
            self.builder.get_object(pron[1] + "C").set_text(d[pron[1]])
            self.builder.get_object(pron[2][:2] + "C").set_text(d[pron[2]])
            self.builder.get_object(pron[3] + "C").set_text(d[pron[3]])
            self.builder.get_object(pron[4] + "C").set_text(d[pron[4]])
            self.builder.get_object(pron[5][:3] + "C").set_text(d[pron[5]])
        else:
            d = conjugate_strong(self.word["German"], self.opt)
            self.builder.get_object(pron[0] + "C").set_text(d[pron[0]])
            self.builder.get_object(pron[1] + "C").set_text(d[pron[1]])
            self.builder.get_object(pron[2][:2] + "C").set_text(d[pron[2]])
            self.builder.get_object(pron[3] + "C").set_text(d[pron[3]])
            self.builder.get_object(pron[4] + "C").set_text(d[pron[4]])
            self.builder.get_object(pron[5][:3] + "C").set_text(d[pron[5]])

        reMix = self.builder.get_object("verbConjugationButtonRedo")
        reMix.connect("clicked", self.change_entry)
        if strongFlag == 0:
            reMix.hide()

        pushButton = self.builder.get_object("verbConjugationButtonPush")
        pushButton.connect("clicked", self.push, t, buff, dict_data)

        webButton = self.builder.get_object("verbConjugationButtonWebSearch")
        webButton.connect("clicked", self.open_web)

        window = self.builder.get_object("verbConjugation")
        window.modify_bg(Gtk.StateType.NORMAL, setColor(166, 231, 158))
        window.connect("delete-event", self.on_destroy)
        window.show()

    def open_web(self, widget):
        webbrowser.open("https://conjugator.reverso.net/conjugation-german-verb-"+self.word["German"]+".html")
    
    def change_entry(self, widget):
        if self.opt == "ie":
            self.opt = "i"
        else:
            self.opt = "ie"
        d = conjugate_strong(self.word["German"], self.opt)
        self.builder.get_object(pron[0] + "C").set_text(d[pron[0]])
        self.builder.get_object(pron[1] + "C").set_text(d[pron[1]])
        self.builder.get_object(pron[2][:2] + "C").set_text(d[pron[2]])
        self.builder.get_object(pron[3] + "C").set_text(d[pron[3]])
        self.builder.get_object(pron[4] + "C").set_text(d[pron[4]])
        self.builder.get_object(pron[5][:3] + "C").set_text(d[pron[5]])

    def push(self, widget, t, buff, dd):
        s = str()
        s = s + self.builder.get_object(pron[0] + "C").get_text()
        s = s + " " + self.builder.get_object(pron[1] + "C").get_text()
        s = s + " " + self.builder.get_object(pron[2][:2] + "C").get_text()
        s = s + " " + self.builder.get_object(pron[3] + "C").get_text()
        s = s + " " + self.builder.get_object(pron[4] + "C").get_text()
        s = s + " " + self.builder.get_object(pron[5][:3] + "C").get_text()
        self.word['Attributes'] = self.word['Attributes'] + " " + s
        if 3 in t:
            dd.append(self.word)
            t.remove(3)
        for x in t:
            buff[x].append(self.word)
        self.builder.get_object("verbConjugation").destroy()

    def on_destroy(self, widget, x):
        widget.destroy() #was hide

class OpenedWord:
    def __init__(self, x):
        gladeFile = "dict.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

        #self.builder.get_object("openWordButtonCollAdd").connect("clicked", self.translate)
        self.builder.get_object("openWordButtonTrAdd").connect("clicked", self.add_to_training, x)

        self.get_attr(x["Attributes"])
        self.builder.get_object("openWordLabelGerman").set_text(x["German"])
        self.builder.get_object("openWordLabelEnglish").set_text(x["English"])
        self.builder.get_object("openWordLabelPart").set_text(x["Type"])

        window = self.builder.get_object("openWord")
        window.modify_bg(Gtk.StateType.NORMAL, setColor(166, 231, 158))
        window.connect("delete-event", self.on_destroy)
        window.show()
    
    def add_to_training(self, widget, x):
        global curTraining
        f = True
        for i in curTraining:
            if (x["German"] == i["German"] and x["English"] == i["English"]):
                f = False
                break
        if f:
            curTraining.append(copy.deepcopy(x))

    def get_attr(self, x):
        y = x.split()
        val = list(map(int, y[0].split("/")))
        acc = 0.0
        if val[1] == 0:
            if val[0] != 0:
                acc = 1.0
        else:
            acc = float(val[0]) / (val[0] + val[1])
        self.builder.get_object("openWordBarProgress").set_value(acc)
        genL = self.builder.get_object("openWordLabelGender")
        if (y[1] == "n"):
            genL.set_markup ("<span foreground='green' weight='bold' font='14'>n</span>")
        elif (y[1] == "m"): 
            genL.set_markup ("<span foreground='blue' weight='bold' font='14'>m</span>")
        elif (y[1] == "f"):
            genL.set_markup ("<span foreground='red' weight='bold' font='14'>f</span>")
        else:
            genL.hide()

    def on_destroy(self, widget, x):
        widget.destroy() #was hide

class NewWord:
    def __init__(self):
        self.dict_data = list()
        gladeFile = "dict.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
        self.toggled = "-"
        self.part = str()
        self.verb = 0
        self.groupBuffer = list()
        self.groupBuffer.append(list())
        self.groupBuffer.append(list())
        self.groupBuffer.append(list())
        self.grToggled = set()

        global buffer
        global fileSize

        self.builder.get_object("addWordCheckUser").connect("toggled", self.on_dest_toggled, 3)
        chk = list()
        chk.append(self.builder.get_object("addWordCheckGroup0"))
        chk[0].connect("toggled", self.on_dest_toggled, 0)
        chk.append(self.builder.get_object("addWordCheckGroup1"))
        chk[1].connect("toggled", self.on_dest_toggled, 1)
        chk.append(self.builder.get_object("addWordCheckGroup2"))
        chk[2].connect("toggled", self.on_dest_toggled, 2)

        global fileName
        my_groups(fileName[:-4])
        global myGroups

        x = len(myGroups)
        for i in range (x):
                chk[i].set_label(myGroups[i])
        if x == 0:
            self.builder.get_object("addWordBoxDestination").hide()
        elif x < 3:
            for i in range (x, 3):
                chk[i].hide()

        self.builder.get_object("addWordButtonAdd").connect("clicked", self.add_word)

        self.builder.get_object("addWordCheckWeak").connect("toggled", self.on_verb_toggled, 0)
        self.builder.get_object("addWordCheckStrong").connect("toggled", self.on_verb_toggled, 1)

        self.builder.get_object("addWordCheckF").connect("toggled", self.on_button_toggled, "f")
        self.builder.get_object("addWordCheckM").connect("toggled", self.on_button_toggled, "m")
        self.builder.get_object("addWordCheckN").connect("toggled", self.on_button_toggled, "n")

        self.builder.get_object("addWordCheck" + parts_of_speech[0][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[0])
        self.builder.get_object("addWordCheck" + parts_of_speech[1][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[1])
        self.builder.get_object("addWordCheck" + parts_of_speech[2][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[2])
        self.builder.get_object("addWordCheck" + parts_of_speech[3][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[3])
        self.builder.get_object("addWordCheck" + parts_of_speech[4][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[4])
        self.builder.get_object("addWordCheck" + parts_of_speech[5][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[5])
        self.builder.get_object("addWordCheck" + parts_of_speech[6][:4]).connect("toggled", self.on_part_toggled, parts_of_speech[6])

        self.builder.get_object(umlautBut[0] + "1").connect("clicked", self.add_umlaut, 0)
        self.builder.get_object(umlautBut[1] + "1").connect("clicked", self.add_umlaut, 1)
        self.builder.get_object(umlautBut[2] + "1").connect("clicked", self.add_umlaut, 2)
        self.builder.get_object(umlautBut[3] + "1").connect("clicked", self.add_umlaut, 3)

        window = self.builder.get_object("addWord")
        window.modify_bg(Gtk.StateType.NORMAL, setColor(222, 229, 232))
        window.connect("delete-event", self.on_destroy)
        window.show()

    def add_umlaut(self, widget, case):
        german = self.builder.get_object("addWordEntryGerman")
        german.set_text(german.get_text() + umlauts[case])      

    def on_destroy(self, widget, x):
        global buffer
        global fileSize
        global fileName
        global myGroups
        overwrite(fileName, self.dict_data, 'a')
        my_groups(fileName[:-4])
        global myGroups
        x = len(myGroups)
        for i in range(x):
            if (len(self.groupBuffer) > 0):
                overwrite_gr(myGroups[i] + ".csv", self.groupBuffer[i], 'a', fileName[:-4])
        buffer = DictBuffer([0, 100])
        widget.destroy() #was hide

    def add_word(self, widget):
        german = self.builder.get_object("addWordEntryGerman")
        english = self.builder.get_object("addWordEntryEnglish")
        wtype = self.part
        word = dict()

        word["German"] = german.get_text().strip()
        word["English"] = english.get_text().strip()
        word["Type"] = wtype.strip()
        word["Attributes"] = "0/4 " + self.toggled

        self.builder.get_object("addWordCheckF").set_active(False)
        self.builder.get_object("addWordCheckM").set_active(False)
        self.builder.get_object("addWordCheckN").set_active(False)

        for i in range(3):
            self.builder.get_object("addWordCheckGroup"+str(i)).set_active(False)

        self.toggled = "-"

        self.builder.get_object("addWordCheck" + self.part[:4]).set_active(False)

        german.set_text(str())
        english.set_text(str())

        if word["Type"] == "Verb":
            VerbConjugation(self.verb, copy.deepcopy(word), copy.deepcopy(self.grToggled), self.groupBuffer, self.dict_data)
        else:
            if 3 in self.grToggled:
                self.dict_data.append(word)
                self.grToggled.remove(3)
            for x in self.grToggled:
                self.groupBuffer[x].append(word)

    def on_verb_toggled(self, widget, val):
        self.verb = val

    def on_dest_toggled(self, widget, val):
        self.grToggled.add(val)
    
    def on_button_toggled(self, widget, val):
        self.toggled = val
        
    def on_part_toggled(self, widget, val):
        self.part = val
        if val == "Noun":
            if widget.get_active() == False:
                self.builder.get_object("addWordBoxGender").hide()
            else:
                self.builder.get_object("addWordBoxGender").show()
        elif val == "Verb":
            if widget.get_active() == False:
                self.builder.get_object("addWordBoxVerb").hide()
            else:
                self.builder.get_object("addWordBoxVerb").show()
        else:
            self.builder.get_object("addWordBoxGender").hide()
        
        for x in parts_of_speech:
            if x != val:
                self.builder.get_object("addWordCheck" + x[:4]).set_active(False)

class Error:
    def __init__(self, text):
        gladeFile = "dict.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
        self.builder.get_object("errorName").set_text(text)
        button = self.builder.get_object("errorButtonTryAgain")
        button.connect("clicked", self.reset_text)
        window = self.builder.get_object("error")
        window.modify_bg(Gtk.StateType.NORMAL, setColor(181, 75, 87))
        window.connect("delete-event", self.on_destroy)
        window.show()

    def reset_text(self, widget):
        self.builder.get_object("error").destroy()

    def on_destroy(self, widget, x):
        widget.destroy() #was hide

class Main:
    def __init__(self):
        gladeFile = "dict.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
        self.rememberMe = False
        self.showedPass = False
        self.curTr = 0

        global script_dir
        abs_in_path = os.path.join(script_dir, "local", "signed_in.txt")
        if os.path.exists(abs_in_path):
            with open(abs_in_path, "r") as file:
                lines = file.readlines()
                if lines:
                    self.builder.get_object("mainEntryLogin").set_text(lines[0].strip())
                    self.builder.get_object("mainEntryPass").set_text(lines[1].strip())
            
        self.builder.get_object("mainCheckRememberMe").connect("toggled", self.remember_me)
        self.builder.get_object("mainCheckShowPassword").connect("toggled", self.show_pass)

        self.builder.get_object("mainButtonLogin").connect("clicked", self.login)
        self.builder.get_object("mainButtonSignUp").connect("clicked", self.signUp)
        self.builder.get_object("mainButtonLogout").connect("clicked", self.logout)

        self.builder.get_object("mainSwitchSetTr").connect('button-press-event', self.setSwitch)
        self.builder.get_object("mainNotebook").connect("switch-page", self.pageSwitch)
        self.builder.get_object("mainComboBoxTrChoose").connect("changed", self.changeCurrentTraining)

        # ============
        # Simple Training
        # ============

        self.STwhich = dict()
        self.STlang= "German"

        self.builder.get_object("simpleTrButtonCheck").connect("clicked", self.STcheck)
        self.builder.get_object("simpleTrButtonNew").connect("clicked", self.STnew)
        self.builder.get_object("simpleTrButtonQuestion").connect("clicked", self.STquestion)
        self.builder.get_object("simpleTrButtonHint").connect("clicked", self.SThint)

        self.builder.get_object(umlautBut[0] + "2").connect("clicked", self.STadd_umlaut, 0)
        self.builder.get_object(umlautBut[1] + "2").connect("clicked", self.STadd_umlaut, 1)
        self.builder.get_object(umlautBut[2] + "2").connect("clicked", self.STadd_umlaut, 2)
        self.builder.get_object(umlautBut[3] + "2").connect("clicked", self.STadd_umlaut, 3)

        # ============
        # Gender Training
        # ============

        self.GTchoice = genders[0]

        self.GTfilter = lambda x: x["Type"] == "Noun" and x["German"][:3] in set(genders)
        self.GTq = get_quantity_f(self.GTfilter) 
        self.GTbuff = fBuffer([0, 100], self.GTfilter)
        self.GTwhich = self.GTbuff.list[int(random() * len(self.GTbuff.list))]
        
        self.builder.get_object("genderTrLabelWord").set_text(self.GTwhich["German"][3:].strip())

        self.builder.get_object("genderTrEvBox0").modify_bg(Gtk.StateType.NORMAL, setColor(53, 92, 125))
        self.builder.get_object("genderTrEvBox1").modify_bg(Gtk.StateType.NORMAL, setColor(108, 91, 123))
        self.builder.get_object("genderTrEvBox2").modify_bg(Gtk.StateType.NORMAL, setColor(192, 108, 132))

        self.builder.get_object(genders[0]).connect("clicked", self.GTset_choice, genders[0])
        self.builder.get_object(genders[1]).connect("clicked", self.GTset_choice, genders[1])
        self.builder.get_object(genders[2]).connect("clicked", self.GTset_choice, genders[2])

        # ============
        # Match Training
        # ============

        self.MTwhich = dict()
        self.MTchoice = 0
        self.MTcorrect = 0

        global buffer
        buffer = DictBuffer([0, 100])
        self.MTwhich = buffer.list[int(random() * len(buffer.list))]
        self.builder.get_object("matchTrLabelWord").set_text(self.MTwhich["German"].strip())

        self.builder.get_object("matchTrEvBox4").modify_bg(Gtk.StateType.NORMAL, setColor(53, 92, 125))
        self.builder.get_object("matchTrEvBox5").modify_bg(Gtk.StateType.NORMAL, setColor(108, 91, 123))
        self.builder.get_object("matchTrEvBox6").modify_bg(Gtk.StateType.NORMAL, setColor(192, 108, 132))
        self.builder.get_object("matchTrEvBox7").modify_bg(Gtk.StateType.NORMAL, setColor(246, 114, 128))

        self.builder.get_object("matchTrButtonChoice0").connect("clicked", self.MTset_choice, 0)
        self.builder.get_object("matchTrButtonChoice1").connect("clicked", self.MTset_choice, 1)
        self.builder.get_object("matchTrButtonChoice2").connect("clicked", self.MTset_choice, 2)
        self.builder.get_object("matchTrButtonChoice3").connect("clicked", self.MTset_choice, 3)

        self.MTset_new()

        # ============
        # Phrase Training
        # ============

        self.PTfilter = lambda x: x["Type"] == "Phrase"
        self.PTq = get_quantity_f(self.PTfilter)
        self.PTbuff = fBuffer([0, 100], self.PTfilter)
        self.PTwhich = self.PTbuff.list[int(random() * len(self.PTbuff.list))]
        self.PTdividedPhrase = self.PTwhich["German"].strip().split()
        self.PTdistr_to_butts()
        for i in range(16):
            self.builder.get_object("phraseButton" + str(i)).connect("clicked", self.PTclick_on_but, "phraseButton" + str(i))

        # ============
        # Dictionary
        # ============

        self.builder.get_object("findWordButtonTranslate").connect("clicked", self.FWtranslate)
        self.builder.get_object("findWordButtonClear").connect("clicked", self.FWclear)

        self.builder.get_object(umlautBut[0] + "0").connect("clicked", self.FWadd_umlaut, 0)
        self.builder.get_object(umlautBut[1] + "0").connect("clicked", self.FWadd_umlaut, 1)
        self.builder.get_object(umlautBut[2] + "0").connect("clicked", self.FWadd_umlaut, 2)
        self.builder.get_object(umlautBut[3] + "0").connect("clicked", self.FWadd_umlaut, 3)

        self.builder.get_object("dictionaryButtonAddNewWord").connect("clicked", self.DictAddNewWord)

        self.DictCurData = list()
        self.DictBound = [0, 10]
        self.DictCurLang = "German"
        
        DictGoDown = self.builder.get_object("dictionaryButtonDown")
        DictGoDown.connect("clicked", self.DictScroll, 1)
        DictGoUp = self.builder.get_object("dictionaryButtonUp")
        DictGoUp.connect("clicked", self.DictScroll, -1)

        self.builder.get_object("dictionaryButtonLanguage").connect("clicked", self.DictChange_Language)

        if (self.DictBound[0] == 0):
            DictGoUp.hide()
        else:
            DictGoUp.show()

        buffer = DictBuffer([0, 100])
        global fileSize
        if (self.DictBound[1] == fileSize):
            DictGoDown.hide()
        else:
            DictGoDown.show()
        if fileSize >= 100:
            if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
            else:
                highBound = min (self.DictBound[1] + 45, fileSize)
                buffer = DictBuffer([min(0, highBound - 100), highBound])
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
        else:
            if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
            else:
                buffer = DictBuffer([0, fileSize])
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]

        for x in range(min(10, len(self.DictCurData))):
            self.builder.get_object("dictionaryWord"+str(x)).set_label(self.DictCurData[x][self.DictCurLang])
        for x in range(min(10, len(self.DictCurData)), 10):
            self.builder.get_object("dictionaryWord"+str(x)).hide()
        for x in range(10):
            self.builder.get_object("dictionaryWord"+str(x)).connect("clicked", self.DictOpen_Word, x)

        # ============
        # Current Training
        # ============

        self.TrainCurData = [0] * 10
        self.TrainBound = [0, 10]
        self.TrainCurLang = "German"
        
        TrainGoDown = self.builder.get_object("trainingButtonDown")
        TrainGoDown.connect("clicked", self.TrainScroll, 1)
        TrainGoUp = self.builder.get_object("trainingButtonUp")
        TrainGoUp.connect("clicked", self.TrainScroll, -1)

        self.builder.get_object("trainingButtonLanguage").connect("clicked", self.TrainChange_Language)

        if (self.TrainBound[0] == 0):
            TrainGoUp.hide()
        else:
            TrainGoUp.show()
        
        global curTraining
        self.TrainCurData = curTraining[:10]
        self.TrainBound[0] = 0
        self.TrainBound[1] = len(self.TrainCurData)
        if (self.TrainBound[1] == len(self.TrainCurData)):
            TrainGoDown.hide()
        else:
            TrainGoDown.show()

        for x in range(min(10, len(self.TrainCurData))):
            wordButton = self.builder.get_object("trainingWord"+str(x))
            wordButton.set_label(self.TrainCurData[x][self.TrainCurLang])
        for x in range(min(10, len(self.TrainCurData)), 10):
            self.builder.get_object("trainingWord"+str(x)).hide()
        for x in range(10):
            self.builder.get_object("trainingWord"+str(x)).connect("clicked", self.TrainOpen_Word, x)

        # ============
        # Groups
        # ============

        self.builder.get_object("addToGroupButtonAdd").connect("clicked", self.addToGroup)
        self.builder.get_object(umlautBut[0] + "3").connect("clicked", self.ATGadd_umlaut, 0)
        self.builder.get_object(umlautBut[1] + "3").connect("clicked", self.ATGadd_umlaut, 1)
        self.builder.get_object(umlautBut[2] + "3").connect("clicked", self.ATGadd_umlaut, 2)
        self.builder.get_object(umlautBut[3] + "3").connect("clicked", self.ATGadd_umlaut, 3)

        self.builder.get_object("createGroupButtonCreate").connect("clicked", self.createGroup)
        self.builder.get_object(umlautBut[0] + "4").connect("clicked", self.CGadd_umlaut, 0)
        self.builder.get_object(umlautBut[1] + "4").connect("clicked", self.CGadd_umlaut, 1)
        self.builder.get_object(umlautBut[2] + "4").connect("clicked", self.CGadd_umlaut, 2)
        self.builder.get_object(umlautBut[3] + "4").connect("clicked", self.CGadd_umlaut, 3)

        self.checkGroups()

        # ============
        # Window Stuff
        # ============

        self.builder.get_object("mainBox").hide()
        window = self.builder.get_object("Main")
       #window.modify_bg(Gtk.StateType.NORMAL, setColor(222, 229, 232))
        window.connect("delete-event", Gtk.main_quit)
        window.show()

    # ==================================================
    # ==================================================
    # Login & Sign Up & Log Out
    # ==================================================
    # ==================================================

    def show_pass(self, widget):
        self.showedPass = not self.showedPass
        passEntry = self.builder.get_object("mainEntryPass")
        if self.showedPass:
            passEntry.set_visibility(True)
        else:
            passEntry.set_visibility(False)
            passEntry.set_invisible_char("•")

    def remember_me(self, widget):
        self.rememberMe = not self.rememberMe

    def logout(self, widget):
        self.builder.get_object("mainBox").hide()
        self.builder.get_object("loginBox").show()
        global fileSize
        global trainingSwitch
        global curTraining
        global fileName
        global myGroups
        fileSize = 0
        trainingSwitch = True
        curTraining = list()
        fileName = str()
        myGroups = list()
        self.rememberMe = False
        self.showedPass = False
        self.builder.get_object("mainCheckRememberMe").set_active(False)
        self.builder.get_object("mainCheckShowPassword").set_active(False)
        global script_dir
        abs_in_path = os.path.join(script_dir, "local", "signed_in.txt")
        if os.path.exists(abs_in_path):
            with open(abs_in_path, "r") as file:
                lines = file.readlines()
                if lines:
                    self.builder.get_object("mainEntryLogin").set_text(lines[0].strip())
                    self.builder.get_object("mainEntryPass").set_text(lines[1].strip())

    def signUp(self, widget):
        login = self.builder.get_object("mainEntryLogin").get_text().strip()
        password = self.builder.get_object("mainEntryPass").get_text().strip()
        flag = False
        if login == "users_die_hard":
            self.builder.get_object("mainEntryLogin").set_text(str())
            self.builder.get_object("mainEntryPass").set_text(str())
            Error("Login uses reserved name!")
            return
        global script_dir
        abs_login_path = os.path.join(script_dir, "system", "login.csv")
        with open(abs_login_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row["login"] == login:
                    flag = True
                    break
        if flag:
            Error("Login already exists!")
            self.builder.get_object("mainEntryLogin").set_text(str())
            self.builder.get_object("mainEntryPass").set_text(str())
        else:
            with open(abs_login_path, mode='a') as csvfile:
                fn = ["login", "password"]
                writer = csv.DictWriter(csvfile, fieldnames=fn)
                lnData = dict()
                lnData["login"] = login
                lnData["password"] = password
                self.builder.get_object("mainEntryLogin").set_text(str())
                self.builder.get_object("mainEntryPass").set_text(str())
                writer.writerow(lnData)
                set_default_file(login.strip() + ".csv")
                csvfile.flush()

    def login(self, widget):
        login = self.builder.get_object("mainEntryLogin").get_text().strip()
        password = self.builder.get_object("mainEntryPass").get_text().strip()
        global script_dir
        abs_login_path = os.path.join(script_dir, "system", "login.csv")
        with open(abs_login_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            flag = False
            for row in csv_reader:
                if row["login"] == login:
                    flag = True
                    if row["password"] == password:
                        self.builder.get_object("mainBox").show()
                        self.builder.get_object("loginBox").hide()
                        self.builder.get_object("mainEntryLogin").set_text(str())
                        self.builder.get_object("mainEntryPass").set_text(str())
                        global fileSize
                        global buffer
                        global fileName
                        fileName = login.strip() + ".csv"
                        get_size(fileName)
                        buffer = DictBuffer([0, 100])
                        abs_in_path = os.path.join(script_dir, "local", "signed_in.txt")
                        if self.rememberMe:
                            with open(abs_in_path, "w") as file:
                                file.write(login.strip() + "\n" + password.strip())
                        elif os.path.exists(abs_in_path):
                            os.remove(abs_in_path)
                    else:
                        Error("Wrong password!")
                        self.builder.get_object("mainEntryPass").set_text(str())
                    break
            if not flag:
                self.builder.get_object("mainEntryLogin").set_text(str())
                self.builder.get_object("mainEntryPass").set_text(str())
                Error("Login doesn't exist!")

    # ==================================================
    # ==================================================
    # Pages
    # ==================================================
    # ==================================================

    def pageSwitch(self, widget, page, page_num):
        global trainingSwitch
        global buffer
        if page_num == 1:
            if trainingSwitch:
                buffer = DictBuffer([0, 100])
            self.STwhich = dict()
            self.STlang= "German"
            self.builder.get_object("mainComboBoxTrChoose").set_active(0)
            self.builder.get_object("simpleTrEntryGerman").set_text(str())
            self.builder.get_object("simpleTrEntryEnglish").set_text(str())
            self.builder.get_object("simpleTrLabelAttributes").set_text(str())
        elif page_num == 2:
            self.builder.get_object("findWordEntryGerman").set_text(str())
            self.builder.get_object("findWordEntryEnglish").set_text(str())
            self.builder.get_object("findWordLabelAttributes").set_text(str())
            self.DictCurData = list()
            for i in range(10):
                self.DictCurData.append(dict())
            self.DictBound = [0, 10]
            self.DictCurLang = "German"
            
            DictGoDown = self.builder.get_object("dictionaryButtonDown")
            DictGoUp = self.builder.get_object("dictionaryButtonUp")

            if (self.DictBound[0] == 0):
                DictGoUp.hide()
            else:
                DictGoUp.show()

            buffer = DictBuffer([0, 100])
            global fileSize
            if (self.DictBound[1] == fileSize):
                DictGoDown.hide()
            else:
                DictGoDown.show()
            if fileSize >= 100:
                if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                    for i in range(buffer.bound[0], buffer.bound[1]):
                        if i < self.DictBound[1] and i >= self.DictBound[0]:
                            self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
                else:
                    highBound = min (self.DictBound[1] + 45, fileSize)
                    buffer = DictBuffer([min(0, highBound - 100), highBound])
                    for i in range(buffer.bound[0], buffer.bound[1]):
                        if i < self.DictBound[1] and i >= self.DictBound[0]:
                            self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
            else:
                if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                    for i in range(buffer.bound[0], buffer.bound[1]):
                        if i < self.DictBound[1] and i >= self.DictBound[0]:
                            self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
                else:
                    buffer = DictBuffer([0, fileSize])
                    for i in range(buffer.bound[0], buffer.bound[1]):
                        if i < self.DictBound[1] and i >= self.DictBound[0]:
                            self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]

            for x in range(min(10, len(self.DictCurData))):
                wordButton = self.builder.get_object("dictionaryWord"+str(x))
                wordButton.set_label(self.DictCurData[x][self.DictCurLang])
                self.builder.get_object("dictionaryWord"+str(x)).show()
            for x in range(min(10, len(self.DictCurData)), 10):
                self.builder.get_object("dictionaryWord"+str(x)).hide()
        elif page_num == 3:
            self.TrainCurData = [0] * 10
            self.TrainBound = [0, 10]
            self.TrainCurLang = "German"
            
            TrainGoDown = self.builder.get_object("trainingButtonDown")
            TrainGoUp = self.builder.get_object("trainingButtonUp")

            if (self.TrainBound[0] == 0):
                TrainGoUp.hide()
            else:
                TrainGoUp.show()
            
            global curTraining
            self.TrainCurData = curTraining[:10]
            self.TrainBound[0] = 0
            self.TrainBound[1] = len(self.TrainCurData)
            if (self.TrainBound[1] == len(self.TrainCurData)):
                TrainGoDown.hide()
            else:
                TrainGoDown.show()

            for x in range(min(10, len(self.TrainCurData))):
                wordButton = self.builder.get_object("trainingWord"+str(x))
                wordButton.set_label(self.TrainCurData[x][self.TrainCurLang])
                self.builder.get_object("trainingWord"+str(x)).show()
            for x in range(min(10, len(self.TrainCurData)), 10):
                self.builder.get_object("trainingWord"+str(x)).hide()
        else:
            self.checkGroups()
                
    # ==================================================
    # ==================================================
    # Training Switch
    # ==================================================
    # ==================================================

    def setSwitch(self, widget, x):
        global trainingSwitch
        trainingSwitch = widget.get_active()
        if trainingSwitch:
            self.builder.get_object("mainButtonStartTr1").show()
            self.builder.get_object("mainButtonStartTr2").show()
        else:
            self.builder.get_object("mainButtonStartTr1").hide()
            self.builder.get_object("mainButtonStartTr2").hide()
    
    # ==================================================
    # ==================================================
    # Trainings
    # ==================================================
    # ==================================================

    def changeCurrentTraining(self, widget):
        if self.curTr == 0:
            self.builder.get_object("simpleTrEntryGerman").set_text(str())
            self.builder.get_object("simpleTrEntryEnglish").set_text(str())
            self.builder.get_object("simpleTrLabelAttributes").set_text(str())
            self.builder.get_object("simpleTrainingBox").hide()
        elif self.curTr == 1:
            self.builder.get_object("genderTrLabelWord").set_text(str())
            self.builder.get_object("genderTrLabelAttributes").set_text(str())
            self.builder.get_object("genderTrainingBox").hide()            
        elif self.curTr == 2:
            self.builder.get_object("matchTrLabelResult").set_text(str())
            self.builder.get_object("matchTrLabelWord").set_text(str())
            self.builder.get_object("matchTrLabelChoice0").set_text(str())
            self.builder.get_object("matchTrLabelChoice1").set_text(str())
            self.builder.get_object("matchTrLabelChoice2").set_text(str())
            self.builder.get_object("matchTrLabelChoice3").set_text(str())
            self.builder.get_object("matchTrainingBox").hide()
        else:
            self.builder.get_object("phraseLabel").set_text(str())
            self.builder.get_object("checkPhraseLabel").set_text(str())
            for i in range(16):
                self.builder.get_object("phraseButton" + str(i)).set_label(str())
            self.builder.get_object("phraseTrainingBox").hide()

        newTr = self.builder.get_object("mainComboBoxTrChoose").get_active_text().strip()
        if newTr == "Simple Training":
            self.builder.get_object("simpleTrainingBox").show()
            self.curTr = 0
        elif newTr == "Gender Training":
            self.builder.get_object("genderTrainingBox").show()
            self.curTr = 1
        elif newTr == "Match Training":
            self.builder.get_object("matchTrainingBox").show()
            self.curTr = 2
        else:
            self.builder.get_object("phraseTrainingBox").show()
            self.curTr = 3

                # ==================================================
                # ==================================================
                # Simple Training
                # ==================================================
                # ==================================================

    def SThint(self, widget):
        self.STwhich["Attributes"] = copy.deepcopy(self.STset_attr(self.STwhich["Attributes"], False))
        f = lambda x: 1 if x["German"] == self.STwhich["German"] and x["English"] == self.STwhich["English"] else 0
        change_database(f, "Attributes", self.STwhich["Attributes"])
        if self.STlang== "German":
            self.builder.get_object("simpleTrEntryEnglish").set_text(make_mask(self.STwhich["English"]))
        else:
            self.builder.get_object("simpleTrEntryGerman").set_text(make_mask(self.STwhich["German"]))

    def STquestion(self, widget):
        OpenedWord(copy.deepcopy(self.STwhich))
        self.STwhich["Attributes"] = copy.deepcopy(self.STset_attr(self.STwhich["Attributes"], False))
        f = lambda x: 1 if x["German"] == self.STwhich["German"] and x["English"] == self.STwhich["English"] else 0
        change_database(f, "Attributes", self.STwhich["Attributes"])
        self.builder.get_object("simpleTrEntryGerman").set_text(str())
        self.builder.get_object("simpleTrEntryEnglish").set_text(str())
        self.builder.get_object("simpleTrLabelAttributes").set_text(str())

    def STadd_umlaut(self, widget, case):
        german = self.builder.get_object("simpleTrEntryGerman")
        german.set_text(german.get_text() + umlauts[case])

    def STset_attr(self, attributes, correct):
        s = str()
        y = attributes.split()
        val = list(map(int, y[0].split("/")))
        if correct:
            val[0] += 1
        else:
            val[1] += 1
        s = str(val[0]) + "/" + str(val[1])
        i = False
        for t in y:
            if i:
                s = s + ' ' + t
            else:
                i = True
        return s
    
    def STget_attr(self, attributes):
        s = str()
        y = attributes.split()
        val = list(map(int, y[0].split("/")))
        acc = 0.0
        if val[1] == 0:
            if val[0] != 0:
                acc = 1.0
        else:
            acc = float(val[0]) / (val[0] + val[1])
        s = "Accuracy: " + str(int(acc * 100)) + "%"
        if y[1] != '-':
            s = s + "\nGender: " + y[1]
        return s

    def STnew(self, widget):
        global trainingSwitch
        global buffer
        self.builder.get_object("simpleTrEntryGerman").set_text(str())
        self.builder.get_object("simpleTrEntryEnglish").set_text(str())
        self.builder.get_object("simpleTrLabelAttributes").set_text(str())
        if trainingSwitch:
            if random() < 0.03:
                newBound = int(random() * (fileSize - 100))
                buffer = DictBuffer([newBound, newBound + 100])
            if random() < 0.33:
                self.STlang= "German"
                self.STwhich = buffer.list[int(len(buffer.list)*random())]
                self.builder.get_object("simpleTrEntryGerman").set_text(self.STwhich["German"])
            else:
                self.STlang= "English"
                self.STwhich = buffer.list[int(len(buffer.list)*random())]
                self.builder.get_object("simpleTrEntryEnglish").set_text(self.STwhich["English"])
        else:
            if random() < 0.33:
                self.STlang= "German"
                self.STwhich = curTraining[int(len(curTraining)*random())]
                self.builder.get_object("simpleTrEntryGerman").set_text(self.STwhich["German"])
            else:
                self.STlang= "English"
                self.STwhich = curTraining[int(len(curTraining)*random())]
                self.builder.get_object("simpleTrEntryEnglish").set_text(self.STwhich["English"])

    def STcheck(self, widget):
        global fileSize
        german = self.builder.get_object("simpleTrEntryGerman")
        english = self.builder.get_object("simpleTrEntryEnglish")
        deText = german.get_text().strip()
        enText = english.get_text().strip()
        if self.STwhich["German"] == deText and self.STwhich["English"] == enText:
            attr = self.builder.get_object("simpleTrLabelAttributes")
            self.STwhich["Attributes"] = copy.deepcopy(self.STset_attr(self.STwhich["Attributes"], True))
            attr.set_text("CORRECT!\n" + self.STget_attr(self.STwhich["Attributes"])+'\nPart of speech: '+self.STwhich["Type"])
        else:
            attr = self.builder.get_object("simpleTrLabelAttributes")
            self.STwhich["Attributes"] = copy.deepcopy(self.STset_attr(self.STwhich["Attributes"], False))
            attr.set_text("INCORRECT!")
        f = lambda x: 1 if x["German"] == self.STwhich["German"] and x["English"] == self.STwhich["English"] else 0
        change_database(f, "Attributes", self.STwhich["Attributes"])

                # ==================================================
                # ==================================================
                # Gender Training
                # ==================================================
                # ==================================================

    def GTset_choice(self, widget, x):
        self.GTchoice = x
        self.GTcheck()
        Gdk.flush()
        GLib.timeout_add(1500, self.GTset_new)

    def GTset_new(self):
        global buffer
        self.builder.get_object("genderTrLabelAttributes").set_text(str())
        if random() < 0.03:
            self.GTq = get_quantity_f(self.GTfilter)
            newBound = int(random() * (max(0, self.GTq - 100)))
            self.GTbuff = fBuffer([newBound, newBound + 100], self.GTfilter)
        self.GTwhich = self.GTbuff.list[int(random() * len(self.GTbuff.list))]
        self.builder.get_object("genderTrLabelWord").set_text(self.GTwhich["German"][3:].strip())
        self.builder.get_object("genderTrEvBox3").modify_bg(Gtk.StateType.NORMAL, setColor(222, 229, 232))

    def GTcheck(self):
        if self.GTchoice == self.GTwhich["German"][:3]:
            self.GTwhich["Attributes"] = self.GTset_attr(self.GTwhich["Attributes"], True)
            self.builder.get_object("genderTrEvBox3").modify_bg(Gtk.StateType.NORMAL, setColor(50, 205, 50))
            self.builder.get_object("genderTrLabelAttributes").set_text("CORRECT!\n")
        else:
            self.GTwhich["Attributes"] = self.GTset_attr(self.GTwhich["Attributes"], False)
            self.builder.get_object("genderTrEvBox3").modify_bg(Gtk.StateType.NORMAL, setColor(255, 67, 71))
            self.builder.get_object("genderTrLabelAttributes").set_text("INCORRECT!")
        f = lambda x: 1 if x["German"] == self.GTwhich["German"] and x["English"] == self.GTwhich["English"] else 0
        change_database(f, "Attributes", self.GTwhich["Attributes"])
    
    def GTset_attr(self, x, cor):
        s = str()
        y = x.split()
        val = list(map(int, y[0].split("/")))
        if cor:
            val[0] += 1
        else:
            val[1] += 1
        s = str(val[0]) + "/" + str(val[1])
        i = False
        for t in y:
            if i:
                s = s + ' ' + t
            else:
                i = True
        return s

                # ==================================================
                # ==================================================
                # Match Training
                # ==================================================
                # ==================================================

    def MTset_choice(self, widget, x):
        self.MTchoice = x
        self.MTcheck()
        Gdk.flush()
        GLib.timeout_add(1500, self.MTset_new)

    def MTset_new(self):
        global buffer
        global fileSize
        self.builder.get_object("matchTrLabelResult").set_text(str())
        if random() < 0.03:
            newBound = int(random() * (max(0, fileSize - 100)))
            buffer = DictBuffer([newBound, newBound + 100])
        self.MTwhich = buffer.list[int(random() * len(buffer.list))]
        self.builder.get_object("matchTrLabelWord").set_text(self.MTwhich["German"].strip())
        self.MTcorrect = int(random() * 4)
        for i in range(4):
            if i != self.MTcorrect:
                self.builder.get_object("matchTrLabelChoice"+str(i)).set_text(unequalRand(self.MTwhich, "English").strip())
        self.builder.get_object("matchTrLabelChoice"+str(self.MTcorrect)).set_text(self.MTwhich["English"].strip())
        self.builder.get_object("matchTrEvBox8").modify_bg(Gtk.StateType.NORMAL, setColor(222, 229, 232))

    def MTcheck(self):
        if self.MTchoice == self.MTcorrect:
            self.MTwhich["Attributes"] = self.MTset_attr(self.MTwhich["Attributes"], True)
            self.builder.get_object("matchTrEvBox8").modify_bg(Gtk.StateType.NORMAL, setColor(50, 205, 50))
            self.builder.get_object("matchTrLabelResult").set_text("CORRECT!")
        else:
            self.MTwhich["Attributes"] = self.MTset_attr(self.MTwhich["Attributes"], False)
            self.builder.get_object("matchTrEvBox8").modify_bg(Gtk.StateType.NORMAL, setColor(255, 67, 71))
            self.builder.get_object("matchTrLabelResult").set_text("INCORRECT!")
        f = lambda x: 1 if x["German"] == self.MTwhich["German"] and x["English"] == self.MTwhich["English"] else 0
        change_database(f, "Attributes", self.MTwhich["Attributes"])
    
    def MTset_attr(self, x, cor):
        s = str()
        y = x.split()
        val = list(map(int, y[0].split("/")))
        if cor:
            val[0] += 1
        else:
            val[1] += 1
        s = str(val[0]) + "/" + str(val[1])
        i = False
        for t in y:
            if i:
                s = s + ' ' + t
            else:
                i = True
        return s

                # ==================================================
                # ==================================================
                # Phrase Training
                # ==================================================
                # ==================================================
    
    def PTset_new(self):   
        global buffer
        global fileSize

        self.builder.get_object("phraseLabel").set_text(str())
        #self.builder.get_object("PTcheckPhraseLabel").hide()
        self.builder.get_object("checkPhraseLabel").set_text(str())
        self.builder.get_object("checkPhraseLabel").modify_bg(Gtk.StateType.NORMAL, setColor(222, 229, 232))

        if random() < 0.03:
            self.PTq = get_quantity_f(self.PTfilter)
            newBound = int(random() * (max(0, self.PTq - 100)))
            self.PTbuff = fBuffer([newBound, newBound + 100], self.PTfilter)

        self.PTwhich = self.PTbuff.list[int(random() * len(self.PTbuff.list))]
        self.PTdividedPhrase = self.PTwhich["German"].strip().split()
        self.PTdistr_to_butts()

    def PTdistr_to_butts(self):
        tmp = list(range(0, len(self.PTdividedPhrase)))
        shuffle(tmp)

        for i in range(len(self.PTdividedPhrase), 16):
            self.builder.get_object("phraseButton" + str(i)).hide()

        for i in range(len(self.PTdividedPhrase)):
            but = self.builder.get_object("phraseButton" + str(i))
            but.set_label(self.PTdividedPhrase[tmp[i]])
            but.show()

    def PTclick_on_but(self, widget, ind):
        s = self.builder.get_object("phraseLabel").get_text().strip()
        s = s + " " + self.builder.get_object(ind).get_label()
        self.builder.get_object("phraseLabel").set_text(s)

        self.builder.get_object(ind).set_label(str())
        self.builder.get_object(ind).hide()

        if len(self.builder.get_object("phraseLabel").get_text().strip()) == len(self.PTwhich["German"].strip()):
            self.PTcheck()
            #self.builder.get_object("PTcheckPhraseLabel").show()
            GLib.timeout_add(1500, self.PTset_new)
    
    def PTcheck(self):
        if self.builder.get_object("phraseLabel").get_text() == self.PTwhich["German"].strip():
            self.PTwhich["Attributes"] = self.PTset_attr(self.PTwhich["Attributes"], True)
            self.builder.get_object("checkPhraseLabel").modify_bg(Gtk.StateType.NORMAL, setColor(50, 205, 50))
            self.builder.get_object("checkPhraseLabel").set_text("CORRECT!")
        else:
            self.PTwhich["Attributes"] = self.PTset_attr(self.PTwhich["Attributes"], False)
            self.builder.get_object("checkPhraseLabel").modify_bg(Gtk.StateType.NORMAL, setColor(255, 67, 71))
            self.builder.get_object("checkPhraseLabel").set_text("INCORRECT!")

        f = lambda x: 1 if x["German"] == self.PTwhich["German"] and x["English"] == self.PTwhich["English"] else 0
        change_database(f, "Attributes", self.PTwhich["Attributes"])
        
    def PTset_attr(self, x, cor):
        s = str()
        y = x.split()
        val = list(map(int, y[0].split("/")))
        if cor:
            val[0] += 1
        else:
            val[1] += 1
        s = str(val[0]) + "/" + str(val[1])
        i = False
        for t in y:
            if i:
                s = s + ' ' + t
            else:
                i = True
        return s

    # ==================================================
    # ==================================================
    # Dictionary
    # ==================================================
    # ==================================================

    def FWadd_umlaut(self, widget, case):
        german = self.builder.get_object("findWordEntryGerman")
        german.set_text(german.get_text() + umlauts[case])

    def FWget_attr(self, x):
        s = str()
        y = x.split()
        val = list(map(int, y[0].split("/")))
        acc = 0.0
        if val[1] == 0:
            if val[0] != 0:
                acc = 1.0
        else:
            acc = float(val[0]) / (val[0] + val[1])
        s = "Accuracy: " + str(int(acc * 100)) + "%"
        if y[1] != '-':
            s = s + "\nGender: " + y[1]
        return s

    def FWclear(self, widget):
        self.builder.get_object("findWordEntryGerman").set_text(str())
        self.builder.get_object("findWordEntryEnglish").set_text(str())
        self.builder.get_object("findWordLabelAttributes").set_text(str())

    def FWtranslate(self, widget):
        german = self.builder.get_object("findWordEntryGerman")
        english = self.builder.get_object("findWordEntryEnglish")
        deText = german.get_text().strip()
        enText = english.get_text().strip()
        flag = False
        t = {}
        global fileName
        if enText:
            t = search(fileName, enText, "English")
            if t:
                german.set_text(t["German"])
                flag = True
            else:
                Error("Error, word not found")
        else:
            t = search(fileName, deText, "German")
            if t:
                english.set_text(t["English"])
                flag = True
            else:
                Error("Error, word not found")
        if flag:
            attr = self.builder.get_object("findWordLabelAttributes")
            attr.set_text(self.FWget_attr(t["Attributes"])+'\nPart of speech: '+t["Type"])

    def DictScroll(self, widget, flag):
        newbound = [self.DictBound[0] + flag, self.DictBound[1] + flag]
        if (newbound[0] == 0):
            self.builder.get_object("dictionaryButtonUp").hide()
        else:
            self.builder.get_object("dictionaryButtonUp").show()

        global buffer
        global fileSize
        if (newbound[1] == fileSize):
            self.builder.get_object("dictionaryButtonDown").hide()
        else:
            self.builder.get_object("dictionaryButtonDown").show()
        self.DictBound = copy.deepcopy(newbound)
        if fileSize >= 100:
            if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
            else:
                highBound = min (self.DictBound[1] + 45, fileSize)
                buffer = DictBuffer([highBound - 100, highBound])
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
        else:
            if buffer.bound[1] <= self.DictBound[1] and buffer.bound[0] >= self.DictBound[0]:
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]
            else:
                buffer = DictBuffer([0, fileSize])
                for i in range(buffer.bound[0], buffer.bound[1]):
                    if i < self.DictBound[1] and i >= self.DictBound[0]:
                        self.DictCurData [i - self.DictBound[0]] = buffer.list[i - buffer.bound[0]]

        for x in range(min(10, len(self.DictCurData))): 
            self.builder.get_object("dictionaryWord"+str(x)).set_label(self.DictCurData[x][self.DictCurLang])
        for x in range(min(10, len(self.DictCurData)), 10): 
            self.builder.get_object("dictionaryWord"+str(x)).hide()

    def DictOpen_Word(self, widget, x):
        OpenedWord(self.DictCurData[x])

    def DictChange_Language(self, widget):
        if self.DictCurLang == "German":
            self.DictCurLang = "English"
            for x in range(min(10, len(self.DictCurData))):
                self.builder.get_object("dictionaryWord"+str(x)).set_label(self.DictCurData[x][self.DictCurLang])
            self.builder.get_object("dictionaryButtonLanguage").set_label("de")
        else:
            self.DictCurLang = "German"
            for x in range(min(10, len(self.DictCurData))):
                self.builder.get_object("dictionaryWord"+str(x)).set_label(self.DictCurData[x][self.DictCurLang])
            self.builder.get_object("dictionaryButtonLanguage").set_label("en")

    def DictAddNewWord(self, widget):
        NewWord()

    # ==================================================
    # ==================================================
    # Current Training
    # ==================================================
    # ==================================================

    def TrainScroll(self, widget, flag, how):
        newbound = [self.TrainBound[0] + flag, self.TrainBound[1] + flag]
        if (newbound[0] == 0):
            self.builder.get_object("trainingButtonUp").hide()
        else:
            self.builder.get_object("trainingButtonUp").show()

        global curTraining
        if (newbound[1] == len(curTraining)):
            self.builder.get_object("trainingButtonDown").hide()
        else:
            self.builder.get_object("trainingButtonDown").show()
        self.TrainBound = copy.deepcopy(newbound)
        self.TrainCurData = curTraining[self.TrainBound[0]:self.TrainBound[1]]

        for x in range(min(10, len(self.TrainCurData))): 
            self.builder.get_object("trainingWord"+str(x)).set_label(self.TrainCurData[x][self.TrainCurLang])
        for x in range(min(10, len(self.TrainCurData)), 10): 
            self.builder.get_object("trainingWord"+str(x)).hide()

    def TrainOpen_Word(self, widget, x):
        OpenedWord(self.TrainCurData[x])

    def TrainChange_Language(self, widget):
        if self.TrainCurLang == "German":
            self.TrainCurLang = "English"
            for x in range(min(10, len(self.TrainCurData))):
                self.builder.get_object("trainingWord"+str(x)).set_label(self.TrainCurData[x][self.TrainCurLang])
            self.builder.get_object("trainingButtonLanguage").set_label("de")
        else:
            self.TrainCurLang = "German"
            for x in range(min(10, len(self.TrainCurData))):
                self.builder.get_object("trainingWord"+str(x)).set_label(self.TrainCurData[x][self.TrainCurLang])
            self.builder.get_object("trainingButtonLanguage").set_label("en")

    # ==================================================
    # ==================================================
    # Groups
    # ==================================================
    # ==================================================

    def ATGadd_umlaut(self, widget, case):
        german = self.builder.get_object("addToGroupEntryName")
        german.set_text(german.get_text() + umlauts[case])

    def addToGroup(self, widget):
        groupName = self.builder.get_object("addToGroupEntryName")
        Name = groupName.get_text().strip()
        global fileName
        add_user_to_group(Name, fileName[:-4])
        global buffer
        buffer = DictBuffer([0, 100])
        self.checkGroups()

    def CGadd_umlaut(self, widget, case):
        german = self.builder.get_object("createGroupEntryName")
        german.set_text(german.get_text() + umlauts[case])

    def checkGroups(self):
        global fileName
        global myGroups
        my_groups(fileName[:-4])
        if len(myGroups) == 0:
            self.builder.get_object("checkMyGroupsLabelInvolved").hide()
            self.builder.get_object("checkMyGroupsLabelNogroups").show()
        else:
            self.builder.get_object("checkMyGroupsLabelNogroups").hide()
            self.builder.get_object("checkMyGroupsLabelInvolved").show()
            for i in range(len(myGroups)):
                label = self.builder.get_object("checkMyGroupsLabel" + str(i))
                label.set_text(myGroups[i])
                self.builder.get_object("checkMyGroupsLabel" + str(i)).show()
                self.builder.get_object("checkMyGroupsLabelGroup" + str(i)).show()
        for i in range(len(myGroups), 3):
            self.builder.get_object("checkMyGroupsLabel" + str(i)).hide()
            self.builder.get_object("checkMyGroupsLabelGroup" + str(i)).hide()

    def createGroup(self, widget):
        groupName = self.builder.get_object("createGroupEntryName")
        Name = groupName.get_text().strip()
        global fileName
        create_group(Name, fileName[:-4])
        self.checkGroups()

fileSize = 0
trainingSwitch = True
curTraining = list()
fileName = "users_die_hard.csv"
myGroups = list()
script_dir = os.path.dirname(__file__)
buffer = DictBuffer([0, 100])
if __name__ == '__main__':
    main = Main()
    Gtk.main()
