import random

tier_chances = {
    5 : 15,
    4 : 40, 
    3 : 75, 
    2 : 90,
    1 : 100
}

tiers = {}

def getTier():
    roll = random.uniform(0,100)
    for tier,chance in tier_chances.items():
        if roll < chance:
            return tier
    return None

# for _ in range(50000):
#     tier = getTier()
#     if tier not in tiers.keys():
#         tiers[tier] = 0
#     tiers[tier] += 1
    
# for x in range(1,6):
#     print(f'{x} : {tiers[x]} - {round(100*tiers[x]/50000)}%')