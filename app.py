import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Painel de Indicadores", layout="wide")

# 1. ESTABELECER CONEXÃO
# Certifique-se de que o e-mail da conta de serviço tem acesso à planilha no Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. GERENCIAR ESTADO DE LOGIN
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_name = ""
    st.session_state.user_role = ""
    st.session_state.user_email = ""

# 3. FUNÇÃO PARA CARREGAR DADOS COM TRATAMENTO DE ERRO
def carregar_aba(nome_aba):
    try:
        # Forçamos ttl=0 durante testes para evitar erros de cache/404 antigos
        return conn.read(worksheet=nome_aba, ttl=0)
    except Exception as e:
        st.error(f"Erro ao acessar a aba '{nome_aba}': {e}")
        return None

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Login do Sistema")
    
    # Carregar base de usuários da aba LOGIN
    df_usuarios = carregar_aba("LOGIN")
    
    if df_usuarios is not None:
        with st.form("login_form"):
            login_input = st.text_input("Login (E-mail)")
            senha_input = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar")
            
            if entrar:
                # Filtrar usuário na base (tratando senha como texto)
                usuario = df_usuarios[
                    (df_usuarios['LOGIN'] == login_input) & 
                    (df_usuarios['SENHA'].astype(str) == str(senha_input))
                ]
                
                if not usuario.empty:
                    st.session_state.logado = True
                    st.session_state.user_name = usuario.iloc[0]['NOME']
                    st.session_state.user_role = usuario.iloc[0]['ACESSO']
                    st.session_state.user_email = login_input
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# --- DASHBOARD (APÓS LOGIN) ---
else:
    st.sidebar.success(f"Bem-vindo, {st.session_state.user_name}!")
    st.sidebar.write(f"Perfil: **{st.session_state.user_role}**")
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📊 Indicadores de Desempenho")

    # Carregar aba de indicadores (ex: Dashboard_Geral)
    df_dados = carregar_aba("Dashboard_Geral")

    if df_dados is not None:
        if st.session_state.user_role == "Administrador":
            st.subheader("Painel Administrativo - Visão Geral")
            st.dataframe(df_dados, use_container_width=True)
        else:
            st.subheader(f"Meus Resultados - {st.session_state.user_name}")
            # Filtrar os dados para mostrar apenas os do usuário logado
            # Assume que a aba de dados tem uma coluna 'LOGIN' para identificação
            if 'LOGIN' in df_dados.columns:
                dados_vendedor = df_dados[df_dados['LOGIN'] == st.session_state.user_email]
                if not dados_vendedor.empty:
                    st.dataframe(dados_vendedor, use_container_width=True)
                else:
                    st.info("Nenhum dado encontrado para o seu usuário.")
            else:
                st.warning("Coluna 'LOGIN' não encontrada na aba de indicadores.")
