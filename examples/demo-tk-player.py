#!/usr/bin/env python2

import sys, os, fnmatch, random, pprint, Tkinter

# Our parent path might contain a self-build musicplayer module. Use that one.
sys.path = [os.path.abspath((os.path.dirname(__file__) or ".") + "/..")] + sys.path

import musicplayer
print "Module:", musicplayer.__file__

class Song:
	def __init__(self, fn):
		self.url = fn
		self.f = open(fn)
	# `__eq__` is used for the peek stream management
	def __eq__(self, other):
		return self.url == other.url
	# this is used by the player as the data interface
	def readPacket(self, bufSize):
		return self.f.read(bufSize)
	def seekRaw(self, offset, whence):
		r = self.f.seek(offset, whence)
		return self.f.tell()

files = []
def getFiles(path):
	for f in sorted(os.listdir(path), key=lambda k: random.random()):
		f = os.path.join(path, f)
		if os.path.isdir(f): getFiles(f) # recurse
		if len(files) > 1000: break # break if we have enough
		if fnmatch.fnmatch(f, '*.mp3'): files.append(f)
getFiles(os.path.expanduser("~/Music"))
random.shuffle(files) # shuffle some more
files = sys.argv[1:] + files
assert files, "give me some files or fill-up ~/Music"

i = 0

def songs():
	global i, files
	while True:
		yield Song(files[i])
		i += 1
		if i >= len(files): i = 0

def peekSongs(n):
	nexti = i + 1
	if nexti >= len(files): nexti = 0
	return map(Song, (files[nexti:] + files[:nexti])[:n])

# Create our Music Player.
player = musicplayer.createPlayer()
player.outSamplerate = 96000 # support high quality :)
player.queue = songs()
player.peekQueue = peekSongs

# Setup a simple GUI.
window = Tkinter.Tk()
window.title("Music Player")
songName = Tkinter.StringVar()
songTime = Tkinter.StringVar()
songLabel = Tkinter.StringVar()

def onSongChange(**kwargs):
	songName.set(os.path.basename(player.curSong.url))
	songLabel.set(pprint.pformat(player.curSongMetadata))
def cmdPlayPause(*args): player.playing = not player.playing
def cmdSeekBack(*args): player.seekRel(-10)
def cmdSeekFwd(*args): player.seekRel(10)
def cmdNext(*args): player.nextSong()

def refreshTime():
	songTime.set("Time: %.1f / %.1f" % (player.curSongPos or -1, player.curSongLen or -1))
	window.after(10, refreshTime) # every 10ms

Tkinter.Button(window, text="Play/Pause", command=cmdPlayPause).pack()
Tkinter.Button(window, text="Seek -10", command=cmdSeekBack).pack()
Tkinter.Button(window, text="Seek +10", command=cmdSeekFwd).pack()
Tkinter.Button(window, text="Next", command=cmdNext).pack()
Tkinter.Label(window, textvariable=songName).pack()
Tkinter.Label(window, textvariable=songTime).pack()
Tkinter.Label(window, textvariable=songLabel).pack()

refreshTime()

player.onSongChange = onSongChange
player.playing = True # start playing
window.mainloop()

