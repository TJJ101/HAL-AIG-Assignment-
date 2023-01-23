import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Archer_BingChiling(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image
        
        self.graph = Graph(self.world)
        self.generate_pathfinding_graphs("archer_pathfinding_graph.txt")
    
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
        self.run = False
        self.defend = False

        seeking_state = ArcherStateSeeking_BingChiling(self)
        attacking_state = ArcherStateAttacking_BingChiling(self)
        ko_state = ArcherStateKO_BingChiling(self)
        dodge_state = ArcherStateDodge_BingChiling(self)
        defend_state = ArcherStateDefend_BingChiling(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(ko_state)
        self.brain.add_state(dodge_state)
        self.brain.add_state(defend_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)
        if SHOW_PATHS:
            self.graph.render(surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        #level_up_stats = ["hp", "speed", "ranged damage", "ranged cooldown", "projectile range"]
        level_up_stats = ["ranged cooldown", "ranged damage", "ranged damage", "ranged cooldown", "ranged damage"]
        if self.can_level_up():
            self.level_up(level_up_stats[self.statChoice])
            if(self.statChoice == len(level_up_stats) - 1):
                self.statChoice = 0
            else:
                self.statChoice += 1


    def generate_pathfinding_graphs(self, filename):

        f = open(filename, "r")

        # Create the nodes
        line = f.readline()
        while line != "connections\n":
            data = line.split()
            self.graph.nodes[int(data[0])] = Node(self.graph, int(data[0]), int(data[1]), int(data[2]))
            line = f.readline()

        # Create the connections
        line = f.readline()
        while line != "paths\n":
            data = line.split()
            node0 = int(data[0])
            node1 = int(data[1])
            distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
            self.graph.nodes[node0].addConnection(self.graph.nodes[node1], distance)
            self.graph.nodes[node1].addConnection(self.graph.nodes[node0], distance)
            line = f.readline()

        # Create the orc paths, which are also Graphs
        self.paths = []
        line = f.readline()
        while line != "":
            path = Graph(self)
            data = line.split()
            
            # Create the nodes
            for i in range(0, len(data)):
                node = self.graph.nodes[int(data[i])]
                path.nodes[int(data[i])] = Node(path, int(data[i]), node.position[0], node.position[1])

            # Create the connections
            for i in range(0, len(data)-1):
                node0 = int(data[i])
                node1 = int(data[i + 1])
                distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
                path.nodes[node0].addConnection(path.nodes[node1], distance)
                path.nodes[node1].addConnection(path.nodes[node0], distance)
                
            self.paths.append(path)

            line = f.readline()

        f.close()


class ArcherStateSeeking_BingChiling(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        #self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]
        self.archer.path_graph = self.archer.paths[0]



    def do_actions(self):

        if self.archer.current_hp <= (self.archer.max_hp * (25/100)):
            self.archer.heal()

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed


    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)

        if not self.archer.run:
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
                
                if (self.archer.run):
                    if (self.archer.position - self.archer.base.position).length() <= 150:
                        self.archer.run = False
                        return "defend"
                    if self.archer.target is not None and self.archer.current_ranged_cooldown <= 0:
                            self.archer.ranged_attack(self.archer.target.position)
                    if((self.archer.position - nearest_opponent.position).length() > 75):
                        self.archer.run = False
                        return "attacking"
                    
        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        if not self.archer.run:
            self.path = pathFindAStar(self.archer.path_graph, \
                                      nearest_node, \
                                      self.archer.path_graph.nodes[self.archer.base.target_node_index])

        else:
            # run away to base
            self.path = pathFindAStar(self.archer.path_graph, \
                                      nearest_node, \
                                      self.archer.path_graph.nodes[self.archer.base.spawn_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            
            if not self.archer.run:
                self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position

            else:
                self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.spawn_node_index].position


class ArcherStateAttacking_BingChiling(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer

    def do_actions(self):

        if self.archer.current_hp <= (self.archer.max_hp * (25/100)):
            self.archer.heal()
            self.archer.run = True
            self.archer.brain.set_state("seeking")

        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        enemy_base = get_enemy_base(self.archer)

        if (self.archer.target is not None) and (self.archer.target.name == "base"):
            pass
        
        else:
            if (enemy_base is not None):
                if((self.archer.position - enemy_base.position).length()) <= 200:
                    self.archer.target = enemy_base
                elif (nearest_opponent.name == "tower"):
                    self.archer.target = nearest_opponent
                elif (nearest_opponent.current_hp <= self.archer.target.current_hp):
                    self.archer.target = nearest_opponent
            
        
        #if nearest_opponent is not None:
            #if nearest_opponent == self.archer.target:
            #    pass
            # if the closest opponent is base, prioritise shooting base
            #    self.archer.target = nearest_opponent

            #else:
                #else shoot tower
                #if nearest_opponent.name == "tower":
                    #self.archer.target = nearest_opponent
               # else:
                    # else shoot lowest hp target
                    #if(nearest_opponent.current_hp < self.archer.target.current_hp):
                        #self.archer.target = nearest_opponent


        opponent_distance = (self.archer.position - self.archer.target.position).length()
        
        # opponent within range
        if opponent_distance <= self.archer.min_target_distance:
            #self.archer.velocity = Vector2(0,0)  
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)
            self.archer.brain.set_state("dodge")
            
        else:
            self.archer.velocity = self.archer.target.position - self.archer.position
            if self.archer.velocity.length() > 0:
                self.archer.velocity.normalize_ip();
                self.archer.velocity *= self.archer.maxSpeed

        #move back if enemy is too close
        if opponent_distance <= (self.archer.min_target_distance * (75/100)):
            self.archer.run = True
            self.archer.brain.set_state("seeking")


    def check_conditions(self):

        # target is gone
        if (self.archer.target is None) or (self.archer.world.get(self.archer.target.id) is None) or (self.archer.target.ko):
            self.archer.target = None
            return "seeking"

        # if archer collides with object, unstuck it
        if (check_collision(self.archer)):
            return "seeking"

        return None

    def entry_actions(self):

        if self.archer.target is None or self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None;
            self.archer.dodge = False;
            self.archer.brain.set_state("seeking")                

        return None

class ArcherStateDodge_BingChiling(State):
    def __init__(self, archer):
        State.__init__(self, "dodge")
        self.archer = archer

    def do_actions(self):

        if(check_collision(self.archer)):
            self.archer.brain.set_state("seeking")

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed

        # if possible, attack while dodging
        if self.archer.current_ranged_cooldown <= 0:
            self.archer.ranged_attack(self.archer.target.position);

    def entry_actions(self):
        edge = check_edge(self.archer)
        
        
        if (self.archer.defend):
            if not self.archer.dodge:
                self.archer.move_target.position = Vector2(self.archer.position[0] + 10, self.archer.position[1] + 5)
            else:
                self.archer.move_target.position = Vector2(self.archer.position[0] - 5, self.archer.position[1] - 10)

        # when edge of screen is to the top of the archer
        if (edge == "up"):
            if not self.archer.dodge:
                if (self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 35, self.archer.position[1] - 45)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 20, self.archer.position[1] - 43)

            else:
                if (self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 15, self.archer.position[1] + 43)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 10, self.archer.position[1] + 43)

        # When edge of screen is to the bottom of the archer
        elif (edge == "down"):
            if not self.archer.dodge:
                if (self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 43, self.archer.position[1] - 35)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 43, self.archer.position[1] - 35)

            else:
                if (self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 5, self.archer.position[1] + 35)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 5, self.archer.position[1] + 35)

        # When edge of screen is to the left of the archer
        elif (edge == "left"):
            if not self.archer.dodge:
                if(self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 25, self.archer.position[1] + 15)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 35, self.archer.position[1] + 15)
            else:
                if(self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 35, self.archer.position[1] - 15)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 45, self.archer.position[1] - 15)

        # When edge of the screen is to the right of the Archer
        elif (edge == "right"):
            if not self.archer.dodge:
                if(self.archer.team_id == 0):
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 40, self.archer.position[1] - 30)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] + 40, self.archer.position[1] + 15)
            else:
                if(self.archer.team_id == 0): 
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 25, self.archer.position[1] + 20)
                else:
                    self.archer.move_target.position = Vector2(self.archer.position[0] - 20, self.archer.position[1] - 20)

        self.archer.dodge = not self.archer.dodge

    def check_conditions(self):
        
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if (self.archer.position - self.archer.base.position).length() <= 150 and (nearest_opponent.position - self.archer.position).length() <= 80:
            return "defend"
            
        if(self.archer.position - self.archer.move_target.position).length() <= 14:
            return "attacking"

        if(self.archer.position[1] <= 5) or (self.archer.position[0] >= 1020) or (self.archer.position[0] <= 5) or  (self.archer.position[1] >= 800):
            return "seeking"

        # returns back to path if no current target
        if self.archer.target is None:
            return "seeking"

        return None

