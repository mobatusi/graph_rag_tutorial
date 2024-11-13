from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self, connection_uri, username, password):
        try:
            self.driver = GraphDatabase.driver(connection_uri, auth=(username, password))
        except Exception as e:
            print(f"Error initializing Neo4j driver: {e}")
    
    def close(self):
        self.driver.close()
    
    def store_entities_relationships(self, entities, relationships):
        with self.driver.session() as session:
            # Store entities
            for entity in entities:
                session.write_transaction(self._create_entity_node, entity)
            
            # Store relationships
            for entity1, relationship, entity2 in relationships:
                session.write_transaction(self._create_relationship, entity1, relationship, entity2)

    @staticmethod
    def _create_entity_node(tx, entity):
        query = "MERGE (e:Entity {name: $entity_name})"
        tx.run(query, entity_name=entity)

    @staticmethod
    def _create_relationship(tx, entity1, relationship, entity2):
        query = """
        MATCH (e1:Entity {name: $entity1})
        MATCH (e2:Entity {name: $entity2})
        MERGE (e1)-[:RELATION {type: $relationship}]->(e2)
        """
        tx.run(query, entity1=entity1, entity2=entity2, relationship=relationship)