#Widgets
#Widgets are user interface elements that you add to your program to provide some kind of functionality.
# They may or may not be visible. Examples would be a file browser, buttons, sliders, lists and so on.
# Widgets receive MotionEvents.
# We have to have a root widget

#Layouts
#You use layouts to arrange widgets.
# It is of course possible to calculate your widgets’ positions yourself,
# but often it is more convenient to use one of our ready made layouts.
# Examples would be Grid Layouts or Box Layouts. You can also nest layouts.

# Input Events (Touches)
# Up, Down, Move - these affect Widgets

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
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
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
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.app import App

# to change the kivy default settings we use this module config
from kivy.config import Config

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)

# Creating class MyGrid to add multiple widgets
class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)

class ScreenOne(Screen):
    filename = ObjectProperty()
    mainScale = ObjectProperty()
    secondScale = ObjectProperty()
    secondScaleCheckBox = ObjectProperty()
    stepBasedToggle = ObjectProperty()
    scaleBasedToggle = ObjectProperty()
    tempo = ObjectProperty()


class ScreenTwo(Screen):

    def on_enter(self, *args):

        # Initalizing to avoid errors
        self.secondScale = None
        self.conversionType = None

        secondScaleCheckBox = App.get_running_app().root.ids.screen_one.secondScaleCheckBox.state
        mainScaleInput = App.get_running_app().root.ids.screen_one.mainScale.text.split(',')

        try:
            self.mainScale = tabsclass.Scale(mainScaleInput)
            scaleToDisplay = self.mainScale
        except:
            print('Format of main scale is wrong... please use commas between notes without space')
            self.mainScale = None
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

        # Checking if user requested to convert to another scale
        secondScaleCheckBox = App.get_running_app().root.ids.screen_one.secondScaleCheckBox.state

        if(secondScaleCheckBox == 'down'):
            secondScaleInput = App.get_running_app().root.ids.screen_one.secondScale.text.split(',')
            try:
                self.secondScale = tabsclass.Scale(secondScaleInput)
            except:
                print('Format of second scale is wrong... please use commas between notes without space')


            scaleToDisplay = self.secondScale

            # Check which type of conversion does user want. Default is step based unless user chooses scale based
            scaleToggleState = App.get_running_app().root.ids.screen_one.scaleBasedToggle.state
            if(scaleToggleState == 'down'):
                self.conversionType = 'scaleConversion'
            else:
                self.conversionType = 'stepConversion'



        if(self.mainScale != None):
            # Fixed positions for FloatLayout
            xpos = [0.45,0.45,0.2,0.7,0.1,0.8,0.2,0.7,0.45]
            ypos = [0.45,0.15,0.2,0.2,0.45,0.45,0.7,0.7,0.75]

            self.noteDict = {}
            for i, note in enumerate(scaleToDisplay.notes):
                btn = NoteButton(text=note, pos_hint={'x':xpos[i], 'y':ypos[i]})
                self.noteDict[note] = btn # Creating new dictionary to reference each button
                self.ids.noteButtons.add_widget(btn)
            self.noteDict['slap'] = self.ids['slap']

    def stopMusic(self, *args):

        allOnSchedules = App.get_running_app().root.ids.screen_two.ids.playbutton.allOnSchedules

        try:
            sound = App.get_running_app().root.ids.screen_two.ids.playbutton.sound

            sound.stop()
        except:
            print('Sound not loaded')

        for onEvent in allOnSchedules:
            Clock.unschedule(onEvent)



class NoteButton(Button):

    def on_press(self):
        print('Play Note')

class PlayButton(Button):


    def __init__(self, **kwargs):
        super(PlayButton, self).__init__(**kwargs)

        self.allOnSchedules = []

    def on_release(self):


        self.mainScale = App.get_running_app().root.ids.screen_two.mainScale
        self.secondScale = App.get_running_app().root.ids.screen_two.secondScale
        print('Second scale is: {}'.format(self.secondScale))

        if(self.secondScale == None):
            self.usedScale = self.mainScale
        else:
            self.usedScale = self.secondScale

        self.noteDict = App.get_running_app().root.ids.screen_two.noteDict
        self.tempo = App.get_running_app().root.ids.screen_one.tempo.text
        self.conversionType = App.get_running_app().root.ids.screen_two.conversionType


        for onEvent in self.allOnSchedules:
            Clock.unschedule(onEvent)

        self.allOnSchedules = []

        self.tabsPath = App.get_running_app().root.ids.screen_one.filename.text
        fileName = self.tabsPath.split('.')[0].split('/')[1]
        tabsLoaded = tabsclass.Tabs(self.tabsPath)

        if(self.conversionType == 'scaleConversion'):
            print('Converting to scale using scale...')
            tabsLoaded = tabsLoaded.mapNewScale(self.mainScale, self.secondScale)
        elif(self.conversionType == 'stepConversion'):
            print('Converting to scale using steps...')
            Melody, Missed, Best = tabsLoaded.applyScaleToTab(self.secondScale, True, False)
            tabsLoaded = tabsclass.Tabs(Melody[Best])

        print('Converted to second scale')

        self.midiPath = "MIDI/" + fileName + '.mid'
        tabsLoaded.writeToMIDI(self.midiPath, int(self.tempo), 1)
        self.sound = SoundLoader.load(self.midiPath)

        print('Playing {} at a tempo of {} '.format(fileName, self.tempo))
        self.sound.play()

        self.displayMIDI()

    def displayMIDI(self):

        midiFile = tabsclass.readMIDI(self.midiPath, False)

        for i, track in enumerate(midiFile.tracks):
            #print('Track {}: {}'.format(i, track.name))
            cumTime = 0

            for msg in track:
                noteAction = str(msg).split()
                if (len(noteAction) == 5 and noteAction[0] != '<meta'):
                    noteStatus = noteAction[0]
                    channel = noteAction[1][8:]
                    if(i==2):
                        notePitch = 'slap'
                    else:
                        notePitch = self.usedScale.MIDIToNote[int(noteAction[2][5:])]
                    noteActionTime = noteAction[4]
                    cumTime += int(noteActionTime[5:])
                    # print('{} on channel {} for note {} at time {}'.format(noteStatus,channel,notePitch,cumTime))

                    timeAdjuster = 1920*(int(self.tempo)/120)
                    if (noteStatus == 'note_on'):
                        # print('Turning on note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        onEvent = Clock.schedule_once(partial(self.pressButton, notePitch), cumTime / timeAdjuster)
                        self.allOnSchedules.append(onEvent)
                        #print('TurnOnSchedule is = {}'.format(allOnSchedules))
                    elif (noteStatus == 'note_off'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        Clock.schedule_once(partial(self.releaseButton, notePitch), (cumTime - 100) / timeAdjuster)

    def pressButton(self, *args):
        self.noteDict[args[0]].state = "down"
        pass

    def releaseButton(self, *args):
        self.noteDict[args[0]].state = "normal"
        pass

class MainLayout(StackLayout):
    pass

class graphicsApp(App):

    def build(self):
        return MainLayout()

if __name__ == '__main__':
    graphicsApp().run()
