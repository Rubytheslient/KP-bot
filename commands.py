import random
import discord
from discord.utils import get
import asyncio
import math
import os
import custommath
from musicplayer import musicplayer

class message_modified(discord.Message):
    def __init__(self,msg,command,args)->discord.Message:
        self.msg = msg
        self.Command = command
        self.Arguments = args
    async def lifetime(self,givenlifetime):
        await asyncio.sleep(givenlifetime)
        await self.delete()
defaultproperties = {
    "repeat":"off",
    "volume":100,
    "prefix":"&"
}
class commands():
    def __init__(self, client:discord.Client,prefix:str = None,guildid:str=None,guildconfigi:dict={}) -> None:
        self.client = client
        self.logger = client.logger
        self.voice = None
        self.guildid = guildid
        self.guildconfig = guildconfigi
        for proper in defaultproperties:
            if not proper in self.guildconfig:
                self.guildconfig[proper] = defaultproperties[proper]
        self.isdestroying = False
        self.musicplayer = musicplayer(self.voice,self.logger)
        self.musicplayer.volume = self.guildconfig["volume"]
        
    async def parse_command(self,msg):
        parsed= await self.__parse_args(msg)
        func = getattr(self,parsed.Command)
        if not func:
            return
        self.logger.debug(f"calling function {parsed.Command}")
        await func(parsed)

    async def __parse_args(self,msg):
        spilted = msg.content.split(" ")
        command = spilted[0][len(self.guildconfig["prefix"]):]
        spilted.pop(0)
        return message_modified(msg,command,spilted)

    async def help(self,m):
        if not self.isdestroying:
            help = """```reload     : reload command
loadplugin : load plugin
ping       : Send Discord API latency as ms
settings   : Config discord bot settings
play       : Play song from youtube
join       : Join voice channel
leave      : Leave voice channel
volume     : Change Volume
repeat     : Repeat song
addword    : Add word for bot to response
removeword : Remove word from response List
eightball  : Answers your question 
coinfilp   : Random Between Head and Tails
"""
            if self.logger.level >= 4:
                help+="\ntest     : Test if bot still functional"
            help+="```"
            await m.msg.channel.send(help)
    async def __find_word(self,args):
        splited = []
        adduntilfoundother = False
        word = ""
        for arg in args:
            for char in arg:
                if char == "\"" and not adduntilfoundother:
                    adduntilfoundother = True
                elif char == "\"" and adduntilfoundother:
                    splited.append(word)
                    word = ""
                    adduntilfoundother = False
                elif adduntilfoundother:
                    word += str(char)
            if adduntilfoundother:
                word +=" "
        return splited
            
    async def addword(self, m):
        if len(m.Arguments) < 1:
            await m.msg.channel.send("```Usage: addword \"response\" \"word\"```")
            return
        Arguments = await self.__find_word(m.Arguments)
        response = await self.__find_word(m.Arguments)
        self.logger.debug(Arguments)
        response.pop(0)
        if not Arguments[0] in self.client.wordlists[str(self.guildid)]["Chat"]:
            self.client.wordlists[str(self.guildid)]["Chat"][Arguments[0]] = []
        for res in response:
            if Arguments[0] == res:
                res = Arguments[1]
            self.client.wordlists[str(self.guildid)]["Chat"][Arguments[0]].append(res)

    async def removeword(self, m):
        if len(m.Arguments) < 1:
            await m.msg.channel.send("```Usage: removeword \"response\"```")
            return
        Arguments = await self.__find_word(m.Arguments)
        self.logger.debug(Arguments)
        if Arguments[0] in self.client.wordlists[str(self.guildid)]["Chat"]:
            self.client.wordlists[str(self.guildid)]["Chat"][Arguments[0]] = []
            self.logger.debug("in word list",self.client.wordlists[str(self.guildid)]["Chat"][Arguments[0]])
        else:
            self.logger.debug(self.client.wordlists[str(self.guildid)]["Chat"])

    async def join(self, m):
        if not self.isdestroying:
            if not discord.opus.is_loaded():
                if os.path.exists('/data/data/com.termux/files/usr/lib/libopus.so'):
                    discord.opus.load_opus("/data/data/com.termux/files/usr/lib/libopus.so")
                elif os.path.exists("clib\linux\libopus.so"):
                    discord.opus.load_opus("clib\linux\libopus.so")
            msg=m.msg
            channelvc = msg.author.voice.channel
            self.voice = get(self.client.voice_clients,guild=msg.guild)
            self.logger.debug(f"joining {channelvc}")
            if self.voice and self.voice.is_connected():
                await self.leave()
            self.voice = await channelvc.connect()
            self.musicplayer.voice = self.voice

    async def play(self,m):
        if not self.voice:
            await self.join(m)
        if self.voice:
            url = " ".join(m.Arguments)
            self.logger.debug(f"adding {url} to queue")
            self.musicplayer.addqueue(url)
        else:
            await m.msg.channel.send("Error: No Voice Client In Guild")

    async def leave(self,_ = None):
        if self.voice and self.voice.is_connected():
            self.logger.debug("disconnecting")
            await self.voice.disconnect()

    async def volume(self,m):
        if self.voice:
            self.logger.debug(f"Volume: {m.Arguments[0]}")
            oldvolume = self.voice.source.volume*100
            self.logger.debug(f"interpolating {oldvolume} -> {float(m.Arguments[0])}")
            for i in range(1,10001,1):
                num = custommath.LerpNumber(float(oldvolume), (float(m.Arguments[0])), float(i)/float(10000))
                self.musicplayer.volume = num
                self.musicplayer.updatevolume()
                await asyncio.sleep(1/10000)
            self.logger.debug(f"interpolated {oldvolume} -> {float(m.Arguments[0])}")
            self.musicplayer.volume = float(m.Arguments[0])
            self.guildconfig["volume"] = self.musicplayer.volume
            self.musicplayer.updatevolume()

    async def queuelist(self,m):
        await m.msg.channel.send(self.musicplayer.queuedisplay())

    async def skip(self,m):
        self.logger.debug("skipping song")
        self.musicplayer.skipqueue()

    async def repeat(self,m):
        if m.Arguments:
            self.logger.debug(f"repeat mode: {m.Arguments[0]}")
            self.musicplayer.repeat = m.Arguments[0]
            self.guildconfig["repeat"] = self.musicplayer.repeat
        else:
            await m.msg.channel.send("""```
Usage: repeat off|once|all
\t\toff  | turn off repeat mode
\t\tonce | single mode
\t\tall  | loop through queue mode
```""")

    async def ping(self,m) -> None:
        await m.msg.channel.send(f"Ping Discord API:{math.floor(self.client.latency*100000)/100}ms")

    async def test(self,m) -> None:
        if self.logger.level >= 4:
            await m.msg.channel.send(f"testing {math.floor(self.client.latency*100000)/100}ms {self.client.user.name}")

    async def settings(self, m):
        if len(m.Arguments)> 0:
            try:
                if len(m.Arguments) == 1:
                    await m.msg.channel.send(f"```{m.Arguments[0]}: {self.guildconfig[m.Arguments[0]]}```")
                elif len(m.Arguments)> 1:
                    self.guildconfig[m.Arguments[0]] = m.Arguments[1]
                    self.client.update_prefix(self.guildid)
                    await m.msg.channel.send("Updated Guild Config")
            except:
                await m.msg.channel.send("Update Guild Config Fail")
        else:
            await m.msg.channel.send("""```
Usage:setting index value
\t\tprefix | new_prefix
\t\trepeat | once|all|off
\t\tvolume | 1-100
            ```""")
    async def eightball(self,m):
        replies = ["Yes","No","Maybe"]
        if len(m.Arguments) >= 1:
            await m.msg.channel.send(f"```Q: {m.Arguments[0]}\nA: {random.choice(replies)}```")
        else:
            await m.msg.channel.send(f"```Usage: eightball Question\n\t\t Question | thing you want to ask {self.client.user.name}```")
    async def coinfilp(self,m):
        coinfilp = ["t","h"]
        listcoinfilped = []
        coins = 1
        if len(m.Arguments)>0:
            coins = int(m.Arguments[0])
        coins = custommath.clamp(1,coins,3)
        for _ in range(0, coins):
            choice = random.choice(coinfilp)
            match choice:
                case "t":
                    listcoinfilped.append("Tails")
                case "h":
                    listcoinfilped.append("Head")
        await m.msg.channel.send(" ".join(listcoinfilped))
    async def destroy_command(self):
        self.isdestroying = True
        self.musicplayer.queue = []
        self.musicplayer.urltoindex = []
        self.musicplayer.repeat = "off"
        if self.voice:
            if self.voice.is_playing:
                self.voice.stop()
        await self.leave()
        self.prefix = None
        self.client = None
        self.musicplayer.cache.stop = True
        self.musicplayer.cache.thread.join()
        self.isdestroying = False
