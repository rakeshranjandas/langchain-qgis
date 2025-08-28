from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from tools import make_distinct_values_tool

# LLM: Gemini Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",   # you can also try gemini-1.5-flash for faster queries
    temperature=0,
)

# Restrict schema to only some tables
db = SQLDatabase.from_uri(
    "postgresql+psycopg2://qgisuser:password@localhost:5432/gisdb",
    include_tables=["mountain_peaks_india", "mountains_india", "rivers_india", "states_india"]
)

# Toolkit with schema + LLM
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
distinct_tool = make_distinct_values_tool(db)


PREFIX = """
You are a PostgreSQL expert with PostGIS enabled.
The database has tables with geometry columns.
Use spatial SQL functions such as ST_Intersects, ST_Within, ST_Contains, ST_Touches, etc.
- rivers_india.geom is a LINESTRING geometry
- states_india.geom is a POLYGON geometry
- mountains_india.geom is a POLYGON geometry
- mountain_peaks_india.geom is a POINT geometry

When asked spatial questions (like "Which rivers flow through Odisha"),
you must join rivers_india with states_india and use ST_Intersects(rivers_india.geom, states_india.geom).
Only return relevant attributes, not the geometry itself.
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


# Test query
#response = agent_executor.run("List the top 5 users by total spending in the last 30 days.")
#response = agent_executor.run("What is the longitude and latitude of 'Adi Kailash' mountain peak")
#response = agent_executor.run("Generate SQL query that will give me all the rivers running in Odisha")
#response = agent_executor.run("Find me 5 longest rivers")

while True:
    # Take input from terminal and run the agent
    user_query = input("Enter your query (or type 'exit' to quit): ")
    if not user_query or user_query.lower() == 'exit':
        break
    response = agent_executor.run(user_query)
    print(response)


