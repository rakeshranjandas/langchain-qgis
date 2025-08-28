from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from tools import make_distinct_values_tool
from sqlalchemy import create_engine, MetaData, inspect
from langchain_community.utilities import SQLDatabase


# LLM: Gemini Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",   # you can also try gemini-1.5-flash for faster queries
    temperature=0,
)


# Create engine with type hinting for geometry
engine = create_engine(
    "postgresql+psycopg2://qgisuser:password@localhost:5432/gisdb",
    connect_args={},  # any additional
    # There's no direct param to register Geometry here, but GeoAlchemy2 ensures type support via reflection
)

# Reflect metadata (geometry will be recognized via GeoAlchemy2)
metadata = MetaData()
metadata.reflect(bind=engine, schema="public")

# Now LangChain database
db = SQLDatabase(
    engine, 
    include_tables=["mountain_peaks_india", "mountains_india", "rivers_india", "states_india"],
    sample_rows_in_table_info=2
)

# print(db.get_table_info(["mountains_india"]))

# exit()

# Toolkit with schema + LLM
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
distinct_tool = make_distinct_values_tool(db)


PREFIX = """
You are a PostgreSQL expert with PostGIS enabled.

The database schema includes:
- rivers_india (rivname TEXT, geom LINESTRING)
- states_india (name TEXT, geom POLYGON)
- mountains_india (name TEXT, geom POLYGON)
- mountain_peaks_india (name TEXT, geom POINT)

Use PostGIS functions like ST_Intersects, ST_Within, ST_Length for geometry queries.

The user will ask a natural language question. 
Your task is to ONLY output a valid SQL query, nothing else.

Before generating any SQL query with columns, make sure you check the table schema first and then use appropriate column names.
"""

# Create agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    extra_tools=[distinct_tool],
    agent="zero-shot-react-description",
    verbose=True,
    prefix=PREFIX
)


# Test queries 1:
#response = agent_executor.run("List the top 5 users by total spending in the last 30 days.")
#response = agent_executor.run("What is the longitude and latitude of 'Adi Kailash' mountain peak")
#response = agent_executor.run("Generate SQL query that will give me all the rivers running in Odisha")
#response = agent_executor.run("Find me 5 longest rivers")



# Test queries 2:
# response = agent_executor.run("SELECT r.rivname FROM rivers_india r JOIN states_india s ON ST_Intersects(r.geom, s.geom) WHERE s.state_name = 'Odisha'")
# response = agent_executor.run("The longest river flows through which states?")
# response = agent_executor.run("Give me all the rivers flowing through Nilgiri Mountains")  -- Not working correctly
# response = agent_executor.run("Give me the query to check if Krishna river flows through the Nilgiri Mountains") -- Not working correctly

print("\nAgent Response:\n", response)



# while True:
#     user_query = input("Enter your query (or type 'exit' to quit): ")
#     if not user_query or user_query.lower() == 'exit':
#         break

#     response = agent_executor.run(user_query)
#     print("\nAgent Response:\n", response)

