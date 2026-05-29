from __future__ import annotations

import networkx as nx
import pandas as pd
from .models import Entity, OwnershipEdge


def build_ownership_graph(entities: list[Entity], ownership: list[OwnershipEdge]) -> nx.DiGraph:
    g = nx.DiGraph()
    for e in entities:
        g.add_node(e.entity_id, name=e.name, inn=e.inn, role=e.role, sector=e.sector)
    for edge in ownership:
        g.add_edge(edge.parent_id, edge.child_id, share=edge.share)
    return g


def graph_edges_dataframe(ownership: list[OwnershipEdge]) -> pd.DataFrame:
    return pd.DataFrame([e.model_dump() for e in ownership])


def graph_metrics(g: nx.DiGraph) -> dict:
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "weak_components": nx.number_weakly_connected_components(g) if g.number_of_nodes() else 0,
        "is_dag": nx.is_directed_acyclic_graph(g) if g.number_of_nodes() else True,
    }
