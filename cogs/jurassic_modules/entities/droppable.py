from .entity import ProfileEntity

class Droppable:
    def drop(self, profile):
        profile_me = ProfileEntity(profile,self)
        Dbh.session.add(profile_me)