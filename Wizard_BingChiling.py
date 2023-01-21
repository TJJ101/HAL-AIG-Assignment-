import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Wizard_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.levelCount = 0
        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        self.dodge = False

        seeking_state = WizardStateSeeking_TeamA(self)
        attacking_state = WizardStateAttacking_TeamA(self)
        ko_state = WizardStateKO_TeamA(self)
        dodge_state = WizardStateDodge_TeamA(self)

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
        level_up_stats = ["ranged damage", "ranged cooldown", "ranged cooldown", "speed"]
        if self.can_level_up():
            self.level_up(level_up_stats[self.levelCount])   
            if self.levelCount == 3:
                self.levelCount = 0
            else: 
                self.levelCount += 1 


class WizardStateSeeking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        #self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
        self.wizard.path_graph = self.wizard.world.paths[0]
        

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if opponent_distance <= self.wizard.min_target_distance:
                    self.wizard.target = nearest_opponent
                    return "attacking"
        
        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

        self.path = pathFindAStar(self.wizard.path_graph, \
                                  nearest_node, \
                                  self.wizard.path_graph.nodes[self.wizard.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position

        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position


class WizardStateAttacking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard

    def do_actions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()
        #nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)

        # opponent within range
        if opponent_distance <= self.wizard.min_target_distance:
            self.wizard.velocity = Vector2(0, 0)
            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)
            self.wizard.brain.set_state("dodge")
        else:
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            self.wizard.dodge = False
            return "seeking"

        #changes target if there is one closer
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            if nearest_opponent == self.wizard.target:
                pass

            else:
                dist_self_target = (self.wizard.position - self.wizard.target.position).length()
                dist_self_nearest_opponent = (self.wizard.position - nearest_opponent.position).length()
                if dist_self_nearest_opponent < dist_self_target:
                    self.wizard.target = nearest_opponent
                    print("opponent changed!")

        

        return None

    def entry_actions(self):
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            self.wizard.dodge = False
            self.wizard.brain.set_state("seeking")
        return None

def get_previous_node(graph, currentNode):
    for con in graph.connections:
        if con.toNode == currentNode:
            return con.fromNode
    
    return None

class WizardStateKO_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "ko")
        self.wizard = wizard

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.wizard.current_respawn_time <= 0:
            self.wizard.current_respawn_time = self.wizard.respawn_time
            self.wizard.ko = False
            #self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
            self.wizard.path_graph = self.wizard.world.paths[0]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None

class WizardStateDodge_TeamA(State):
    def __init__(self, wizard):
        State.__init__(self, "dodge")
        self.wizard = wizard

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed
        
        
        

    def entry_actions(self):
        closeEdge = closer_edge(self.wizard)
        print(closeEdge)

        #direction of dodging changes according to which edge of screen is closer
        print(self.wizard.dodge)
        if closeEdge == "up":
            if not self.wizard.dodge:
                self.wizard.move_target.position = Vector2(self.wizard.position[0]-20, self.wizard.position[1]- 43)

            else:
                self.wizard.move_target.position = Vector2(self.wizard.position[0]-10, self.wizard.position[1]+ 43)
    
        elif closeEdge == "right":
            if not self.wizard.dodge:
                self.wizard.move_target.position = Vector2(self.wizard.position[0] + 40, self.wizard.position[1])
            else:
                self.wizard.move_target.position = Vector2(self.wizard.position[0] - 40, self.wizard.position[1])

        self.wizard.dodge = not self.wizard.dodge

    def check_conditions(self):
        if (self.wizard.position - self.wizard.move_target.position).length() <= 14:
            return "attacking"
        
        #unstuck wizard when dodging
        if (self.wizard.position[1] <= 5 or self.wizard.position[0] >= 1015 ):
            return "seeking"


        return None

def closer_edge(wizard):
    if wizard.position[1] < 170 and wizard.position[0] < 965:
        return "up"
    
    if wizard.position [0] > 900 and wizard.position[1] > 55:
        return "right"

    if wizard.position[0] > 45 and wizard.position[1] > 640:
        return "down"

    return "left"

