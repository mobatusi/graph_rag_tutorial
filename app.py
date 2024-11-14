import os
import streamlit as st
from entity_relationship_extraction import get_entities_relationships
from visualize_graph import plot_knowledge_graph
from neo4j_db import Neo4jHandler
from dotenv import load_dotenv



# Streamlit app
st.title("Knowledge Graph Generator from Raw Text")

# Read raw text from an existing file in the same directory
st.write("Reading raw_text file...")
text_file_path = "raw_text.txt"
wordsPerChunk = 2665

# Extract entities and relationships from the raw text
if 'extracted' not in st.session_state:
    with st.spinner("Extracting entities and relationships..."):
        entities, relationships = get_entities_relationships(text_file_path, wordsPerChunk)
        st.session_state['entities'] = entities  # Store entities in session state
        st.session_state['relationships'] = relationships  # Store relationships in session state
        st.session_state['extracted'] = True

# Display the extracted entities and relationships
if 'extracted' in st.session_state:
    entities = st.session_state['entities']  # Retrieve entities from session state
    relationships = st.session_state['relationships']  # Retrieve relationships from session state
    st.write("### Extracted Entities")
    st.write(entities)

    st.write("### Extracted Relationship Tuples")
    st.write(relationships)

    # Display the knowledge graph
    st.write("### Knowledge Graph")
    plot_knowledge_graph(entities, relationships)

# Button to store entities
if st.button("Store entities and relationships to Neo4j"):
    load_dotenv()
    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_user = os.environ.get("NEO4J_USER")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    st.write(f"Connecting to Neo4j at {neo4j_uri} with user {neo4j_user}")
    neo4j_handler = Neo4jHandler(neo4j_uri, neo4j_user, neo4j_password)

    with st.spinner("Storing entities and relationships to Neo4j..."):
        neo4j_handler.store_entities_relationships(entities, relationships)
        neo4j_handler.close()
    st.success("Entities and relationships successfully stored in Neo4j!")