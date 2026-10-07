import os

import streamlit as st

from backend.rag import RAGPipeline
from backend.document_processor import DocumentProcessor
from backend.analyzer import HLDAnalyzer
from backend.consistency_checker import ConsistencyChecker


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AUTOSAR HLD Assistant",
    page_icon="🚗",
    layout="wide"
)


# ==================================================
# TITLE
# ==================================================

st.title("🚗 AUTOSAR HLD Analysis Assistant")

st.write(
    "Upload an AUTOSAR High-Level Design document "
    "and ask questions or analyze its structure using grounded AI."
)


# ==================================================
# LOAD RAG PIPELINE
# ==================================================

@st.cache_resource
def load_rag_pipeline():

    return RAGPipeline()


with st.spinner("Loading AUTOSAR HLD Assistant..."):

    rag = load_rag_pipeline()


# ==================================================
# DOCUMENT PROCESSOR
# ==================================================

document_processor = DocumentProcessor(
    embedding_model=rag.embedding_model,
    vector_store=rag.vector_store
)


# ==================================================
# HLD ANALYZER
# ==================================================

analyzer = HLDAnalyzer(rag.llm)
consistency_checker = None


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("📄 HLD Assistant")

    st.write(
        "Upload an AUTOSAR HLD document and "
        "analyze it using semantic search and AI."
    )

    st.divider()

    # --------------------------------------------------
    # Upload HLD
    # --------------------------------------------------

    st.subheader("Upload HLD")

    uploaded_file = st.file_uploader(
        "Choose an HLD PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button(
            "⚙️ Process Document",
            type="primary"
        ):

            os.makedirs(
                "data/uploads",
                exist_ok=True
            )

            file_path = os.path.join(
                "data/uploads",
                uploaded_file.name
            )

            # Save uploaded PDF
            with open(file_path, "wb") as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            try:

                with st.spinner(
                    "Processing HLD document..."
                ):

                    info = (
                        document_processor
                        .process_document(
                            file_path
                        )
                    )

                # Save document information
                st.session_state[
                    "document_info"
                ] = info

                # Clear previous HLD analysis
                if "hld_analysis" in st.session_state:

                    del st.session_state[
                        "hld_analysis"
                    ]

                # Clear previous consistency results
                if "consistency_result" in st.session_state:

                    del st.session_state[
                        "consistency_result"
                    ]

                st.success(
                    "Document processed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Error processing document: {e}"
                )

    # --------------------------------------------------
    # Current Document
    # --------------------------------------------------

    st.divider()

    st.subheader("Current Document")

    if "document_info" in st.session_state:

        info = st.session_state[
            "document_info"
        ]

        st.info(
            f"📄 {info['filename']}"
        )

        st.caption(
            f"Pages: {info['pages']} | "
            f"Chunks: {info['chunks']}"
        )

    else:

        st.info(
            "No document uploaded yet."
        )

    # --------------------------------------------------
    # Example Questions
    # --------------------------------------------------

    st.divider()

    st.subheader("Example Questions")

    st.write(
        "• What are the responsibilities of "
        "BrakeControlSWC?"
    )

    st.write(
        "• What ports does BrakeControlSWC have?"
    )

    st.write(
        "• What interfaces are available?"
    )

    st.write(
        "• How does the braking process work?"
    )

    st.write(
        "• How does BrakeControlSWC communicate "
        "with BrakeActuatorSWC?"
    )


# ==================================================
# MAIN TABS
# ==================================================

tab_analysis, tab_consistency, tab_qa = st.tabs(
    [
        "📊 HLD Analysis",
        "🔍 Check HLD",
        "💬 Ask Questions"
    ]
)


# ==================================================
# TAB 1 — HLD ANALYSIS
# ==================================================

