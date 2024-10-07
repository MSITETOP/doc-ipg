import hmac
import streamlit as st
import assemblyai as aai
from openai import OpenAI
from htmlTemplates import links

st.set_page_config(page_title="AI анализ файлов",layout="wide")

st.title("📄 AI анализ файлов")
st.write("Загрузите документ ниже и задайте по нему вопрос – GPT ответит! ")