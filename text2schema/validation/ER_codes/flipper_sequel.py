from graphviz import Digraph
dot = Digraph()
# Entities: rectangles
dot.attr('node', shape='box')
entities = ['flipper_features', 'flipper_gates']
for entity in entities:
    dot.node(entity)
# Attributes: ellipses
dot.attr('node', shape='ellipse')
attributes = {
    'flipper_features': ['key', 'created_at', 'updated_at'],
    'flipper_gates': ['feature_key', 'key', 'value', 'created_at', 'updated_at']
}
for entity, attrs in attributes.items():
    for attr in attrs:
        attr_node = f'{entity}_{attr}'
        dot.node(attr_node, attr)
        dot.edge(entity, attr_node)
# Relationships: diamonds + edges with cardinality
dot.attr('node', shape='diamond')
relations = [
    ('flipper_features', 'flipper_gates', 'has-rules', '1', 'N')
]
for src, tgt, label, card_src, card_tgt in relations:
    rel_node = f'rel_{label}'
    dot.node(rel_node, label)
    dot.edge(src, rel_node, label=card_src)
    dot.edge(rel_node, tgt, label=card_tgt)
# Save and render
dot.render('er_diagram_cardinality_edges', format='png', cleanup=True)