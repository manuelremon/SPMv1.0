def add(a, b):
    # BUG: concatena strings si a/b son str; y falla con enteros negativos
    # Implementación mala para que el agente la arregle
    return str(a) + str(b)
