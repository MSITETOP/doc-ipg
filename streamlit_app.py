import streamlit as st
from openai import OpenAI

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
        "Загрузите документы (.txt, .doc, .pdf)", type=("txt", "doc", "pdf")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Задай вопросы по документу",
        placeholder="Можешь дать мне краткое содержимое документа?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Вот документы: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
