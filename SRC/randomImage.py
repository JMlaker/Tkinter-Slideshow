
# Created By: Josh Mlaker
# 
# Description:  Slideshows random images from directories in ./.. or chosen directories
#               Assumes the same structure from my Image Grabber
# Dependencies: tkinter, win32, Pillow

import os
from PIL import Image, ImageTk
import random
import win32gui, win32con
import tkinter
import tkfilebrowser
import re

# Load the image into the image window
class imgCanvas(tkinter.Frame):
    # Setup stuff
    def __init__(self, master, *args):
        tkinter.Frame.__init__(self, master, args)
        self.path = None
        self.keepInfo = []
        self.background = tkinter.Label(self)
        self.background.pack(fill="both", expand="yes")
        # If the window is resized, resize the image too
        self.background.bind("<Configure>", lambda e: self.updateImage(self.path) if self.path is not None and e.width != ((self.master.winfo_width() + 4 and e.height != self.master.winfo_height() + 4) if self.master else False) else ())
        # You can use space to store an image's path for testing/master purposes. Printed when everything is closed
        self.master.bind("<space>", lambda e: self.keepInfo.append(self.master.title()) if self.master.title() not in self.keepInfo else ())
    
    # Update the image shown
    def updateImage(self, imgPath):
        # Store path and open the image
        self.path = imgPath
        self.image = Image.open(imgPath)

        # Resize the image to be the size of the window
        # the -4 is needed for border purposes
        self.image.thumbnail((self.master.winfo_width() - 4, self.master.winfo_height() - 4), Image.Resampling.LANCZOS)
        
        # Set the image
        self.img = ImageTk.PhotoImage(self.image)
        self.background.configure(image = self.img)
        
        # Change the window name to the image's file path
        self.master.title(imgPath.split("\\")[-2] + " - " + imgPath.split("\\")[-1])

        # Make sure to free the memory
        self.image.close()

# Method for picking a random image from a list of directories
def getRandom(directories):
    global imageWindow

    # The following code closes the photos app if opened.
    # While not always necessary, some problems could occur if an image is opened in Photos and here
    # Feel free to comment/remove this code if you do not want Photos to close
    hwnds = []
    win32gui.EnumWindows(lambda hwnd, ctx: enum_helper(hwnd, ctx, hwnds), None)
    for hwnd in hwnds:
        if win32gui.GetWindowText(hwnd) == "Photos": pass
        try: win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except: pass

    # Weighs the directory choice by how many images are in such directory
    # This just felt "nicer" for me, but is not necessary
    # Feel free to remove this code (and the use of weights) if desired
    weights = []
    dirSum = 0
    for dir in directories:
        weights.append(len(next(os.walk(dir))[2]))
        dirSum += len(next(os.walk(dir))[2])
    weights = list(map(lambda x: x / dirSum, weights))
    
    # Grab a random directory from the list
    randDir = random.choices(directories, weights=weights, k=1)[0]

    # Grab a random image from the chosen directory
    try: 
        if (imageWindow.winfo_exists() == 0):
            createImageWindow()
        photoArr = next(os.walk(randDir))[2]
        photoArr = [x for x in photoArr if "VID" not in x]
        randImage = random.choice(photoArr)
        imgPath = randDir + "\\" + randImage
        imageWindow.updateImage(imgPath=imgPath)
        imageWindow.background.configure(width=1000,height=780)
        imageWindow.lift()

    # If something that couldn't be opened was chosen, print it out
    except Exception as e:
        print(e)
        print(randDir)

# Maps directories to absolute
# PLEASE CHANGE THIS TO YOUR OWN FILE PATH!
def directoryMapper(x):
    return f"F:\\Personal\\Image-Grabber\\{x}"

# Grabs all directories from ./..
def allDirectories():
    # Get ./..
    path = __file__.replace("SRC\RandomImage.py", "")
    
    # Store all directories found inside directories array
    directories = []
    for x in next(os.walk(path))[1]:
        directories.append(x)
    
    # PUT ANY DIRECTORIES TO REMOVE FROM ALL SELECT FROM ./.. BELOW IN ORDER TO AVOID ERRORS!
    directories.remove('SRC')
    directories.remove('.vs')

    # Map directories to absolute pathing
    directories = list(map(directoryMapper, directories))

    # Return the list of directories
    return directories

# Helper function for enumerator
def enum_helper(hwnd, ctx, hwnds):
    if re.match(u".*Photos", win32gui.GetWindowText(hwnd)):
        hwnds.append(hwnd)

