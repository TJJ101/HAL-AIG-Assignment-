import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Archer_BingChiling(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None

        self.statChoice = 0

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        self.dodge = False

        seeking_state = ArcherStateSeeking_BingChiling(self)
        attacking_state = ArcherStateAttacking_BingChiling(self)
        ko_state = ArcherStateKO_BingChiling(self)
        dodge_state = ArcherStateDodge_BingChiling(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(dodge_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        #level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        level_up_stats = ["ranged cooldown", "ranged cooldown", "projectile range", "ranged damage", "ranged cooldown"]
        if self.can_level_up():
            self.level_up(level_up_stats[self.statChoice])
            if(self.statChoice == len(level_up_stats) - 1):
                self.statChoice = 0
            else:
                self.statChoice += 1


class ArcherStateSeeking_BingChiling(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        #self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]
        self.archer.path_graph = self.archer.world.paths[0]



    def do_actions(self):

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"
        
        if (self.archer.position - self.archer.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position


class ArcherStateAttacking_BingChiling(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer

    def do_actions(self):

        opponent_distance = (self.archer.position - self.archer.target.position).length()
        opp_pos = self.archer.position - self.archer.target.position
        opp_pos.normalize_ip()

        nearest_opp_distance = (self.archer.position - self.archer.world.get_nearest_opponent(self.archer).position).length()
        
        kite = randint(1, 4);
        
        # opponent within range
        if opponent_distance <= self.archer.min_target_distance:
            self.archer.velocity = Vector2(0,0)
            #if self.archer.min_target_distance - nearest_opp_distance <= 8:
            #    enemy_close = True
            #else:
                #enemy_close = False
                #self.archer.velocity = Vector2(self.archer.target.position - self.archer.position).rotate(180)
##            if randint(0, 1) == 0:
##                self.archer.velocity = Vector2(-1, 0) * self.archer.maxSpeed
            #else:
                #check if enemy is below or above archer
                #if opp_pos.y <= -0.2 and opp_pos.y >= 0.2:
                    # move left & right
                    #self.archer.velocity = Vector2(randint(-1, 1), 0) * self.archer.maxSpeed
                #else:
                    #self.archer.velocity = Vector2(0, randint(-1, 1)) * self.archer.maxSpeed
            #if enemy_close == True:
            #    self.archer.velocity = Vector2(self.archer.target.position - self.archer.position).rotate(180)
            #else:
            #    if kite == 1:
            #        self.archer.velocity = Vector2(1, 0) * self.archer.maxSpeed
            #    if kite == 2:
            #        self.archer.velocity = Vector2(-1, 0) * self.archer.maxSpeed
            #    if kite == 3:
            #        self.archer.velocity = Vector2(0, 1) * self.archer.maxSpeed
            #    if kite == 4:
            #        self.archer.velocity = Vector2(0, -1) * self.archer.maxSpeed
                
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)
            self.archer.brain.set_state("dodge")
##                if randint(0, 1) == 1:
##                        self.archer.velocity = self.archer.position - Vector2(nearest_node.position)
                
        else:
            self.archer.velocity = self.archer.target.position - self.archer.position
            if self.archer.velocity.length() > 0:
                self.archer.velocity.normalize_ip();
                self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"

        return None

    def entry_actions(self):

        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None;
            self.archer.dodge = False;
            self.archer.brain.set_state("seeking")

        return None

class ArcherStateDodge_BingChiling(State):
    def __init__(self, archer):
        State.__init__(self, "dodge")
        self.archer = archer

    def do_actions(self):

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed

    def entry_actions(self):

        #check up
        if (self.archer.position[1] < 170) and (self.archer.position[0] < 965):
            if not self.archer.dodge:
                self.archer.move_target.position = Vector2(self.archer.position[0] - 20, self.archer.position[1] - 43)

            else:
                self.archer.move_target.position = Vector2(self.archer.position[0] - 10, self.archer.position[1] + 43)
                
        #check up
        elif (self.archer.position[0] > 900) and (self.archer.position[1] > 55):
            if not self.archer.dodge:
                self.archer.move_target.position = Vector2(self.archer.position[0] + 35, self.archer.position[1])
            else:
                self.archer.move_target.position = Vector2(self.archer.position[0] - 35, self.archer.position[1])

        self.archer.dodge = not self.archer.dodge

    def check_conditions(self):
        if(self.archer.position - self.archer.move_target.position).length() <= 14:
            return "attacking"

        if(self.archer.position[1] <= 5) or (self.archer.position[0] >= 1020):
            return "seeking"

        return None

class ArcherStateKO_BingChiling(State):

    def __init__(self, archer):

        State.__init__(self, "ko")
        self.archer = archer

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.archer.current_respawn_time <= 0:
            self.archer.current_respawn_time = self.archer.respawn_time
            self.archer.ko = False
            self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None
