import streamlit as st

from database import (
    initialize_database,
    save_memory,
    search_memories,
    get_memories
)

from conversation import (
    get_relevant_memories,
    ask_groq
)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

initialize_database()


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="ECHO",
    page_icon="🧠",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #0b1020;
}

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

.echo-title {
    font-size: 4rem;
    font-weight: 700;
    letter-spacing: 8px;
    margin-bottom: 0;
}

.echo-subtitle {
    font-size: 1.2rem;
    opacity: 0.7;
    margin-top: 0;
    margin-bottom: 3rem;
}

.memory-card {
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    background-color: rgba(255,255,255,0.04);
    margin-bottom: 1rem;
}

.memory-id {
    font-size: 0.8rem;
    opacity: 0.5;
}

.memory-text {
    font-size: 1.1rem;
    margin-top: 0.8rem;
    margin-bottom: 1rem;
}

.source {
    font-size: 0.85rem;
    opacity: 0.7;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="echo-title">ECHO</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="echo-subtitle">A memory that outlives you.</div>',
    unsafe_allow_html=True
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("ECHO")

st.sidebar.markdown(
    "### Digital Memory Legacy"
)

st.sidebar.markdown(
    """
Preserve experiences today so
future generations can ask about them tomorrow.
"""
)

option = st.sidebar.radio(
    "Navigate",
    [
        "🧠 Preserve Memory",
        "🔎 Explore Memories",
        "💬 Talk to ECHO",
        "📜 Memory Timeline"
    ]
)


# ==========================================
# PRESERVE MEMORY
# ==========================================

if option == "🧠 Preserve Memory":

    st.header("🧠 Preserve a Memory")

    st.write(
        "Tell ECHO something you want future generations to remember."
    )

    person = st.text_input(
        "Who is this memory about?"
    )

    memory_text = st.text_area(
        "Tell the story",
        height=180,
        placeholder="Write the memory here..."
    )

    col1, col2 = st.columns(2)

    with col1:

        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=2026
        )

    with col2:

        place = st.text_input(
            "Place"
        )

    importance = st.slider(
        "How important is this memory?",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )


    if st.button(
        "Preserve Memory 🧠",
        use_container_width=True
    ):

        if not person or not memory_text:

            st.warning(
                "Please provide the person and the memory."
            )

        else:

            memory = {
                "person": person,
                "text": memory_text,
                "year": year,
                "place": place,
                "importance": importance
            }

            save_memory(memory)

            st.success(
                "Memory successfully preserved in ECHO."
            )


# ==========================================
# EXPLORE MEMORIES
# ==========================================

elif option == "🔎 Explore Memories":

    st.header("🔎 Explore Memories")

    keyword = st.text_input(
        "What do you want to remember?"
    )


    if keyword:

        results = search_memories(keyword)


        if not results:

            st.info(
                "ECHO couldn't find a matching memory."
            )

        else:

            st.write(
                f"Found {len(results)} preserved memory(s)."
            )


            for memory in results:

                st.markdown(
                    f"""
                    <div class="memory-card">

                    <div class="memory-id">
                    MEMORY #{memory[0]}
                    </div>

                    <div class="memory-text">
                    {memory[2]}
                    </div>

                    <div class="source">
                    👤 {memory[1]}
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    📅 {memory[3] if memory[3] else "Unknown"}
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    📍 {memory[4] if memory[4] else "Unknown"}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ==========================================
# TALK TO ECHO
# ==========================================

elif option == "💬 Talk to ECHO":

    st.header("💬 Talk to ECHO")

    st.write(
        "Ask questions about the memories that have been preserved."
    )


    if "messages" not in st.session_state:

        st.session_state.messages = []


    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])


    question = st.chat_input(
        "Ask ECHO something..."
    )


    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        with st.chat_message("user"):

            st.write(question)


        with st.chat_message("assistant"):

            with st.spinner(
                "Searching preserved memories..."
            ):

                try:

                    memory_context = get_relevant_memories(
                        question
                    )

                    answer = ask_groq(
                        memory_context,
                        question
                    )

                    st.write(answer)

                    st.caption(
                        "🧠 Response generated from preserved memories."
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                except Exception as error:

                    st.error(
                        f"Something went wrong: {error}"
                    )


# ==========================================
# MEMORY TIMELINE
# ==========================================

elif option == "📜 Memory Timeline":

    st.header("📜 Memory Timeline")

    memories = get_memories()


    if not memories:

        st.info(
            "No memories have been preserved yet."
        )

    else:

        memories = sorted(
            memories,
            key=lambda memory: (
                memory[3] is None,
                memory[3]
                if memory[3] is not None
                else 0
            )
        )


        for memory in memories:

            year = (
                memory[3]
                if memory[3] is not None
                else "Unknown"
            )

            st.markdown(
                f"""
                ### 📅 {year}

                **{memory[1]}**

                {memory[2]}

                📍 {memory[4] if memory[4] else "Unknown"}

                ---
                """
            )