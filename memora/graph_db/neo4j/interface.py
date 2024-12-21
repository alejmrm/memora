import os
import neo4j
from neo4j import AsyncGraphDatabase
from typing_extensions import override

from .organization import Neo4jOrganization
from .agent import Neo4jAgent
from .user import Neo4jUser
from .interaction import Neo4jInteraction
from .memory import Neo4jMemory

class Neo4jGraphInterface(Neo4jOrganization, Neo4jAgent, Neo4jUser, Neo4jInteraction, Neo4jMemory):

    def __init__(self,
                 uri: str = os.getenv("NEO4J_URI"),
                 username: str = os.getenv("NEO4J_USERNAME"),
                 password: str = os.getenv("NEO4J_PASSWORD"),
                 database: str = os.getenv("NEO4J_DATABASE")):

        self.driver = AsyncGraphDatabase.driver(uri=uri, auth=(username, password))
        self.database = database

    @override
    async def close(self):
        await self.driver.close()

    # Setup method
    @override
    async def setup(self, *args, **kwargs) -> None:
        """Sets up Neo4j database constraints and indices for the graph schema."""
    
        async def create_constraints_and_indexes(tx):
            # Organization node key
            await tx.run("""
                CREATE CONSTRAINT unique_org_id IF NOT EXISTS 
                FOR (o:Org) REQUIRE o.org_id IS NODE KEY
            """)

            # User node key
            await tx.run("""
                CREATE CONSTRAINT unique_org_user IF NOT EXISTS
                FOR (u:User) REQUIRE (u.org_id, u.user_id) IS NODE KEY
            """)

            # Agent node key
            await tx.run("""
                CREATE CONSTRAINT unique_org_agent IF NOT EXISTS 
                FOR (a:Agent) REQUIRE (a.org_id, a.agent_id) IS NODE KEY
            """)

            # Memory node key
            await tx.run("""
                CREATE CONSTRAINT unique_user_memory IF NOT EXISTS
                FOR (m:Memory) REQUIRE (m.org_id, m.user_id, m.memory_id) IS NODE KEY
            """)

            # Interaction node key
            await tx.run("""
                CREATE CONSTRAINT unique_user_interaction IF NOT EXISTS
                FOR (i:Interaction) REQUIRE (i.org_id, i.user_id, i.interaction_id) IS NODE KEY
            """)

            # Date node key
            await tx.run("""
                CREATE CONSTRAINT unique_user_date IF NOT EXISTS
                FOR (d:Date) REQUIRE (d.org_id, d.user_id, d.date) IS NODE KEY
            """)

        async with self.driver.session(database=self.database, default_access_mode=neo4j.WRITE_ACCESS) as session:
            await session.execute_write(create_constraints_and_indexes)

