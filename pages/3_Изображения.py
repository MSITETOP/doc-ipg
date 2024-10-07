import hmac
import streamlit as st
import assemblyai as aai
from openai import OpenAI
from htmlTemplates import links

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
st.title("Анализ изображений")
st.write("Загрузите документ ниже и задайте по нему вопрос – GPT ответит! ")

# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["KEY"])