top = tkinter.Tk() # Top most widget, which contains everything

# Create the window which will contain the image
def createImageWindow():
    global imageWindow # Important global variable for tracking the window

    # Create a new widget
    imageCarrier = tkinter.Toplevel()
    imageCarrier.geometry("+260+0")

    # Create a window inside the widget
    imageWindow = imgCanvas(imageCarrier)
    imageWindow.background.configure(width=80,height=40)
    # Pack the window and make sure it takes up the entire widget
    imageWindow.pack(fill='both', expand='yes')

createImageWindow() # Create the image window

# Variables used to determine slideshow logic
loop = tkinter.BooleanVar()
timer = tkinter.StringVar()
curLoop = None
selectedDirs = None

# Randomly select an image from all possible directories
def rotateAll():
    global curLoop
    if curLoop is not None: top.after_cancel(curLoop)
    getRandom(allDirectories())
    if loop.get(): curLoop = top.after(int(timer.get()), rotateAll)

# Example rotates for preset buttons if desired
# If not desired, comment or delete both of these functions and their respective buttons
def rotateExample1():
    global curLoop
    if curLoop is not None: top.after_cancel(curLoop)
    directories = allDirectories()
    directories = [directory for directory in directories if "ex1" in directory]
    getRandom(directories)
    if loop.get(): curLoop = top.after(int(timer.get()), lambda: rotateSelect(directories))

def rotateExample2():
    global curLoop
    if curLoop is not None: top.after_cancel(curLoop)
    directories = allDirectories()
    directories = [directory for directory in directories if "ex2" in directory]
    getRandom(directories)
    if loop.get(): curLoop = top.after(int(timer.get()), lambda: rotateSelect(directories))

# Randomly get an image from a selection of directories
def rotateSelect(selection):
    global curLoop
    getRandom(selection)
    if loop.get(): curLoop = top.after(int(timer.get()), lambda: rotateSelect(selection))

# Select directories using tkinter's file browser
def selectDir():
    global selectedDirs, curLoop, imageWindow

    # Check to make sure two images never appear
    if curLoop is not None: top.after_cancel(curLoop)

    # If the selected directories is empty, set to none (for next check)
    if selectedDirs == []: selectedDirs = None

    # If the selected directories is not empty, grab a new image from the previous selection
    if selectedDirs != None: return rotateSelect(selectedDirs)

    # Make sure the image window still exists
    if imageWindow.winfo_exists() == 0: createImageWindow()
    
    # Open window to select directories
    selectedDirs = list(tkfilebrowser.askopendirnames(top, initialdir="\\".join(__file__.split("\\")[:-2])))
    R.pack() # Pack the reset directories button
    
    # If nothing is chosen, assume all directories are wanted
    if len(selectedDirs) == 0: return rotateAll()

    # Return the selected directories
    return rotateSelect(selectedDirs)

# Reset the selection of directories
def resetSel():
    global selectedDirs, curLoop
    selectedDirs = None
    if curLoop is not None: top.after_cancel(curLoop)
    R.pack_forget()

# Make sure a window is topmost
def always_top():
    top.lift()
    top.attributes("-topmost", True)

# Validation method for text input
def validate(action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
    if value_if_allowed:
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False
    else:
        return False

# Add the validation method to top
vcmd = (top.register(validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

B = tkinter.Button(top, text="New Image - All", command=rotateAll)          # All button

A = tkinter.Button(top, text="EXAMPLE BUTTON 1", command=rotateExample1)    # EX1 button

L = tkinter.Button(top, text="EXAMPLE BUTTON 2", command=rotateExample2)    # EX2 button

S = tkinter.Button(top, text="New Image - Select", command=selectDir)       # Selected button

# Checkbox to automatically slideshow the images
C = tkinter.Checkbutton(top, text="Loop?", variable=loop, onvalue=True, offvalue=False)

# Textbox to input how long the images are on screen (milliseconds)
T = tkinter.Entry(top, textvariable=timer, validate='key', validatecommand=vcmd)
T.insert(0, "2500")

# Selection reset button (not packed unless a selection is made)
R = tkinter.Button(top, text="Reset Selection", command=resetSel)

always_top()

top.geometry("+0+0")

B.pack()
A.pack()
L.pack()
S.pack()
C.pack()
T.pack()

top.mainloop()

print(imageWindow.keepInfo)
