from .jurassicprofile import JurassicProfile as JP
from .dino_info import StaticDino
from .discovery import Discovery
from .part_info import StaticPart
from ..utils.dbconnector import DatabaseHandler as Dbh
#from .notifier import Notifier

class voiceStateUpdateHandler:
    def __init__(self,member,before,after,bot):
        self.member = member
        self.before = before
        self.after  = after
        self.bot = bot
        self.handle()
    
    def handle(self):
        if not self.after.channel:
            return
        if self.after.channel == self.before.channel:
            return
        
        if self.after.channel.name in [dino.name for dino in StaticDino.getAll()]:
            #notifier = Notifier()
            profile = JP.getProfile(self.member)
            if not profile:
                profile = JP(self.member.id,self.member.guild.id)
                Dbh.session.add(profile)

            static_dino = StaticDino.getDino(self.after.channel.name.lower())
            if not static_dino.discovered:
                static_dino.discover()
                disc = Discovery(static_dino.name,profile.id)

                profile.addExp(5)
                Dbh.session.add(disc)
                print(f"NEW DISCOVERY: {static_dino.name} FOUND by {profile.id}!")

            StaticPart.drop(static_dino,profile)
            profile.getAllParts()
            profile.buildDino(static_dino)
            profile.printOwnedDinos()
        Dbh.commit()