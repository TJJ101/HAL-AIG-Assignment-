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
        self.graph = Graph(self.world)

        #custom path graph
        self.generate_pathfinding_graphs("wizard_pathfinding_graph.txt")

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.levelCount = 0
        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        #check if wizard had attempt to dodge
        self.dodge = False
        #check if wizard is running away 
        self.tacticalRetreat = False
        #check if wizard is has already reached the base when running away
        self.retreatToBase = False

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
        if SHOW_PATHS:
            self.graph.render(surface)


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

class WizardStateSeeking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        #self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
        self.wizard.path_graph = self.wizard.paths[0]
        

    def do_actions(self):
        #Heal if hp <= 70%
        if self.wizard.current_hp <= (70/100) * self.wizard.max_hp:
            self.wizard.heal()

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed
        

    def check_conditions(self):
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        # check if opponent is in range
        # check if wizard is not tactical retreating
        if not self.wizard.tacticalRetreat:
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
                

                if self.wizard.tacticalRetreat:
                    if self.current_connection == self.path_length:
                        self.wizard.retreatToBase == True
                        return "attacking"

                    if (self.wizard.position - nearest_opponent.position).length() > 90:
                        self.wizard.tacticalRetreat = False
                        return "attacking"
        
        #change path to towards enemy base after enemy dies
        if self.wizard.tacticalRetreat:
            if self.wizard.target is None or self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
                self.wizard.tacticalRetreat = False
                self.wizard.retreatToBase = False
                return "seeking"

                
        
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

        #if wizard is tactical retreating, set path to go towards base otherwise go towards enemy
        if not self.wizard.tacticalRetreat:
            self.path = pathFindAStar(self.wizard.path_graph, \
                                    nearest_node, \
                                    self.wizard.path_graph.nodes[self.wizard.base.target_node_index])

        else:
            self.path = pathFindAStar(self.wizard.path_graph, \
                                    nearest_node, \
                                    self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index])

        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position

        else:
            if not self.wizard.tacticalRetreat:
                self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position
            else:
                self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index].position


class WizardStateAttacking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard
        self.find_enemy_base_spawn_point()

    def do_actions(self):

        #heal if wizard <= 50%hp and tactical retreats
        if self.wizard.current_hp <= (20/100) * self.wizard.max_hp:
            self.wizard.heal()
            self.wizard.tacticalRetreat = True
            if not self.wizard.retreatToBase:
                self.wizard.brain.set_state("seeking")
        
        #changes target if there is one closer
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            if nearest_opponent == self.wizard.target:
                pass

            else:
                self.wizard.target = nearest_opponent

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        # opponent within range
        if opponent_distance <= self.wizard.min_target_distance:
            self.wizard.velocity = Vector2(0, 0)
            if self.wizard.current_ranged_cooldown <= 0:
                if self.wizard.target.name == "base":
                    self.wizard.ranged_attack(self.enemyBaseSpawn, self.wizard.explosion_image)
                else:
                    self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)
            self.wizard.brain.set_state("dodge")
        else:
            self.wizard.velocity = self.wizard.target.position - self.wizard.position
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed
        
        #tactical retreats when enemy near wizard
        if opponent_distance <= 90:
            #do not do anything if already at base
            if self.wizard.retreatToBase:
                pass
            self.wizard.tacticalRetreat = True
            self.wizard.brain.set_state("seeking")

        


    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            self.wizard.dodge = False
            self.wizard.retreatToBase = False
            return "seeking"

        #unstuck the wizard
        if check_collision(self.wizard):
            return "seeking"

        return None

    def entry_actions(self):
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            self.wizard.dodge = False
            self.wizard.retreatToBase = False
            self.wizard.brain.set_state("seeking")
        return None

    def find_enemy_base_spawn_point(self):
        for ent in self.wizard.world.entities.values():
            if ent.name == "base" and ent.team_id != self.wizard.team_id:
                self.enemyBaseSpawn = ent.spawn_position

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
            self.wizard.path_graph = self.wizard.paths[0]
            self.wizard.tacticalRetreat = False
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

        #unstuck wizard
        if (check_collision(self.wizard)):
            self.wizard.brain.set_state("seeking")

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed
        
        #attempts to shoot when dodging
        if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)
        
        
        

    def entry_actions(self):
        closeEdge = closer_edge(self.wizard)

        #direction of dodging changes according to which edge of screen is closer
        if closeEdge == "up":
            if not self.wizard.dodge:
                if (self.wizard.team_id == 0):
                    self.wizard.move_target.position = Vector2(self.wizard.position[0]-20, self.wizard.position[1]- 43)
                else:
                    self.wizard.move_target.position = Vector2(self.wizard.position[0]+20, self.wizard.position[1]- 43)

            else:
                if (self.wizard.team_id == 0):
                    self.wizard.move_target.position = Vector2(self.wizard.position[0]-10, self.wizard.position[1]+ 43)
                else:
                    self.wizard.move_target.position = Vector2(self.wizard.position[0]+10, self.wizard.position[1]+ 43)
    
        elif closeEdge == "right":
            if not self.wizard.dodge:
                if (self.wizard.target.name == "tower" or "base"):
                    self.wizard.move_target.position = Vector2(self.wizard.position[0] + 60, self.wizard.position[1])
                else:
                    self.wizard.move_target.position = Vector2(self.wizard.position[0] + 50, self.wizard.position[1])
            else:
                if (self.wizard.target.name == "tower" or "base"):
                    self.wizard.move_target.position = Vector2(self.wizard.position[0] - 60, self.wizard.position[1])
                else:
                    self.wizard.move_target.position = Vector2(self.wizard.position[0] - 50, self.wizard.position[1])

        #For checking of which direction to dodge
        self.wizard.dodge = not self.wizard.dodge

    def check_conditions(self):
        #reached dodge move position
        if (self.wizard.position - self.wizard.move_target.position).length() <= 14:
            return "attacking"
        
        #unstuck wizard when dodging
        if (self.wizard.position[1] <= 5 or self.wizard.position[0] >= 1015 ):
            return "seeking"

        if self.wizard.target is None:
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

def check_collision(wizard):
    for obs in wizard.world.obstacles:
        if pygame.sprite.collide_rect(wizard, obs):
            return True
    return False

