from pyngrok import ngrok
import os

# Открываем туннель на локальный Streamlit (порт 8501)
public_url = ngrok.connect(8501)
print("🌐 Public URL:", public_url)

# Запускаем Streamlit
os.system("streamlit run main.py")
