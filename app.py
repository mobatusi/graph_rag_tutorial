import os
import streamlit as st
from entity_relationship_extraction import get_entities_relationships
from visualize_graph import plot_knowledge_graph
from neo4j_db import Neo4jHandler
from dotenv import load_dotenv

load_dotenv()

# Streamlit app
st.title("Knowledge Graph Generator from Raw Text")

# Read raw text from an existing file in the same directory
st.write("Reading raw_text file...")
text_file_path = "raw_text.txt"
wordsPerChunk = 2665

# Extract entities and relationships from the raw text
with st.spinner("Extracting entities and relationships..."):
    entities, relationships = get_entities_relationships(text_file_path, wordsPerChunk)

# Display the extracted entities and relationships
st.write("### Extracted Entities")
st.write(entities)

st.write("### Extracted Relationship Tuples")
st.write(relationships)

# Display the knowledge graph
st.write("### Knowledge Graph")
plot_knowledge_graph(entities, relationships)

# Neo4j connection details
neo4j_uri = os.environ.get("URL")
neo4j_user = os.environ.get("USERNAME")
neo4j_password = os.environ.get("PASSWORD")

# Button to store entities and relationships in Neo4j
if st.button("Store entities and relationships to Neo4j"):
    with st.spinner("Storing entities and relationships to Neo4j..."):
        neo4j_handler = Neo4jHandler(neo4j_uri, neo4j_user, neo4j_password)
        # print(neo4j_uri)
        neo4j_handler.store_entities_relationships(entities, relationships)
        neo4j_handler.close()
    st.success("Entities and relationships successfully stored in Neo4j!")