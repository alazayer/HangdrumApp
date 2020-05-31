import pandas as pd
import numpy as np
from midiutil import MIDIFile
from mido import MidiFile as MIDIread




# GLOBAL VARIABLES

# Assigning all notes a value in a dictionary (noteToValues)
# that will be used to calculate steps between notes
noteToValues = {'C0': 0, 'C#0': 1, 'D0': 2, 'D#0': 3, 'E0': 4, 'F0': 5, 'F#0': 6, 'G0': 7, 'G#0': 8, 'A0': 9, 'A#0': 10,
                'B0': 11,
                'C1': 12, 'C#1': 13, 'D1': 14, 'D#1': 15, 'E1': 16, 'F1': 17, 'F#1': 18, 'G1': 19, 'G#1': 20, 'A1': 21,
                'A#1': 22, 'B1': 23,
                'C2': 24, 'C#2': 25, 'D2': 26, 'D#2': 27, 'E2': 28, 'F2': 29, 'F#2': 30, 'G2': 31, 'G#2': 32, 'A2': 33,
                'A#2': 34, 'B2': 35,
                'C3': 36, 'C#3': 37, 'D3': 38, 'D#3': 39, 'E3': 40, 'F3': 41, 'F#3': 42, 'G3': 43, 'G#3': 44, 'A3': 45,
                'A#3': 46, 'B3': 47,
                'C4': 48, 'C#4': 49, 'D4': 50, 'D#4': 51, 'E4': 52, 'F4': 53, 'F#4': 54, 'G4': 55, 'G#4': 56, 'A4': 57,
                'A#4': 58, 'B4': 59,
                'C5': 60, 'C#5': 61, 'D5': 62, 'D#5': 63, 'E5': 64, 'F5': 65, 'F#5': 66, 'G5': 67, 'G#5': 68, 'A5': 69,
                'A#5': 70, 'B5': 71,
                'C6': 72, 'C#6': 73, 'D6': 74, 'D#6': 75, 'E6': 76, 'F6': 77, 'F#6': 78, 'G6': 79, 'G#6': 80, 'A6': 81,
                'A#6': 82, 'B6': 83,
                'Db0': 1, 'Db1': 13, 'Db2': 25, 'Db3': 37, 'Db4': 49, 'Db5': 61, 'Db6': 73,
                'Eb0': 3, 'Eb1': 15, 'Eb2': 27, 'Eb3': 39, 'Eb4': 51, 'Eb5': 63, 'Eb6': 75,
                'Gb0': 6, 'Gb1': 18, 'Gb2': 30, 'Gb3': 42, 'Gb4': 54, 'Gb5': 66, 'Gb6': 78,
                'Ab0': 8, 'Ab1': 20, 'Ab2': 32, 'Ab3': 44, 'Ab4': 56, 'Ab5': 68, 'Ab6': 80,
                'Bb0': 10, 'Bb1': 22, 'Bb2': 34, 'Bb3': 46, 'Bb4': 58, 'Bb5': 70, 'Bb6': 82,
                }

# Adding 24 because GarageBand starts from C-2 instead of C0
noteToValues = {key: value + 24 for (key, value) in noteToValues.items()}

# Dirty solution to problem of flat and sharp mix up
fsNoteToValues = {'Db0,C#0': 1, 'Db1,C#1': 13, 'Db2,C#2': 25, 'Db3,C#3': 37, 'Db4,C#4': 49, 'Db5,C#5': 61,
                  'Db6,C#6': 73,
                  'Eb0,D#0': 3, 'Eb1,D#1': 15, 'Eb2,D#2': 27, 'Eb3,D#3': 39, 'Eb4,D#4': 51, 'Eb5,D#5': 63,
                  'Eb6,D#6': 75,
                  'Gb0,F#0': 6, 'Gb1,F#1': 18, 'Gb2,F#2': 30, 'Gb3,F#3': 42, 'Gb4,F#4': 54, 'Gb5,F#5': 66,
                  'Gb6,F#6': 78,
                  'Ab0,G#0': 8, 'Ab1,G#1': 20, 'Ab2,G#2': 32, 'Ab3,G#3': 44, 'Ab4,G#4': 56, 'Ab5,G#5': 68,
                  'Ab6,G#6': 80,
                  'Bb0,A#0': 10, 'Bb1,A#1': 22, 'Bb2,A#2': 34, 'Bb3,A#3': 46, 'Bb4,A#4': 58, 'Bb5,A#5': 70,
                  'Bb6,A#6': 82}

