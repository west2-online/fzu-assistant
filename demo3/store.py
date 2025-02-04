from langchain_chroma import Chroma
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector
from embeddings import embeddings


vector_store = Chroma(embedding_function=embeddings)

graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="neo4j", database="neo4j")
