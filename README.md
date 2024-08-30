# Lobster-Remake
Remake of the game I wrote back in g11. (See https://github.com/DiceSpinner/lobster/tree/master/mike.yuan)

The goal of this project is to gain experience in building up programs of larger scale with application of materials learned in CSC148 at UofT (data structures, OOP inheritance, etc) as well as exploring new python features. The game will have the same features as its predecessor with some improvements/generalization as well some new mechanics. Currently I'm focusing on the design of the gameplay system and building up the frame of the game before filling in the content, so there won't be that much gameplay update in the near future, but I will try add more content throughout the process. 

See Game_Structure.pdf for more info about how various systems are organized.

Requires: Python 3.7.0 or newer, pygame 2.0.0 or newer
To run the game, simply open main.py in an IDE and run.

[Game Scene](./Lobster%20Remake.mp4)

## Implemented Features
- Dynamic tile map
- Zoomable Camera
- Customizable Tile Map
- Customizable Attack Visual
- Collision Detection between circles and axis-aligned squares 
- Customizable tile lighting 
- Action System
- Health/Damage Entity System 
- Omni-Directional Sprite Movement 
- Melee/Ranged AOE Attack 
- Guarding
- Basic Player Control 
   - WASD - Move
   - Mouse movement - Aiming
   - Spacebar - Launch Fireball
   - Mouse Left Click: Melee AOE Attack
   - Hold Mouse Right Button: Guard (Reduces Incoming Damage)
    - Hold Left-Tab: View Inventory
    - F: Interact (i.e pick up items, open doors)
    - Up/Down Arrow Key: Zoom in/out
    - Hold L_Shift: Sprint (Boosts movement speeed)
- Item/Inventory System

## Planned Features
- Layered tile maps
- Particle Animation
- Sounds/Music
- GUI Title Screen, Pause Menu, Inventory Menu and etc.

## What Is there
Currently there are no meaningful gameplay just yet. Game mechanics were implemented but not content is filled. NPCs in the scene have a placeholder AI in effect to test out entity damage/health system. Some items and doors are left in to test out the interaction & inventory system.

Map, Block, Item & Entity data can be edited in the corresponding text files. Use existing data for reference to the editing format. There's a simple expression evaluator that takes in string expression and evaluates it as the death condition for the entity.

It is normal for the game to crash as the player dies since the GUI functions does not verify invalid data computed using health number of 0.

## Remark
The game is still largely unfinished. I've only managed to create the general structure of how things should be filled in. The features listed in the previous section will take quite a while to implement as everything must be done from scratch. As of now, this project is not of high priority to finish not only because I've got other more important tasks at hand but also it has already served its purpose well as I've gained valuable software engineering experience and realized there are issues with the current system layout and it could use a complete redesign when I get back in the future and it'd be a massive amount of work on its own.
