import kivy

# this restrict the kivy version i.e
# below this kivy version you cannot
# use the app or software
kivy.require("1.9.1")

# base Class of your App inherits from the App class.
# app:always refers to the instance of your application
from kivy.app import App

# For features
import tabsclass
import pandas as pd
import numpy as np
from kivy.uix.popup import Popup
import csv
import os
from os.path import sep, expanduser, isdir, dirname
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.graphics import Rectangle
from kivy.graphics import Line
from kivy.graphics import Ellipse
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from functools import partial # to be able to load arguments in Clock
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition, SlideTransition
from kivy.app import App
import pygame
import math

# to change the kivy default settings we use this module config
from kivy.config import Config

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)

# Creating Screen Manager class to manage two screens
class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)
    screen_three = ObjectProperty(None)
    popup_window = ObjectProperty(None)

# Screen one class will be responsible for taking all input from user
class ScreenOne(Screen):
    filename = ObjectProperty()
    mainScale = ObjectProperty()
    secondScale = ObjectProperty()
    secondScaleCheckBox = ObjectProperty()
    stepBasedToggle = ObjectProperty()
    scaleBasedToggle = ObjectProperty()
    reverseScaleCheckBox = ObjectProperty()

# Screen two will display the notes being played
class ScreenTwo(Screen):

    startTime = ObjectProperty()
    endTime = ObjectProperty()
    tempo = ObjectProperty()
    # Other variables available under screen two
    # timeBar
    # playbutton
    # noteButtons
    # backbutton
    # pausebutton
    # loopbutton

    # On entering the screen we are loading everything from the main screen
    def on_enter(self, *args):

        self._checkMainScreenInput()
        self._displayNoteButtons()
        self._loadmainMIDI()

    def _checkMainScreenInput(self):

        # Initalizing to avoid errors in case these options were not selected
        self.playbutton.state = 'normal'
        self.loopbutton.state = 'normal'
        self.secondScale = None
        self.conversionType = None
        self.formatError = False
        self.allOnScheduled = []
        self.allOffScheduled = []
        self.currentTime = 0

        # Loading the main scale and check if it is in the expected Scale class format
        # Goes back to main screen if input is in an invalid format
        mainScaleInput = self.readScaleCSV(App.get_running_app().root.ids.screen_one.mainScale.path)

        try:
            self.mainScale = tabsclass.Scale(mainScaleInput)
            self.scaleToDisplay = self.mainScale
        except:
            print('Format of main scale is wrong... please use commas between notes without space')
            self.formatError = True
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

        # Checking if user requested to convert to another scale. If box is ticked read second scale
        self.secondScaleCheckBox = App.get_running_app().root.ids.screen_one.secondScaleCheckBox.state
        self.reverseScaleCheckBox = App.get_running_app().root.ids.screen_one.reverseScaleCheckBox.state

        if(self.secondScaleCheckBox == 'down'):

            secondScaleInput = self.readScaleCSV(App.get_running_app().root.ids.screen_one.secondScale.path)
            try:
                self.secondScale = tabsclass.Scale(secondScaleInput)
            except:
                print('Format of second scale is wrong... please use commas between notes without space')
                App.get_running_app().root.ids.screen_manager.current = 'screen1'
                self.formatError = True

            # Overwrites main scale to display in second screen
            self.scaleToDisplay = self.secondScale

            # Check which type of conversion does user want. Default is step based unless user chooses scale based
            scaleToggleState = App.get_running_app().root.ids.screen_one.scaleBasedToggle.state
            if(scaleToggleState == 'down'):
                self.conversionType = 'scaleConversion'
            else:
                self.conversionType = 'stepConversion'

        if(self.secondScale == None):
            self.usedScale = self.mainScale
        else:
            self.usedScale = self.secondScale

    def _displayNoteButtons(self):
        # Does not display anything in second screen if main scale was not entered correctly
        if(not self.formatError):
            # Fixed positions for FloatLayout (NEEDS WORK)
            if(self.reverseScaleCheckBox == 'down'):
                self.posOrd = [0,1,3,2,5,4,7,6,8]
            else:
                self.posOrd = [0,1,2,3,4,5,6,7,8]

            xpos = [0.45, 0.45, 0.2, 0.7, 0.1, 0.8, 0.2, 0.7, 0.45]
            ypos = [0.55, 0.25, 0.3, 0.3, 0.55, 0.55, 0.8, 0.8, 0.85]

            # Creating the notes as button and storing them in dictionary to be referenced later
            self.noteDict = {}
            for i, note in enumerate(self.scaleToDisplay.notes):
                btn = NoteButton(text= str(i+1)+'\n'+note, halign='center', bold=True, pos_hint={'x':xpos[self.posOrd[i]], 'y':ypos[self.posOrd[i]]})
                self.noteDict[note] = btn # Creating new dictionary to reference each button
                self.ids.noteButtons.add_widget(btn)
            # slap is always added separately (Not related to input)
            self.noteDict['slap'] = self.ids['slap']

    def _loadmainMIDI(self):

        # Loads the desired tabs from the path and create a Tabs class
        filename = App.get_running_app().root.ids.screen_one.filename
        tabsPath = filename.path
        self.fileName = filename.text
        tabsLoaded = tabsclass.Tabs(tabsPath)

        self.songTime = tabsLoaded.songTime
        print('Total time of song loaded is {}'.format(round_up(self.songTime,1)))

        # setting default times
        self.startTime.text = '0'
        self.endTime.text = str(round_up(self.songTime,1))
        self.timeBar.value = 0
        self.timeBar.max = round_up(self.songTime,1)


        # If conversion to secondary scale is desired, Tabs class is used to change to the new tabs
        if(self.conversionType == 'scaleConversion'):
            tabsLoaded = tabsLoaded.mapNewScale(self.mainScale, self.secondScale)
        elif(self.conversionType == 'stepConversion'):
            Melody, Missed, Best = tabsLoaded.applyScaleToTab(self.secondScale, True, False)
            tabsLoaded = tabsclass.Tabs(Melody[Best])


        # Comparing notes in tab and scale
        missingNotes = set(tabsLoaded.MIDIvalues) - set(self.scaleToDisplay.MIDIvalues)
        missingNotes.discard('S')
        if(len(missingNotes)>0):
            print('Cannot play melody on loaded scale...')
            print('Missing notes are {}'.format(missingNotes))
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

        # Write tempMainMIDI file in case it was converted
        tabsLoaded.writeToMIDI('MIDI/tempMain.mid', float(self.tempo.text), 1)

    def displayMIDI(self):

        # reads the MIDI file
        midiFile = tabsclass.readMIDI('MIDI/tempCut.mid', False)

        # Loops through each track and schedules each event (Note on or off) using the Clock class
        # MIDI message that have '<meta' are excluded. Format of msgs: note_event channel=# note=# velocity=# time=#
        # Event 'on' or 'off'. Note is the pitch and time is the time between each event (hence the need for cumTime)
        # track 2 is for slaps and hence notePitch is fixed as 'slap'
        # Using Scale class method 'MIDIToNote' to convert from MIDI value to Letter Note (e.g. C4)
        # 'partial' function is used to add arguments to the scheduled call from Clock
        for i, track in enumerate(midiFile.tracks):
            self.cumTime = 0

            for msg in track:
                noteAction = str(msg).split()
                if (not msg.is_meta):
                    noteStatus = noteAction[0]
                    if(i==2):
                        notePitch = 'slap'
                    else:
                        notePitch = self.usedScale.MIDIToNote[int(noteAction[2][5:])]
                    noteActionTime = noteAction[4]
                    self.cumTime += int(noteActionTime[5:])

                    # Time adjuster is used to change the tempo.
                    # 1920 seems to be equivalent to a second in MIDI time. (e.g. reading 960 in MIDI msg is 0.5 second)

                    timeAdjuster = 1920*(float(self.tempo.text)/120)

                    if (noteStatus == 'note_on'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        onEvent = Clock.schedule_once(self.noteDict[notePitch].on_press, self.cumTime / timeAdjuster)
                        self.allOnScheduled.append(onEvent)
                    elif (noteStatus == 'note_off'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        offEvent = Clock.schedule_once(self.noteDict[notePitch].on_release, (self.cumTime - 100) / timeAdjuster)
                        self.allOffScheduled.append(offEvent)

    def readScaleCSV(self, path):
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                scale = row

        return scale

class ScreenThree(Screen):

    # variables
    # ---------
    #     noteButtonsRecord
    #     recordbutton
    #     tempoRec
    #     fileToSave
    #     tabOutput

    def on_enter(self, *args):
        self._checkMainScreenInput()
        self._displayNoteButtons()

    def _checkMainScreenInput(self):

        # Initalizing to avoid errors in case these options were not selected
        self.formatError = False
        self.currentTime = 0
        self.tabOutput.text = ''

        self.reverseScaleCheckBox = App.get_running_app().root.ids.screen_one.reverseScaleCheckBox.state

        # Loading the main scale and check if it is in the expected Scale class format
        # Goes back to main screen if input is in an invalid format
        mainScaleInput = self.readScaleCSV(App.get_running_app().root.ids.screen_one.mainScale.path)
        # mainScaleInput = App.get_running_app().root.ids.screen_one.mainScale.text.split(',')

        try:
            self.mainScale = tabsclass.Scale(mainScaleInput)
            self.scaleToDisplay = self.mainScale
        except:
            print('Format of main scale is wrong... please use commas between notes without space')
            self.formatError = True
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

    def _displayNoteButtons(self):
        # Does not display anything in second screen if main scale was not entered correctly
        if (not self.formatError):
            # Fixed positions for FloatLayout (NEEDS WORK)
            if (self.reverseScaleCheckBox == 'down'):
                self.posOrd = [0, 1, 3, 2, 5, 4, 7, 6, 8]
            else:
                self.posOrd = [0, 1, 2, 3, 4, 5, 6, 7, 8]

            xpos = [0.45, 0.45, 0.2, 0.7, 0.1, 0.8, 0.2, 0.7, 0.45]
            ypos = [0.55, 0.25, 0.3, 0.3, 0.55, 0.55, 0.8, 0.8, 0.85]

            # Creating the notes as button and storing them in dictionary to be referenced later
            self.noteDict = {}
            for i, note in enumerate(self.scaleToDisplay.notes):
                btn = NoteButton(text= str(i+1)+'\n'+note, halign='center', bold=True, pos_hint={'x':xpos[self.posOrd[i]], 'y':ypos[self.posOrd[i]]})
                self.noteDict[note] = btn  # Creating new dictionary to reference each button
                self.ids.noteButtonsRecord.add_widget(btn)
            self.noteDict['slapRecord'] = self.ids['slapRecord']
            self.noteDict['blankRecord'] = self.ids['blankRecord']

    def readScaleCSV(self, path):
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                scale = row

        return scale

class BrowseWindow(BoxLayout):

    def __init__(self, title=None):
        self.title = title

        super(BoxLayout, self).__init__()

    def selected(self, filename):

        screenOne = App.get_running_app().root.ids.screen_one
        try:
            self.label.text = filename[0]

            if (self.title == 'Browse File...'):
                screenOne.filename.text = filename[0].split('/')[-1]
                screenOne.filename.path = filename[0]
            elif(self.title == 'Browse Main Scale...'):
                screenOne.mainScale.text = filename[0].split('/')[-1]
                screenOne.mainScale.path = filename[0]
            elif (self.title == 'Browse Second Scale...'):
                screenOne.secondScale.text = filename[0].split('/')[-1]
                screenOne.secondScale.path = filename[0]
        except:
            pass

    def dismiss_popup(self):

        try:
            if (self.title == 'Browse File...'):
                App.get_running_app().root.ids.screen_one.browseFile.popupWindow.dismiss()
            elif (self.title == 'Browse Main Scale...'):
                App.get_running_app().root.ids.screen_one.browseMainScale.popupWindow.dismiss()
            elif (self.title == 'Browse Second Scale...'):
                App.get_running_app().root.ids.screen_one.browseSecondScale.popupWindow.dismiss()
        except:
            pass

class BrowseButton(Button):

    def on_release(self):
        self.show_popup()

    def show_popup(self):
        show = BrowseWindow(self.title) # Create a new instance of the P class
        self.popupWindow = Popup(title=self.title, content=show, size_hint=(None,None),size=(1200,800))
        # Create the popup window

        self.popupWindow.open() # show the popup

####### NOT IMPLEMENTED ###########
class loadRecordButton(Button):

    def on_release(self):

        self.loadFunction()

        self.recordFunction()

    def loadFunction(self):
        pass

    def recordFunction(self):
        pass
####### END NOT IMPLEMENTED ###########

class RecordButton(ToggleButton):

    def on_release(self):
        if(self.state == 'down'):
            # Initialize recorded notes
            self.recordedNotes = []

        elif(self.state == 'normal'):

            try:
                self.recordedNotes[0] # To test if anything has been recorded
                self.recordMIDI()
            except:
                print('Nothing has been recorded')

    def recordMIDI(self):

        screenThree = App.get_running_app().root.ids.screen_three

        screenThree.tabOutput.text = ''

        numOfNotes = len(self.recordedNotes)
        numRows, notesOnLastRow = divmod(numOfNotes,16)

        header = 'o,oe,oen,oend,t,te,ten,tend,th,the,then,thend,f,fe,fen,fend'.split(',')
        newRecordedTabs = pd.DataFrame('-', index=np.arange(numRows+1*notesOnLastRow), columns=header)

        noteCounter = 0

        for r in np.arange(0, numRows+1):
            for c in np.arange(0,16):

                if (r == numRows and c == notesOnLastRow):
                    break

                if(self.recordedNotes[noteCounter] != '-'):
                        newRecordedTabs.iloc[r][c] = self.recordedNotes[noteCounter]

                noteCounter += 1

        midiPath = "userAccessFolder/MIDI/" + screenThree.fileToSave.text + '.mid'
        csvPath =  "userAccessFolder/Tabs/" + screenThree.fileToSave.text + '.csv'

        # Creating Tabs class with new tabs
        newTabsClass = tabsclass.Tabs(newRecordedTabs)

        newTabsClass.tab.to_csv(csvPath, index=False, header=False)
        newTabsClass.writeToMIDI(midiPath,int(screenThree.tempoRec.text))

# A class that can be used to load the audio for each note to be played when pressed
class NoteButton(Button):


    def on_press(self, *args):

        screenThree = App.get_running_app().root.ids.screen_three

        if(screenThree.recordbutton.state == 'down'):
            try: # to remove number associated with note
                note = self.text.split('\n')[1]
            except: # in case slap or blank (-) are pressed
                note = self.text

            print('Pressing Note {}'.format(note))
            screenThree.recordbutton.recordedNotes.append(note)
            screenThree.tabOutput.text = self.listToString(screenThree.recordbutton.recordedNotes)


        self.state = 'down'

    def listToString(self,list):

        stringToOutput = ''
        for i, entry in enumerate(list):
            if((i+1) % 16 == 0):
                stringToOutput += entry + '\n'
            else:
                stringToOutput += entry + ','



        return stringToOutput

    def on_release(self, *args):

        self.state = 'normal'

class TimeBar(Slider):

    def increment_time(self, interval):

        screenTwo = App.get_running_app().root.ids.screen_two

        screenTwo.currentTime += interval*(float(screenTwo.tempo.text)/120)
        if(screenTwo.currentTime <= screenTwo.songTime):
            screenTwo.timeBar.value = round_up(screenTwo.currentTime,1)
        else:
            screenTwo.timeBar.value = round_up(screenTwo.songTime,1)
            Clock.unschedule(screenTwo.timeBar.increment_time)
            screenTwo.playbutton.state = 'normal'

    def on_touch_down(self, touch):

        timeBarValue = str(round_up(App.get_running_app().root.ids.screen_two.ids.timeBar.value,1))
        if self.collide_point(*touch.pos):
            App.get_running_app().root.ids.screen_two.startTime.text = timeBarValue
            # App.get_running_app().root.ids.screen_two.pausebutton.on_release()
            App.get_running_app().root.ids.screen_two.playbutton.pauseButtonAction()

        return super(TimeBar, self).on_touch_down(touch)

    def on_touch_move(self, touch):

        if self.collide_point(*touch.pos):
            timeBarValue = str(round_up(App.get_running_app().root.ids.screen_two.ids.timeBar.value,1))
            App.get_running_app().root.ids.screen_two.startTime.text = timeBarValue

        return super(TimeBar, self).on_touch_move(touch)

    def on_touch_up(self, touch):

        timeBarValue = str(round_up(App.get_running_app().root.ids.screen_two.ids.timeBar.value,1))

        if self.collide_point(*touch.pos):
            App.get_running_app().root.ids.screen_two.startTime.text = timeBarValue

        return super(TimeBar, self).on_touch_up(touch)

class PlayButton(ToggleButton):


    def on_release(self):

        screenTwo = App.get_running_app().root.ids.screen_two

        if(self.state == 'down'):
            if(screenTwo.loopbutton.state == 'normal'):
                self.playButtonAction()
            elif(screenTwo.loopbutton.state == 'down'):
                loopTime = (float(screenTwo.endTime.text) - float(screenTwo.startTime.text))*(120/float(screenTwo.tempo.text))
                self.playButtonAction()
                self.loopEvent = Clock.schedule_interval(self.playButtonAction, loopTime)

        elif(self.state == 'normal'):

            self.pauseButtonAction()

    def playButtonAction(self, *args):

        # Make sure state is normal
        self.state = 'down'

        # Retrieve running screen two class
        screenTwo = App.get_running_app().root.ids.screen_two

        # Stop any On scheduled events in the case the play button is pressed again (Restarting music)
        # Off events are kept to turn off any notes there were on from last play
        for event in screenTwo.allOnScheduled:
            Clock.unschedule(event)

        startTime = float(screenTwo.startTime.text)
        endTime = float(screenTwo.endTime.text)
        tempo = float(screenTwo.tempo.text)

        # Constraining start and end times
        if(startTime >= screenTwo.songTime or startTime < 0):
            App.get_running_app().root.ids.screen_two.startTime.text = '0'
            startTime = 0

        if(endTime < startTime or endTime > screenTwo.songTime):
            endTime = screenTwo.songTime
            App.get_running_app().root.ids.screen_two.endTime.text = str(round_up(screenTwo.songTime,1))

        # Checking if cut required. Always stores new MIDI file called 'temp' and is played
        tabsclass.cutMIDI('MIDI/tempMain.mid','MIDI/tempCut.mid', startTime, endTime, tempo)
        print('Playing {} at a tempo of {} from {} to {}'.format(screenTwo.fileName,tempo, startTime, round_up(endTime,1)))
        screenTwo.sound = self.playMusic('MIDI/tempCut.mid')

        # Loading current time in watch.
        screenTwo.currentTime = startTime
        Clock.unschedule(screenTwo.timeBar.increment_time)
        Clock.schedule_interval(screenTwo.timeBar.increment_time, 0.1)

        # Calls function to display the notes
        screenTwo.displayMIDI()

    def playMusic(self, song):
        pygame.init()
        pygame.mixer.music.load(song)
        self.sound = pygame.mixer.music
        self.sound.play()

        return self.sound

    def pauseButtonAction(self):

        self.state = 'normal'

        screenTwo = App.get_running_app().root.ids.screen_two

        # Stoping scheduled loops
        screenTwo.loopbutton.unscheduleLoops()

        if(screenTwo.currentTime > screenTwo.songTime):
            screenTwo.currentTime = screenTwo.songTime

        screenTwo.startTime.text = str(round_up(screenTwo.currentTime,1))
        # to stop music
        self.stopMusic()

    def stopMusic(self):

        screenTwo = App.get_running_app().root.ids.screen_two

        # Stoping scheduled loops
        screenTwo.loopbutton.unscheduleLoops()

        for note, noteButton in screenTwo.noteDict.items():
            noteButton.state = 'normal'

        Clock.unschedule(screenTwo.timeBar.increment_time)
        # If play button was never pressed then no sound was loaded and no need to stop anything
        try:
            screenTwo.sound.stop()

            # Unscheduling all events to avoid re-entering screen two with different buttons (KeyError)
            allScheduled = zip(screenTwo.allOnScheduled, screenTwo.allOffScheduled)
            for OnEvent, OffEvent in allScheduled:
                Clock.unschedule(OnEvent)
                Clock.unschedule(OffEvent)
        except:
            print('Sound not loaded')

class LoopButton(ToggleButton):

    def on_release(self):

        if (self.state == 'normal'):
            self.unscheduleLoops()

    def unscheduleLoops(self):

        self.state == 'normal'
        # Incase play has not been pressed
        try:
            loopEvent = App.get_running_app().root.ids.screen_two.playbutton.loopEvent
            Clock.unschedule(loopEvent)
        except:
            pass

class RotateButton(Button):

    def on_release(self):

        self.rotateHangdrum()

    def updatePositions(self):

        currentPos = App.get_running_app().root.ids.screen_three.posOrd

        newPos = []
        for pos in currentPos:
            if(pos==0):
                newPos.append(0)
            elif(pos==1 or pos==3 or pos== 5):
                newPos.append(pos+2)
            elif(pos==4 or pos==6 or pos==8):
                newPos.append(pos-2)
            elif(pos==2):
                newPos.append(1)
            elif(pos==7):
                newPos.append(8)

        App.get_running_app().root.ids.screen_three.posOrd = newPos

        return newPos

    def rotateHangdrum(self):

        newPos = self.updatePositions()

        xpos = [0.45, 0.45, 0.2, 0.7, 0.1, 0.8, 0.2, 0.7, 0.45]
        ypos = [0.55, 0.25, 0.3, 0.3, 0.55, 0.55, 0.8, 0.8, 0.85]

        noteDict = App.get_running_app().root.ids.screen_three.noteDict

        noteCounter = 0
        for key, value in noteDict.items():
            if(noteCounter >= 9):
                break
            value.pos_hint = {'x': xpos[newPos[noteCounter]], 'y': ypos[newPos[noteCounter]]}
            noteCounter += 1

class BackButton(Button):

    def on_release(self):

        SM = App.get_running_app().root.ids.screen_manager
        if(SM.current == 'screen2'):
            App.get_running_app().root.ids.screen_two.playbutton.stopMusic()

        SM.transition = SlideTransition(direction='right')
        SM.current = 'screen1'
        SM.transition = SlideTransition(direction='left')

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

class MainLayout(StackLayout):
    pass

class graphicsApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    graphicsApp().run()
