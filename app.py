import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão Interna", layout="wide")

# Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INICIALIZAÇÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_data = None

# Função para carregar dados - Use ttl=0 para forçar a leitura real e evitar o erro Not Found
def carregar_dados(aba):
    try:
        # worksheet deve ser EXATAMENTE como na planilha: "USUARIO-SITE"
        return conn.read(worksheet=aba, ttl=0)
    except Exception as e:
        st.error(f"Erro ao acessar a aba '{aba}': {e}")
        return None

# --- LÓGICA DE INTERFACE ---
if not st.session_state.logado:
    st.title("🔐 Login do Sistema")
    
    # Busca a aba renomeada conforme sua última imagem
    df_usuarios = carregar_dados("USUARIO-SITE")
    
    if df_usuarios is not None:
        with st.form("painel_login"):
            email = st.text_input("Login (E-mail)")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Acessar")
            
            if entrar:
                # Validação convertendo senha para string
                filtro = df_usuarios[
                    (df_usuarios['LOGIN'] == email) & 
                    (df_usuarios['SENHA'].astype(str) == str(senha))
                ]
                
                if not filtro.empty:
                    st.session_state.logado = True
                    st.session_state.user_data = filtro.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Tente novamente.")
else:
    # --- ÁREA LOGADA ---
    u = st.session_state.user_data
    st.sidebar.title(f"Bem-vindo, {u['NOME']}")
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📊 Painel de Indicadores")
    
    # Carrega os dados da aba de indicadores
    df_geral = carregar_dados("Dashboard_Geral")

    if df_geral is not None:
        if u['ACESSO'] == "Administrador":
            st.subheader("Visão Geral do Administrador")
            st.dataframe(df_geral, use_container_width=True)
        else:
            st.subheader(f"Meus Resultados")
            if 'LOGIN' in df_geral.columns:
                dados_filtrados = df_geral[df_geral['LOGIN'] == u['LOGIN']]
                st.dataframe(dados_filtrados, use_container_width=True)
