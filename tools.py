from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import json

def make_distinct_values_tool(db):
    class DistinctValuesInput(BaseModel):
        input: str = Field(
            description='A JSON string: {"table": "mytable", "column": "mycolumn"}'
        )

    def _get_distinct_values(input: str) -> str:
        try:
            data = json.loads(input)
            table = data["table"]
            column = data["column"]
            query = f'SELECT DISTINCT "{column}" FROM {table} LIMIT 20;'
            return db.run(query)
        except Exception as e:
            return f"Error: {e}"

    return StructuredTool.from_function(
        func=_get_distinct_values,
        name="get_distinct_values",
        description="Fetch distinct values from a column in a given table",
        args_schema=DistinctValuesInput,
    )
