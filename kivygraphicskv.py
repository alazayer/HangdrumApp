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
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
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

    # On entering the screen we are loading everything from the main screen
    def on_enter(self, *args):

        self._checkMainScreenInput()
        self._displayNoteButtons()
        self._loadmainMIDI()

    def _checkMainScreenInput(self):

        # Initalizing to avoid errors in case these options were not selected
        self.playbutton.state = 'normal'
        self.secondScale = None
        self.conversionType = None
        self.formatError = False
        self.allOnScheduled = []
        self.allOffScheduled = []
        self.currentTime = 0

        # Loading the main scale and check if it is in the expected Scale class format
        # Goes back to main screen if input is in an invalid format
        mainScaleInput = App.get_running_app().root.ids.screen_one.mainScale.text.split(',')

        try:
            self.mainScale = tabsclass.Scale(mainScaleInput)
            self.scaleToDisplay = self.mainScale
        except:
            print('Format of main scale is wrong... please use commas between notes without space')
            self.formatError = True
            App.get_running_app().root.ids.screen_manager.current = 'screen1'

        # Checking if user requested to convert to another scale. If box is ticked read second scale
        self.secondScaleCheckBox = App.get_running_app().root.ids.screen_one.secondScaleCheckBox.state
        self.reversedScaleCheckBox = App.get_running_app().root.ids.screen_one.reverseScaleCheckBox.state

        if(self.secondScaleCheckBox == 'down'):
            secondScaleInput = App.get_running_app().root.ids.screen_one.secondScale.text.split(',')
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
            if(self.reversedScaleCheckBox == 'down'):
                xpos = [0.45,0.45,0.7,0.2,0.8,0.1,0.7,0.2,0.45]
                ypos = [0.55, 0.25, 0.3, 0.3, 0.55, 0.55, 0.8, 0.8, 0.85]
            else:
                xpos = [0.45,0.45,0.2,0.7,0.1,0.8,0.2,0.7,0.45]
                ypos = [0.55, 0.25, 0.3, 0.3, 0.55, 0.55, 0.8, 0.8, 0.85]
            # Creating the notes as button and storing them in dictionary to be referenced later
            self.noteDict = {}
            for i, note in enumerate(self.scaleToDisplay.notes):
                btn = NoteButton(text=note, pos_hint={'x':xpos[i], 'y':ypos[i]})
                self.noteDict[note] = btn # Creating new dictionary to reference each button
                self.ids.noteButtons.add_widget(btn)
            self.noteDict['slap'] = self.ids['slap']

    def _loadmainMIDI(self):

        # Loads the desired tabs from the path and create a Tabs class
        tabsPath = App.get_running_app().root.ids.screen_one.filename.text
        fileName = tabsPath.split('.')[0].split('/')[1]
        tabsLoaded = tabsclass.Tabs(tabsPath)

        self.songTime = tabsLoaded.songTime
        print('Total time of song loaded is {}'.format(round(self.songTime,1)))

        # setting default times
        self.startTime.text = '0'
        self.endTime.text = str(round_up(self.songTime,1))
        self.timeBar.value = 0
        self.timeBar.max = math.ceil(self.songTime)


        # If conversion to secondary scale is desired, Tabs class is used to change to the new tabs
        if(self.conversionType == 'scaleConversion'):
            tabsLoaded = tabsLoaded.mapNewScale(self.mainScale, self.secondScale)
        elif(self.conversionType == 'stepConversion'):
            Melody, Missed, Best = tabsLoaded.applyScaleToTab(self.secondScale, True, False)
            tabsLoaded = tabsclass.Tabs(Melody[Best])


        # Main MIDI file is stored if read from xlsx file
        if('xlsx' in tabsPath):
            self.midiPath = "MIDI/" + fileName + '.mid'
            tabsLoaded.writeToMIDI(self.midiPath, float(self.tempo.text), 1)

    def displayMIDI(self):

        # reads the MIDI file
        midiFile = tabsclass.readMIDI('MIDI/temp.mid', False)

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
                        # onEvent = Clock.schedule_once(partial(self.pressButton, notePitch), self.cumTime / timeAdjuster)
                        onEvent = Clock.schedule_once(self.noteDict[notePitch].on_press, self.cumTime / timeAdjuster)
                        self.allOnScheduled.append(onEvent)
                    elif (noteStatus == 'note_off'):
                        # print('Turning off note {} at time {}'.format(notePitch, cumTime / timeAdjuster))
                        # offEvent = Clock.schedule_once(partial(self.releaseButton, notePitch), (self.cumTime - 100) / timeAdjuster)
                        offEvent = Clock.schedule_once(self.noteDict[notePitch].on_release, (self.cumTime - 100) / timeAdjuster)
                        self.allOffScheduled.append(offEvent)

# A class that can be used to load the audio for each note to be played when pressed
class NoteButton(Button):

    def on_press(self, *args):
        self.state = 'down'
        # print('Playing Note {}'.format(self.text))

    def on_release(self, *args):
        self.state = 'normal'
        # print('Releasing Note {}'.format(self.text))

class TimeBar(Slider):

    def increment_time(self, interval):

        screenTwo = App.get_running_app().root.ids.screen_two

        screenTwo.currentTime += interval*(float(screenTwo.tempo.text)/120)
        if(screenTwo.currentTime <= screenTwo.songTime):
            screenTwo.timeBar.value = round_up(screenTwo.currentTime,1)
        else:
            screenTwo.timeBar.value = screenTwo.songTime
            Clock.unschedule(screenTwo.timeBar.increment_time)

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
        if(self.state == 'down'):
            self.playButtonAction()
        elif(self.state == 'normal'):
            self.pauseButtonAction()

    def playButtonAction(self):

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
        tabsclass.cutMIDI(screenTwo.midiPath,'MIDI/temp.mid', startTime, endTime, tempo)
        print('Playing {} at a tempo of {} from {} to {}'.format(screenTwo.midiPath,tempo, startTime, endTime))
        screenTwo.sound = self.playMusic('MIDI/temp.mid')

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

        if(screenTwo.currentTime > screenTwo.songTime):
            screenTwo.currentTime = screenTwo.songTime

        screenTwo.startTime.text = str(round_up(screenTwo.currentTime,1))
        # to stop music
        self.stopMusic()

    def stopMusic(self):

        screenTwo = App.get_running_app().root.ids.screen_two

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

class BackButton(Button):

    def on_release(self):

        App.get_running_app().root.ids.screen_two.playbutton.stopMusic()

        App.get_running_app().root.ids.screen_manager.current = 'screen1'

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
