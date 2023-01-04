# HAL-AIG-Assignment-
## Objective
	
The aim of the assignment is to assess the student's ability to implement artificial intelligence techniques in a game called Heroes of Ancient Legends (HAL), a Mobile Online Battle Arena (MOBA)-style game. You will be required to do your own research, code your own strategies and test them thoroughly.

## Scope

Working in a team of 3 students, you are required to devise and implement an overall strategy for your team. In addition, each team member is in charge of coding the AI for one of the hero characters: Knight, Archer or Wizard.  

## HAL Game Design

In the game of HAL, three good heroes have arrived in the Orc lands. They have agreed to help the good local Orc tribe to defeat their evil sworn enemies. However, the evil Orc tribe has also enlisted the help of three evil heroes, and the battle will be swift and bloody.

The three heroes will support a never-ending horde of Orc soldiers. Unlike the orcs, heroes can improve their abilities by leveling up as they deal damage. 

To win the game, you have to either destroy the opposing tribe’s base or have the most points when the time limit has expired.


### Heroes

Each side has three heroes:

*	Knight: A sturdy warrior with lots of hit points who deals melee damage
*	Archer: A quick ranged fighter who can rapidly fire arrows from a distance
*	Wizard: A magic-user whose fireballs hit a large area, but these deadly spells take some time to recharge

Unlike Orcs, heroes respawn after 5 seconds when killed. In addition, heroes may heal up a portion of their hit points, **_but they then cannot attack for a period of time._**

A hero can level up when he deals 100 damage. After the first level up, he needs an additional 100 damage to level up again (i.e., to level up a second time, he needs to deal 200 damage; to level up a third time, he must deal 300 damage, and so on). When leveling up, the hero can choose to improve the following:

*	Hit points
*	Movement speed
*	Melee damage
*	Melee cooldown
*	Ranged damage
*	Ranged cooldown
*	Projectile range
*	Healing amount
*	Healing cooldown


### Towers and Bases

Bases fire boulders at the closest opposing unit. Each base is defended by two towers that also fire boulders at opponents. The towers can be attacked.

In addition, there is a neutral tower at the centre of the map that fires at the closest unit. The neutral central tower cannot be attacked.


### Orcs

Each base produces an unlimited supply of Orcs. The orcs will randomly choose one of 4 paths towards the enemy base, and will attack any opposing unit they come across.


### Points

Teams gain points by killing opponents:
*	Orc: 10 points
*	Hero: 40 points
*	Tower: 100 points
*	Base: 500 points

Note that your team wins the game as soon as you destroy your opponent’s base. Points will decide the winner only if time runs out and neither base is destroyed.
 
## Tasks

Each team is to devise an overall strategy for their team. Each student will be in charge of a different hero, and will have to design and implement the AI for their assigned hero.

You main challenge is to defeat the given AI in Easy and Hard mode. In Easy mode, the AI has no advantage over you. In hard mode, the AI heroes, base and towers have an additional 15% hit points and damage.


### Overall Strategy

In your report, describe your overall strategy and explain why it is effective. You may wish to include the following:

* How you came up with your strategy
* What was observed during playtesting, and the resulting changes
* Strengths and weaknesses of your strategy


### Individual Hero Strategy

Each student is to design and implement the strategy for one hero. In your report, you should include the following:

* Overall approach
*	Approach to leveling up
*	How to decide on a target to attack
*	Use of healing, if applicable

Note that there is no friendly fire in this game, i.e., you will not be able to hit units from your own team.


### Restrictions

You are only allowed to implement the AI for the heroes, which may include adding, removing or modifying states. You are **_not_** allowed to change the AI for Orcs, Bases or Towers.

You are not allowed to directly change the attributes for your heroes. You are only allowed to affect the attributes of your heroes using the following methods:

*	Knights may only attack using Character.melee_attack(target): 
    * target is a Character. The Knight will deal its damage to the target if it is colliding with it.
