# CITRACUT v1.2
# 02/08/22
# www.samoe.me/code

# This software was created for use alongside Onyx Thrive RIP Queue
# 
# Plug each Graphtec cutter into its OWN computer that is running
# Onyx Thrive CUT-Server
#
# Enable "Automatically cut new files"
# Enable "Delete files when finished"
# Add the "Hot Folder" that you configured in the software
#
# In CitraCut, select a cut file from one of the lists, corresponding
# with the cutter you want to use. Then, click "Submit" and the cutter
# should whir to life and cut the sheet.

import tkinter
from tkinter.font import Font
from PIL import Image, ImageTk
import os
import data.params
import xml.etree.cElementTree as ET

################################################################
## INITIALIZE WINDOW ###########################################

root = tkinter.Tk()
rootFrame = tkinter.Frame(bg = data.params.color_BG_header)

################################################################
## INITIALIZE VARIABLES AND CONSTANTS ##########################

global scriptDir
scriptDir = os.path.dirname(__file__)

global fileList
fileList = os.listdir(data.params.cutFileSource)

global hotFolders
hotFolders = [
    data.params.hotFolder1,
    data.params.hotFolder2,
    data.params.hotFolder3
]

global cuttersArray
cuttersArray = []

###########################################################
# CUSTOM BUTTON CLASS #-----------------------------------#

class HoverButton(tkinter.Button):
    def __init__(self, master, icons, **kw):
        tkinter.Button.__init__(self, master = master, highlightthickness = 0, bd = 0, **kw)
        tkinter.Button.config(self, relief = 'flat')
        self.padding = 0

        self.selectable = True
        self.selected = False

        self.defaultImage = icons.idle
        self.hoverImage = icons.hovered
        self.clickedImage = icons.clicked
        self.selectedImage = icons.selected

        self['image'] = self.defaultImage

        self.bind("<Enter>", on_hover)
        self.bind("<Leave>", on_unhover)
        self.bind("<Button-1>", on_clicked)

class Icons() :
    idle = '',
    hovered = '',
    clicked = '',
    selected = ''

###########################################################
# FUNCTIONS FOR BUTTONS #---------------------------------#

def on_hover(event):
    if event.widget.selected == False :
        event.widget['image'] = event.widget.hoverImage

def on_unhover(event):
    if event.widget.selected == False :
        event.widget['image'] = event.widget.defaultImage

def on_clicked(event):
    event.widget['image'] = event.widget.clickedImage
    root.update()
    event.widget.selected = False
    root.after(100, on_hover(event))

####################################################
## REFRESH FILE LIST ###############################

def refreshFileList() :

    global fileList
    fileList = os.listdir(data.params.cutFileSource)

    for i in cuttersArray :
        i.listBox1.delete(0, 'end')
        i.Update(fileList)

####################################################
## OPEN SETTINGS ###################################

def openSettings() :
    osCommand = "notepad.exe " + scriptDir + "/data/params.py"
    os.system(osCommand)

####################################################
## CREATE GUI ######################################

# Fonts
fontList = Font(family = 'Roboto', size = data.params.listFontSize)
selectedFont = Font(family = 'Avenir Next Bold', size = data.params.selectedFontSize)

# Header
headerFrame = tkinter.Frame(rootFrame, bg = data.params.color_BG_header)

logoImageRef = Image.open(data.params.image_Logo)
logoImage = ImageTk.PhotoImage(logoImageRef)

logoImageLabel = tkinter.Label(headerFrame, image = logoImage, bg = data.params.color_BG_header)
logoImageLabel.pack(side = 'left')

spacerFrame = tkinter.Frame(headerFrame, bg = data.params.color_BG_header)
spacerFrame.pack(side = 'left', padx=280)

icons_Settings = Icons()
icons_Settings.idle = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_settingsIcon_idle.png")
icons_Settings.hovered = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_settingsIcon_hovered.png")
icons_Settings.clicked = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_settingsIcon_clicked.png")

icons_Refresh = Icons()
icons_Refresh.idle = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_refresh_idle.png")
icons_Refresh.hovered = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_refresh_hovered.png")
icons_Refresh.clicked = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_refresh_clicked.png")

refreshButton = HoverButton(headerFrame, bg = data.params.color_BG_header, icons = icons_Refresh)
refreshButton.pack(side = 'left')
refreshButton.config(command = refreshFileList)

settingsButton = HoverButton(headerFrame, bg = data.params.color_BG_header, icons = icons_Settings)
settingsButton.pack(side = 'left')
settingsButton.config(command = openSettings)

headerFrame.grid(ipady = 8, ipadx = 8, column = 0, row = 0, columnspan = 5)

