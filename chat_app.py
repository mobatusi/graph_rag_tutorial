import streamlit as st
from LLM import get_entities, generate_response, get_user_input_embedding
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

URL = os.environ.get("NEO4J_URI")
USERNAME = os.environ.get("NEO4J_USER")
PASSWORD = os.environ.get("NEO4J_PASSWORD")

# Function to handle input submission
def handle_submit():
    user_input = st.session_state["user_input"]
    if user_input:
        # Step 1: Extract entities from the user query
        extracted_entities = get_entities(user_input)
        print("Entities in the query: ", extracted_entities)

        # Step 2: Generate an embedding from the user input
        user_input_embedding = get_user_input_embedding(user_input)

        # Step 3: Retrieve similar entities and relationships from the Neo4j knowledge graph
        neo4j_handler = Neo4jHandler(URL, USERNAME, PASSWORD)
        related_relationships_tuple_list = neo4j_handler.get_similar_entities_and_relationships(user_input_embedding)
        neo4j_handler.close()
        print("Extracted context from the Knowledge Graph: ", related_relationships_tuple_list)

        # Step 4: Augment the query with knowledge graph context
        context = "\n".join([f"({e1}) -[{rel}]-> ({e2}) [Similarity: {sim:.2f}]" for e1, rel, e2, sim in related_relationships_tuple_list])

        messages = [
            {"role": "system", "content": f"Use the following knowledge graph context (provided as relationships with similarity scores) to answer the user queries.\n{context}"},
            {"role": "user", "content": user_input},
        ]

        # Step 5: Get GPT-4 response using the augmented query
        bot_response = generate_response(messages)

        # Step 6: Append the user message and bot response to the session state chat history
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": bot_response})

        # Clear the input field in session state
        st.session_state["user_input"] = ""

# Add sidebar with questions
st.sidebar.title("Questions you can ask the dataset:")

if st.sidebar.button("Who is Abraham Lincoln?"):
    st.session_state["user_input"] = "Who is Abraham Lincoln?"
    handle_submit()

if st.sidebar.button("Who was the sixteenth President of the United States?"):
    st.session_state["user_input"] = "Who was the sixteenth President of the United States?"
    handle_submit()

if st.sidebar.button("What significant act did Lincoln sign in 1863?"):
    st.session_state["user_input"] = "What significant act did Lincoln sign in 1863?"
    handle_submit()

if st.sidebar.button("In what year did Lincoln begin his political career?"):
    st.session_state["user_input"] = "In what year did Lincoln begin his political career?"
    handle_submit()

if st.sidebar.button("What was established by The Legal Tender Act of 1862?"):
    st.session_state["user_input"] = "What was established by The Legal Tender Act of 1862?"
    handle_submit()

if st.sidebar.button("Who assassinated Abraham Lincoln?"):
    st.session_state["user_input"] = "Who assassinated Abraham Lincoln?"
    handle_submit()

if st.sidebar.button("What was the primary goal of the Emancipation Proclamation issued by Lincoln?"):
    st.session_state["user_input"] = "What was the primary goal of the Emancipation Proclamation issued by Lincoln?"
    handle_submit()

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