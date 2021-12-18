from io import BytesIO
from pytube import YouTube
import tempfile
import discord
import time
import traceback
from Caching import cacher
def interact(f,op,indata:bytes = None): #prevent cursor from moving
    method = getattr(f,op)
    if op == "read":
        data = method()
        f.seek(0)
        return data
    elif op == "write":
        method(indata)
        f.seek(0)

class musicplayer():
    def __init__(self,voice=None,loggeri = None) -> None:
        self.queue = []
        self.logger = loggeri
        self.urltoindex = []
        self.repeat = "off"
        self.voice = voice
        self.cache = cacher(10,600,self.logger)
        self.volume = float(100)
        self.state = "Idle"
    def skipqueue(self):
        if self.state == "playing":
            self.state = "skipping"
            self.voice.stop()
            self.queue.pop(0)
            time.sleep(0.5)
            if len(self.queue)>0:
                oldrepeat = self.repeat
                self.repeat = "off"
                self.playfromqueue()
                self.repeat = oldrepeat
    def addqueue(self,url):
        while self.state == "removing":
            pass
        bytefp = BytesIO()
        self.logger.info(f"Finding if {url} still in cache before load/stream")
        datafromcache=self.cache.get(url)
        if not datafromcache:
            self.logger.info(f"no data with {url} in cache try load/stream")
            if url.startswith("http"):
                self.logger.info("Streaming Song From Youtube!")
                YouTube(url).streams.filter(only_audio=True).first().stream_to_buffer(bytefp)
                bytefp.seek(0)
            else:
                self.logger.info("[info]Loading Local-File")
                with open(url,"rb") as fp:
                    interact(bytefp, "write", fp.read())
            self.cache.set(url,interact(bytefp, "read"))
        else:
            self.logger.info("[info]Found! Load data from cache into queue")
            interact(bytefp, "write", datafromcache)
        self.urltoindex.append(url)
        self.queue.append(bytefp.read())
        if self.state == "Idle":
            self.state = "playing"
            self.playfromqueue()
    def removequeue(self,index):
        if self.state != "removing" and self.state != "skipping":
            oldstate = self.state
            self.state = "removing"
            index = int(index)
            index-=1
            if int(index) > 0:
                self.queue.pop(int(index))
            self.state = oldstate
    def queuedisplay(self):
        return_queue_string = "```\n"
        if len(self.urltoindex)>0:
            for i,u in enumerate(self.urltoindex):
                return_queue_string += f"{str(i+1)}){u}\n"
        else:
            return_queue_string += "no song in queue\n"
        return_queue_string += "```"
        return return_queue_string
    def updatevolume(self):
        self.voice.source.volume = self.volume/float(100)
    def nextsong(self):
        self.state = "played"
        self.logger.debug(f"repeat mode: {self.repeat}")
        if self.repeat != "once":
            if self.repeat == "all":
                
                if len(self.queue) > 0:
                    self.queue.append(self.queue[0])
                if len(self.urltoindex) > 0:
                    self.urltoindex.append(self.urltoindex[0])
            if len(self.urltoindex) > 0:
                self.urltoindex.pop(0)
            if len(self.queue) > 0:
                self.queue.pop(0)
        if len(self.queue) > 0:
            self.playfromqueue()
        else:
            self.state = "Idle"
    def playfromqueue(self):
        self.state = "playing"
        try:
            self.logger.info("Playing!")
            with tempfile.NamedTemporaryFile() as f:
                interact(f,"write",self.queue[0])
                if interact(f,"read"):
                    audio_file=discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f, executable='ffmpeg',pipe=True,before_options=None,options=None),self.volume/float(100))
                    self.voice.play(audio_file, after= lambda e:self.nextsong())
                else:
                    self.logger.error("NO BYTES")
                    self.nextsong()
        except discord.errors.ClientException as e:
            if e == "Already playing audio." or e == "Not connected to voice.":
                self.logger.error(e)
            else:
                self.logger.error(traceback.format_exc())
                self.nextsong()


