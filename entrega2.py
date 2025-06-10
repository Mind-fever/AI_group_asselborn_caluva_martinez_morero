from simpleai.search import CspProblem, backtrack

def restric_distintos(variables, valores):
    return valores[0] != valores[1]

def restric_droides_adyacentes(variables, valores, droids):
    (f1, c1), (f2, c2) = valores
    i = int(variables[0].split('_')[1])
    j = int(variables[1].split('_')[1])
    adyacentes = abs(f1 - f2) + abs(c1 - c2) == 1
    if adyacentes:
        return droids[i] + droids[j] <= 6
    return True

def restric_jedi_no_aislado(variables, valores, filas, columnas):
    pos_jedi = valores[0]
    paredes = valores[1:]
    vecinos = [
        (pos_jedi[0] + dx, pos_jedi[1] + dy)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
        if 0 <= pos_jedi[0] + dx < filas and 0 <= pos_jedi[1] + dy < columnas
    ]
    for v in vecinos:
        if v not in paredes:
            return True
    return False

def build_map(map_size, walls, droids):
    filas, columnas = map_size
    posiciones = [(f, c) for f in range(filas) for c in range(columnas)]

    variables = ["jedi"] + [f"wall_{i}" for i in range(walls)] + [f"droid_{i}" for i in range(len(droids))]

    dominios = {
        "jedi": [(f, c) for f in range(1, filas - 1) for c in range(1, columnas - 1)]
    }
    for i in range(walls):
        dominios[f"wall_{i}"] = posiciones[:]
    for i in range(len(droids)):
        dominios[f"droid_{i}"] = posiciones[:]

    restricciones = []

    # Paredes distintas
    for i in range(walls):
        for j in range(i + 1, walls):
            restricciones.append(([f"wall_{i}", f"wall_{j}"], restric_distintos))

    # Jedi y paredes distintas
    for i in range(walls):
        restricciones.append((["jedi", f"wall_{i}"], restric_distintos))

    # Droides y paredes distintas
    for i in range(len(droids)):
        for j in range(walls):
            restricciones.append(([f"droid_{i}", f"wall_{j}"], restric_distintos))

    # Droides distintas
    for i in range(len(droids)):
        for j in range(i + 1, len(droids)):
            restricciones.append(([f"droid_{i}", f"droid_{j}"], restric_distintos))
            restricciones.append(
                ([f"droid_{i}", f"droid_{j}"], lambda variables, valores, droids=droids: restric_droides_adyacentes(variables, valores, droids))
            )

    # Jedi no rodeado de paredes
    restricciones.append(
        (["jedi"] + [f"wall_{i}" for i in range(walls)],
         lambda variables, valores, filas=filas, columnas=columnas: restric_jedi_no_aislado(variables, valores, filas, columnas))
    )

    problema = CspProblem(variables, dominios, restricciones)
    solucion = backtrack(problema)

    resultado = [("jedi", *solucion["jedi"])]
    for i in range(walls):
        resultado.append(("wall", *solucion[f"wall_{i}"]))
    for i, cantidad in enumerate(droids):
        resultado.append((cantidad, *solucion[f"droid_{i}"]))
    return resultado

if __name__ == "__main__":
    mapa = build_map(
        map_size=(5, 6),
        walls=8,
        droids=(4, 4, 2, 2, 1, 1),
    )
    for item in mapa:
        print(item)