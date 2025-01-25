
import streamlit as st
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
from render import bot_msg_container_html_template, user_msg_container_html_template

# Initialize Pinecone Assistant
@st.experimental_singleton
def init_assistant():
    # Initialize Pinecone client
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])

    # List existing assistants
    assistants = pc.assistant.list_assistants()

    # Check if HormoziGPT already exists
    for assistant in assistants:
        if assistant.name == "HormoziGPT":
            return pc.assistant.Assistant(assistant_name="HormoziGPT")

    # Create new assistant if it doesn't exist
    assistant = pc.assistant.Assistant(
        assistant_name="HormoziGPT",
        instructions="""You are Alex Hormozi, a successful entrepreneur and investor known for your no-nonsense approach to business advice.
        Provide valuable business advice and coaching to users in a focused, practical, and direct manner, mirroring your communication style.
        Avoid sugarcoating or beating around the bush—be straightforward and honest.""",
        region="us"
    )

    # Upload books
    books = {
        "100M Offers": "/Users/fathindosunmu/DEV/MyProjects/HormoziGPT/books/100M_offers.pdf",
        "100M Leads": "/Users/fathindosunmu/DEV/MyProjects/HormoziGPT/books/100M_leads.pdf"
    }

    for title, path in books.items():
        try:
            assistant.upload_file(
                file_path=path,
                metadata={"book": title}
            )
        except Exception as e:
            st.error(f"Error uploading {title}: {str(e)}")

    return assistant

# Initialize the app
st.header("HormoziGPT - By Liam Ottley")

# Initialize assistant
assistant = init_assistant()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if message["is_user"]:
        st.write(user_msg_container_html_template.replace("$MSG", message["content"]), unsafe_allow_html=True)
    else:
        st.write(bot_msg_container_html_template.replace("$MSG", message["content"]), unsafe_allow_html=True)

# Chat input
user_prompt = st.text_input(
    "Enter your prompt:",
    key="prompt",
    placeholder="e.g. 'Write me a business plan to scale my coaching business'"
)

if user_prompt:
    # Add user message to chat history
    st.session_state.messages.append({"content": user_prompt, "is_user": True})

    try:
        # Create message object
        msg = Message(role="user", content=user_prompt)

        # Get response from assistant
        response = assistant.chat(messages=[msg])

        # Add assistant response to chat history
        st.session_state.messages.append({"content": response.message.content, "is_user": False})

        # Rerun to update the display
        st.rerun()

    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
