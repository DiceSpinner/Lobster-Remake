# Lobster-Remake
Remake of the game I wrote back in g11. (See https://github.com/DiceSpinner/lobster/tree/master/mike.yuan)

The goal of this project is to gain experience in building up programs of larger scale with application of materials learned in CSC148 at UofT (data structures, OOP inheritance, etc) as well as exploring new python features. The game will have the same features as its predecessor with some improvements/generalization as well some new mechanics. Currently I'm focusing on the design of the gameplay system and building up the frame of the game before filling in the content, so there won't be that much gameplay update in the near future, but I will try add more content throughout the process. 

Checkout Game_Structure.pdf for more info about how the game runs if you're interested. (Will be updated irregularly)

Video Clips:
- https://streamable.com/vlb1jn

Implemented Features:
- Dynamic tile map
- Zoomable Camera
- Customizable Tile Map
- Customizable Attack Texture 
- Collision Detection between circles and axis-aligned squares 
- Customizable tile lighting 
- Particle Action System
- Living Particles
- Omni-Directional Particle Movement 
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

Planned Features:
- Layered tile maps
- Particle Animation
- Sounds/Music
- GUI Title Screen, Pause Menu, Inventory Menu and etc.

PS: There's no death event atm so the game will simply crash when the player is dead.