with tab_analysis:

    st.header("📊 HLD Document Analysis")

    if "document_info" not in st.session_state:

        st.info(
            "Upload and process an HLD document "
            "from the sidebar to begin analysis."
        )

    else:

        info = st.session_state[
            "document_info"
        ]

        st.write(
            f"Analysis of **{info['filename']}**"
        )

        st.caption(
            f"{info['pages']} pages • "
            f"{info['chunks']} chunks"
        )

        # ----------------------------------------------
        # Analyze Button
        # ----------------------------------------------

        if st.button(
            "🧠 Analyze HLD",
            type="primary"
        ):

            try:

                with st.spinner(
                    "Analyzing HLD structure..."
                ):

                    # Get all indexed documents
                    stored = (
                        rag.vector_store
                        .collection
                        .get()
                    )

                    documents = stored[
                        "documents"
                    ]

                    metadatas = stored[
                        "metadatas"
                    ]

                    # Run HLD analysis
                    analysis = analyzer.analyze(
                        documents,
                        metadatas
                    )

                    # Store analysis
                    st.session_state[
                        "hld_analysis"
                    ] = analysis

                st.success(
                    "HLD analysis completed!"
                )

            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )

        # ----------------------------------------------
        # Display Analysis
        # ----------------------------------------------

        if "hld_analysis" in st.session_state:

            analysis = st.session_state[
                "hld_analysis"
            ]

            # ==========================================
            # SUMMARY
            # ==========================================

            st.subheader(
                "📋 Document Summary"
            )

            st.write(
                analysis.get(
                    "summary",
                    "No summary available."
                )
            )

            st.divider()

            # ==========================================
            # SOFTWARE COMPONENTS
            # ==========================================

            st.subheader(
                "🧩 Software Components"
            )

            components = analysis.get(
                "components",
                []
            )

            if components:

                for component in components:

                    component_name = component.get(
                        "name",
                        "Unknown Component"
                    )

                    with st.expander(
                        f"🔹 {component_name}"
                    ):

                        st.write(
                            component.get(
                                "description",
                                "No description available."
                            )
                        )

                        st.caption(
                            f"Source: Page "
                            f"{component.get('page', '?')}"
                        )

            else:

                st.info(
                    "No software components found."
                )

            st.divider()

            # ==========================================
            # INTERFACES
            # ==========================================

            st.subheader(
                "🔌 Interfaces"
            )

            interfaces = analysis.get(
                "interfaces",
                []
            )

            if interfaces:

                for interface in interfaces:

                    interface_name = interface.get(
                        "name",
                        "Unknown Interface"
                    )

                    with st.expander(
                        f"🔗 {interface_name}"
                    ):

                        st.write(
                            interface.get(
                                "purpose",
                                "No purpose available."
                            )
                        )

                        st.caption(
                            f"Source: Page "
                            f"{interface.get('page', '?')}"
                        )

            else:

                st.info(
                    "No interfaces found."
                )

            st.divider()

            # ==========================================
            # PORTS
            # ==========================================

            st.subheader(
                "📡 Ports"
            )

            ports = analysis.get(
                "ports",
                []
            )

            if ports:

                for port in ports:

                    component = port.get(
                        "component",
                        "Unknown"
                    )

                    port_name = port.get(
                        "name",
                        "Unknown"
                    )

                    port_type = port.get(
                        "type",
                        "Unknown"
                    )

                    page = port.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**{component}** → "
                        f"`{port_name}` "
                        f"({port_type})"
                    )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No ports found."
                )

            st.divider()

            # ==========================================
            # FUNCTIONAL FLOW
            # ==========================================

            st.subheader(
                "🔄 Functional Flow"
            )

            functional_flow = analysis.get(
                "functional_flow",
                []
            )

            if functional_flow:

                for item in functional_flow:

                    step = item.get(
                        "step",
                        "?"
                    )

                    description = item.get(
                        "description",
                        ""
                    )

                    page = item.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**Step {step}** — "
                        f"{description}"
                    )

                    st.caption(
                        f"Source: Page {page}"
                    )

                st.success(
                    f"{len(functional_flow)} "
                    "functional steps detected."
                )

            else:

                st.info(
                    "No functional flow found."
                )

            st.divider()

            # ==========================================
            # DATA FLOW
            # ==========================================

            st.subheader(
                "🔀 Data Flow"
            )

            data_flow = analysis.get(
                "data_flow",
                []
            )

            if data_flow:

                for item in data_flow:

                    source = item.get(
                        "from",
                        "Unknown"
                    )

                    destination = item.get(
                        "to",
                        "Unknown"
                    )

                    description = item.get(
                        "description",
                        ""
                    )

                    page = item.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**{source}** → "
                        f"**{destination}**"
                    )

                    if description:

                        st.caption(
                            description
                        )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No data-flow information found."
                )

            st.divider()

            # ==================================================
            # TRACEABILITY
            # ==================================================

            st.subheader(
                "🔗 Traceability Matrix"
            )

            st.write(
                "Trace relationships between software components, "
                "ports, interfaces, and data flow."
            )

            # --------------------------------------------------
            # Component → Ports
            # --------------------------------------------------

            st.markdown("### 🧩 Component → Ports")

            if ports:

                for port in ports:

                    component = port.get(
                        "component",
                        "Unknown"
                    )

                    port_name = port.get(
                        "name",
                        "Unknown"
                    )

                    port_type = port.get(
                        "type",
                        "Unknown"
                    )

                    page = port.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**{component}** → "
                        f"`{port_name}` "
                        f"({port_type})"
                    )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No port traceability information found."
                )


            st.divider()


            # --------------------------------------------------
            # Component → Interfaces
            # --------------------------------------------------

            st.markdown("### 🔌 Component → Interfaces")

            if interfaces:

                for interface in interfaces:

                    interface_name = interface.get(
                        "name",
                        "Unknown Interface"
                    )

                    purpose = interface.get(
                        "purpose",
                        "No purpose available."
                    )

                    page = interface.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**{interface_name}**"
                    )

                    st.caption(
                        purpose
                    )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No interface traceability information found."
                )


            st.divider()


            # --------------------------------------------------
            # Functional Flow Traceability
            # --------------------------------------------------

            st.markdown(
                "### 🔄 Functional Flow Traceability"
            )

            if functional_flow:

                for item in functional_flow:

                    step = item.get(
                        "step",
                        "?"
                    )

                    description = item.get(
                        "description",
                        ""
                    )

                    page = item.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**Step {step}** → {description}"
                    )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No functional-flow traceability information found."
                )


            st.divider()


            # --------------------------------------------------
            # Data Flow Traceability
            # --------------------------------------------------

            st.markdown(
                "### 🔀 Data Flow Traceability"
            )

            if data_flow:

                for item in data_flow:

                    source = item.get(
                        "from",
                        "Unknown"
                    )

                    destination = item.get(
                        "to",
                        "Unknown"
                    )

                    description = item.get(
                        "description",
                        ""
                    )

                    page = item.get(
                        "page",
                        "?"
                    )

                    st.write(
                        f"**{source}** → **{destination}**"
                    )

                    if description:

                        st.caption(
                            description
                        )

                    st.caption(
                        f"Source: Page {page}"
                    )

            else:

                st.info(
                    "No data-flow traceability information found."
                )


            st.divider()


            # ==========================================
            # OBSERVATIONS
            # ==========================================

            st.subheader(
                "🔎 Document Observations"
            )

            observations = analysis.get(
                "observations",
                []
            )

            if observations:

                for observation in observations:

                    st.write(
                        f"• {observation}"
                    )

            else:

                st.info(
                    "No observations identified."
                )


