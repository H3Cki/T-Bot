from .entity import ProfileEntity
import discord
from datetime import datetime, timedelta


class Droppable:
    def drop(self, profile):
        profile_me = ProfileEntity(profile,self)
        Dbh.session.add(profile_me)
        
    @property
    def dropEmbed(self):
        e = Embed(title=member.display_name,description=f'{self.getEmoji()} **{static_part.dino_name.capitalize()}** {static_part.type}')
        footer = str((datetime.now()+timedelta(hours=1)).time())[:5]
        if nostorage:
            footer += f"\n{no_storage_warning}"
        e.set_footer( text= footer)
        return e