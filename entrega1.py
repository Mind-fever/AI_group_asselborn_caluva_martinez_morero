from simpleai.search import astar, SearchProblem
from simpleai.search.viewers import WebViewer
import time
import matplotlib.pyplot as plt

def play_game (jedi_at, jedi_concentration, walls, droids):

    initial_state = (jedi_at, jedi_concentration,tuple(droids))

    class jedi_problem(SearchProblem):

        def actions(self, state):
            jedi, concentration, droids = state
            droids_vivos = tuple([(a, b, c) for (a, b, c) in droids if c > 0])
            actions = []

            actions.extend(self.moverse_func(jedi[0],jedi[1]))

            actions.extend(self.atacar_func(jedi[0],jedi[1],concentration,droids_vivos))

            actions.extend(self.saltar_func(jedi[0],jedi[1],concentration))

            if self.puede_descansar(jedi[0], jedi[1], droids):
                actions.append(("rest", None))

            return actions


        def heuristic(self, state):
            jedi, concentration, droids = state
            droides_vivos=[(a, b,c) for (a, b, c) in droids if c > 0]
            #cant_droides_vivos = sum(1 for x in droids if x[2]>0)
            #return len(droides_vivos)+len(droides_vivos)-1
            if not droides_vivos:
                return 0
                #return sum(x[2] for x in droids) #Provisional

            distancia_cercano, coord_cercano = min(
                ((max(abs(jedi[0] - x), abs(jedi[1] - y)), (x, y)) for (x, y, _) in droides_vivos),
                key=lambda t: t[0]
            )

            distancia_lejano, coord_lejano = max(
                ((max(abs(coord_cercano[0] - x), abs(coord_cercano[1] - y)), (x, y)) for (x, y, _) in droides_vivos),
                key=lambda t: t[0]
            )
            costo_ataque = 0
            for _, _, c in droides_vivos:
                if c == 1:
                    costo_ataque += 1
                else:
                    costo_ataque += 2

            #positions = [jedi] + droides_vivos
            return abs(distancia_lejano)+abs(distancia_cercano) + costo_ataque


        def result(self, state, action):
            jedi,concentration,droids = state

            droids_list = list(droids)
            if action[0] == "rest":
                concentration += 10
            elif action[0] == "jump":
                jedi = action[1]
                concentration -= 1
            elif action[0] == "move":
                jedi = action[1]
            elif action[0] == "slash":
                droids_list = [(a, b, (c-1)) if ((a,b)==jedi) else (a, b, c) for (a, b, c) in droids_list]
                concentration-=1
            elif action[0] == "force":
                droids_list = [(a, b, 0) if ((a,b)==jedi) else (a, b, c) for (a, b, c) in droids_list]
                concentration -= 5


            droids_list = tuple(droids_list)
            jedi=tuple(jedi)

            #droids_vivos= tuple([(a, b, c) for (a, b, c) in droids_list if c > 0])

            return jedi, concentration,tuple(droids_list)

        def cost(self, state, action, state2):
            jedi,concentration,droids = state
            if action[0] == "rest":
                return 3
            elif action[0] == "jump":
                return 1
            elif action[0] == "move":
                return 1
            elif action[0] == "slash":
                return 1
            elif action[0] == "force":
                return 2
            else:
                return 0

        def is_goal(self, state):
            jedi, concentration, droids = state
            return  sum(x[2] for x in droids) == 0

        def saltar_func(self,fila,columna,concentration):
            actions_saltar = []
            if concentration >= 1:
                if not((fila+1,columna+1) in walls):
                    actions_saltar.append(("jump", (fila+1,columna+1)))

                if not((fila-1,columna+1) in walls):
                    actions_saltar.append(("jump", (fila-1,columna+1)))

                if not((fila+1,columna-1) in walls):
                    actions_saltar.append(("jump", (fila+1,columna-1)))

                if not((fila-1,columna-1) in walls):
                    actions_saltar.append(("jump", (fila-1,columna-1)))

            return actions_saltar

        def puede_descansar(self, fila, columna, droids):
            posiciones = [
                (fila, columna),
                (fila + 1, columna),
                (fila - 1, columna),
                (fila, columna + 1),
                (fila, columna - 1),
            ]
            droides_pos = [(a, b) for (a, b, c) in droids if c > 0]
            for pos in posiciones:
                if pos in droides_pos:
                    return False
            return True
        def moverse_func(self,fila,columna):
            actions_moverse=[]

            if not((fila+1,columna) in walls):
                actions_moverse.append(("move", (fila+1, columna)))

            if not((fila-1,columna) in walls):
                actions_moverse.append(("move", (fila-1, columna)))

            if not((fila,columna+1) in walls):
                actions_moverse.append(("move", (fila, columna+1)))

            if not((fila,columna-1) in walls):
                actions_moverse.append(("move", (fila, columna-1)))

            return actions_moverse
        def atacar_func(self, fila, columna,concentration,droides):
            actions_atacar=[]
            #lista_droides = list(zip(*droids))
            if (fila,columna) in [(a,b) for (a,b,_) in droides]:
                if concentration >=1:
                    actions_atacar.append(("slash", None))
                if concentration >= 5:
                    actions_atacar.append(("force", None))
            return actions_atacar

    viewer = WebViewer()
    problem = jedi_problem(initial_state)
    start_time = time.time()
    result = astar(problem, viewer=viewer)
    end_time = time.time()
    #result = astar(problem, viewer=viewer)
    elapsed = end_time - start_time
    print("Estado final:", result.state)
    print(f"Tiempo de resolución: {elapsed:.4f} segundos")
    acciones = [action for action, _ in result.path()[1:]]  # omite el estado inicial
    return acciones

jedi_actions = play_game(
    jedi_at=(2, 4),
    jedi_concentration=0,
    walls=[(0, 1), (1, 1), (2, 1), (3, 3), (3, 4), (3, 5)],
    droids=[(1, 2, 2), (1, 4, 1)]
)

print("Camino de acciones:")
for accion in jedi_actions:
    print(f"Acción: {accion}")
# . . . . #
# # # J # # #
# # 2 . # 1 #
# . # # # . #
# # . . . 10 #