*	Archers may only attack using Character.ranged_attack(target_position):
    * target_position is a Vector2. The Archer will fire an arrow, and the arrow will hit and damage the first opponent it hits and then disappear.
*	Wizards may only attack using Character.ranged_attack(target_position, explosion_image):
    *	target_position is a Vector2. explosion_image is an image. The Wizard will fire a fireball, and the fireball will only explode when it hits reaches target_position, damaging all opponents that collide with the explosion.
*	All heroes can heal using Character.heal(). However, the hero will not be able to attack for Character.healing_cooldown seconds.
•	All heroes can level up using Character.level_up(stat). If the hero has enough XP, he will level up one attribute; otherwise the method does nothing. The possible values for stat are:
    *	_hp_: increase hit points by 10%
    *	_speed_: increase movement speed by 10%
    *	_melee damage_: increase melee damage by 10%
    *	_melee cooldown_: make melee cooldown faster by 10%
    * _ranged damage_: increase ranged damage by 10%
    *	_ranged cooldown_: make ranged cooldown faster by 10%
    *	_projectile range_: increase projectile range by 10%
    *	_healing_: increase healing amount by 20%
    *	_healing cooldown_: make healing cooldown faster by 10%


### Competition

There will be a head-to-head double round robin competition between all teams. Each team’s AI will compete against the other teams’ AI twice, once as the Blue team and once as the Red team. Teams will score as follows:

*	Destroy opposing base: 3 points
*	Win by points after time runs out: 2 points
*	Lose by points after time runs out: 1 point
*	Own base destroyed: 0 points

If multiple teams have the same number of points, ties will be broken as follows:
*	Most bases destroyed
*	Most time remaining from bases destroyed
*	Most points from games after time runs out

Every member of a team will be awarded up to 5 bonus marks depending on the result of the competition (subject to change depending on number of teams):

*	1st: 5 marks
*	2nd-3rd: 4 marks
*	4th-5th: 3 marks
*	6th-7th: 2 marks
*	8th-9th: 1 mark

## Deliverables

a)	The final submission deadline for the assignment is on ***Thursday 21st January 2021, 2pm.*** The submission consists of the following:

*	Report in Microsoft word document format that clearly indicates:
    *	Cover page with team members’ names, student IDs and group name
    *	Overview of team strategy
    *	Description of individual strategy for each hero, including a state machine diagram
    *	Other relevant appendices (diagrams, references to online resources, etc.) wherever appropriate
* [Individual] Python files in the following naming format:

[hero name]_[team name].py

For example, if you are coding the AI for the Knight and your team name is TeamA, then your filename will be Knight_TeamA.py. In addition, all the state classes in your file should have the suffix _TeamA.

**Note 1:** You are required to upload your python file to the MeL assignment folder *ARTIFICIAL INTELLIGENCE FOR GAMES > ASSIGNMENT.*

**Note 2:**  A penalty of 10 marks per day from Thursday 21st January 2021 onwards will be applied for late submission.

* There will be a presentation on your team and individual strategies from 21st January 2021. The head-to-head competition will be held on the week of 28th January 2021 after all the presentations have been completed.

For the 15-minute presentation:
* Team
    *Overview of team strategy
* Individual
    *	Descriptions of hero strategies
    *	Explanation of implementation
    * Q&A

## Marking Scheme

### Team work (40%)

* Overall strategy write-up (10 marks)
    *	Explanation of strategy, analysis of why it is effective

* Defeat easy level (10 marks)
    *	Consistently defeat opponents

* Defeat hard level (10 marks)
    *	Consistently defeat opponents with RED_MULTIPLIER = 1.15

* Group demo and presentation (10 marks)
    * Comprehensiveness, clarity

* Competition (5 bonus marks)
    *	Ranking in head-to-head competition


### Individual Work (60%)

* Strategy write-up (20 marks)
    * Combat tactics
    * Level-up strategy

* Implementation of AI (20 marks)
    * Proper use of states
    * Correctness

* Individual presentation (20 marks)
    * Show understanding of implementation of AI
