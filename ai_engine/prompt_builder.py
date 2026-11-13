
def build_sql_prompt(question, schema, history=None):
    
    history = history or []

    conversation_context = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history[-8:]
    )

    if not conversation_context:
        conversation_context = "No previous conversation."
    

    schema_description = []

    for table_name, details in schema.items():

        columns = []

        for column in details["columns"]:
            columns.append(
                f"{column['name']} ({column['type']})"
            )

        foreign_keys = []

        for fk in details["foreign_keys"]:
            foreign_keys.append(
                f"{fk['columns']} references "
                f"{fk['referenced_table']} "
                f"{fk['referenced_columns']}"
            )

        table_info = f"""
Table: {table_name}
Rows: {details['row_count']}
Columns: {', '.join(columns)}
Foreign Keys: {', '.join(foreign_keys) if foreign_keys else 'None'}
"""

        schema_description.append(table_info)

    schema_text = "\n".join(schema_description)

    prompt = f"""
You are QueryPilot, an expert MySQL query generator.

PREVIOUS CONVERSATION:
{conversation_context}

CURRENT USER QUESTION:
{question}

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

RULES:
1. Generate SQL only for MySQL 8.0.
2. Use only tables and columns present in the schema.
3. Generate only one SELECT query.
4. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CREATE, or other modifying commands.
5. Use correct JOIN conditions based on foreign keys.
6. Do not invent column names or table names.
7. Use meaningful aliases.
8. Add LIMIT 100 when the question does not specify
   a smaller or larger result limit.
9. Return only the SQL query.
10. Do not use Markdown code fences or explanations.

Generate the SQL query now.
"""

    return prompt
