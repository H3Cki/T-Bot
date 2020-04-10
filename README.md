# T-Bot
[WORK IN PROGRESS] discord bot with dinosaur-based minigame

#Logic
From time to time bot creates a voice channel in specified category, named by some dinosaur. When users enter the channel they are given a drop (part of a dino or entire dino). After few seconds channel disappears.
Bot rewards online members and those who are active on voice channel by passively giving resources.
Using collected parts and resources members can build dinosaurs in their lab and add them to their army.
Owned dinosaurs can be used to attack others and steal their resources.

# Run
```
$ python T-Bot.py
```

## Commands and Features
# Dinosaur discovery
Shows dino's info when first discovered, there are over 1100 dinosaurs in db.
![](screenshots/discovery.png)
# Command: !profile
Shows members profile.
![](screenshots/profile.png)
# Command: !lab
Shows build progress for dinos.
![](screenshots/lab.png)
# Command: !attack
Lets you attack another member and plunder his resources.
![](screenshots/attack.png)
# Command: !slot
The only currently implemented minigame, not balanced at all.
![](screenshots/slot.png)

