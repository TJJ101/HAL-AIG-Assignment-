import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Knight_BingChiling(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None

        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.
        self.levelCount = 0

        seeking_state = KnightStateSeeking_BingChiling(self)
        attacking_state = KnightStateAttacking_BingChiling(self)
        ko_state = KnightStateKO_BingChiling(self)
        sticking_state = KnightStateStick_BingChiling(self)
        defend_state = KnightStateDef_BingChiling(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(sticking_state)
        self.brain.add_state(defend_state)

        self.brain.set_state("defend")
        

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)

        if self.can_level_up():
            if self.levelCount <=2:
                self.level_up("healing")
            else:
                self.level_up("hp")
            self.levelCount += 1
            

   


class KnightStateSeeking_BingChiling(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight

        self.knight.path_graph = self.knight.world.paths[0]


    def do_actions(self):
        self.knight.velocity = self.knight.move_target.position - self.knight.position
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):
        
        if self.knight.current_hp <= (0.8 * self.knight.max_hp):
            self.knight.heal()

        
        
        # check if opponent is in range
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
       
        if nearest_opponent is not None:
            
            nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                self.knight.target = nearest_opponent
                
                return "attacking"
            
  

            
            
        
        if (self.knight.position - self.knight.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None


    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)

        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position

        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


class KnightStateAttacking_BingChiling(State):

    def __init__(self, knight):

        State.__init__(self, "attacking")
        self.knight = knight

    def do_actions(self):

        # colliding with target
        if pygame.sprite.collide_rect(self.knight, self.knight.target):
            self.knight.velocity = Vector2(0, 0)
            self.knight.melee_attack(self.knight.target)

            

        else:
            self.knight.velocity = self.knight.target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):
        if self.knight.current_hp <= (0.8 * self.knight.max_hp):
            self.knight.heal()
        # target is gone
        if self.knight.world.get(self.knight.target.id) is None or self.knight.target.ko:
            self.knight.target = None
            return "sticking"
        
            
        return None

    def entry_actions(self):

        return None

class KnightStateStick_BingChiling(State):

    def __init__(self, knight):

        State.__init__(self, "sticking")
        self.knight = knight

    def do_actions(self):
        
        #stick to the wizard
        if self.knight.target is not None:
            if self.knight.target.name == "wizard":
                if self.knight.position[0] > 969:
                    self.knight.velocity = self.knight.target.position - self.knight.position + Vector2(0,45)
                else:
                    self.knight.velocity = self.knight.target.position - self.knight.position + Vector2(45,0)
                if self.knight.velocity.length() > 0:
                    self.knight.velocity.normalize_ip();
                    self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):
        #set wizard as target
        wizard_target = self.knight.world.get_entity("wizard")
        if wizard_target.team_id == self.knight.team_id:
            self.knight.target = wizard_target


        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
       
        if nearest_opponent is not None:
            
            nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                self.knight.target = nearest_opponent
                return "attacking"
        
        #if hp below 80% then heal
        if self.knight.current_hp <= (0.8 * self.knight.max_hp):
            self.knight.heal()

        #incase the knight gets stuck    
        if self.knight.position.distance_to(self.knight.target.position) >=200:
            return "seeking"

    def entry_actions(self):

        return None

class KnightStateDef_BingChiling(State):

    def __init__(self, knight):

        State.__init__(self, "defend")
        self.knight = knight

    def do_actions(self):

        if self.knight.move_target is not None:
            self.knight.velocity = self.knight.move_target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed



    def check_conditions(self):

        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
       #changet he target to be bottom left of screen afterknight has reached the first location
        if self.knight.position[0] >= 260:
            self.knight.move_target.position = Vector2(158,216)
       
        #check if got nearest opponent and knight has reached the second position/node
        if nearest_opponent is not None and self.knight.position[1] >= 216:
            
            nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                self.knight.target = nearest_opponent
                return "attacking"
            else:
                return "seeking"

        


    def entry_actions(self):
        #target to be the top right of base
        self.knight.move_target.position = Vector2(260,111)

class KnightStateKO_BingChiling(State):

    def __init__(self, knight):

        State.__init__(self, "ko")
        self.knight = knight

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.knight.current_respawn_time <= 0:
            self.knight.current_respawn_time = self.knight.respawn_time
            self.knight.ko = False
            self.knight.path_graph = self.knight.world.paths[0]
            return "defend"
            
        return None

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None