class ArcherStateDefend_BingChiling(State):
    def __init__(self, archer):

        State.__init__(self, "defend")
        self.archer = archer

        self.archer.defend = True

    def do_actions(self):

        print("Current State of Archer: defend")

        if(self.archer.target is None):
            nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
            if (self.archer.position - nearest_opponent).length() > 80:
                self.archer.brain.set_state("seeking")
            else:
                self.archer.target = nearest_opponent

        opponent_distance = (self.archer.position - self.archer.target.position).length()

        # opponent within range
        self.archer.brain.set_state("dodge")
        if opponent_distance <= self.archer.min_target_distance:
            #self.archer.velocity = Vector2(0,0)  
            if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)

    def check_conditions(self):
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        
        # target is gone
        if (self.archer.target is None) or (self.archer.world.get(self.archer.target.id) is None) or (self.archer.target.ko):
            self.archer.target = None
            self.archer.run = False
            self.archer.defend = False
            return "seeking"

        if ((nearest_opponent - self.archer.position).length() >= 80):
            self.archer.run = False
            self.archer.defend = False
            return "seeking"

        # if archer collides with object, unstuck it
        if (check_collision(self.archer)):
            self.archer.defend = False
            self.archer.run = False
            return "seeking"

        return None

    def entry_actions(self):
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
            #self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]
            self.archer.path_graph = self.archer.paths[1]
            self.archer.run = False

            nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
            if ((nearest_opponent.position - self.archer.position).length() <= 150):
                self.archer.target = nearest_opponent
                return "defend"
            else:
                return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None


def check_edge(archer):

    if (archer.position[0] > 10) and (archer.position[1] < 640):
        return "left"
    
    if (archer.position[0] > 45) and (archer.position[1] > 640):
        return "down"
    
    if (archer.position[1] < 170) and (archer.position[0] < 965):
        return "up"
    
    if (archer.position [0] > 900) and (archer.position[1] > 55):
        return "right"


# check for collisions
def check_collision(archer):
    for obs in archer.world.obstacles:
        if pygame.sprite.collide_rect(archer, obs):
            return True
    return False

def get_enemy_base(archer):
    for i in archer.world.entities:
        if archer.world.entities[i].name == "base" and archer.world.entities[i].team_id == 1:
            return archer.world.entities[i]

    return None
