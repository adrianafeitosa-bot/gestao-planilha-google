import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Dashboard Restrito", layout="wide")

# --- CONEXÃO E CARREGAMENTO DE USUÁRIOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Carrega a aba de logins (ajuste o nome da worksheet se necessário)
# Tente ajustar esta linha no seu código:
https://docs.google.com/spreadsheets/d/17nviSL3em2Z4NrkQIINDUskjtHPNiYTVNH5UwSfC8Pk/edit?gid=1610446452#gid=1610446452
df_usuarios = conn.read(worksheet="LOGIN", ttl=60)

# --- SISTEMA DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.session_state.user_name = ""

def realizar_login():
    email_input = st.text_input("E-mail (Login)")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        # Verifica se existe a combinação e-mail e senha (convertendo senha para string)
        usuario_validado = df_usuarios[
            (df_usuarios['LOGIN'] == email_input) & 
            (df_usuarios['SENHA'].astype(str) == str(senha_input))
        ]
        
        if not usuario_validado.empty:
            st.session_state.logado = True
            st.session_state.user_email = email_input
            st.session_state.user_role = usuario_validado.iloc[0]['ACESSO']
            st.session_state.user_name = usuario_validado.iloc[0]['NOME']
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# --- TELA PRINCIPAL ---
if not st.session_state.logado:
    st.header("Por favor, faça o login")
    realizar_login()
else:
    # Sidebar com informações do usuário
    with st.sidebar:
        st.write(f"👤 **Usuário:** {st.session_state.user_name}")
        st.write(f"🔑 **Acesso:** {st.session_state.user_role}")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    st.title(f"Bem-vindo, {st.session_state.user_name}!")

    # --- LÓGICA DE FILTRAGEM ---
    # Vamos ler a aba de dados (ex: Dashboard_Geral ou META)
    # Importante: a aba de dados deve ter uma coluna de 'E-mail' ou 'Vendedor' para filtrar
    df_dados = conn.read(worksheet="Dashboard_Geral", ttl=5)

    if st.session_state.user_role == "Administrador":
        st.subheader("Visualização Completa (Admin)")
        st.dataframe(df_dados)
    else:
        st.subheader("Meus Indicadores")
        # FILTRO: Aqui você deve filtrar pela coluna que identifica o vendedor.
        # Ajuste o nome da coluna 'LOGIN' ou 'Email' conforme estiver na sua aba de dados
        dados_filtrados = df_dados[df_dados['LOGIN'] == st.session_state.user_email]
        
        if dados_filtrados.empty:
            st.warning("Não foram encontrados dados para o seu usuário.")
        else:
            st.dataframe(dados_filtrados)