# Adding 24 because GarageBand starts from C-2 instead of C0
fsNoteToValues = {key: value + 24 for (key, value) in fsNoteToValues.items()}

# Opposite of above dictionary
valueToNotes = {value: key for (key, value) in noteToValues.items()}
fsValueToNotes = {value: key for (key, value) in fsNoteToValues.items()}


# The class Tabs can be intialized by either loading a dataframe in Tabs format
# or inputting a path and reading an excel
# ------------------------------------------
# Attributes:
# - tab (DataFrame)
# - notes (List of all notes without S)
# - notesLoc (List of the coordinates of the notes plus whether it's a chord)
# - tabSteps (List of steps between the notes in the tab)
# - MIDIvalues (List of MIDIvalues)
# ------------------------------------------
# Methods:
# - _loadTabs(path): reads tab from excel sheet. Called by constructor.
# - _storeTabNotes(): returns list of notes in sparse format with list of coordinates
# - _convertTabToSteps(): computes steps between all the notes in comparison to first note
# - _replaceTabWithNewNotes(newNotes): To place the new notes in dataframe
# - _extractMIDIvalues(): Stores the MIDI values for each note. Stores 'S' for slaps.
# - _bestNoteToStart(cumMissedNotes): Used in applyScaleToTab to identify the note with the least missed notes
# - _replaceWithClosest(scale,value): Finds the closest note in the scale when a note is missed in applyScaleToTab
# - applyScaleToTab(scale): Checks if the tabs can be applied to a specific scale based on the steps between notes
# - mapNewScale(tabScale,newScale): replaces the scale used to compose the tab with the newScale
# - writeToMIDI(path): Writes the tab as a MIDI file to the entered path
# - readMIDI(path): Reads MIDI file and outputs all the tracks/notes

