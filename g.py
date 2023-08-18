from graphviz import Digraph

gra = Digraph()


gra.node('a', 'Machine Learning Errors')

gra.node('b', 'RMSE')

gra.node('c', 'MAE')

gra.edges(['ab', 'ac'])

print(gra.source)

gra.render('doctest-output/round-table.gv', view=True)
