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
import pygame

# to change the kivy default settings we use this module config
from kivy.config import Config

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)

# Creating Screen Manager class to manage two screens
class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)

# Screen one class will be responsible for taking all input from user
class ScreenOne(Screen):
    filename = ObjectProperty()
    mainScale = ObjectProperty()
    secondScale = ObjectProperty()
    secondScaleCheckBox = ObjectProperty()
    stepBasedToggle = ObjectProperty()
    scaleBasedToggle = ObjectProperty()
    tempo = ObjectProperty()
    reverseScaleCheckBox = ObjectProperty()

# Screen two will display the notes being played
class ScreenTwo(Screen):

    # On entering the screen
    def on_enter(self, *args):

        # Initalizing to avoid errors in case these options were not selected
        self.secondScale = None
        self.conversionType = None
        formatError = False
        self.ids['slap'].state = 'normal' # in case back button was pressed while slap was on

        # Loading the main scale and check if it is in the expected Scale class format
        # Goes back to main screen if input is in an invalid format
        mainScaleInput = App.get_running_app().root.ids.screen_one.mainScale.text.split(',')

        try:
            self.mainScale = tabsclass.Scale(mainScaleInput)
            scaleToDisplay = self.mainScale
        except:
            print('Format of main scale is wrong... please use commas between notes without space')
            formatError = True
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

        # Checking if user requested to convert to another scale. If box is ticked read second scale
        secondScaleCheckBox = App.get_running_app().root.ids.screen_one.secondScaleCheckBox.state
        reversedScaleCheckBox = App.get_running_app().root.ids.screen_one.reverseScaleCheckBox.state

        if(secondScaleCheckBox == 'down'):
            secondScaleInput = App.get_running_app().root.ids.screen_one.secondScale.text.split(',')
            try:
                self.secondScale = tabsclass.Scale(secondScaleInput)
            except:
                print('Format of second scale is wrong... please use commas between notes without space')
                App.get_running_app().root.ids.screen_manager.current = 'screen1'
                formatError = True

            # Overwrites main scale to display in second screen
            scaleToDisplay = self.secondScale

            # Check which type of conversion does user want. Default is step based unless user chooses scale based
            scaleToggleState = App.get_running_app().root.ids.screen_one.scaleBasedToggle.state
            if(scaleToggleState == 'down'):
                self.conversionType = 'scaleConversion'
            else:
                self.conversionType = 'stepConversion'

        # Does not display anything in second screen if main scale was not entered correctly
        if(not formatError):
            # Fixed positions for FloatLayout (NEEDS WORK)
            if(reversedScaleCheckBox == 'down'):
                xpos = [0.45,0.45,0.7,0.2,0.8,0.1,0.7,0.2,0.45]
                ypos = [0.45,0.15,0.2,0.2,0.45,0.45,0.7,0.7,0.75]
            else:
                xpos = [0.45,0.45,0.2,0.7,0.1,0.8,0.2,0.7,0.45]
                ypos = [0.45,0.15,0.2,0.2,0.45,0.45,0.7,0.7,0.75]

            # Creating the notes as button and storing them in dictionary to be referenced later
            self.noteDict = {}
            for i, note in enumerate(scaleToDisplay.notes):
                btn = NoteButton(text=note, pos_hint={'x':xpos[i], 'y':ypos[i]})
                self.noteDict[note] = btn # Creating new dictionary to reference each button
                self.ids.noteButtons.add_widget(btn)
            self.noteDict['slap'] = self.ids['slap']

    # Function to stop the music and all scheduled events if 'Back' button is clicked
    def stopMusic(self, *args):

        allOnScheduled = App.get_running_app().root.ids.screen_two.ids.playbutton.allOnScheduled
        allOffScheduled = App.get_running_app().root.ids.screen_two.ids.playbutton.allOffScheduled

        # If play button was never pressed then no sound was loaded and no need to stop anything
        try:
            sound = App.get_running_app().root.ids.screen_two.ids.playbutton.sound
            sound.stop()

            # Unscheduling all events to avoid re-entering screen two with different buttons (KeyError)
            allScheduled = zip(allOnScheduled, allOffScheduled)
            for OnEvent, OffEvent in allScheduled:
                Clock.unschedule(OnEvent)
                Clock.unschedule(OffEvent)
        except:
            print('Sound not loaded')


