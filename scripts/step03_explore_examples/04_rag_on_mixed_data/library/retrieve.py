import sys
from logging import getLogger

from utils.hana import (
    get_connection_to_hana_db,
    get_connection_string,
)

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.types import AgentType

from .tools import RAGTool
from .prompts import SQL_AGENT_PREFIX
from .config import (
    VECTOR_EMBEDDINGS_TABLE_NAME,
    STRUCTURED_DATA_TABLE_NAME,
)

log = getLogger(__name__)


def create_retriever(embeddings):
    assert (
        STRUCTURED_DATA_TABLE_NAME
    ), "STRUCTURED_DATA_TABLE_NAME is not defined. Please define it before proceeding."

    try:
        connection_to_hana = get_connection_to_hana_db()

        vector_db = HanaDB(
            embedding=embeddings,
            connection=connection_to_hana,
            table_name=VECTOR_EMBEDDINGS_TABLE_NAME,
        )
        return vector_db.as_retriever(search_kwargs={"k": 10})
    except Exception as e:
        log.error(f"An error occurred while creating the retriever: {str(e)}")
        sys.exit()


def create_agent(llm, retriever):
    try:
        rag_tool = RAGTool(llm=llm, retriever=retriever)
        db = SQLDatabase.from_uri(f"{get_connection_string()}")
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=SQLDatabaseToolkit(db=db, llm=llm),
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            extra_tools=[rag_tool],
            prefix=SQL_AGENT_PREFIX,
            agent_executor_kwargs={"handle_parsing_errors": True},
        )
        return agent_executor
    except Exception as e:
        log.error(f"An error occurred while creating the agent: {str(e)}")
        sys.exit()
