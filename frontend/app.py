import streamlit as st
import requests
import base64
# ==========================================
# CONFIGURATION
# ==========================================

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Christian AI Assistant",
    page_icon="✝",
    layout="wide"
)

# ==========================================
# CUSTOM STYLING
# ==========================================

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.stTextInput input {
    border-radius: 10px;
}

.stButton button {
    border-radius: 10px;
    width: 100%;
}

.response-box {
    padding: 1rem;
    border-radius: 10px;
    background-color: #f7f7f7;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================

st.title("✝ Christian AI Assistant")

st.markdown("""
Ask Christianity-related questions with:
- Scripture-grounded responses
- Bible verse citations
- Denomination-aware handling
- Christian image generation
- Safety moderation
""")

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("⚙ Settings")

denomination = st.sidebar.selectbox(
    "Select denomination",
    [
        "Catholic",
        "Protestant",
        "Orthodox",
        "Non-denominational"
    ]
)

mode = st.sidebar.radio(
    "Choose Mode",
    [
        "Chat Assistant",
        "Image Generation"
    ]
)

# ==========================================
# MEMORY CONTROLS
# ==========================================

if st.sidebar.button("🧹 Clear Conversation Memory"):

    try:

        response = requests.post(
            f"{BACKEND_URL}/clear-memory"
        )

        data = response.json()

        st.sidebar.success(
            data["message"]
        )

    except Exception as e:

        st.sidebar.error(
            f"Error: {str(e)}"
        )

# ==========================================
# CHAT MODE
# ==========================================

if mode == "Chat Assistant":

    st.header("💬 Christian Chat")

    user_question = st.text_area(
        "Ask a Christianity-related question",
        height=120,
        placeholder=(
            "Example: What does the Bible "
            "say about forgiveness?"
        )
    )

    ask_button = st.button(
        "Ask Assistant"
    )

    if ask_button:

        if not user_question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Retrieving scripture and generating response..."
            ):

                try:

                    payload = {
                        "question": user_question,
                        "denomination": denomination
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/chat",
                        json=payload
                    )

                    data = response.json()

                    if not data.get("success"):

                        st.error(
                            data.get(
                                "response",
                                "Something went wrong."
                            )
                        )

                    else:

                        # ==========================
                        # ASSISTANT RESPONSE
                        # ==========================

                        st.subheader(
                            "📖 Assistant Response"
                        )

                        st.markdown(
                            f"""
                            <div class="response-box">
                            {data['response']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # ==========================
                        # SCRIPTURE GROUNDING
                        # ==========================

                        st.subheader(
                            "📜 Scripture Grounding"
                        )

                        verses = data.get(
                            "verses",
                            []
                        )

                        if verses:

                            for verse in verses:

                                st.markdown(
                                    f"""
                                    **{verse['reference']}**

                                    {verse['text']}
                                    """
                                )

                                st.divider()

                        else:

                            st.info(
                                "No scripture references found."
                            )

                except Exception as e:

                    st.error(
                        f"Connection Error: {str(e)}"
                    )

# ==========================================
# IMAGE GENERATION MODE
# ==========================================

# ==========================================
# IMAGE GENERATION MODE
# ==========================================

elif mode == "Image Generation":

    st.header("🎨 Christian Image Generation")

    image_prompt = st.text_area(
        "Describe the Christian image",
        height=120,
        placeholder=(
            "Example: Moses parting the Red Sea"
        )
    )

    generate_button = st.button(
        "Generate Christian Image"
    )

    if generate_button:

        if not image_prompt.strip():

            st.warning(
                "Please enter an image description."
            )

        else:

            with st.spinner(
                "Generating Christian artwork..."
            ):

                try:

                    payload = {
                        "prompt": image_prompt
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/generate-image",
                        json=payload
                    )

                    data = response.json()

                    if not data.get("success"):

                        st.error(
                            data.get(
                                "error",
                                "Image generation failed."
                            )
                        )

                    else:

                        st.subheader(
                            "🖼 Generated Image"
                        )

                        # Decode base64 image
                        image_bytes = base64.b64decode(
                            data["image_base64"]
                        )

                        # Display image
                        st.image(
                            image_bytes,
                            use_container_width=True
                        )

                        # Optional description
                        if data.get("description"):

                            st.subheader(
                                "✨ Image Description"
                            )

                            st.write(
                                data["description"]
                            )

                except Exception as e:

                    st.error(
                        f"Connection Error: {str(e)}"
                    )
# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Christian AI Assistant • "
    "Built with FastAPI, Gemini, ChromaDB, and Streamlit"
)