import hmac
import streamlit as st
import assemblyai as aai
from openai import OpenAI
from swarm import Swarm, Agent
from htmlTemplates import links
import json

st.set_page_config(page_title="AI анализ ауди/видео файлов",layout="wide")
st.markdown(links, unsafe_allow_html=True)
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Пароль входа", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Пароль не верный")
    return False

def stream_data():
    agent_a = Agent(
        name="Agent A",
        model="gpt-4o-mini",#"gpt-4o",#"gpt-4o-mini","o1-preview
        instructions="Ты универсальный AI Ассистент",
    )

    stream = sw.run(
        agent=agent_a,
        stream=True,
        messages=st.session_state.messages,
    )

    for chunk in stream:
        if "content" in chunk and chunk["content"]:
            yield chunk["content"]

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Show title and description.
st.title("Анализ изображений")
st.write("Загрузите документ ниже и задайте по нему вопрос – GPT ответит! ")

# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["KEY"])
sw = Swarm(client = client)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_files = st.file_uploader(
    "Загрузи изображения", key = "upload_file", label_visibility = "hidden", accept_multiple_files = True, type=(".png", ".jpg", ".jpeg", ".webp")
)

files = []
if uploaded_files:
    with st.spinner('Загрузка изображений...'):
        for uploaded_file in uploaded_files:
            message_file = client.files.create(file=uploaded_file, purpose="assistants")
            files.append({ 
                "file_id": message_file.id, 
                "tools": [{"type": "file_search"}] 
            })
    st.success("Изображения загружены!")

if prompt := st.chat_input("Ваш запрос"):
    st.session_state.messages.append({
        "role": "user", 
        "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {"url":"https://image-coze.msite.top/20d30076-a108-42a9-b1b7-f0b29ccd4ef3.jpg"}
            },
        ], 
        #"attachments": files
    })

    print(st.session_state.messages)
    with st.chat_message("assistant"):
        response = st.write_stream(stream_data)

    files = []            
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response, 
        "attachments": []
    })