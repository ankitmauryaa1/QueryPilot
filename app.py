
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
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# VISUAL SYSTEM
# ==========================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --qp-bg: #070816;
        --qp-surface: rgba(19, 21, 44, 0.72);
        --qp-surface-strong: rgba(25, 28, 58, 0.92);
        --qp-border: rgba(255, 255, 255, 0.10);
        --qp-text: #f6f7ff;
        --qp-muted: #9da5c7;
        --qp-purple: #8b5cf6;
        --qp-cyan: #38bdf8;
        --qp-green: #34d399;
    }

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 18% 10%, rgba(99, 102, 241, 0.16), transparent 28rem),
            radial-gradient(circle at 84% 18%, rgba(56, 189, 248, 0.10), transparent 24rem),
            linear-gradient(145deg, #070816 0%, #0b0d20 52%, #080a18 100%);
        color: var(--qp-text);
    }

    .stApp::before,
    .stApp::after {
        content: "";
        position: fixed;
        z-index: 0;
        width: 24rem;
        height: 24rem;
        border-radius: 50%;
        filter: blur(90px);
        pointer-events: none;
        opacity: 0.15;
        animation: qp-float 15s ease-in-out infinite alternate;
    }

    .stApp::before {
        top: 12%;
        left: 24%;
        background: #7c3aed;
    }

    .stApp::after {
        right: 5%;
        bottom: 5%;
        background: #0891b2;
        animation-delay: -6s;
    }

    @keyframes qp-float {
        from { transform: translate3d(-2rem, -1rem, 0) scale(0.92); }
        to { transform: translate3d(3rem, 2rem, 0) scale(1.08); }
    }

    @keyframes qp-rise {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes qp-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.36); }
        50% { box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        animation: qp-rise 0.55s ease-out both;
    }

    h1, h2, h3 {
        font-family: "Space Grotesk", sans-serif !important;
        letter-spacing: -0.035em;
        color: var(--qp-text) !important;
    }

    p, label, .stMarkdown {
        color: var(--qp-muted);
    }

    [data-testid="stSidebar"] {
        background: rgba(8, 10, 25, 0.88);
        border-right: 1px solid var(--qp-border);
        backdrop-filter: blur(20px);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .qp-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.1rem 0 1.8rem;
    }

    .qp-logo {
        display: grid;
        width: 2.65rem;
        height: 2.65rem;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 0.85rem;
        background: linear-gradient(135deg, #8b5cf6, #2563eb 58%, #06b6d4);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.35);
        color: white;
        font-size: 1.25rem;
        transform: rotate(-4deg);
        transition: transform 0.25s ease;
    }

    .qp-brand:hover .qp-logo { transform: rotate(4deg) scale(1.04); }

    .qp-brand-name {
        color: #ffffff;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.16rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }

    .qp-brand-caption {
        margin-top: 0.08rem;
        color: #7f88ad;
        font-size: 0.78rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.45rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 0.68rem 0.75rem;
        border: 1px solid transparent;
        border-radius: 0.75rem;
        transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.055);
        border-color: var(--qp-border);
        transform: translateX(3px);
    }

    .qp-hero {
        position: relative;
        overflow: hidden;
        margin-bottom: 1.55rem;
        padding: 1.7rem 1.8rem;
        border: 1px solid var(--qp-border);
        border-radius: 1.3rem;
        background: linear-gradient(125deg, rgba(25, 28, 59, 0.86), rgba(14, 17, 38, 0.72));
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(18px);
    }

    .qp-hero::after {
        content: "";
        position: absolute;
        top: -80%;
        right: -8%;
        width: 20rem;
        height: 20rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.30), transparent 66%);
        animation: qp-float 9s ease-in-out infinite alternate;
    }

    .qp-eyebrow {
        margin-bottom: 0.55rem;
        color: #a78bfa;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .qp-hero h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        font-size: clamp(2rem, 4vw, 3.25rem);
        line-height: 1.04;
    }

    .qp-hero p {
        position: relative;
        z-index: 1;
        max-width: 42rem;
        margin: 0.75rem 0 0;
        color: #aeb6d8;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .qp-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1rem;
        color: #b9f7df;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .qp-status-dot {
        width: 0.48rem;
        height: 0.48rem;
        border-radius: 50%;
        background: var(--qp-green);
        animation: qp-pulse 2s ease-out infinite;
    }

    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stExpander"] {
        border-color: var(--qp-border) !important;
        border-radius: 1rem !important;
        background: var(--qp-surface) !important;
        backdrop-filter: blur(16px);
    }

    [data-testid="stMetric"] {
        padding: 1rem 1.15rem;
        transition: transform 0.22s ease, border-color 0.22s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(139, 92, 246, 0.45) !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        min-height: 2.75rem;
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-radius: 0.75rem;
        background: rgba(255, 255, 255, 0.055);
        color: #edf0ff;
        font-weight: 650;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        border-color: rgba(139, 92, 246, 0.65);
        box-shadow: 0 10px 26px rgba(49, 46, 129, 0.24);
    }

    .stButton > button[kind="primary"] {
        border: 0;
        background: linear-gradient(110deg, #7c3aed, #4f46e5 55%, #0284c7);
        box-shadow: 0 10px 28px rgba(79, 70, 229, 0.30);
    }

    .stButton > button:active { transform: translateY(0) scale(0.985); }

    .stTextArea textarea,
    [data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"] {
        border-color: var(--qp-border) !important;
        border-radius: 0.85rem !important;
        background: rgba(10, 12, 29, 0.72) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stTextArea textarea:focus {
        border-color: rgba(139, 92, 246, 0.75) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.12) !important;
    }

    [data-testid="stChatMessage"] {
        margin: 0.6rem 0;
        border: 1px solid var(--qp-border);
        border-radius: 1rem;
        background: rgba(17, 20, 42, 0.62);
        animation: qp-rise 0.35s ease both;
    }

    [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid var(--qp-border);
        border-radius: 0.9rem;
    }

    [data-testid="stAlert"] {
        border-radius: 0.85rem;
        border: 1px solid var(--qp-border);
    }

    hr { border-color: var(--qp-border) !important; }

    @media (max-width: 768px) {
        .block-container { padding: 1.25rem 1rem 3rem; }
        .qp-hero { padding: 1.35rem 1.2rem; }
        .qp-hero h1 { font-size: 2rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


def render_page_header(eyebrow, title, description, show_status=False):
    status = """
        <div class="qp-status">
            <span class="qp-status-dot"></span>
            AI engine ready
        </div>
    """ if show_status else ""

    st.markdown(
        f"""
        <section class="qp-hero">
            <div class="qp-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
            {status}
        </section>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# SESSION STATE
# ==========================================

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationMemory()


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.markdown(
    """
    <div class="qp-brand">
        <div class="qp-logo">✦</div>
        <div>
            <div class="qp-brand-name">QueryPilot</div>
            <div class="qp-brand-caption">AI data workspace</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Workspace",
    [
        "✦  AI SQL Analyst",
        "▦  Database Explorer",
        "↑  Dataset Upload"
    ]
)


# ==========================================
# PAGE 1: AI SQL ANALYST
# ==========================================

if page == "✦  AI SQL Analyst":

    render_page_header(
        "Natural language analytics",
        "Ask your data anything.",
        "Turn plain-English questions into validated SQL, live results, "
        "and clear visualizations in one focused workspace.",
        show_status=True
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
        "What would you like to know?",
        placeholder="Try: Show the top 10 products by revenue this month",
        height=120
    )

    # Generate and execute SQL
    if st.button(
        "Run analysis",
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

                st.subheader("Generated query")
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

                st.subheader("Query results")

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
                st.subheader("Visualize results")

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
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(8,10,25,0.34)",
                                    font=dict(
                                        family="DM Sans",
                                        color="#aeb6d8"
                                    ),
                                    title_font=dict(
                                        family="Space Grotesk",
                                        color="#f6f7ff",
                                        size=20
                                    ),
                                    colorway=[
                                        "#8b5cf6",
                                        "#38bdf8",
                                        "#34d399",
                                        "#f472b6",
                                        "#fbbf24"
                                    ],
                                    hoverlabel=dict(
                                        bgcolor="#171a35",
                                        bordercolor="#343861",
                                        font_color="#f6f7ff"
                                    ),
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

elif page == "▦  Database Explorer":

    render_page_header(
        "Schema intelligence",
        "Know your database.",
        "Inspect tables, columns, row counts, and relationships across "
        "your connected MySQL database."
    )

    if st.button("Scan database", type="primary"):

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

elif page == "↑  Dataset Upload":

    render_page_header(
        "Data ingestion",
        "Bring your data aboard.",
        "Preview CSV datasets and load them into MySQL as query-ready "
        "tables without leaving the workspace."
    )

    st.info(
        "Uploaded datasets are stored in your "
        "existing querypilot_db database."
    )

    uploaded_files = st.file_uploader(
        "Drop CSV files here",
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