class Tabs():

    def __init__(self, path):

        if (isinstance(path, pd.DataFrame)):
            self.tab = path
        else:
            self.tab = self._loadTabs(path)

        self.notes, self.notesLoc = self._storeTabNotes()
        self.tabSteps = self._convertTabToSteps()
        self.MIDIvalues = self._extractMIDIvalues()

    # Loads the tabs from excel. Fills the Na values of '-' and organizes the dataframe
    def _loadTabs(self, path):
        # Reading tabs from excel sheet and fill NaNs with '-'
        tabs = pd.read_excel(path)
        tabs = tabs.fillna('-')

        # Set the first row as a header
        headers = tabs.iloc[0]
        tabs = pd.DataFrame(tabs.values[1:], columns=headers)

        # Set the first Column as indices in the dataframe
        tabs = tabs.set_index('Row')

        self.tab = tabs

        return tabs

    # Method that loops over the tabs and stores the the note and corresponding location in two lists
    # Input:
    # - tabs dataframe (Usually export from excel file)
    # Output:
    # - List of all notes in string format (allNotesInTab)
    # - List of corresponding note locations + chord indicator (cordOfNotesInTab)
    def _storeTabNotes(self):

        numRows = self.tab.shape[0]
        numColumns = self.tab.shape[1]
        allNotesInTab = []
        cordOfNotesInTab = []

        # Loops across the tabs and stores any note(s) in allNotesInTab (List of Strings)
        # It also the stores the location of the notes in locOfNotesInTab (List of Tuples)
        for r in range(0, numRows):
            for c in range(0, numColumns):
                if (self.tab.iloc[r][c] != '-'):
                    # Check if we have a chord
                    notes = self.tab.iloc[r][c].split(',')
                    for i, note in enumerate(notes):
                        allNotesInTab.append(note)
                        if (len(notes) > 1):  # To identify whether stored note is a chord
                            cordOfNotesInTab.append((r, c, 'C{}'.format(i)))  # index will show if first note in chord
                        elif (note == 'S'):
                            cordOfNotesInTab.append((r, c, 'S'.format(i)))  # index will show if note is slap
                        else:
                            cordOfNotesInTab.append((r, c, ''))

        return allNotesInTab, cordOfNotesInTab

    # function that computes the number of steps in reference to the first note in the tabs
    # Note that the function skips Slaps (S)
    # Input: tabs
    # Output: numpy array in integer format
    def _convertTabToSteps(self):

        # Extracts the notes and corresponding locations from tabs dataframe (excel sheet)
        # tabNotes, cord = storeTabNotes(tabs)

        # Construct list with values instead of notes
        allValuesInTab = [];
        for note in self.notes:
            if (note == 'S'):
                allValuesInTab.append(float('inf'))
            else:
                allValuesInTab.append(noteToValues[note])

        # Computes the steps of all the notes compared to first note
        tabSteps = np.array(allValuesInTab) - allValuesInTab[0]

        # returns reversed list
        return tabSteps

    # Function to place notes in dataframe
    # Input: tabs, cordinate list and new notes list
    # Output: new tabs in dataframe format
    def _replaceTabWithNewNotes(self, newNotes):

        newTabs = self.tab.copy()

        # Loop through combined list to place notes in the correct location in dataframe
        combinedList = list(zip(self.notesLoc, newNotes))
        for cord, newNote in combinedList:
            if ('C' in cord[2]):
                if (int(cord[2][1]) > 0):
                    # If it is not the first note in chord, we apend it to same location
                    newTabs.iloc[cord[0]][cord[1]] += ',{}'.format(newNote)
                else:
                    # If it is the first note in chord we replace contents
                    newTabs.iloc[cord[0]][cord[1]] = newNote
            else:
                # Replace contents with new note
                newTabs.iloc[cord[0]][cord[1]] = newNote

        return newTabs

    # Stores the MIDI values for each note. Stores 'S' for slaps.
    def _extractMIDIvalues(self):

        # Store corresponding MIDI value for each note. If 'S' just store 'S'.
        MIDIvalues = [];
        for note in self.notes:
            if (note == "S"):
                MIDIvalues.append("S")
            else:
                MIDIvalues.append(noteToValues[note])

        return MIDIvalues

    # Function to identify the tabs with least missed notes
    def _bestNoteToStart(self, cumMissedNotes):

        bestNoteToStart = []
        missedNotes = float('inf')
        for note in cumMissedNotes:
            if (cumMissedNotes[note] < missedNotes):
                bestNoteToStart = note
                missedNotes = cumMissedNotes[note]

        return bestNoteToStart

    # Finds the closest note in the scale when a note is missed in applyScaleToTab
    def _replaceWithClosest(self, scale, value):

        # Since we're allowing either a list or Scale to be entered into applyScaleToTab
        # We have to recalculate the MIDI values
        MIDIvalues = [];
        for note in scale:
            MIDIvalues.append(noteToValues[note])

        MIDIarray = np.asarray(MIDIvalues)
        index = (np.abs(MIDIarray - value)).argmin()

        return scale[index]

    # Check if the tabs can be applied to a specific scale based on the steps between notes
    # Returns a tab for each note in the scale with that note as the starting note.
    # Also returns the number of notes that could not be applied for each note.
    def applyScaleToTab(self, scale, replaceClosest=False, replaceActual=False):

        # In case the input is a Scale object or just a list
        if (type(scale) == Scale):
            scale = scale.notes

        # Initialize dictionary to load all possible tabs + corresponding missed notes
        allPossibleTabs = {}
        cumMissedNotes = {}
        # traverse every note in the given scale
        for note in scale:

            # Add the value of the note to the computed steps to identify the notes needed
            newTabValues = noteToValues[note] + self.tabSteps

            # Initialize/Reset list to add new notes
            newNotes = []
            # Used to compute missed notes
            missedNotes = 0
            # Loop through all values and check if it is available in scale
            for value in newTabValues:

                if (value == float('inf')):
                    newNotes.append('S')
                elif (valueToNotes[value] in scale):
                    newNotes.append(valueToNotes[value])
                elif (value in fsValueToNotes.keys()):  # Checks if the value corresponds to flat or sharp note
                    fsNotes = fsValueToNotes[value].split(',')  # Extract both notes that correspond to value
                    found = False
                    for fsNote in fsNotes:  # Loop through both to check if they exist in scale
                        if (fsNote in scale):
                            found = True
                    # After checking both check to add or count as missed note
                    if (found):
                        newNotes.append(fsNote)
                    else:
                        if (replaceActual):
                            newNotes.append(fsNote)
                        elif (replaceClosest):
                            newNotes.append(self._replaceWithClosest(scale, value))
                        else:
                            newNotes.append(str(value))
                        missedNotes += 1
                else:
                    if (replaceActual):
                        newNotes.append(valueToNotes[value])
                    elif (replaceClosest):
                        newNotes.append(self._replaceWithClosest(scale, value))
                    else:
                        newNotes.append(str(value))
                    missedNotes += 1

            # Make copy of tabs with new notes and count number of missed notes
            allPossibleTabs[note] = self._replaceTabWithNewNotes(newNotes)
            cumMissedNotes[note] = missedNotes

        return allPossibleTabs, cumMissedNotes, self._bestNoteToStart(cumMissedNotes)

    def mapNewScale(self, tabScale, newScale):

        # In case the input is a Scale object or just a list
        if (type(tabScale) == Scale):
            tabScale = tabScale.notes

        if (type(newScale) == Scale):
            newScale = newScale.notes

            # Create two dictionaries
        # ScaleOne
        tabScaleNoteToIndex = {}
        for i, note in enumerate(tabScale):
            tabScaleNoteToIndex[note] = i

        # ScaleTwo
        newScaleIndexToNote = {}
        for i, note in enumerate(newScale):
            newScaleIndexToNote[i] = note

        # Loop through allNotesInTab and replace with notes from new scale
        newNotes = self.notes.copy()
        for i, note in enumerate(self.notes):
            if (note != 'S'):
                newNotes[i] = newScaleIndexToNote[tabScaleNoteToIndex[note]]

        return Tabs(self._replaceTabWithNewNotes(newNotes))

    def writeToMIDI(self, path):

        # Loop through all notes
        Melody = list(zip(self.MIDIvalues, self.notesLoc))

        MIDInotes = []
        MIDItimes = []

        # Creating two lists of the MIDIvalues and corresponding times
        for note, cord in Melody:
            # MIDInotes will store the track on the first slot and the noteValue on the 2nd slot
            if (note == 'S'):
                MIDInotes.append([1, 37])
            else:
                MIDInotes.append([0, note])

            # we multiply cord[0] by 16 since there are 16 counts in each row
            MIDItimes.append(cord[0] * 16 + cord[1])

        # create your MIDI object (fixed values at the moment)
        mf = MIDIFile(2)  # 2 tracks
        tempo = 120
        volume = 100
        duration = 1
        time = 0
        track = 0

        mf.addTrackName(track, time, "Sample Track")
        mf.addTempo(track, time, tempo)

        # Adding Notes to Channel 0
        channel = 0

        melody = list(zip(MIDInotes, MIDItimes))

        # If track is zero it will store on channel zero (Piano)
        # If track is one it will store on channel nine (Drums)
        for pitch, time in melody:
            # print('Adding to track {}, channel {}, note {}, time {}'.format(pitch[0], pitch[0]*9, pitch[1], time/4))
            mf.addNote(pitch[0], pitch[0] * 9, pitch[1], time / 4, duration, volume)
            #  MyMIDI.addNote(track, channel, pitch, time, duration, volume)

        with open(path, 'wb') as outf:
            mf.writeFile(outf)

        return mf