# ==================================================
# TAB 2 — CONSISTENCY CHECK
# ==================================================

with tab_consistency:

    st.header("🔍 HLD Consistency Check")

    st.write(
        "Run deterministic checks on components, "
        "interfaces, ports, functional flow, and "
        "data flow."
    )

    if "hld_analysis" not in st.session_state:

        st.info(
            "First run HLD Analysis from the "
            "📊 HLD Analysis tab."
        )

    else:

        analysis = st.session_state[
            "hld_analysis"
        ]

        if st.button(
            "🔍 Run Consistency Check",
            type="primary"
        ):

            try:

                checker = ConsistencyChecker(
                    analysis
                )

                result = (
                    checker.run_all_checks()
                )

                st.session_state[
                    "consistency_result"
                ] = result

                st.success(
                    "Consistency check completed!"
                )

            except Exception as e:

                st.error(
                    f"Consistency check failed: {e}"
                )

        # ------------------------------------------
        # Display Results
        # ------------------------------------------

        if (
            "consistency_result"
            in st.session_state
        ):

            result = st.session_state[
                "consistency_result"
            ]

            summary = result[
                "summary"
            ]

            findings = result[
                "findings"
            ]

            st.subheader(
                "📊 Consistency Summary"
            )

            # --------------------------------------
            # Summary metrics
            # --------------------------------------

            # --------------------------------------
            # Findings
            # --------------------------------------

            st.subheader(
                "🔎 Engineering Findings"
            )

            if not findings:

                st.success(
                    "No consistency findings detected."
                )

            else:

                for finding in findings:

                    severity = finding[
                        "severity"
                    ]

                    category = finding[
                        "category"
                    ]

                    finding_text = finding[
                        "finding"
                    ]

                    evidence = finding[
                        "evidence"
                    ]

                    page = finding[
                        "page"
                    ]

                    recommendation = finding[
                        "recommendation"
                    ]

                    status = finding[
                        "status"
                    ]

            # ----------------------------------
            # Severity icon
            # ----------------------------------

            if severity == "PASS":

                icon = "✅"

            elif severity == "HIGH":

                icon = "🔴"

            elif severity == "MEDIUM":

                icon = "🟠"

            elif severity == "LOW":

                icon = "🟡"

            else:

                icon = "ℹ️"

            # ----------------------------------
            # Finding card
            # ----------------------------------

            with st.container(
                border=True
            ):

                st.markdown(
                    f"## {icon} {severity}"
                )

                st.caption(
                    f"Category: {category}"
                )

                st.markdown(
                    "### Finding"
                )

                st.write(
                    finding_text
                )

                st.markdown(
                    "### 📄 Evidence"
                )

                st.info(
                    evidence
                )

                if page:

                    st.caption(
                        f"Source: Page {page}"
                    )

                    st.markdown(
                        "### 💡 Recommendation"
                    )

                    st.write(
                        recommendation
                    )

                    st.markdown(
                        f"**Status:** `{status}`"
                    )

                st.divider()

            # --------------------------------------
            # Findings
            # --------------------------------------

            st.subheader(
                "🔎 Engineering Findings"
            )

            if not findings:

                st.success(
                    "No consistency findings detected."
                )

            else:

                for finding in findings:

                    severity = finding[
                        "severity"
                    ]

                    category = finding[
                        "category"
                    ]

                    finding_text = finding[
                        "finding"
                    ]

                    evidence = finding[
                        "evidence"
                    ]

                    page = finding[
                        "page"
                    ]

                    recommendation = finding[
                        "recommendation"
                    ]

                    status = finding[
                        "status"
                    ]
                    
                    

            # ----------------------------------
            # Severity icon
            # ----------------------------------

            if severity == "PASS":

                icon = "✅"

            elif severity == "HIGH":

                icon = "🔴"

            elif severity == "MEDIUM":

                icon = "🟠"

            elif severity == "LOW":

                icon = "🟡"

            else:

                icon = "ℹ️"

            # ----------------------------------
            # Finding card
            # ----------------------------------

            with st.container(
                border=True
            ):

                st.markdown(
                    f"## {icon} {severity}"
                )

                st.caption(
                    f"Category: {category}"
                )

                st.markdown(
                    "### Finding"
                )

                st.write(
                    finding_text
                )

                st.markdown(
                    "### 📄 Evidence"
                )

                st.info(
                    evidence
                )

                if page:

                    st.caption(
                        f"Source: Page {page}"
                    )

                    st.markdown(
                        "### 💡 Recommendation"
                    )

                    st.write(
                        recommendation
                    )

                    st.markdown(
                        f"**Status:** `{status}`"
                    )

                    # ------------------------------
                    # PASS
                    # ------------------------------

                    if severity == "PASS":

                        icon = "✅"

                    # ------------------------------
                    # WARNING
                    # ------------------------------

                    elif severity == "WARNING":

                        icon = "⚠️"

                    # ------------------------------
                    # INFO
                    # ------------------------------

                    else:

                        icon = "ℹ️"


                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### {icon} {severity}"
                        )

                        st.write(
                            f"**Category:** "
                            f"{category}"
                        )

                        # Finding
                        st.markdown(
                            "**Finding**"
                        )

                        st.write(
                            finding["finding"]
                        )

                        # Evidence
                        st.markdown(
                            "**📄 Evidence**"
                        )

                        st.info(
                            finding["evidence"]
                        )

                        # Source page
                        if finding["page"]:

                            st.caption(
                                f"Source: Page {finding['page']}"
                            )

                        # Recommendation
                        st.markdown(
                            "**💡 Recommendation**"
                        )

                        st.write(
                            finding["recommendation"]
                        )

                        # Status
                        st.markdown(
                            f"**Status:** `{finding['status']}`"
                        )


