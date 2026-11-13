
import streamlit as st
import pandas as pd
import plotly.express as px

from ai_engine.conversation import ConversationMemory
from ai_engine.sql_generator import generate_sql
from sql_engine.executor import execute_sql
from database.connection import get_engine
from database.schema_detector import detect_schema
from database.upload_handler import upload_csv_to_mysql


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="QueryPilot AI Analyst",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# SESSION STATE
# ==========================================

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationMemory()


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("🚀 QueryPilot")
st.sidebar.caption("AI-Powered SQL Analytics Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "AI SQL Analyst",
        "Database Explorer",
        "Dataset Upload"
    ]
)


# ==========================================
# PAGE 1: AI SQL ANALYST
# ==========================================

if page == "AI SQL Analyst":

    st.title("🤖 AI SQL Analyst")

    st.write(
        "Ask questions about your database "
        "in plain English."
    )

    # Clear conversation
    if st.button("Clear Conversation"):

        st.session_state.conversation.clear_history()
        st.rerun()

    # Display conversation history
    for message in st.session_state.conversation.get_history():

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User question
    question = st.text_area(
        "Enter your business question",
        placeholder="Example: Show top 10 products by price",
        height=100
    )

    # Generate and execute SQL
    if st.button(
        "Generate & Execute SQL",
        type="primary"
    ):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            # Get previous conversation context
            history = st.session_state.conversation.get_context(
                limit=8
            )

            # Save current question
            st.session_state.conversation.add_message(
                "user",
                question
            )

            try:

                # Generate SQL
                with st.spinner("Generating SQL..."):

                    sql_query = generate_sql(
                        question,
                        history=history
                    )

                st.subheader("Generated SQL")
                st.code(sql_query, language="sql")

                # Execute SQL with automatic correction
                with st.spinner(
                    "Validating and executing SQL..."
                ):

                    result = execute_sql(
                        sql_query,
                        question=question,
                        max_retries=2
                    )

                # Create DataFrame
                df = pd.DataFrame(
                    result["rows"],
                    columns=result["columns"]
                )

                # Convert numeric columns
                for column in df.columns:

                    converted = pd.to_numeric(
                        df[column],
                        errors="coerce"
                    )

                    if (
                        df[column].notna().any()
                        and converted.notna().sum()
                        == df[column].notna().sum()
                    ):

                        df[column] = converted

                # Display results
                st.success("Query executed successfully!")

                st.subheader("📋 Query Results")

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # Metrics
                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Rows Returned",
                        result["row_count"]
                    )

                with col2:

                    st.metric(
                        "Columns",
                        len(df.columns)
                    )

                # Save assistant response
                st.session_state.conversation.add_message(
                    "assistant",
                    (
                        f"Generated SQL:\n{sql_query}\n\n"
                        f"Rows returned: {result['row_count']}"
                    )
                )

                # ==================================
                # DATA VISUALIZATION
                # ==================================

                st.divider()
                st.subheader("📊 Data Visualization")

                if df.empty:

                    st.info(
                        "No data available for visualization."
                    )

                else:

                    # Detect numeric columns
                    numeric_columns = df.select_dtypes(
                        include=["number"]
                    ).columns.tolist()

                    # Detect categorical columns
                    categorical_columns = df.select_dtypes(
                        include=["object", "category", "string"]
                    ).columns.tolist()

                    # Detect date columns
                    datetime_columns = df.select_dtypes(
                        include=["datetime"]
                    ).columns.tolist()

                    categorical_columns += [
                        column for column in datetime_columns
                        if column not in categorical_columns
                    ]

                    if not numeric_columns:

                        st.warning(
                            "No numeric columns found. "
                            "This result cannot be plotted "
                            "using the available chart types."
                        )

                    else:

                        # Chart type
                        chart_type = st.selectbox(
                            "Choose Chart Type",
                            [
                                "Bar Chart",
                                "Line Chart",
                                "Area Chart",
                                "Pie Chart",
                                "Scatter Plot"
                            ],
                            key="querypilot_chart_type"
                        )

                        # Select X-axis options
                        if chart_type == "Scatter Plot":

                            x_options = numeric_columns

                        else:

                            x_options = (
                                categorical_columns
                                if categorical_columns
                                else numeric_columns
                            )

                        # Axis selection
                        col1, col2 = st.columns(2)

                        with col1:

                            x_column = st.selectbox(
                                "Select X-axis",
                                x_options,
                                key="querypilot_x_axis"
                            )

                        with col2:

                            y_column = st.selectbox(
                                "Select Y-axis",
                                numeric_columns,
                                key="querypilot_y_axis"
                            )

                        # Optional grouping
                        color_options = ["None"] + [
                            column
                            for column in categorical_columns
                            if column != x_column
                        ]

                        color_column = st.selectbox(
                            "Group / Color By",
                            color_options,
                            key="querypilot_color"
                        )

                        color_value = (
                            None
                            if color_column == "None"
                            else color_column
                        )

                        try:

                            fig = None

                            # BAR CHART
                            if chart_type == "Bar Chart":

                                fig = px.bar(
                                    df,
                                    x=x_column,
                                    y=y_column,
                                    color=color_value,
                                    title=f"{y_column} by {x_column}",
                                    template="plotly_dark"
                                )

                            # LINE CHART
                            elif chart_type == "Line Chart":

                                fig = px.line(
                                    df,
                                    x=x_column,
                                    y=y_column,
                                    color=color_value,
                                    markers=True,
                                    title=f"{y_column} Trend",
                                    template="plotly_dark"
                                )

                            # AREA CHART
                            elif chart_type == "Area Chart":

                                fig = px.area(
                                    df,
                                    x=x_column,
                                    y=y_column,
                                    color=color_value,
                                    title=f"{y_column} Analysis",
                                    template="plotly_dark"
                                )

                            # PIE CHART
                            elif chart_type == "Pie Chart":

                                if x_column in numeric_columns:

                                    st.warning(
                                        "Choose a categorical "
                                        "column for the Pie Chart."
                                    )

                                else:

                                    fig = px.pie(
                                        df,
                                        names=x_column,
                                        values=y_column,
                                        title=f"{y_column} Distribution",
                                        template="plotly_dark"
                                    )

                            # SCATTER PLOT
                            elif chart_type == "Scatter Plot":

                                fig = px.scatter(
                                    df,
                                    x=x_column,
                                    y=y_column,
                                    color=color_value,
                                    title=f"{x_column} vs {y_column}",
                                    template="plotly_dark"
                                )

                            # Display chart
                            if fig is not None:

                                fig.update_layout(
                                    height=500,
                                    margin=dict(
                                        l=20,
                                        r=20,
                                        t=60,
                                        b=20
                                    )
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                        except Exception as error:

                            st.error(
                                f"Visualization error: {error}"
                            )

            except Exception as error:

                st.error(f"Query failed: {error}")

                st.session_state.conversation.add_message(
                    "assistant",
                    f"The query could not be completed: {error}"
                )


# ==========================================
# PAGE 2: DATABASE EXPLORER
# ==========================================

elif page == "Database Explorer":

    st.title("🗂️ Database Explorer")

    st.write(
        "Explore all tables available in your MySQL database."
    )

    if st.button("Refresh Database Schema"):

        engine = get_engine()

        try:

            schema = detect_schema(engine)

            st.success(
                f"Detected {len(schema)} tables."
            )

            for table_name, details in schema.items():

                with st.expander(
                    f"{table_name} ({details['row_count']:,} rows)"
                ):

                    st.write("Columns")

                    st.dataframe(
                        pd.DataFrame(details["columns"]),
                        use_container_width=True
                    )

                    if details["foreign_keys"]:

                        st.write("Foreign Keys")

                        st.json(
                            details["foreign_keys"]
                        )

                    else:

                        st.info("No foreign keys found.")

        except Exception as error:

            st.error(f"Schema error: {error}")

        finally:

            engine.dispose()


# ==========================================
# PAGE 3: DATASET UPLOAD
# ==========================================

elif page == "Dataset Upload":

    st.title("📂 Dataset Upload")

    st.write(
        "Upload CSV datasets into QueryPilot "
        "and store them as MySQL tables."
    )

    st.info(
        "Uploaded datasets are stored in your "
        "existing querypilot_db database."
    )

    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            st.divider()

            st.subheader(uploaded_file.name)

            try:

                # Preview CSV
                preview_df = pd.read_csv(uploaded_file)

                st.write("Dataset Preview")

                st.dataframe(
                    preview_df.head(10),
                    use_container_width=True
                )

                # Dataset information
                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Total Rows",
                        len(preview_df)
                    )

                with col2:

                    st.metric(
                        "Total Columns",
                        len(preview_df.columns)
                    )

                # Upload button
                if st.button(
                    f"Upload {uploaded_file.name}",
                    key=f"upload_{uploaded_file.name}"
                ):

                    with st.spinner(
                        "Uploading dataset to MySQL..."
                    ):

                        result = upload_csv_to_mysql(
                            uploaded_file
                        )

                    st.success(
                        "Dataset uploaded successfully!"
                    )

                    st.write(
                        "MySQL Table:",
                        result["table_name"]
                    )

                    st.write(
                        "Rows Imported:",
                        result["rows"]
                    )

                    st.write(
                        "Columns:",
                        result["columns"]
                    )

            except Exception as error:

                st.error(
                    f"Upload failed: {error}"
                )