class Scale():

    def __init__(self, scale):
        self.notes = scale
        self.steps = self._stepsIn(scale)
        self.MIDIvalues = self._extractMIDIvalues()

    # function to compute steps in the inputted scale
    # Returns a list that is length(scale)-1
    # Uses the noteToValue dictionary to reference the note value
    def _stepsIn(self, scale):
        steps = [];
        for note in range(0, len(scale) - 1):
            steps.append(noteToValues[scale[note + 1]] - noteToValues[scale[note]])
        return steps

    # Stores the MIDI values for each note. Stores 'S' for slaps.
    def _extractMIDIvalues(self):

        # Store corresponding MIDI value for each note. If 'S' just store 'S'.
        MIDIvalues = [];
        for note in self.notes:
            MIDIvalues.append(noteToValues[note])

        return MIDIvalues


''' pg_midi_sound101.py
play midi music files (also mp3 files) using pygame
tested with Python273/331 and pygame192 by vegaseat

Taken from
https://www.daniweb.com/programming/software-development/code/454835/let-pygame-play-your-midi-or-mp3-files 
'''
import pygame as pg

def play_music(music_file):
    '''
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
    '''
    freq = 44100  # audio CD quality
    bitsize = -16  # unsigned 16 bit
    channels = 2  # 1 is mono, 2 is stereo
    buffer = 2048  # number of samples (experiment to get right sound)
    pg.mixer.init(freq, bitsize, channels, buffer)
    # optional volume 0 to 1.0
    pg.mixer.music.set_volume(1.0)

    clock = pg.time.Clock()
    try:
        pg.mixer.music.load(music_file)
        print("Music file {} loaded!".format(music_file))
    except pygame.error:
        print("File {} not found! {}".format(music_file, pg.get_error()))
        return

    pg.mixer.music.play()

    # check if playback has finished
    while pg.mixer.music.get_busy():
        clock.tick(30)

