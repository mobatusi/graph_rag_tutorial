import json
from neo4j import GraphDatabase
import os
from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Neo4jHandler:
    def __init__(self, connection_uri, username, password):
        try:
            self.driver = GraphDatabase.driver(connection_uri, auth=(username, password))
            print('Connected to Neo4j database')
        except Exception as e:
            print(f"Error initializing Neo4j driver: {e}")
    
    def close(self):
        if self.driver:
            self.driver.close()
            print('Neo4j driver closed')
    
    # def store_entities_relationships(self, entities, relationships):
    #     with self.driver.session() as session:
    #         # Store entities
    #         for entity in entities:
    #             session.write_transaction(self._create_entity_node, entity)
            
    #         # Store relationships
    #         for entity1, relationship, entity2 in relationships:
    #             session.write_transaction(self._create_relationship, entity1, relationship, entity2)

    def store_entities_relationships(self, entities, relationships):
        print('Storing entities and relationships to Neo4j...')
        with self.driver.session() as session:
            # Store entities and generate embeddings
            for entity in entities:
                session.write_transaction(self._create_entity_node, entity)
            print('Entities stored')
            # Store relationships
            for entity1, relationship, entity2 in relationships:
                session.write_transaction(self._create_relationship, entity1, relationship, entity2)
            print('Relationships stored')

    @staticmethod
    def _generate_embedding(tx, entity):
        print('Generating embedding for entity: ', entity)
        # Logic to generate embedding using OpenAI API
        try:
            query = '''
            CALL genai.vector.encode($to_encode, 'OpenAI', { token: $token }) 
            YIELD vector
            RETURN vector
            '''
            result = tx.run(query, to_encode=entity, token=openAI_token).single()
            return result["vector"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
        

    @staticmethod
    def _create_entity_node(tx, entity):
        # Generate embedding for the entity
        try:
            # Generate embedding using OpenAI API
            model="text-embedding-3-small"
            embedding = openai_client.embeddings.create(input = [entity], model=model).data[0].embedding

            query = """
            MERGE (e:Entity {name: $entity_name})
            SET e.embedding = $embedding
            """
            tx.run(query, entity_name=entity, embedding=embedding)
        except Exception as e:
            print(f"Error creating entity node: {e}")

    @staticmethod
    def _create_relationship(tx, entity1, relationship, entity2):
        query = """
        MATCH (e1:Entity {name: $entity1})
        MATCH (e2:Entity {name: $entity2})
        MERGE (e1)-[:RELATION {type: $relationship}]->(e2)
        """
        tx.run(query, entity1=entity1, entity2=entity2, relationship=relationship)