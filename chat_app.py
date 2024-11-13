import streamlit as st
from LLM import get_entities, generate_response
from Neo4j import Neo4jHandler
from dotenv import load_dotenv
import os
load_dotenv()
# Streamlit app title
st.title("Knowledge Graph-Powered Chat: Query Your Dataset")

# Initialize session state to store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

URL = os.environ.get("URL")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

# Function to handle input submission
def handle_submit():
    user_input = st.session_state["user_input"]
    if user_input:
        # Step 1: Extract entities from the user query
        extracted_entities = get_entities(user_input)
        print("Entities in the query: ", extracted_entities)

        # Step 2: Retrieve associated relationships from the Neo4j knowledge graph
        neo4j_handler = Neo4jHandler(URL, USERNAME, PASSWORD)
        related_relationships_tuple_list = neo4j_handler.get_entities_and_relationships(extracted_entities)
        neo4j_handler.close()
        print("Extracted context from the Knowledge Graph: ", related_relationships_tuple_list)

        # Step 3: Augment the query with knowledge graph context
        messages = [
            {"role": "system", "content": f"Use the following knowledge graph context (provided as relationship tuple list: (Entity 1, Relation, Entity 2)) to answer the user queries.\n{related_relationships_tuple_list}"},
            {"role": "user", "content": user_input},
        ]

        # Step 4: Get GPT-4 response using the augmented query
        bot_response = generate_response(messages)

        # Step 5: Append the user message and bot response to the session state chat history
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": bot_response})

        # Clear the input field in session state
        st.session_state["user_input"] = ""

# User input section
st.text_input("Ask a question related to your dataset:", value=st.session_state["user_input"], key="user_input", on_change=handle_submit)

# Function to display messages in colored boxes
def display_message(message, is_user):
    if is_user:
        st.markdown(f"""
        <div style="background-color:#DCF8C6;padding:10px;border-radius:10px;margin-bottom:10px;">
        {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#E6E6FA;padding:10px;border-radius:10px;margin-bottom:10px;">
        {message}
        </div>
        """, unsafe_allow_html=True)

# Display the conversation history
if st.session_state["messages"]:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            display_message(msg["content"], is_user=True)
        elif msg["role"] == "assistant":
            display_message(msg["content"], is_user=False)