# Output in the form(Note on or off, Channel, note, volume, time from previous note)
def readMIDI(path,display=False):

    mid = MIDIread(path)

    if(display):
        for i, track in enumerate(mid.tracks):
            print('Track {}: {}'.format(i, track.name))
            for msg in track:
                print(msg)

    return mid


landOfCole = Tabs("Tabs/LandOfColeHDtabs.xlsx")
AliScale = Scale(['D3','A3','Bb3','C4','D4','E4','F4','G4','A4'])
AlaScale = Scale(['B2','C4','C#4','D4','E4','F#4','G4','B4','C#5'])


#Writing landOfCole MIDI
landOfCole.writeToMIDI("MIDI/LOC.mid")

# landOfCole using Ala scale replacing with closest note
Melody,Missed,Best = landOfCole.applyScaleToTab(AlaScale,True,False)
LOCAlaScaleReplacedClosest = Tabs(Melody[Best])
LOCAlaScaleReplacedClosest.writeToMIDI("MIDI/LOC_Ala_Steps_Closest.mid")

# landOfCole using Ala scale replacing with actual note even if it doesn't exist in scale
Melody,Missed,Best = landOfCole.applyScaleToTab(AlaScale,False,True)
LOCAlaScaleReplacedActual = Tabs(Melody[Best])
LOCAlaScaleReplacedActual.writeToMIDI("MIDI/LOC_Ala_Steps_Actual.mid")

# landOfCole by mapping directly to Ala scale replacing with actual note even if it doesn't exist in scale
LOCAlaScaleMapped = landOfCole.mapNewScale(AliScale,AlaScale)
LOCAlaScaleMapped.writeToMIDI("MIDI/LOC_Ala_Scale_Mapped.mid")

# Replace missed notes with chord notes (check note before and after)

music_file = "MIDI/LOC.mid"

play_music(music_file)
# try:
#     play_music(music_file)
# except KeyboardInterrupt:
#     # if user hits Ctrl/C then exit
#     # (works only in console mode)
#     pg.mixer.music.fadeout(1000)
#     pg.mixer.music.stop()
#     raise SystemExit