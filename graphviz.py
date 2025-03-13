from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship
from pyvis.network import Network
import networkx as nx
from config import conf

# Neo4j连接配置
class Neo4jVisualizer:
    def __init__(self):
        self.driver = GraphDatabase.driver(conf.neo4j.url, auth=(conf.neo4j.username, conf.neo4j.password))

    def close(self):
        self.driver.close()

    def fetch_data(self, cypher_query):
        """从Neo4j获取数据"""
        records = []
        with self.driver.session() as session:
            result = session.run(cypher_query)
            records = [record for record in result]
        return records

    def create_networkx_graph(self, records):
        """创建NetworkX图"""
        G = nx.MultiDiGraph()
        
        for record in records:
            # 添加节点
            for node in record.values():
                if isinstance(node, Node):
                    label = list(node.labels)[0]
                    G.add_node(node.element_id, label=label, properties=dict(node))
            
            # 添加边
            if 'r' in record.keys():
                rel = record['r']
                G.add_edge(
                    rel.start_node.element_id,
                    rel.end_node.element_id,
                    label=rel.type,
                    properties=dict(rel)
                )
        return G

    def visualize_with_pyvis(self, G):
        """使用PyVis进行交互式可视化"""
        net = Network(height="900px", width="100%", directed=True, cdn_resources="remote", select_menu=True, filter_menu=True, neighborhood_highlight=True)
        
        for node in G.nodes(data=True):
            net.add_node(
                node[0],
                label=node[1]['properties']['id'],
                title=node[1]['label']
            )
            
        for edge in G.edges(data=True):
            net.add_edge(
                edge[0],
                edge[1],
                label=edge[2]['label'],
                title=str(edge[2]['properties'])
            )
        net.show_buttons(filter_=['nodes', 'edges', 'physics'])
        net.write_html("neo4j_graph.html")

if __name__ == "__main__":
    visualizer = Neo4jVisualizer()
    
    # 示例Cypher查询（可自定义）
    query = """
    MATCH (n:`__Entity__`)-[r]->(m)
    RETURN n, r, m
    LIMIT 30000
    """
    
    try:
        records = visualizer.fetch_data(query)
        G = visualizer.create_networkx_graph(records)
        
        # 选择可视化方式
        # visualizer.visualize_with_networkx(G)  # 静态可视化
        visualizer.visualize_with_pyvis(G)     # 交互式可视化
    finally:
        visualizer.close()