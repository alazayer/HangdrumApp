import tabsclass
import math
import pandas as pd
import csv
import numpy as np

AliScale = tabsclass.Scale(['D3','A3','Bb3','C4','D4','E4','F4','G4','A4'])
AlaScale = tabsclass.Scale(['B2','C4','C#4','D4','E4','F#4','G4','B4','C#5'])

csvRead = tabsclass.Tabs('CSV/csvRead.csv')
print(csvRead.tab)

# xlsRead = tabsclass.Tabs('Tabs/LandOfColeHDtabs.xlsx')
# print(xlsRead.songTime)
#
# xlsRead.applyScaleToTab(AlaScale)
#
# Melody, Missed, Best = xlsRead.applyScaleToTab(AlaScale, True, False)
# print(Melody[Best])

# midiRead = tabsclass.Tabs('MIDI/LOC.mid')
# print(midiRead.tab)
# print(midiRead.songTime)




