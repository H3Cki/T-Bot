from .entities.entity import Entity, ProfileEntity
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from ..utils.dbconnector import DatabaseHandler as Dbh    



class StaticPart(Entity):
    # CLASS ATTRIBUTES --------------------- #
    DROPS_AS = ProfileEntity
    PARENT = Entity
    
    TYPE   = "part"
    NAME   = "Item Part"
    TIERED = False
    
    PART_TYPES = []
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    
    parent = Column(Integer, ForeignKey(Entity.entity_id))

    id = Column(Integer, primary_key=True)
    parent_entity_id = Column(String, ForeignKey(PARENT.entity_id))
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }
    

    def __init__(self,parent):
        self.parent_entity_id = parent.entity_id
        
    def getEmoji(self,**kwg):
        return PartTypes.emojis[self.type+kwg.get('extra','')]
    
    @property
    def name(self):
        return self.NAME

    @property
    def parent(self):
        return self.PARENT.get(name=self.dino_name)

    @property
    def briefText(self):
        text = f"{self.emoji} {self.name}"
        return text

    @property
    def type(self):
        return DinoPartTypes.types[self.type_idx]

    @property
    def emoji(self):
        return DinoPartTypes.emojis[self.type]
    
    @classmethod
    def create(cls,parent,**kwargs):
        obj = cls(parent)
        for 
    @classmethod
    def selectForDrop(cls,profile,dino):
        static_parts = dino.getPartsRequired()
        
        if random.randint(0,100) <= 60:
            unowned = []
            for sp in static_parts:
                if not ProfilePart.getProfileEntity(profile,sp):
                    unowned.append(sp)
        else:
            unowned = static_parts
        if len(unowned) == 0:
            unowned = static_parts
            
        return random.choice(unowned)
         

    
    @classmethod
    def update(cls, dinolist):
        for dino in dinolist:
            for t in range(0,len(PartTypes.types)):
                part = cls.getEntity(dino.name,t)
                if not part:
                    p = cls(dino.name,t)
                    Dbh.session.add(p)
                    print(f"CREATING {p.name}")

        Dbh.session.commit()


    @classmethod
    def removeDinoPartComplelty(cls,dino):
        for part in StaticPart.getAll():
            if part.dino_name == dino.name:
                for ppart in ProfilePart.getAll():
                    if ppart.part_id == part.id:
                        Dbh.session.delete(ppart)
                        print(f"DELETED OWNED PART")
                Dbh.session.delete(part)
                print(f"DELETED {part.dino_name} {part.type}")
                Dbh.session.commit()