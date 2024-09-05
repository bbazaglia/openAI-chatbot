from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import uuid

# Load environment variables from .env file
load_dotenv()

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Generate a unique session ID for each new session
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# Add sidebar for assistant selection
st.sidebar.header("Sobre qual tema você quer falar?")
assistant_options = {
    "RH e Sustentabilidade": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("RH_SUSTENTABILIDADE_SYSTEM_MESSAGE")
    },
    "Liderança e Estratégia": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("LIDERANCA_E_ESTRATEGIA_SYSTEM_MESSAGE")
    },
    "Tecnologia, Produto e Inovação": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("TECNOLOGIA_PRODUTO_INOVACAO_SYSTEM_MESSAGE")
    },
    "Cibersegurança": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("CIBERSEGURANCA_SYSTEM_MESSAGE")
    },
    "Jurídico e Compliance": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("JURIDICO_COMPLIANCE_SYSTEM_MESSAGE")
    },
    "Marketing e Sales": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("MARKETING_SALES_SYSTEM_MESSAGE")
    },
    "Finanças e Contabilidade": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("FINANCAS_CONTABILIDADE_SYSTEM_MESSAGE")
    },
    "CX e Atendimento ao Cliente": {
        "model": "gpt-4o-mini",
        "system_message": os.getenv("CX_ATENDIMENTO_CLIENTE_SYSTEM_MESSAGE")
    }
}

selected_assistant = st.sidebar.selectbox(
    "Selecione o tipo de assistente:",
    list(assistant_options.keys())
)

# Load selected assistant settings
st.session_state["openai_model"] = assistant_options[selected_assistant]["model"]
system_message_content = assistant_options[selected_assistant]["system_message"]

# Load chat history from shelve file based on session ID
def load_chat_history(session_id):
    with shelve.open("chat_history") as db:
        return db.get(session_id, [])

# Save chat history to shelve file based on session ID
def save_chat_history(session_id, messages):
    with shelve.open("chat_history") as db:
        db[session_id] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    # Only add user-visible messages to the session state
    st.session_state.messages = load_chat_history(st.session_state["session_id"])

# This system message is used for setting the assistant's behavior
system_message = {"role": "system", "content": system_message_content}

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("Como eu posso te ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        # Include the system message in the request, but not in the visible chat history
        conversation_history = [system_message] + st.session_state["messages"]
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=conversation_history,
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state["session_id"], st.session_state.messages)
