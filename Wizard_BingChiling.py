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

        seeking_state = WizardStateSeeking_TeamA(self)
        attacking_state = WizardStateAttacking_TeamA(self)
        ko_state = WizardStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)

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

        # opponent within range
        if opponent_distance <= self.wizard.min_target_distance:
            self.wizard.velocity = Vector2(0, 0)
            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)
        else:
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed

        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)

        #Need to fix bug when near edge of screen 
        #Wizard starts to move back when melee enemy is 90pixel or less away
        if (self.wizard.position - nearest_opponent.position).length() <= 90:
            if (self.wizard.position - Vector2(self.wizard.base.spawn_position)).length() <= 500:
                pass

            print("enemy near wizard")
            self.wizard.velocity = Vector2(nearest_opponent.position - self.wizard.position).rotate(180)
            print("this is the rect " + str(self.wizard.rect.x) + ", " + str(self.wizard.rect.y))
            if(self.wizard.rect.x <= 150 or self.wizard.rect.x >= SCREEN_WIDTH - 150 or self.wizard.rect.y <= 20 or self.wizard.rect.y >= SCREEN_HEIGHT - 50):
                print("condition triggered")
                for obs in self.wizard.world.obstacles:
                    if (pygame.sprite.collide_rect(self.wizard, obs)):
                        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)
                        self.wizard.velocity = self.wizard.position - Vector2(nearest_node.position)
                if (self.wizard.rect.x > SCREEN_WIDTH - 150 and self.wizard.rect.y < 50):
                    print("move left")
                    self.wizard.velocity = Vector2(-1,0)
                elif (self.wizard.rect.x < 150 and self.wizard.rect.y < SCREEN_HEIGHT - 250) or (self.wizard.rect.x > SCREEN_WIDTH - 200):
                    print("move up")
                    self.wizard.velocity = Vector2(0,-1)


            self.wizard.velocity.normalize_ip()
            self.wizard.velocity *= self.wizard.maxSpeed
            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)

    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            return "seeking"

        #changes target if there is one closer
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            if nearest_opponent == self.wizard.target:
                pass
            
            elif self.wizard.target.name == "archer" or "wizard":
                pass

            else:
                dist_self_target = (self.wizard.position - self.wizard.target.position).length()
                dist_self_nearest_opponent = (self.wizard.position - nearest_opponent.position).length()
                if dist_self_nearest_opponent < dist_self_target:
                    self.wizard.target = nearest_opponent
                    print("opponent changed!")

        

        return None

    def entry_actions(self):

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
            self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None