from neo4j import GraphDatabase
import networkx as nx
import os
from pyvis.network import Network

def viz():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "neo4j"
    driver = GraphDatabase.driver(uri, auth=(user, password))

    G = nx.DiGraph()


    def fetch_nodes_and_relationships(tx):
        result = tx.run("MATCH (n)-[r]->(m) RETURN id(n) as n_id, n, type(r) as r_type, properties(r) as r_props, id(m) as m_id, m")
        for record in result:
            n_id = record["n_id"]
            node1 = record["n"]
            r_type = record["r_type"]
            r_props = record["r_props"]
            m_id = record["m_id"]
            node2 = record["m"]

            # 添加节点到 NetworkX 图
            G.add_node(n_id, **node1)
            G.add_node(m_id, **node2)

            # 添加关系到 NetworkX 图
            edge_attr = {"type": r_type, **r_props}
            G.add_edge(n_id, m_id, **edge_attr)


    with driver.session() as session:
        session.read_transaction(fetch_nodes_and_relationships)

    # 关闭驱动
    driver.close()

    # 导出为 GraphML 文件
    nx.write_graphml(G, 'graph.graphml')

    # Load the GraphML file
    G = nx.read_graphml('graph.graphml')

    # Create a Pyvis network
    net = Network(notebook=True)

    # Convert NetworkX graph to Pyvis network
    net.from_nx(G)

    # Save and display the network
    net.show('knowledge_graph.html')
