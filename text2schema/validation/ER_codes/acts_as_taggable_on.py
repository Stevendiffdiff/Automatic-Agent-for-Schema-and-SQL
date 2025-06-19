from graphviz import Digraph
dot = Digraph()
# Entities: rectangles
dot.attr('node', shape='box')
entities = ['tagger', 'tags', 'taggings']
for entity in entities:
    dot.node(entity)
# Attributes: ellipses
dot.attr('node', shape='ellipse')
attributes = {
    'tagger': ['tagger_id', 'tagger_type'],
    'tags': ['tag_id', 'name', 'created_at', 'updated_at', 'taggings_count'],
    'taggings': ['tagging_id', 'tag_id', 'tagger_id', 'taggable_id', 'taggable_type', 'context', 'created_at']
}
for entity, attrs in attributes.items():
    for attr in attrs:
        attr_node = f'{entity}_{attr}'
        dot.node(attr_node, attr)
        dot.edge(entity, attr_node)
# Relationships: diamonds + edges with cardinality
dot.attr('node', shape='diamond')
relations = [
    ('tagger', 'taggings', 'creates', '1', 'N'),
    ('tags', 'taggings', 'is_used_in', '1', 'N'),
    ('taggings', 'taggable_entity', 'tags', 'N', 'M')
]
for src, tgt, label, card_src, card_tgt in relations:
    rel_node = f'rel_{label}'
    dot.node(rel_node, label)
    dot.edge(src, rel_node, label=card_src)
    dot.edge(rel_node, tgt, label=card_tgt)
# Save and render
dot.render('er_diagram_cardinality_edges', format='png', cleanup=True)