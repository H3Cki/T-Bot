class Craftable:
    cost = [0,0,0]
    
    def getCraftCost(self):
        c = self.__class__
        if isinstance(c.cost,dict):
            return c.cost[self.tier_idx]
        else:
            return c.cost
        
    def canProfileCraft(self, profile):
        pr = profile.resources
        if pr.isGreaterThan(self.getCraftCost()):
            return True
        return False
    
    def _craft(self,profile):
        c = self.__class__
        return c(profile)
    
    def craft(self,profile):
        if self.canProfileCraft(profile):
            return self._craft(profile)
        else:
            raise Exception(f"❗ You do not have a matching key for {self.dropText}.")