####################################################
## Cutter Class ####################################
class Cutter() :

    ####################################################
    # Live Search
    def searchUpdate(self, event) :
        
        val = event.widget.get()
        if val == '':
            data = fileList
        else:
            data = []
            for item in fileList:
                if val.lower() in item.lower():
                    data.append(item)				

        self.Update(data)

    ####################################################
    # Select Entire Search Box When Clicking On It
    def selectAllInSearch(self, event) :

        event.widget.select_range(0, tkinter.END)
        event.widget.icursor(tkinter.END)
        event.widget.focus()

        return 'break'

    ####################################################
    # Update Listbox
    def Update(self, data) :
        
        self.listBox1.delete(0, 'end')
        for item in data:
            self.listBox1.insert('end', item.split(".")[0])

    ####################################################
    # Update List Selected Item
    def updateListSelection(self, event) :

        index = int(event.widget.curselection()[0])
        value = event.widget.get(index)
        self.selectedItem.set(value)

    ####################################################
    # Submit Cut File
    def submitCutFile(self) :

        # Initialize the file name (with no suffix), file source (full file path), and destination (full file path)
        self.file = self.selectedItem.get()
        self.source = data.params.cutFileSource + "/" + self.file + ".xml"
        self.dest = hotFolders[self.id] + "/" + self.file + ".xml"

        # Rotate the cut file 180 degrees, this is necessary on the Graphtec FC9000 for some reason
        tree = ET.parse(self.source)
        xmlRoot = tree.getroot()
        xmlRoot.set("rotation", "180")

        # Write the new XML file to the hot folder destination
        tree.write(self.dest)

    ####################################################
    # Init Cutter Frame GUI
    def __init__(self, master, title, id) :
        
        self.id = id

        ####################################################
        ## Main Frame

        self.frame = tkinter.Frame(master, bg = data.params.color_BG)

        ####################################################
        ## Title

        self.title = title
        self.titleLabel = tkinter.Label(self.frame, text = title, bg = data.params.color_BG, fg = "#FFFFFF", font = selectedFont)
        self.titleLabel.pack(padx = 8, ipady = 16)

        ####################################################
        ## Search

        self.searchFrame = tkinter.Frame(self.frame, bg = data.params.color_BG)

        #
        self.searchInput = tkinter.StringVar()

        self.searchLabel = tkinter.Label(self.frame, text = "SEARCH", fg = "#DDDDDD", bg = data.params.color_BG)
        self.searchLabel.pack(anchor = 'w', padx = 8)

        self.searchEntryBox = tkinter.Entry(self.frame, width = 32, textvariable = self.searchInput, font = fontList)
        self.searchEntryBox.pack(ipady = 2, padx = 8)
        self.searchEntryBox.bind('<KeyRelease>', self.searchUpdate)
        self.searchEntryBox.bind('<Button-1>', self.selectAllInSearch)
        #

        self.searchFrame.pack(padx = 8, pady = 8)

        ####################################################
        ## List Box

        self.listFrame = tkinter.Frame(self.frame, bg = data.params.color_BG)

        self.scrollbar = tkinter.Scrollbar(self.listFrame)

        self.listBox1 = tkinter.Listbox(self.listFrame, exportselection=False, height = data.params.listHeight, width = 30, font = fontList, yscrollcommand = self.scrollbar.set)
        self.listBox1.bind('<<ListboxSelect>>', self.updateListSelection)

        self.scrollbar.config(command = self.listBox1.yview)

        self.listBox1.pack(side = 'left', fill = 'y')
        self.scrollbar.pack(side = 'right', fill = 'y')

        self.listFrame.pack(padx = 2, pady = 8)

        ####################################################
        ## Selected Item

        self.selectedFrame = tkinter.Frame(self.frame, bg = data.params.color_BG)

        #
        self.selectedItem = tkinter.StringVar()

        self.selectedFrameLabel = tkinter.Label(self.selectedFrame, text = "SELECTED: ", bg = data.params.color_BG, fg = "#FFFFFF")
        self.selectedFrameLabel.pack(padx = 4)

        self.selectedItemLabel = tkinter.Label(self.selectedFrame, text = "NONE", textvariable = self.selectedItem, bg = data.params.color_BG, fg = "#FFFFFF", font = selectedFont)
        self.selectedItemLabel.pack(padx = 4)
        #

        self.selectedFrame.pack(padx = 8, pady = 4)

        ####################################################
        ## Submit Button

        self.submitIcons = Icons()
        self.submitIcons.idle = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_submit_idle.png")
        self.submitIcons.hovered = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_submit_hovered.png")
        self.submitIcons.clicked = ImageTk.PhotoImage(file = "L:/Scripting/CitraCut Dev Branch/assets/citraCut_submit_clicked.png")

        self.submitButton = HoverButton(self.frame, command = self.submitCutFile, icons = self.submitIcons, bg = data.params.color_BG)
        self.submitButton.pack(pady = 8, padx = 8)
    
####################################################
####################################################

cutterFrame = tkinter.Frame(rootFrame, bg = data.params.color_BG)

column1 = Cutter(cutterFrame, "GRAPHTEC FC9000-1", 0)
column1.frame.grid(column = 0, row = 1, padx = 8)
column1.Update(fileList)
cuttersArray.append(column1)

column2 = Cutter(cutterFrame, "GRAPHTEC FC9000-2", 1)
column2.frame.grid(column = 1, row = 1, padx = 8)
column2.Update(fileList)
cuttersArray.append(column2)

column3 = Cutter(cutterFrame, "GRAPHTEC FC9000-3", 2)
column3.frame.grid(column = 2, row = 1, padx = 8)
column3.Update(fileList)
cuttersArray.append(column3)

cutterFrame.grid(row = 2)

bottomSpacer = tkinter.Frame(rootFrame, bg = data.params.color_BG, height = 20, width = 972)
bottomSpacer.grid(row = 3, column = 0, columnspan = 3)

rootFrame.pack()
root.mainloop()