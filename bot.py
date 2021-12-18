import discord
import importlib
import commands
import json
from database_client import database_client

database = database_client()

class bot(discord.Client):
    def __init__(self, config, loggeri, *, loop=None, **options):
        self.config = config
        self.logger = loggeri
        database.logger = self.logger
        self.commands = {}
        self.wordlists = {}
        self.plugins={}
        self.modules={}
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        self.logger.info(f"Login as {self.user.name}")

    async def loadplugin(self,name):
        self.modules[name] = importlib.import_module(name)
        self.plugins[name] = self.modules[name].main(self)

    async def on_message(self,message):
        if not message.guild:
            return
        if not message.guild.id in self.commands:
            guildconfig = {}
            self.logger.debug("Fetching Data From Database")
            fetched = self.fetchdatafromdatabase(f"GuildConfig_{message.guild.id}")
            self.logger.debug(f"Fetched Data From Database {fetched} {type(fetched)}")
            if fetched and type(fetched) == bytes and fetched != "0":
                guildconfig = json.loads(fetched)
            if not "prefix" in guildconfig:
                guildconfig["prefix"] = self.config["DefaultPrefix"]
            self.config["prefixes"][message.guild.id] = guildconfig["prefix"]
            self.commands[message.guild.id] = commands.commands(self,self.config["prefixes"][message.guild.id],message.guild.id,guildconfig)
        if message.guild:
            if message.guild.id in self.config["prefixes"]:
                prefix = self.config["prefixes"][message.guild.id]
            else:
                self.config["prefixes"][message.guild.id] = self.config["DefaultPrefix"]
                prefix = self.config["prefixes"][message.guild.id]
        else:
            prefix = self.config["DefaultPrefix"]

        
        if not str(message.guild.id) in self.wordlists and (str(message.author) != str(self.user)):
            data = database.get(str(message.guild.id)+"_wordlist")
            if not data:
                self.logger.debug("No Data From Database Load Default WordList")
                data = database.get("defaultwordlist")
            if not data:
                data = b"{\"DiscordEvent\": {\"New member\": \"\\u0e22\\u0e34\\u0e19\\u0e14\\u0e35\\u0e15\\u0e2d\\u0e19\\u0e23\\u0e31\\u0e1a\\u0e19\\u0e30\\u0e04\\u0e30 \\u0e04\\u0e38\\u0e13 {{REPLACE}} \\u0e2d\\u0e22\\u0e48\\u0e32\\u0e25\\u0e37\\u0e21\\u0e44\\u0e1b\\u0e2d\\u0e48\\u0e32\\u0e19 {{REPLACE0}} \\u0e01\\u0e31\\u0e1a {{REPLACE1}} \\u0e14\\u0e49\\u0e27\\u0e22\\u0e19\\u0e30\\u0e04\\u0e30\", \"Member Leave\": \"\\u0e02\\u0e2d\\u0e43\\u0e2b\\u0e49\\u0e42\\u0e0a\\u0e14\\u0e14\\u0e35\\u0e19\\u0e30\\u0e04\\u0e30 \\u0e04\\u0e38\\u0e13 {{REPLACE}}\", \"\\u0e15\\u0e2d\\u0e19\\u0e23\\u0e31\\u0e1a\\u0e04\\u0e19\\u0e40\\u0e02\\u0e49\\u0e32 voicechat\": \"\\u0e2a\\u0e27\\u0e31\\u0e2a\\u0e14\\u0e35\\u0e19\\u0e30\\u0e04\\u0e30 \\u0e04\\u0e38\\u0e13 {{REPLACE}}\", \"\\u0e1a\\u0e2d\\u0e01\\u0e25\\u0e32\\u0e04\\u0e19\\u0e2d\\u0e2d\\u0e01 voicechat\": \"\\u0e44\\u0e27\\u0e49\\u0e21\\u0e32\\u0e40\\u0e08\\u0e2d\\u0e01\\u0e31\\u0e19\\u0e43\\u0e2b\\u0e21\\u0e48\\u0e19\\u0e30\\u0e04\\u0e30 \\u0e04\\u0e38\\u0e13 {{REPLACE}}\"}, \"Chat\": {\"\\u0e2a\\u0e27\\u0e31\\u0e2a\\u0e14\\u0e35\\u0e04\\u0e48\\u0e30\": [\"\\u0e2a\\u0e27\\u0e31\\u0e2a\\u0e14\\u0e35 {{self.user.name}}\"], \"\\u0e1d\\u0e31\\u0e19\\u0e14\\u0e35\\u0e19\\u0e30\\u0e04\\u0e30\": [\"\\u0e1d\\u0e31\\u0e19\\u0e14\\u0e35\\u0e19\\u0e30{{self.user.name}}\"], \"\\u0e40\\u0e23\\u0e32 \\u0e2d\\u0e32\\u0e22\\u0e38 18(\\u0e2d\\u0e19\\u0e31\\u0e19\\u0e15\\u0e4c) \\u0e1b\\u0e35 \\u0e04\\u0e48\\u0e30\": [\"\\u0e2d\\u0e32\\u0e22\\u0e38\\u0e40\\u0e17\\u0e48\\u0e32\\u0e44\\u0e23\\u0e2b\\u0e23\\u0e2d {{self.user.name}}\"]}}"
            try:
                if not self.wordlists[str(message.guild.id)] == 0:
                    wordlist = self.wordlists[str(message.guild.id)] = json.loads(data)
            except:
                self.wordlists[str(message.guild.id)] = data
            self.wordlists[str(message.guild.id)] = json.loads(data)
        if (str(message.author) != str(self.user)):
            wordlist = self.wordlists[str(message.guild.id)]
            for propertye in wordlist["Chat"]:
                for value in wordlist["Chat"][propertye]:
                    self.logger.debug(f"{value.replace('{{self.user.name}}',self.user.name)}","==",f"{message.content}")
                    if value.replace("{{self.user.name}}",self.user.name) == message.content:
                        await message.channel.send(propertye)
        
        if message.content.startswith(prefix):
            if message.content == prefix+"reload":
                self.logger.info("Reload_Module!")
                importlib.reload(commands)
                old = self.commands[message.guild.id]
                old.musicplayer.cache.clear_cache()
                self.commands[message.guild.id] = commands.commands(self,prefix,message.guild.id)
                self.commands[message.guild.id].guildconfig = old.guildconfig
                self.commands[message.guild.id].voice = old.voice
                self.commands[message.guild.id].musicplayer = old.musicplayer
                return
            elif message.content == prefix+"loadplugin":
                pluginname = message.content.replace(prefix+"loadplugin ","")
                if not pluginname in self.plugins:
                    self.loadplugin(pluginname)
                else:
                    importlib.reload(self.modules[pluginname])
            await self.commands[message.guild.id].parse_command(message)

    def update_prefix(self,guild_id):
        self.config["prefixes"][guild_id] = self.commands[guild_id].guildconfig["prefix"]

    def fetchdatafromdatabase(self,key)->bytes:
        raw_data = database.get(key)
        return raw_data

    def putdatatodatabase(self,key,data:str):
        data = data.encode('utf-8')
        database.set(key,data)

    async def shutingdown(self):
        database.cache.stop = True
        database.cache.thread.join()
        for guild_id in self.wordlists:
            jsdumped = json.dumps(self.wordlists[guild_id])
            self.logger.debug("Json Dump",jsdumped)
            self.putdatatodatabase(f"{guild_id}_wordlist",jsdumped)
        for guild_id in self.commands:
            jsdumped = json.dumps(self.commands[guild_id].guildconfig)
            self.logger.debug("Json Dump",jsdumped)
            self.putdatatodatabase(f"GuildConfig_{guild_id}",jsdumped)
            await self.commands[guild_id].destroy_command()
        database.redisclient.save()
