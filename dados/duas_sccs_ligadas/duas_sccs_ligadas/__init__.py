"""Exemplo: duas componentes cíclicas ligadas em um único sentido.

Componente A = {a1, a2} (ciclo a1 <-> a2) e componente B = {b1, b2, b3}
(ciclo b1 -> b2 -> b3 -> b1). O único arco entre elas é a1 -> b1: A depende de B,
mas B não depende de A.
"""
