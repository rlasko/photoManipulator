from kivy.app import App
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as Im
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.core.image import ImageData
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.uix.colorpicker import ColorPicker
from PIL import Image, ImageDraw
import random
import copy
import math
import sys
import os

##################################################

        ##### Load Photo Screen #####

##################################################

class photoLoadScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(photoLoadScreen, self).__init__(**kwargs)
        self.imagePath = None
        # init load photo screen background as black
        with self.canvas.before:
            Color(0, 0, 0, 1)  # colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        # change it dynamically to match screen resizing
        self.bind(size=self.rectSize, pos=self.rectSize)

        logo = Im(source="logo.jpg", size_hint=(.75,.75), pos_hint={'center_x':.5, 'center_y':.6}, allow_stretch=True)
        self.add_widget(logo)

        loadButton = Button(text = "Get Started", size_hint=(.2,.08), pos_hint={'center_x':.5, 'center_y':.25})
        self.add_widget(loadButton)
        loadButton.bind(on_press=lambda x: self.loadButtonCallback())

    # dynamically resize background rectangle
    def rectSize(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def loadButtonCallback(self):
        self.loadContent = LoadDialog()
        # create containers for things
        buttonLayout = BoxLayout(size_hint_y=(1, .1), height=60)
        cancelButton = Button(text='Cancel')
        loadButton = Button(text="Load")
        buttonLayout.add_widget(cancelButton)
        buttonLayout.add_widget(loadButton)
        self.loadContent.add_widget(buttonLayout)

        # create and open load popup
        self.popup = Popup(title="Load file", content=self.loadContent,
                            size_hint=(1, 1))
        cancelButton.bind(on_release=self.popup.dismiss)
        loadButton.bind(on_press=lambda x: self.loadCallBack())
        self.popup.open()

    # called when user loads an image, closes load screen
    def loadCallBack(self):
        try:  # verify that user selected an image
            self.imagePath = self.loadContent.loadedFile()  # get selected file path
            if self.imagePath[-4:].upper() == "JPEG":
                self.imagePath = self.imagePath[:-4] + 'jpg'
            assert('JPG' in self.imagePath.upper())  # make sure correct file type selected
            self.popup.dismiss() # close pop up
            self.parent.remove_widget(self) # close load screen
            print(self.imagePath)
        except:
            # error occurred!!
            errorContent = Label(text='There was a problem loading your file. \n Please select a jpg file',
                                 halign='center', line_height=1.4)
            errorPopup = Popup(title="Error", content=errorContent, size_hint=(None, None), size=(700, 300))
            errorPopup.open()

    # method to return path of user selected image
    def photoPath(self):
        return self.imagePath if self.imagePath is not None else print("No File Loaded")

class LoadDialog(FloatLayout):
    def __init__(self,**kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.fileChooser = FileChooserIconView()
        layout.add_widget(self.fileChooser)
        self.add_widget(layout)

    # return user selected file path
    def loadedFile(self):
        return self.fileChooser.selection[0]

##################################################

         ##### UI Instructions #####

##################################################

# tool bar class to allow user to select desired mode
class ToolBar(GridLayout):
    # init tool bar vals
    def __init__(self, topBars, **kwargs):
        super(ToolBar, self).__init__(**kwargs)
        self.cols = 1
        self.col_default_width = 160
        self.padding = [self.col_default_width / 8, self.size[1] / 11]
        self.spacing = [0, self.size[1] / 3]
        self.topBars = topBars
        self.currBar = (None, None)
        self.buttonAdded = False
        self.infoButton = self.createInfoButton()
        ToolBar.addButtons(self)
        self.keyboardCommands()

    # add tool buttons that open each tool bar
    # pass key to determine which kind of bar to open
    def addButtons(self):
        # brightness button
        brightness = ToggleButton(text="Brightness", group="state")
        brightness.bind(on_press=lambda x: self.selectControlBar(0))
        self.add_widget(brightness)
        # levels button
        levels = ToggleButton(text="Levels", group="state")
        levels.bind(on_press=lambda x: self.selectControlBar(1))
        self.add_widget(levels)
        # blur button
        blur = ToggleButton(text="Blur", group="state")
        blur.bind(on_press=lambda x: self.selectControlBar(2))
        self.add_widget(blur)
        # bw button
        bw = ToggleButton(text="B/W", group="state")
        bw.bind(on_press=lambda x: self.selectControlBar(3))
        self.add_widget(bw)
        # threshold button
        threshold = ToggleButton(text="Threshold", group="state")
        threshold.bind(on_press=lambda x: self.selectControlBar(4))
        self.add_widget(threshold)
        # abstract button
        abstract = ToggleButton(text="Abstract", group="state")
        abstract.bind(on_press=lambda x: self.selectControlBar(6))
        self.add_widget(abstract)
        # always be last
        # tools button
        tools = ToggleButton(text="Tools", group="state")
        tools.bind(on_press=lambda x: self.selectControlBar(5))
        self.add_widget(tools)

    # selects correct TopBar based on mode
    def selectControlBar(self, currState):
        # switch controlBars
        if currState == 0: bar = "TopBar0"
        elif currState == 1: bar = "TopBar1"
        elif currState == 2: bar = "TopBar2"
        elif currState == 3: bar = "TopBar3"
        elif currState == 4: bar = "TopBar4"
        elif currState == 5: bar = "TopBar5"
        elif currState == 6: bar = "TopBar6"

        self.popupMode(currState)
        # remove old bar, add new one
        for widget in self.topBars:
            if widget != bar:
                # be sure there's a tool bar open
                if self.currBar != (None, None):
                    self.parent.remove_widget(self.currBar[1])
                self.currBar = (widget, self.topBars[bar])
                self.parent.add_widget(self.topBars[bar])
        if self.buttonAdded == False:
            self.parent.add_widget(self.infoButton)
            self.buttonAdded = True

    # get current state to determine text of info
    def popupMode(self, currState):
        if currState == 0:
            self.popup.title = "Brightness"
            content = "Click the brightness button to adjust the brightness"
        elif currState == 1:
            self.popup.title = "Levels"
            content = "Use the “Random Levels” button to randomly change the image \n" + "Alternately, " \
                                "use the sliders for more control \n over different luminosity ranges of the image"
        elif currState == 2:
            self.popup.title = "Blur"
            content = "Box blur blurs each pixel by its neighboring pixels in all directions \n " \
                      "Motion blur blurs each pixel by its horizontal neighbors \n " \
                      "Vertical blur blurs each pixel by its vertical neighbors \n \n Enter a number in the popup to " \
                      "determine the number of \n neighbors in each direction each pixel is averaged by."
            self.popup.size = (1000, 460)
        elif currState == 3:
            self.popup.title = "B/W"
            content = 'Chose “Simple B/W” to change the image to grayscale ' \
                      '\n \n Or select one of the “weighted” buttons ' \
                      'to make those colors darker than the other  \n \n “High Contrast” creates a black and white ' \
                      'image \n with fewer neutral grays, and more extreme darks and light \n \n Use selective black and' \
                      'white to only make part of the image black and white. \n ' \
                      'Click anywhere on the image to choose the color'
            self.popup.size = (1175, 630)
        elif currState == 4:
            self.popup.title = "Threshold"
            content = 'Changes your image to only black and white pixels by sorting the pixels by ' \
                      'luminosity \n “Random Threshold” randomly selects a threshold value for the image \n ' \
                      'Alternative enter your own between 0 and 1 and press “Submit”'
            self.popup.size = (1200, 350)
        elif currState == 5:
            self.popup.title = "Tools"
            content = 'Keyboard shortcuts: \n [  undo \n ]  redo \n- opens a new photo and closes the current ' \
                      'one \n=  save \n` crop: click on any two points to crop the image accordingly '
            self.popup.size = (1000, 470)
        elif currState == 6:
            self.popup.title = "Abstract"
            content = '“Optical Dots Illusion” takes a threshold images and converts it to dots. \n ' \
                      'Enter values in the popup to customize. \n ' \
                      'Works best with images that have very strong outlines.' \
                      '\nCross your eyes and see the original image! \n \n “Polarize” converts the image from ' \
                      'rectangular to polar coordinates. \n Works best on panoramas \n \n Distanfy distorts the ' \
                      'image and makes it look distant \n \n “Ghost Color” inverts the colors of the image. \n ' \
                      'Stare at the center for 30 seconds then blink rapidly. \n You’ll see the original image'
            self.popup.size = (1000, 830)
        contentLabel = Label(text=content, line_height=1.35, halign="justify")
        self.popup.content = contentLabel

    # create blue info button
    def createInfoButton(self):
        infoButton = Button(pos_hint={'x': .94, 'y': .01}, size_hint=(.05, .07))
        infoButton.background_down = "info.png"
        infoButton.background_normal = "info.png"
        self.popup = Popup(title="", content=Label(), size_hint=(None,None), size=(1000, 420))
        infoButton.bind(on_release=self.popup.open)
        return infoButton

    # create keyboard listener
    def keyboardCommands(self):
        self.myKeyboard = Window.request_keyboard(
            None, self, 'text')
        self.myKeyboard.bind(on_key_down=self.keyPress)

    # do things when key board is pressed
    def keyPress(self, keyboard, keycode, text, modifiers):
        correctTopBar = self.topBars['TopBar5']  # only does things that relates to topbar 5
        if keycode[1] == "[":  # undo
            change = correctTopBar.undoPhoto()  # change sliders back
            if change == 'TopBar1':  # if the undo done was relating to the levels bar, relet those sliders
                self.topBars["TopBar1"].resetLevelsSliders()
        elif keycode[1] == ']':  # redo
            correctTopBar.redoPhoto()
        elif keycode[1] == "\\":
            self.topBars["TopBar1"].resetLevelsSliders()  # reset the sliders
            correctTopBar.resetPhoto()
        elif keycode[1] == "-":
            correctTopBar.newPhoto()
        elif keycode[1] == "=":
            correctTopBar.save()
        elif keycode[1] == "`":
            correctTopBar.cropImage()

# topBar contains controls to manipulate image
class TopBar(GridLayout):
    # init vals for each top bar
    def __init__(self, barNum, photoArea, **kwargs):
        super(TopBar, self).__init__(**kwargs)
        self.barNum = barNum
        self.myPhotoArea = photoArea
        self.rows = 1
        self.spacing = [30, self.size[1] / 7]
        self.padding = [self.size[0] / 6, self.size[1] / 7]
        self.highlightLevel = .5
        self.addButtons(barNum)
        self.clickState = False

    # change picuture back to original
    def resetPhoto(self):
        self.myPhotoArea.reset()

    # redo the last undo
    def redoPhoto(self):
        self.myPhotoArea.redoChanges()

    # undo the last change
    def undoPhoto(self):
        val = self.myPhotoArea.undoChanges()
        if val is not None:
            if val == "levels":
                return 'TopBar1'

    # determine TopBar type and add correct tools
    def addButtons(self, barNum):
        if barNum == 0:
            brightness = Button(text="Random Brightness")
            self.add_widget(brightness)
            brightness.bind(on_release=lambda x: self.brightnessCallback(random.uniform(.25, 1.75)))
            increase = Button(text="Increase Brightness")
            decrease = Button(text="Decrease Brightness")
            increase.bind(on_release=lambda x: self.brightnessCallback(1.1))
            decrease.bind(on_release=lambda x: self.brightnessCallback(.9))
            self.add_widget(increase)
            self.add_widget(decrease)
            self.add_widget(Label())
        elif barNum == 1:
            self.createLevelsToolBar()
        elif barNum == 2:
            self.createBlurBar()
        elif barNum == 3:
            self.createBWToolBar()
        elif barNum == 4:
            self.createThresholdToolBar()
        elif barNum == 5:
            self.createTools()
        elif barNum == 6:
            self.createAbstractButtons()

    # create BW toolbar
    def createBWToolBar(self):
        # create buttons
        BW = Button(text="Simple B/W")
        contrastBW = Button(text="High Contrast")
        redBW = Button(text="Red Weighted")
        greenBW = Button(text="Green Weighted")
        blueBW = Button(text="Blue Weighted")
        selectiveColorBW = Button(text="Selective Color")

        # bind buttons to functions
        BW.bind(on_release=lambda x: self.myPhotoArea.BW(1, 1, 1))
        redBW.bind(on_release=lambda x: self.myPhotoArea.BW(.1, 1.5, 1.5))
        greenBW.bind(on_release=lambda x: self.myPhotoArea.BW(1.5, .1, 1.5))
        blueBW.bind(on_release=lambda x: self.myPhotoArea.BW(1.5, 1.5, .1))
        contrastBW.bind(on_release=lambda x:self.myPhotoArea.contrastBW())
        selectiveColorBW.bind(on_release=lambda x: self.clickListener())

        # add them to the top bar
        self.add_widget(BW)
        self.add_widget(Label(size_hint_x=None, width=70))
        self.add_widget(redBW)
        self.add_widget(greenBW)
        self.add_widget(blueBW)
        self.add_widget(contrastBW)
        self.add_widget(selectiveColorBW)

    def clickListener(self):
        self.myPhotoArea.clickState = "sBW"

    # create the blur bar buttons
    def createBlurBar(self):
        # create blur buttons
        boxBlur = Button(text="Box Blur")
        motionBlur = Button(text="Motion Blur")
        verticalBlur = Button(text="Vertical Blur")

        # bind to funtions
        boxBlur.bind(on_release= lambda x:self.createPopup("box"))
        motionBlur.bind(on_release=lambda x: self.createPopup("motion"))
        verticalBlur.bind(on_release=lambda x: self.createPopup("vertical"))

        # add to tool bar
        self.add_widget(boxBlur)
        self.add_widget(motionBlur)
        self.add_widget(verticalBlur)

    # create popup with different info based on selected blur
    def createPopup(self,blurType):
        if blurType == "box": # box blur
            boxBlurPopupContent = self.blurPopupContent()
            self.blurFactor.text = '2'
            self.boxBlurPopup = Popup(title="Simple Blur Factor", content=boxBlurPopupContent,
                                         size_hint=(None, None), size=(500, 300))
            self.myCancelButton.bind(on_release=self.boxBlurPopup.dismiss)
            self.blurButton.bind(on_release=self.boxBlurPopup.dismiss,
                                 on_press=lambda x: self.myPhotoArea.boxBlur(int(self.blurFactor.text)))
            self.boxBlurPopup.open()
        elif blurType == "motion": # motion blur
            motionBlurPopupContent = self.blurPopupContent()
            self.motionBlurPopup = Popup(title="Motion Blur Factor", content=motionBlurPopupContent,
                                         size_hint=(None, None), size=(500, 300))
            self.myCancelButton.bind(on_release=self.motionBlurPopup.dismiss)
            self.blurButton.bind(on_press=self.motionBlurPopup.dismiss,
                                 on_release=lambda x: self.myPhotoArea.motionBlur(int(self.blurFactor.text)))
            self.motionBlurPopup.open()
        elif blurType == "vertical": # vertical blur
            verticalBlurPopupContent = self.blurPopupContent()
            self.verticalBlurPopup = Popup(title="Vertical Blur Factor", content=verticalBlurPopupContent,
                                           size_hint=(None, None), size=(500, 300))
            self.myCancelButton.bind(on_release=self.verticalBlurPopup.dismiss)
            self.blurButton.bind(on_press=self.verticalBlurPopup.dismiss,
                                 on_release=lambda x: self.myPhotoArea.verticalBlur(int(self.blurFactor.text)))
            self.verticalBlurPopup.open()

    # create content for the blur popup
    def blurPopupContent(self):
        popupLayout = GridLayout(rows=2, cols=1, spacing=[30,30])
        blurLabel = Label(text="Blur by Factor of: ", size_hint_x=None, width=320)
        self.blurFactor = TextInput(text="6", multiline=False, padding_y=[30, 20], cursor_blink=True, size_hint_y=None)
        self.myCancelButton = Button(text="Cancel")
        self.blurButton = Button(text="Blur")
        topLayout = GridLayout(cols=2, padding=[0,0,0,35])
        bottomLayout = GridLayout(cols=2,spacing=[15,15])

        topLayout.add_widget(blurLabel)
        topLayout.add_widget(self.blurFactor)
        bottomLayout.add_widget(self.myCancelButton)
        bottomLayout.add_widget(self.blurButton)

        popupLayout.add_widget(topLayout)
        popupLayout.add_widget(bottomLayout)
        return popupLayout

    # tool bar that contains non photo manipulation stuff
    def createTools(self):
        # create buttons
        self.crop = Button(text="Crop")
        self.undoBut = Button(text="Undo")
        self.redoBut = Button(text="Redo")
        self.resetBut = Button(text="Reset")
        self.saveBut = Button(text="Save")
        self.newPhotoBut = Button(text="New Photo")

        # bind buttons
        self.crop.bind(on_release=lambda x: self.cropImage())
        self.undoBut.bind(on_release=lambda x: self.undoPhoto())
        self.redoBut.bind(on_release=lambda x: self.redoPhoto())
        self.resetBut.bind(on_release=lambda x: self.resetPhoto())
        self.saveBut.bind(on_release=lambda x: self.save())
        self.newPhotoBut.bind(on_release=lambda x: self.newPhoto())

        # add to bar
        self.add_widget(self.crop)
        self.add_widget(self.newPhotoBut)
        self.add_widget(self.undoBut)
        self.add_widget(self.redoBut)
        self.add_widget(self.resetBut)
        self.add_widget(self.saveBut)

    # crop image
    def cropImage(self):
        self.myPhotoArea.clickState = "crop"

    # load new image, remove old
    def newPhoto(self):
        self.loadContent = LoadDialog()
        # create containers for things
        buttonLayout = BoxLayout(size_hint_y=(1, .1), height=60)
        cancelButton = Button(text='Cancel')
        loadButton = Button(text="Load")
        buttonLayout.add_widget(cancelButton)
        buttonLayout.add_widget(loadButton)
        self.loadContent.add_widget(buttonLayout)

        # create and open load popup
        self.popup = Popup(title="Load file", content=self.loadContent,
                           size_hint=(1, 1))
        cancelButton.bind(on_release=self.popup.dismiss)
        loadButton.bind(on_press=lambda x: self.loadCallBack())
        self.popup.open()

    # load new image
    def loadCallBack(self):
        try:  # verify that user selected an image
            self.imagePath = self.loadContent.loadedFile()  # get selected file path
            if self.imagePath[-4:].upper() == "JPEG":
                self.imagePath = self.imagePath[:-4] + 'jpg'
            assert ('JPG' in self.imagePath.upper())  # make sure correct file type selected
            self.popup.dismiss()  # close pop up
            self.parent.remove_widget(self)  # close load screen
            print(self.imagePath)
        except:
            # error occurred!!
            errorContent = Label(text='There was a problem loading your file. \n Please select a jpg file',
                                 halign='center', line_height=1.4)
            errorPopup = Popup(title="Error", content=errorContent, size_hint=(None, None), size=(700, 300))
            errorPopup.open()

        self.myPhotoArea.removeOldPhoto()
        self.resetSliders()
        self.myPhotoArea.__init__(self.imagePath)  # reset photo area with new photo

    # since sliders are the only things that are visibly changed, reset all of them when changing pictures
    # buttons don't save values
    def resetSliders(self):
        self.highlightsLevelsSlider = 0
        self.midtonesLevelsSlider = 0
        self.shadowsLevelsSlider = 0

        # empty the undo list
        self.undo = []

    # create save dialog box, and save photo at selected path
    def save(self):
        # add stuff to the popup
        self.saveContent = self.createContent()
        buttonLayout = BoxLayout(size_hint_y=(1, .1), height=60)
        cancelButton = Button(text='Cancel')
        fileSaveButton = Button(text="Save")
        buttonLayout.add_widget(cancelButton)
        buttonLayout.add_widget(fileSaveButton)
        self.saveContent.add_widget(buttonLayout)
        # create popup
        self.savePopup = Popup(title="Save file", content=self.saveContent,
                               size_hint=(1, 1))
        cancelButton.bind(on_release=self.savePopup.dismiss)
        fileSaveButton.bind(on_release=lambda x: self.saveCallBack())
        # open popup
        self.savePopup.open()

    # handle unwanted user input and if all correct, save file
    def saveCallBack(self):
        fileName = self.pathTextBox.text
        if not self.noErrors(fileName): return # check for entry errors
        # get save directory
        dir = self.getDir()

        # try to get full file path and close save dialog
        try:
            self.saveImagePath = dir + "/" + fileName
            if len(self.saveImagePath) > 4 and self.saveImagePath[-4:].upper() == "JPEG":
                self.saveImagePath = self.saveImagePath[:-4] + 'jpg'
            if 'JPG' not in self.saveImagePath.upper():  # add .jpg ext if needed
                self.saveImagePath += ".jpg"
            print(self.saveImagePath)
        except:  # error
            errorContent = Label(text='There was a problem saving your file. \n Error: ' + str(sys.exc_info()[0]),
                                 halign='center', line_height=1.4)
            self.openErrorDialog(errorContent)

        saveVal = self.myPhotoArea.saveImage(self.saveImagePath)
        if saveVal != 1: # error in saving
            errorContent = Label(text='There was a problem saving your image. \n Error: ' + str(saveVal) + "\n \n"
                                    + "Please try again", halign='center', line_height=1.4)
            self.openErrorDialog(errorContent)
        self.savePopup.dismiss()  # all's good, close dialog

    def noErrors(self, fileName):
        # user didn't input filename
        if fileName == '':
            errorContent = Label(text="Please enter a file name", halign='center', line_height=1.4)
            self.openErrorDialog(errorContent)
            return False
        # invalid characters in filename
        for char in [":", ",", "\\"]:
            if char in fileName:
                errorContent = Label(text=char + "is not a valid filename character", halign='center', line_height=1.4)
                self.openErrorDialog(errorContent)
                return False
        # wrong file type
        if fileName.find('.') != -1:
            index = fileName.find('.')
            ext = fileName[index + 1:]
            if ext.upper() not in ["JPEG", "JPG"]:
                errorContent = Label(text="File extensions must be .jpg or .jpeg. \n Please change it to an accepted "
                                "file \n extention or remove it from the file name", halign='center', line_height=1.4)
                self.openErrorDialog(errorContent)
                return False
        return True

    # determine if file or directory selected
    def getDir(self):
        if self.saveFileChooser.selection == []:
            dir = self.saveFileChooser.path  # file selected: save in current directory
        else:
            dir = self.saveFileChooser.selection[0]  # directory selected: save here

        if os.path.isfile(dir):  # delete selected file name from path
            reversedDir = dir[::-1]  # temporarily reverse path
            i = reversedDir.find("/")  # find last instance of /
            if i != -1:
                dir = reversedDir[i + 1:]  # remove unwanted selected file
                dir = dir[::-1]  # reverse it back
        return dir

    # create popup contents
    def createContent(self):
        # main layouts
        mainLayout = FloatLayout()
        layout = GridLayout(rows=2)

        # sub layouts and create stuff
        pathLayout = GridLayout(cols=2, size_hint=(None, None))
        pathLayout.add_widget(Label(text="Save as:", size_hint_x=None, width=400))
        self.pathTextBox = TextInput(multiline=False, padding_y=[20, 0], cursor_blink=True, size_hint_y=.5)
        self.saveFileChooser = FileChooserIconView(dirselect=True)

        # add stuff
        pathLayout.add_widget(self.pathTextBox)
        layout.add_widget(pathLayout)
        layout.add_widget(self.saveFileChooser)
        mainLayout.add_widget(layout)

        return mainLayout

    # create error dialog box with specified message
    def openErrorDialog(self, errorContent):
        errorPopup = Popup(title="Error", content=errorContent, size_hint=(None, None), size=(800, 400))
        errorPopup.open()

    # add levels tools to levels TopBar
    def createLevelsToolBar(self):
        self.lastHighlight = 0
        self.lastMidtone = 0
        self.lastShadow = 0

        self.autoLevels = Button(text="Random Levels")
        self.add_widget(self.autoLevels)
        self.autoLevels.bind(on_release=lambda x: self.changeLevels())

        # create highlights slider and label
        highlightsLayOut = BoxLayout(orientation="vertical")
        self.highlightsLevelsSlider = Slider(min=-1, max=1, value=0, step=.1)
        highlightsLayOut.add_widget(Label(text="Highlights"))
        highlightsLayOut.add_widget(self.highlightsLevelsSlider)
        self.highlightsLevelsLabel = Label(text=str(0), size_hint_x=None)

        self.highlightsLevelsSlider.bind(value=lambda x,y: self.changeLevels(key="H"))
        self.add_widget(highlightsLayOut)
        self.add_widget(self.highlightsLevelsLabel)

        # create midtones slider and label
        midtonesLayout = BoxLayout(orientation="vertical")
        self.midtonesLevelsSlider = Slider(min=-1, max=1, value=0,step=.1)
        midtonesLayout.add_widget(Label(text="Midtones"))
        self.midtonesLevelsLabel = Label(text=str(0), size_hint_x=None)
        midtonesLayout.add_widget(self.midtonesLevelsSlider)

        self.midtonesLevelsSlider.bind(value=lambda x,y: self.changeLevels(key="M"))
        self.add_widget(midtonesLayout)
        self.add_widget(self.midtonesLevelsLabel)

        # create shadows slider and label
        shadowsLevelsLayout = BoxLayout(orientation='vertical')
        self.shadowsLevelsSlider = Slider(min=-1, max=1, value=0,step=.1)
        self.shadowsLevelsLabel = Label(text=str(0), size_hint_x=None)
        shadowsLevelsLayout.add_widget(Label(text="Shadows"))
        shadowsLevelsLayout.add_widget(self.shadowsLevelsSlider)

        self.shadowsLevelsSlider.bind(value=lambda x,y: self.changeLevels(key="S"))
        self.add_widget(shadowsLevelsLayout)
        self.add_widget(self.shadowsLevelsLabel)

    def resetLevelsSliders(self):
        self.highlightsLevelsSlider.value = 0
        self.midtonesLevelsSlider.value = 0
        self.shadowsLevelsSlider.value = 0

    # create threshold bar
    def createThresholdToolBar(self):
        # create random button
        self.lastThreshold = -1
        self.threshold = Button(text="Random Threshold")
        self.add_widget(self.threshold)
        self.threshold.bind(on_release=lambda x: self.changeThreshold())
        # create threshold input
        thresholdLayout = AnchorLayout(size_hint_x=None, anchor_x="left")
        self.thresholdValue = TextInput(text="0.5", multiline=False, size_hint=(.7, .5), cursor_blink=True)
        thresholdLayout.add_widget(self.thresholdValue)
        self.add_widget(Label(text="Input Threshold Value"))
        self.add_widget(thresholdLayout)
        submitButton = Button(text="Submit", size_hint_x=.4)
        submitButton.bind(on_release=lambda x: self.changeThreshold(key='T'))
        self.add_widget(submitButton)
        self.add_widget(Label(size_hint_x=.2))
        self.add_widget(Label())

    # create dots illusion popup and bind
    def dotsIll(self):
        popupContent = self.dotsIllPopupContent()
        self.dotsIllPopup = Popup(title="Enter Optical Illusion Values", content=popupContent,
                                      size_hint=(None,None), size=(800, 800))
        self.cancelButton.bind(on_release=self.dotsIllPopup.dismiss)
        self.createButton.bind(on_press=self.dotsIllPopup.dismiss, on_release=lambda x: self.dotIllusion())
        self.dotsIllPopup.open()

    def dotsIllPopupContent(self):
        myBoxLayout = BoxLayout(orientation='vertical')
        layout1 = GridLayout(cols=2)
        layout2 = GridLayout(cols=2)
        layout3 = GridLayout(cols=1, size_hint_y=None, height=450)
        layout4 = BoxLayout(orientation='horizontal')

        dotDensityLabel = Label(text="Dot Density")
        self.dotDensityValue = TextInput(text='30', multiline=False, padding_y=[20, 0], cursor_blink=True)

        illusionIntensityLabel = Label(text="Illusion Intensity")
        self.illusionIntensityValue = TextInput(text='40', multiline=False, padding_y=[20, 0], cursor_blink=True)

        colorLabel = Label(text="Color")
        # change to kivy ui color selector
        colorTextLayout = GridLayout(cols=3, spacing=[15,0])
        self.colorValueR = TextInput(text='0', multiline=False, padding_y=[20, 0], cursor_blink=True)
        self.colorValueG = TextInput(text='0', multiline=False, padding_y=[20, 0], cursor_blink=True)
        self.colorValueB = TextInput(text='0', multiline=False, padding_y=[20, 0], cursor_blink=True)
        colorTextLayout.add_widget(self.colorValueR)
        colorTextLayout.add_widget(self.colorValueG)
        colorTextLayout.add_widget(self.colorValueB)

        self.cancelButton = Button(text="Cancel")
        self.createButton = Button(text="Create")

        layout1.add_widget(dotDensityLabel)
        layout1.add_widget(self.dotDensityValue)

        layout2.add_widget(illusionIntensityLabel)
        layout2.add_widget(self.illusionIntensityValue)

        self.clrPicker = ColorPicker(color=(0,0,0,1))
        layout3.add_widget(self.clrPicker)

        layout4.add_widget(self.cancelButton)
        layout4.add_widget(self.createButton)

        myBoxLayout.add_widget(layout1)
        myBoxLayout.add_widget(layout2)
        myBoxLayout.add_widget(layout3)
        myBoxLayout.add_widget(layout4)

        return myBoxLayout

    # abstract tool bar
    def createAbstractButtons(self):
        # create buttons
        self.spacing = [30,10]
        opticalIllusion = Button(text="Optical Dots Illusion")
        polarize = Button(text="Polarize")
        distanfy = Button(text="Distanfy")
        ghostColor = Button(text="Ghost Color")
        pointillism = Button(text="Pointillism")

        # bind to correct functions
        opticalIllusion.bind(on_release=lambda x: self.dotsIll())
        polarize.bind(on_release=lambda x: self.myPhotoArea.polarize())
        distanfy.bind(on_release=lambda x: self.myPhotoArea.distanfy())
        ghostColor.bind(on_release=lambda x: self.myPhotoArea.negative())
        pointillism.bind(on_release=lambda x: self.myPhotoArea.pointillism())

        # add to tool bar
        self.add_widget(opticalIllusion)
        self.add_widget(polarize)
        self.add_widget(distanfy)
        self.add_widget(ghostColor)
        self.add_widget(pointillism)

    # get values and change the photo levels
    def changeLevels(self, key="R"):
        highlight = 0
        midtone = 0
        shadow = 0
        # random button
        if key == "R":
            highlight = random.uniform(-.75, .75)
            midtone = random.uniform(-.75, .75)
            shadow = random.uniform(-.75, .75)
        # highlights slider
        elif key == "H":
            if self.highlightsLevelsSlider == self.lastHighlight: pass
            highlight = .1 if (self.highlightsLevelsSlider.value - self.lastHighlight) > 0 else - .1
            self.lastHighlight = self.highlightsLevelsSlider.value
            self.highlightsLevelsLabel.text = str(round(self.highlightsLevelsSlider.value, 1))
        # midtones slider
        elif key == "M":
            midtone = .1 if (self.midtonesLevelsSlider.value - self.lastMidtone) > 0 else - .1
            self.lastMidtone = self.midtonesLevelsSlider.value
            self.midtonesLevelsLabel.text = str(round(self.midtonesLevelsSlider.value, 1))
        # shadow slider
        elif key == "S":
            shadow = .1 if (self.shadowsLevelsSlider.value - self.lastShadow) > 0 else - .1
            self.lastShadow = self.shadowsLevelsSlider.value
            self.shadowsLevelsLabel.text = str(round(self.shadowsLevelsSlider.value, 1))
        self.myPhotoArea.levels(highlight, midtone, shadow)

    # change brightness
    def brightnessCallback(self,brightnessValue):
        self.myPhotoArea.brightness(brightnessValue)

    # change image to threshold
    def changeThreshold(self, key="R"):
        value = .5
        # random button
        if key == "R":
            value = random.uniform(.25, .75)
        # text input
        elif key == "T":
            try:
                value = float(self.thresholdValue.text)
            except:
                content = Label(text="Please enter a number between 0 and 1")
                self.openErrorDialog(content)
                return
        self.myPhotoArea.threshold(value)

    # get values and verify valid for dot illusion
    def dotIllusion(self):
        max = 255
        try: # check for valid inputs
            dotDen = int(self.dotDensityValue.text)
            assert (dotDen != 0)
            intes = int(self.illusionIntensityValue.text)
            assert (intes != 0)
            color = (int(self.clrPicker.color[0] * max), int(self.clrPicker.color[1]) * max, int(self.clrPicker.color[2] * max))
        except:
            errorContent = Label(text='One or more of your inputs was incorrect \n Verify that all inputs '
                                      'are numbers greater than 0', halign='center', line_height=1.4)
            errorPopup = Popup(title="Error", content=errorContent, size_hint=(None,None), size=(700, 300))
            errorPopup.open() # invalid input dialog box
        try:
            self.myPhotoArea.dotIllusion(dotDen, intes, color)
        except:
            print("dot illusion failed")

##################################################

        ##### Change Image #####

##################################################

# photoArea holds and displays image
class photoArea(Scatter):
    # init values
    def __init__(self, imagePath, **kwargs):
        super(photoArea, self).__init__(**kwargs)
        self.undo = []
        self.redo = []
        self.lastChange = -1
        self.currChange = -1
        self.filePath = imagePath
        self.displayImage = None
        self.pilImage = Image.open(self.filePath)
        # issues with differences between kivy object and pil requires flipping the image to start
        self.pilImage = self.pilImage.transpose(Image.FLIP_TOP_BOTTOM)
        self.auto_bring_to_front = False
        self.do_rotation = False
        # don't scale the picture too big or too small
        self.scale_max = 8
        self.scale_min = .2
        self.clickState = None
        self.cropState = False
        self.cropStart = (0,0)
        self.cropEnd = (100,100)
        try:
            self.display(None)
        except:
            errorContent = Label(text="Sorry that image appears to be corrupt \n Please select another")
            errorPopup = Popup(title="Error", content=errorContent, size_hint=(None,None), size=(700, 300))
            errorPopup.open()
        # basic pixel data
        self.maxDepth = 256
        self.black = (0, 0, 0)
        self.white = (256, 256, 256)
        self.lastSize = self.displayImage.size
        self.lastPos = self.displayImage.pos
        # display the initial picture
        # keep a copy of the original for easy resetting
        self.origImage = copy.copy(self.pilImage)
        self.oldPil = copy.copy(self.pilImage)

    # called every time the mouse is clicked down (or touch on touch screen)
    def on_touch_down(self, touch):
        super(photoArea, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            # selective bw state
            if self.clickState == "sBW":
                self.pixelLocation()
            # crop click one
            elif not self.cropState and self.clickState == "crop":
                self.cropStart = self.pixelLocation('cropStart')
                self.cropState = True
            # crop click 2
            elif self.cropState and self.clickState == "crop":
                self.cropEnd = self.pixelLocation('cropEnd')
                if self.cropState == False: return # don't continue if it was a click out of bounds
                self.crop()
                self.cropState = False
                self.clickState = None

    # undo last action
    def undoChanges(self):
        if len(self.undo) > 0:
            self.lastChange = -1
            self.remove_widget(self.displayImage)
            new = self.undo.pop()
            self.redo.append((self.displayImage, self.pilImage, new[2]))
            self.displayImage = copy.copy(new[0])
            self.pilImage = copy.copy(new[1])
            self.add_widget(self.displayImage)
            return new[2]

    # start over
    def reset(self):
        self.pilImage = copy.copy(self.origImage)
        self.undo = []
        self.display("reset")

    # redo last undo
    def redoChanges(self):
        if len(self.redo) > 0:
            self.remove_widget(self.displayImage)
            new = self.redo.pop()
            self.undo.append((self.displayImage,self.pilImage,new[2]))
            self.displayImage = new[0]
            self.pilImage = new[1]
            self.add_widget(self.displayImage)

    # bw adjustment
    def BW(self, r, g, b):
        self.redo = []
        self.currChange = 0
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        for i in range(self.width):
            for j in range(self.height):
                (red, green, blue) = self.pixels[i, j]
                total = red * r + green * g + blue * b
                avg = int(total // 3)
                self.pixels[i, j] = (avg, avg, avg)
        self.display("BW")

    # brightness adjustment
    def brightness(self, scale):
        self.redo = []
        self.currChange = 1
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        for i in range(self.width):
            for j in range(self.height):
                (red, green, blue) = self.pixels[i, j]
                self.pixels[i, j] = (int(red * scale), int(green * scale), int(blue * scale))
        self.display("brightness")

    # threshold adjustment
    def threshold(self,threshold):
        self.redo = []
        self.currChange = 2
        self.oldPil = copy.copy(self.pilImage)

        thresholdCutoff = self.maxDepth * 3 * threshold # get cutoff
        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        for i in range(self.width):
            for j in range(self.height):
                total = sum(self.pixels[i, j])
                if total < thresholdCutoff:
                    self.pixels[i, j] = self.black
                else:
                    self.pixels[i, j] = self.white
        self.display("threshold")

    # levels adjustment
    def levels(self, highlights, midtones, shadows):
        self.redo = []
        self.currChange = 3
        self.oldPil = copy.copy(self.pilImage)

        highlightScale = highlights + 1
        midtoneScale = midtones + 1
        shadowScale = shadows + 1
        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        for i in range(self.width):
            for j in range(self.height):
                (red, green, blue) = self.pixels[i, j]
                total = red + green + blue
                # separate channels
                if total < self.maxDepth // 3:  # shadows
                    self.pixels[i, j] = (int(red * shadowScale), int(green * shadowScale), int(blue * shadowScale))
                elif total < 2 * self.maxDepth // 3:  # midtones
                    self.pixels[i, j] = (
                    int(red * midtoneScale), int(green * midtoneScale), int(blue * midtoneScale))
                else:  # highlights
                    self.pixels[i, j] = (
                        int(red * highlightScale), int(green * highlightScale), int(blue * highlightScale))
        self.display("levels")

    # create dots illusion
    def dotIllusion(self, dotDensity, intesity, color):
        self.redo = []
        self.currChange = 4
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        new = Image.new("RGB", self.pilImage.size, (255, 255, 255))
        draw = ImageDraw.Draw(new) # create draw image
        step = self.width // dotDensity
        totalPix = step ** 2
        mar = 2
        # iterate through width, height by step. (Creates dot map)
        for row in range(0, self.height + 1, step):
            for col in range(0, self.width + 1, step):
                blacks = 0
                # calculate the proportion of black to white pixels
                for j in range((row - step // 2) % self.height, (row + step // 2) % self.height):
                    for i in range((col - step // 2) % self.width, (col + step // 2) % self.width):
                        if self.pixels[i, j] == (0, 0, 0): blacks += 1  # black pixel
                # use proportion to calculate dot size
                dotRadius = (((step*(intesity-mar))/intesity+(step*mar/intesity)*(blacks/totalPix))/2.1)
                x0, x1, y0, y1 = col - dotRadius, col + dotRadius, row - dotRadius, row + dotRadius
                draw.ellipse([x0, y0, x1, y1], fill=color)  # draw dot on new image
        self.pilImage = copy.copy(new)
        self.display("DIll")

    # with reference to Tim's optional lecture
    # change coordinate from rectagular to polar
    def polarize(self):
        self.redo = []
        self.currChange = 5
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        self.newSize = min(self.height, self.width)
        new = Image.new("RGB", (self.newSize, self.newSize))
        newPixels = new.load()
        # switch vals
        for i in range(self.newSize):
            for j in range(self.newSize):
                (iRef, jRef) = self.getPolarCoords(i, j)
                newPixels[i, j] = self.pixels[iRef, jRef]

        self.pilImage = copy.copy(new)
        self.display("Polarize")

    # convert the coordinate
    def getPolarCoords(self,i,j):
        halfSize = self.newSize / 2
        radius = (halfSize ** 2 + halfSize ** 2) ** 0.5
        currRad = ((i - halfSize) ** 2 + (j - halfSize) ** 2) ** .5
        # get vals
        fullAngle = math.pi * 2
        currAngle = math.atan2(halfSize - i, halfSize - j) % fullAngle
        # get old location
        iRef = int((self.width - 1) * currAngle / fullAngle)
        jRef = int((self.height - 1) * (1 - currRad / radius))

        return iRef, jRef

    # distort and make pic look further away
    def distanfy(self):
        self.redo = []
        self.currChange = 6
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        new = Image.new("RGB", (self.width, self.height))
        newPixels = new.load()

        # convert to polar
        for ypix in range(self.height):
            for xpix in range(self.width):
                # get from 0 to 1
                yNormalized = ((2*ypix) / self.height) -1
                xNormalized = ((2*xpix) / self.width) -1
                radius = math.sqrt((yNormalized**2 + xNormalized**2))
                if radius >= 0 and radius <= 1:
                    newRadius = math.sqrt(1 - radius * radius)
                    newRadius = (radius + (1 - newRadius)) / 2
                    if newRadius <= 1:
                        angle = math.atan2(yNormalized,xNormalized)
                        newNormalizedX = newRadius * math.cos(angle)
                        newNormalizedY = newRadius * math.sin(angle)
                        newX = int(((newNormalizedX+1)*self.width)/2)
                        newY = int(((newNormalizedY+1)*self.height)/2)
                        newPixels[newX, newY] = self.pixels[xpix, ypix]

        self.pilImage = copy.copy(new)
        self.display("distanfy")

    # speed up box blur by capitalizing on exiting motion (horizontal) and vertical blur
    def boxBlur(self,factor, currChange=7):
        self.redo = []
        self.currChange = currChange
        self.motionBlur(factor, self.currChange)
        self.verticalBlur(factor, self.currChange)

    def motionBlur(self,factor,currChange=8):
        self.redo = []
        self.currChange = currChange
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        new = Image.new("RGB", (self.width, self.height))
        newPixels = new.load()

        for i in range(self.width):
            for j in range(self.height):
                colorTotal = self.pixels[i, j]
                num = 1
                for iFact in range(i - factor, i + factor):
                    if iFact > 0 and iFact < self.width:
                        colorTotal = tuple([colorTotal[color] + self.pixels[iFact, j][color] for color in range(3)])
                        num += 1
                newPixels[i, j] = tuple([colorTotal[color] // num for color in range(3)])

        self.pilImage = copy.copy(new)
        self.display("vertical")

    # blur image vertically
    def verticalBlur(self,factor,currChange=9):
        self.redo = []
        self.currChange = currChange
        self.oldPil = copy.copy(self.pilImage)

        # create new
        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        new = Image.new("RGB", (self.width, self.height))
        newPixels = new.load()

        for i in range(self.width):
            for j in range(self.height):
                colorTotal = self.pixels[i,j]
                num = 1
                for jFact in range(j-factor, j+factor): # vertical neighbors
                    if jFact > 0 and jFact < self.height:
                        colorTotal = tuple([colorTotal[pix] + self.pixels[i, jFact][pix] for pix in range(3)])
                        num += 1
                newPixels[i, j] = tuple([colorTotal[pix] // num for pix in range(3)])

        self.pilImage = copy.copy(new)
        self.display("vertical")

    # add high contrast to BW
    def contrastBW(self):
        self.redo = []
        self.currChange = 11
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        for i in range(self.width):
            for j in range(self.height):
                (red, green, blue) = self.pixels[i, j]
                total = red + green + blue
                avg = int(total // 3)
                # create greater difference
                if avg < self.maxDepth//2:
                    avg -= 50 # lower
                elif avg > self.maxDepth//2:
                    avg += 50 # increase
                if avg > self.maxDepth:
                    avg = self.maxDepth
                elif avg < 0:
                    avg = 0 # correct vals
                self.pixels[i, j] = (avg, avg, avg)
        self.display("BWContrast")

    # blur only select part of image
    def selectiveBlackWhite(self,perX,perY):
        self.redo = []
        self.currChange = 12
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        xPix,yPix = round(perX * self.width,1), round(perY * self.height,1)  # nearest pixel to clicked location
        rtarget, gtarget, btarget = self.pixels[xPix, yPix]
        factor = 80

        new = Image.new("RGB", (self.width, self.height))
        newPixels = new.load()

        for i in range(self.width):
            for j in range(self.height):
                (red, green, blue) = self.pixels[i, j]
                if (red > rtarget - factor and red < rtarget + factor and green > gtarget - factor and
                            green < gtarget + factor and blue > btarget - factor and blue < btarget + factor):
                    continue
                total = red + green + blue
                avg = int(total // 3)
                self.pixels[i, j] = (avg, avg, avg)

        self.display("selective")

    # crop image
    def crop(self):
        print("called crop")
        self.redo = []
        self.currChange = 13
        self.oldPil = copy.copy(self.pilImage)
        # convert vals
        perX,perY = self.cropStart
        perXEnd, perYEnd = self.cropEnd
        self.width, self.height = self.pilImage.size
        xPixStart, yPixStart = round(perX * self.width, 1), round(perY * self.height, 1)
        xPixEnd, yPixEnd = round(perXEnd * self.width, 1), round(perYEnd * self.height, 1)
        print(xPixStart,yPixStart,xPixEnd,yPixEnd)
        # get crop locations
        left = min(xPixStart, xPixEnd)
        upper = min(yPixStart, yPixEnd)
        right = max(xPixStart, xPixEnd)
        lower = max(yPixStart, yPixEnd)
        # crop
        self.pilImage = copy.copy(self.pilImage.crop((left,upper,right,lower)))

        self.pilImage.load()
        self.display('crop')

    # invert image
    def negative(self):
        self.redo = []
        self.currChange = 14
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size

        for i in range(self.width):
            for j in range(self.height):
                r,g,b = self.pixels[i,j]
                self.pixels[i,j] = (self.maxDepth - r, self.maxDepth - g, self. maxDepth -b)

        self.display("negative")

    # convert to pointillism
    def pointillism(self):
        self.redo = []
        self.currChange = 14
        self.oldPil = copy.copy(self.pilImage)

        self.pixels = self.pilImage.load()
        self.width, self.height = self.pilImage.size
        new = copy.copy(self.pilImage) # use orginal as background
        draw = ImageDraw.Draw(new)
        newPixels = new.load()
        val = self.width * self.height / 30
        radius = int(self.width/80)

        # get random pixel location and draw a dot
        for dot in range(int(val)):
            x = random.randint(0,self.width-1)
            y = random.randint(0,self.height-1)
            r,g,b = self.pixels[x,y]
            x0, x1 = x - radius, x + radius
            y0, y1 = y - radius, y + radius
            draw.ellipse([x0,y0,x1,y1],(r,g,b))
        self.pilImage = copy.copy(new)

        self.display("point")

    # get click location relative to image
    def pixelLocation(self,state=""):
        print("called", state)
        click = Window.mouse_pos[0] * 2, Window.mouse_pos[1] * 2  # weird kivy bug only returns half the correct value
        left, right = self.displayImage.x, self.displayImage.right
        top, bottom = self.displayImage.top, self.displayImage.y
        if right == 100: # correct for what seems to be another weird kivy bug
            left, right = self.lastPos[0], self.lastPos[0] + self.lastSize[0]
            top, bottom = self.lastPos[1] + self.lastSize[1], self.lastPos[1]
        else:
            self.lastPos, self.lastSize = self.displayImage.pos, self.displayImage.size
        def inBounds(click): # check if click in image
            print(left,click[0],right)
            if click[0] > left and click[0] < right and click[1] > bottom and click[1] < top:
                return True
            else: # don't do anything
                self.clickState = None
                self.cropState = False
                self.cropStart = (0,0)
                self.cropEnd = (100,100)
                return False
        if inBounds(click): # do stuff
            x,y = click[0]-left, click[1]-bottom  # relative to image
            perX, perY = x/(right-left), y/(top-bottom)
            if self.clickState == "sBW":  # selective BW
                self.selectiveBlackWhite(perX, perY)
            elif state == "cropStart":
                return (perX,perY)
            elif state == "cropEnd":
                return (perX,perY)
        self.clickState = None

    # display kivy image from pil image
    def display(self,action):
        # deal with undoing and redoing stuff
        if self.currChange != self.lastChange:
            self.undo.append((self.displayImage, self.oldPil, action))
            self.lastChange = self.currChange
            if len(self.undo) == 10:
                self.undo.pop(0)

        # actual display stuff
        imgDatalst = list(self._img_read(self.pilImage))
        imgData = imgDatalst[0]
        imgData.flip_vertical = False
        myTex = Texture.create_from_data(imgData) # get a texture from image data type
        if self.displayImage is not None:
            self.remove_widget(self.displayImage)
        ratio = self.pilImage.size[1]/self.pilImage.size[0]
        width = 1000
        self.displayImage = Im(texture=myTex, allow_stretch=True, size_hint=(None,None),
                               width=width, height=width*ratio)
        self.displayImage.center = (Window.size[0] // 2, Window.size[1] // 2)
        self.add_widget(self.displayImage)

    # taken and modified from kivy "work in progress" module to convert PIL image to kivy image
    # original API opened an ImageData object from a filepath
    # Extracted it from the coverage of the API in order to open an ImageData object from a PIlImage object
    # https://kivy.org/build/coverage/kivy_core_image_img_pil.html
    def _img_read(self, im):
        im.seek(0)
        try:
            img_ol = None
            while True:
                img_tmp = im
                if img_ol and (hasattr(im, 'dispose') and not im.dispose):
                    img_ol.paste(img_tmp, (0, 0), img_tmp)
                    img_tmp = img_ol
                img_ol = img_tmp
                yield ImageData(img_tmp.size[0], img_tmp.size[1],
                                img_tmp.mode.lower(), img_tmp.tobytes())
                im.seek(im.tell() + 1)
        except EOFError:
            pass

    # save image
    def saveImage(self,filePath):
        try:
            # issues with differences between kivy object and pil requires flipping the image back
            saveVersion = self.pilImage.transpose(Image.FLIP_TOP_BOTTOM)
            saveVersion.save(filePath)
            return 1  # success!
        except:
            return sys.exc_info()[0]  # something went wrong!

    # get rid of old pic
    def removeOldPhoto(self):
        self.remove_widget(self.displayImage)


##################################################

        ##### Init App #####

##################################################

class TermProject(App):
    def __init__(self,**kwargs):
        super(TermProject, self).__init__(**kwargs)
        self.image = None
        self.imagePath = None
        self.photoLoaded = False
        self.tempFileName = "tempFile.png"

    def build(self):
        # create things
        self.canvas = FloatLayout()
        self.loadScreen = photoLoadScreen()

        self.background = BoxLayout(size=Window.size)
        self.background.bind(size=self.windowSize)
        print(self.background.size)
        with self.background.canvas: # init background
            Color(.075, .075, .075)
            self.rect = Rectangle(size=self.background.size)
        self.canvas.add_widget(self.background)

        # uncomment this out later
        self.photoTrigger = Clock.create_trigger(self.getPhotoPath)
        self.canvas.bind(children=self.photoTrigger)
        # add widgets to canvas
        self.canvas.add_widget(self.loadScreen)

        return self.canvas

    def windowSize(self, *args):
        print(Window.size)
        self.background.size=Window.size
        self.rect.size = Window.size

    # get path of selected photo
    def getPhotoPath(self,*args):
        if not self.photoLoaded and self.loadScreen.photoPath() is not None: # check state
            self.imagePath = self.loadScreen.photoPath() # load path
            # create things
            self.myPhotoArea = photoArea(self.imagePath)
            self.topBars = self.createTopBars()
            self.tools = ToolBar(self.topBars, size_hint=(.1, .9), pos_hint={'x': 0, 'y': 0})
            self.canvas.add_widget(self.myPhotoArea)
            self.canvas.add_widget(self.tools)
            self.photoLoaded = True # change state
            print("loaded")

    # create all the possible TopBars
    def createTopBars(self):
        topBarDict = dict()
        numBars = 7
        for bar in range(numBars):
            topBarName = "TopBar" + str(bar)
            topBarDict[topBarName] = TopBar(bar, self.myPhotoArea, size_hint=(1, .1), pos_hint={'x': 0, 'y': .9})
        return topBarDict

TermProject().run()
