import json
from bot import bot
import asyncio
from printdebug import printer
import sys
programloop = asyncio.new_event_loop()
logger = printer()
class client():
    def __init__(self, config, levellog):
        self.logger = logger
        self.loglevel = levellog
        self.event = asyncio.new_event_loop()
        self.client = bot(config, self.logger, loop=self.event)
    async def exit(self):
        self.event.close()
    def exiting(self):
        for task in asyncio.all_tasks(self.event):
            task.cancel()
        programloop.run_until_complete(self.exit())
    def run(self):
        self.logger.info("Start Client")
        try:
            self.event.run_until_complete(self.client.start(self.client.config["token"], bot=True))
        except KeyboardInterrupt:
            self.logger.debug("Calling shutingdown")
            self.event.run_until_complete(self.client.shutingdown())
            self.logger.debug("Calling close")
            self.event.run_until_complete(self.client.close())
            self.logger.debug("Canceling All Task")
            self.exiting()
            self.logger.debug("Closing Program Async Loop")
            programloop.close()
            self.logger.info("Saving Config")
            configfile = open("config.json","w")
            json.dump(self.client.config, configfile, indent="  ")
            configfile.close()
            self.logger.info("Saved Config")
        finally:
            self.logger.info("Client Exited")
argv = sys.argv
argv.pop(0)
if len(argv) < 1:
   argv=["info"]
debuglevel = 1
if argv[0] == "debug":
    debuglevel = 4
elif argv[0] == "error":
    debuglevel = 3
elif argv[0] == "warn":
    debuglevel = 2
elif argv[0] =="info":
   debuglevel = 1
elif argv[0] == "slient":
   debuglevel = 0
logger.level = debuglevel
logger.debug("mode:", argv, "level:", debuglevel)
configfile = open("config.json", "r")
clientc = client(json.load(configfile), debuglevel)
configfile.close()
clientc.run()
