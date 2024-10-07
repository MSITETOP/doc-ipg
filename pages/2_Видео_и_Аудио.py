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

if True:
    uploaded_file = st.file_uploader(
        "Загрузи файл", type=(".webm", ".aac", ".mov", ".ac3", ".mp2", ".aif", ".mp4", ".m4p", ".m4v", ".aiff", ".flac", ".flv", ".m4a", ".mp3", ".mpga", ".ogg", ".wav", ".wma")
    )

    if uploaded_file:
        with st.spinner('Идет обработка...'):
            aai.settings.api_key = st.secrets["AAI"]
            config = aai.TranscriptionConfig(speaker_labels=True, language_code = "ru")
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(uploaded_file, config=config)

            if transcript.status == aai.TranscriptStatus.error:
                st.error(f"Transcription failed: {transcript.error}")
            else:
                st.write(f"Длительность: {transcript.audio_duration} сек.")
                for utterance in transcript.utterances:
                    st.chat_message("user", avatar="🧑‍💻").write(f"{utterance.speaker} {utterance.start//1000} - {utterance.end//1000}: {utterance.text}")
#😈👹😺👾👻🤡🤠