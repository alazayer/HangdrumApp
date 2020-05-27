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
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from functools import partial # to be able to load arguments in Clock



# to change the kivy default settings we use this module config
from kivy.config import Config

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)

# Creating class MyGrid to add multiple widgets

class Anchor_Layout(FloatLayout):

    # Adding functionality and arranging a callback to a button
    def __init__(self, **kwargs):
        super(Anchor_Layout, self).__init__(**kwargs)

        # self.filename = StringProperty(None)
        self.filename = 'MIDI/LOC.mid'
        self.sound = ObjectProperty(None, allownone=True)


        # Can use this to schedule an event repeatedly or once
        # self.function_interval = Clock.schedule_interval(self.pressButton, 4)
        # Clock.schedule_once(self.stop_interval, 2)
        # Clock.schedule_once(partial(self.pressButton, 'F4'), 2)
        # Clock.schedule_once(partial(self.releaseButton, 'F4'), 4)
        # Clock.schedule_once(partial(self.pressButton, 'A4'), 6)

    def say_hello(self, *args):

        landOfCole = tabsclass.Tabs("Tabs/LandOfColeHDtabsNoSlap.xlsx")
        landOfCole.writeToMIDI("MIDI/LOC.mid")
        AliScale = tabsclass.Scale(['D3', 'A3', 'Bb3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4'])
        AlaScale = tabsclass.Scale(['B2', 'C4', 'C#4', 'D4', 'E4', 'F#4', 'G4', 'B4', 'C#5'])

        midiFile = tabsclass.readMIDI('MIDI/LOC.mid',False)

        for i, track in enumerate(midiFile.tracks):
            print('Track {}: {}'.format(i, track.name))
            cumTime = 0
            for msg in track:
                noteAction = str(msg).split()
                if(len(noteAction)==5 and noteAction[0] != '<meta'):
                    noteStatus = noteAction[0]
                    channel = noteAction[1][8:]
                    notePitch = AliScale.MIDIToNote[int(noteAction[2][5:])]
                    noteActionTime = noteAction[4]
                    cumTime += int(noteActionTime[5:])
                    #print('{} on channel {} for note {} at time {}'.format(noteStatus,channel,notePitch,cumTime))

                    timeAdjuster = 1920
                    if(noteStatus == 'note_on'):
                        print('Turning on note {} at time {}'.format(notePitch,cumTime/timeAdjuster))
                        Clock.schedule_once(partial(self.pressButton, notePitch), cumTime/timeAdjuster)
                    elif(noteStatus == 'note_off'):
                        print('Turning off note {} at time {}'.format(notePitch,cumTime/timeAdjuster))
                        Clock.schedule_once(partial(self.releaseButton, notePitch), (cumTime-100)/timeAdjuster)

        #if self.sound is None:
        self.sound = SoundLoader.load(self.filename)
        # stop the sound if it's currently playing
        #if self.sound.status != 'stop':
        #    self.sound.stop()
        #self.sound.volume = self.volume
        self.sound.play()

    def stop_interval(self, *args):
        self.function_interval.cancel()

    def pressButton(self, *args):
        # print(args)
        self.ids[args[0]].state = "down"

    def releaseButton(self, *args):
        # print(args)
        self.ids[args[0]].state = "normal"





class graphicsApp(App):

    def build(self):
        return Anchor_Layout()

if __name__ == '__main__':
    graphicsApp().run()
