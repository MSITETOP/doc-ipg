import hmac
import streamlit as st
from openai import OpenAI

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


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Show title and description.
st.title("📄 Ответы по документу")
st.write(
    "Загрузите документ ниже и задайте по нему вопрос – GPT ответит! "
)

if True:
    # Create an OpenAI client.
    client = OpenAI(api_key=st.secrets["KEY"])

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Загрузите документы", type=("c", "cpp", "css", "csv", "docx", "gif", "go", "html", "java", "jpeg", "jpg", "js", "json", "md", "pdf", "php", "pkl", "png", "pptx", "py", "rb", "tar", "tex", "ts", "txt", "webp", "xlsx", "xml", "zip")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Задай вопросы по документу",
        placeholder="Можешь дать мне краткое содержимое документа?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Upload the user provided file to OpenAI
        message_file = client.files.create(file=uploaded_file, purpose="assistants")
        # Create a thread and attach the file to the message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                    # Attach the new file to the message.
                    "attachments": [
                        { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
                    ],
                }
            ]
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id="asst_nB18mkuiU34T645GttfB9Dpl"
        )

        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")
     
        st.write(message_content.value)