# A class that can be used to load the audio for each note to be played when pressed
class NoteButton(Button):

    def on_press(self):
        print('Playing Note {}'.format(self.text))

class PlayButton(Button):

    # Initalize list of note events (on/off). These will be used to unschedule the events in case
    # back or play buttons are pressed
    def __init__(self, **kwargs):
        super(PlayButton, self).__init__(**kwargs)

        self.allOnScheduled = []
        self.allOffScheduled = []

    def on_release(self):

        # Loading scales and determine which will be used
        self.mainScale = App.get_running_app().root.ids.screen_two.mainScale
        self.secondScale = App.get_running_app().root.ids.screen_two.secondScale

        if(self.secondScale == None):
            self.usedScale = self.mainScale
        else:
            self.usedScale = self.secondScale

        # Retrieve dictionary with all notes displayed + desired tempo and conversion type from user
        self.noteDict = App.get_running_app().root.ids.screen_two.noteDict
        self.tempo = App.get_running_app().root.ids.screen_one.tempo.text
        self.conversionType = App.get_running_app().root.ids.screen_two.conversionType

        # Stop any On scheduled events in the case the play button is pressed again (Restarting music)
        # Off events are kept to turn off any notes there were on from last play
        for event in self.allOnScheduled:
            Clock.unschedule(event)

        # Loads the desired tabls from the path and create a Tabs class
        self.tabsPath = App.get_running_app().root.ids.screen_one.filename.text
        fileName = self.tabsPath.split('.')[0].split('/')[1]
        tabsLoaded = tabsclass.Tabs(self.tabsPath)

        # If conversion to secondary scale is desired, Tabs class is used to change to the new tabs
        if(self.conversionType == 'scaleConversion'):
            tabsLoaded = tabsLoaded.mapNewScale(self.mainScale, self.secondScale)
        elif(self.conversionType == 'stepConversion'):
            Melody, Missed, Best = tabsLoaded.applyScaleToTab(self.secondScale, True, False)
            tabsLoaded = tabsclass.Tabs(Melody[Best])

        # MIDI file is stored, loaded and played
        self.midiPath = "MIDI/" + fileName + '.mid'
        tabsLoaded.writeToMIDI(self.midiPath, int(self.tempo), 1)
        # self.sound = SoundLoader.load(self.midiPath)

        print('Playing {} at a tempo of {} '.format(fileName, self.tempo))
        self.play_with_pygame(self.midiPath)

        # Calls function to display the notes
        self.displayMIDI()

    def play_with_pygame(self, song):
        pygame.init()
        pygame.mixer.music.load(song)
        pygame.mixer.music.load('MIDI/LandOfColeHDtabs.mp3')
        self.sound = pygame.mixer.music
        length = pygame.time.get_ticks()
        print('Length of song is: {}'.format(length))
        self.sound.play()
        # length = pygame.time.get_ticks()
        #while self.sound.get_busy():
        #    pygame.time.Clock().tick(length)

    def displayMIDI(self):

        # reads the MIDI file
        midiFile = tabsclass.readMIDI(self.midiPath, False)

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
                    timeAdjuster = 1920*(int(self.tempo)/120)
                    if (noteStatus == 'note_on'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        onEvent = Clock.schedule_once(partial(self.pressButton, notePitch), self.cumTime / timeAdjuster)
                        self.allOnScheduled.append(onEvent)
                    elif (noteStatus == 'note_off'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        offEvent = Clock.schedule_once(partial(self.releaseButton, notePitch), (self.cumTime - 100) / timeAdjuster)
                        self.allOffScheduled.append(offEvent)

    # Function called to light up a button (note)
    def pressButton(self, *args):
        self.noteDict[args[0]].state = "down"
        print('Current time is: {}'.format(self.sound.get_pos()))
        #self.sound.set_pos(2)

    # Function called to turn off a button (note)
    def releaseButton(self, *args):
        self.noteDict[args[0]].state = "normal"
        # print('Current time is: {}'.format(self.sound.get_pos()))


class MainLayout(StackLayout):
    pass

class graphicsApp(App):

    def build(self):
        return MainLayout()

if __name__ == '__main__':
    graphicsApp().run()
