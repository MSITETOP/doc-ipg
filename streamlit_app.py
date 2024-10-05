import hmac
import streamlit as st
import assemblyai as aai
from openai import OpenAI
from htmlTemplates import links

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
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id="asst_nB18mkuiU34T645GttfB9Dpl",
    ) as stream:
        for event in stream:
            #print(event)
            # Print the text from text delta events
            if event.event == "thread.message.delta" and event.data.delta.content:
                #print(event.data.delta.content[0].text)
                yield event.data.delta.content[0].text.value


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Show title and description.
st.title("📄 Ответы по документу")
st.write("Загрузите документ ниже и задайте по нему вопрос – GPT ответит! ")

# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["KEY"])


type = st.radio(
    "Выбери тип документа",
    ["Аудио/Видео", "Текст"],
    index = None
)

if type == "Аудио/Видео":
    uploaded_file = st.file_uploader(
        "Загрузи файл", type=(".webm", ".aac", ".mov", ".ac3", ".mp2", ".aif", ".mp4", ".m4p", ".m4v", ".aiff", ".flac", ".flv", ".m4a", ".mp3", ".mpga", ".ogg", ".wav", ".wma")
    )

    if uploaded_file:
        aai.settings.api_key = st.secrets["AAI"]
        config = aai.TranscriptionConfig(speaker_labels=True, language_code = "ru")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(uploaded_file, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            st.error(f"Transcription failed: {transcript.error}")
        else:
            st.write(f"Длительность: {transcript.audio_duration} сек.")
            for utterance in transcript.utterances:
                st.write(f"Speaker {utterance.speaker} {utterance.start//1000} - {utterance.end//1000}: {utterance.text}")
elif type == "Текст":
    # Let the user upload a file via `st.file_uploader`.
    uploaded_files = st.file_uploader(
        "Загрузи документы", accept_multiple_files = True, type=(".c", ".cpp", ".css", ".doc", ".docx", ".go", ".html", ".java", ".js", ".json", ".md", ".pdf", ".php", ".pptx", ".py", ".rb", ".sh", ".ts", ".txt")
    )

    if uploaded_files:
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.attach = []
            for uploaded_file in uploaded_files:
                message_file = client.files.create(file=uploaded_file, purpose="assistants")
                st.session_state.attach.append({ 
                    "file_id": message_file.id, 
                    "tools": [{"type": "file_search"}] 
                })

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := st.chat_input("Задай вопросы по документу"):
            # Store and display the current prompt.
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt, 
                "attachments": st.session_state.attach
            })
            with st.chat_message("user"):
                st.markdown(prompt)

            thread = client.beta.threads.create(
                messages=[
                    {"role": m["role"], "content": m["content"], "attachments": m["attachments"]}
                    for m in st.session_state.messages
                ]
            )

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream_data)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "attachments": []
            })
        
    
