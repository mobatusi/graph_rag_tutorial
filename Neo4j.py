from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self, connection_uri, username, password):
        self.driver = GraphDatabase.driver(connection_uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def get_entities_and_relationships(self, entities):
        with self.driver.session() as session:
            results = []
            for entity in entities:
                result = session.read_transaction(self._retrieve_relationships, entity)
                results.extend(result)
            return results
        
    def get_similar_entities_and_relationships(self, user_embedding, top_n=5):
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity)
            WHERE e.embedding IS NOT NULL
            WITH e, gds.similarity.cosine(e.embedding, $user_embedding) AS similarity
            ORDER BY similarity DESC
            LIMIT $top_n
            MATCH (e)-[r]->(related)
            RETURN e.name AS entity1, r.type AS relation, related.name AS entity2, similarity
            """
            result = session.run(query, user_embedding=user_embedding, top_n=top_n)
            return [(record["entity1"], record["relation"], record["entity2"], record["similarity"]) for record in result]
    # @staticmethod
    # def _retrieve_relationships(tx, entity_name):
    #     query = """
    #     MATCH (e1:Entity {name: $entity_name})-[r:RELATION]->(e2:Entity)
    #     RETURN e1.name AS entity1, r.type AS relationship, e2.name AS entity2
    #     """
    #     result = tx.run(query, entity_name=entity_name)
    #     return [(record["entity1"], record["relationship"], record["entity2"]) for record in result]    
    @staticmethod
    def _retrieve_relationships(tx, entity_name):
        query = """
        MATCH (e:Entity {name: $entity_name})-[r:RELATION]->(other)
        RETURN e.name AS entity, other.name AS other, properties(e) AS properties, properties(other) AS other_properties
        """
        result = tx.run(query, entity_name=entity_name)
        # return [(record["entity"], record["other"], record["properties"], record["other_properties"]) for record in result]   
        return [(record["entity"], record["other"]) for record in result]   