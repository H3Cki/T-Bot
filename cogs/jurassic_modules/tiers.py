import random

class Tier:
    T = -1
    VALUE_RANGE = (0,1)
    V_TYPE = int

    @classmethod
    def getValue(cls):
        return cls.V_TYPE(random.uniform(cls.VALUE_RANGE[0],cls.VALUE_RANGE[1]))

class DamageTier5(Tier):
    T = 5
    VALUE_RANGE = (1,10)

class DamageTier4(Tier):
    T = 4
    VALUE_RANGE = (10,20)

class DamageTier3(Tier):
    T = 3
    VALUE_RANGE = (20,30)

class DamageTier2(Tier):
    T = 2
    VALUE_RANGE = (30,40)

class DamageTier1(Tier):
    T = 1
    VALUE_RANGE = (40,50)


class DefenseTier5(Tier):
    T = 5
    VALUE_RANGE = (0,3)

class DefenseTier4(Tier):
    T = 4
    VALUE_RANGE = (3,5)

class DefenseTier3(Tier):
    T = 3
    VALUE_RANGE = (5,8)

class DefenseTier2(Tier):
    T = 2
    VALUE_RANGE = (9,13)

class DefenseTier1(Tier):
    T = 1
    VALUE_RANGE = (13,17)


class SpeedTier5(Tier):
    T = 5
    VALUE_RANGE = (0.4,0.6)
    V_TYPE = float

class SpeedTier4(Tier):
    T = 4
    VALUE_RANGE = (0.6,0.8)
    V_TYPE = float

class SpeedTier3(Tier):
    T = 3
    VALUE_RANGE = (0.8,1.0)
    V_TYPE = float

class SpeedTier2(Tier):
    T = 2
    VALUE_RANGE = (1.0,1.2)
    V_TYPE = float

class SpeedTier1(Tier):
    T = 1
    VALUE_RANGE = (1.2,1.4)
    V_TYPE = float

class HealthTier3(Tier):
    T = 5
    VALUE_RANGE = (30,60)

class HealthTier5(Tier):
    T = 4
    VALUE_RANGE = (60,90)

class HealthTier4(Tier):
    T = 3
    VALUE_RANGE = (90,120)

class HealthTier2(Tier):
    T = 2
    VALUE_RANGE = (120,160)

class HealthTier1(Tier):
    T = 1
    VALUE_RANGE = (160,200)


DAMAGE_TIERS = [DamageTier1,DamageTier2,DamageTier3,DamageTier4,DamageTier5]
DEFENSE_TIERS = [DefenseTier1,DefenseTier2,DefenseTier3,DefenseTier4,DefenseTier5]
SPEED_TIERS = [SpeedTier1,SpeedTier2,SpeedTier3,SpeedTier4,SpeedTier5]
HEALTH_TIERS = [HealthTier1,HealthTier2,HealthTier3,HealthTier4,HealthTier5]