# ==================================================
# TAB 3 — QUESTIONS & ANSWERS
# ==================================================

with tab_qa:

    st.header("💬 Ask Questions")

    st.write(
        "Ask questions about the uploaded HLD "
        "and receive grounded answers with "
        "source evidence."
    )

    # ----------------------------------------------
    # Question Input
    # ----------------------------------------------

    question = st.text_input(
        "Enter your question:",
        placeholder=(
            "e.g. What are the responsibilities "
            "of BrakeControlSWC?"
        )
    )

    # ----------------------------------------------
    # Analyze Question
    # ----------------------------------------------

    if st.button(
        "🔍 Analyze HLD",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        elif "document_info" not in st.session_state:

            st.warning(
                "Please upload and process an "
                "HLD document first."
            )

        else:

            try:

                with st.spinner(
                    "Analyzing HLD document..."
                ):

                    answer, sources = (
                        rag.answer_question(
                            question,
                            top_k=3
                        )
                    )

                # ======================================
                # ANSWER
                # ======================================

                st.subheader(
                    "💡 Answer"
                )

                st.write(answer)

                # ======================================
                # SOURCES
                # ======================================

                st.subheader(
                    "📚 Sources & Evidence"
                )

                displayed_sources = set()

                for source in sources:

                    source_name = source[
                        "source"
                    ]

                    page = source[
                        "page"
                    ]

                    distance = source[
                        "distance"
                    ]

                    content = source[
                        "content"
                    ]

                    source_key = (
                        source_name,
                        page
                    )

                    if (
                        source_key
                        not in displayed_sources
                    ):

                        with st.expander(
                            f"📄 {source_name} — "
                            f"Page {page}"
                        ):

                            st.caption(
                                f"Semantic distance: "
                                f"{distance:.4f}"
                            )

                            st.markdown(
                                "**Retrieved Evidence:**"
                            )

                            st.write(
                                content
                            )

                        displayed_sources.add(
                            source_key
                        )

            except Exception as e:

                st.error(
                    f"Question processing failed: {e}"
                )