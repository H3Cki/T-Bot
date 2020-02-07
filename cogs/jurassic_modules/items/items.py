from item_info import StaticItem, ProfileItem
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String

class DinoChest(StaticItem):
    TYPE = "chest"