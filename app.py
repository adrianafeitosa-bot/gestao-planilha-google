import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão Interna", layout="wide")

# Conexão com a planilha configurada nas 'Secrets' do Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INICIALIZAÇÃO DO ESTADO DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_data = None

# --- FUNÇÃO PARA CARREGAR DADOS COM SEGURANÇA ---
def carregar_dados(aba):
    try:
        # Busca a aba pelo nome exato configurado na planilha
        # ttl=0 evita erros de cache durante os testes
        return conn.read(worksheet=aba, ttl=0)
    except Exception as e:
        st.error(f"Erro ao acessar a aba '{aba}': Verifique se o e-mail da conta de serviço foi adicionado como 'Editor' na planilha.")
        return None

# --- LÓGICA DE INTERFACE ---
if not st.session_state.logado:
    st.title("🔐 Login do Sistema")
    
    # Tenta carregar a aba de logins
    df_usuarios = carregar_dados("LOGIN")
    
    if df_usuarios is not None:
        with st.form("painel_login"):
            email = st.text_input("Login (E-mail)")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Acessar")
            
            if entrar:
                # Validação (trata a senha como texto para evitar erros com números)
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
    # --- ÁREA LOGADA (Apenas após login bem-sucedido) ---
    u = st.session_state.user_data
    st.sidebar.title(f"Bem-vindo, {u['NOME']}")
    st.sidebar.write(f"Perfil: **{u['ACESSO']}**")
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📊 Painel de Indicadores")

    # Carrega os dados da aba de indicadores (ex: Dashboard_Geral)
    df_geral = carregar_dados("Dashboard_Geral")

    if df_geral is not None:
        if u['ACESSO'] == "Administrador":
            st.subheader("Visão Geral do Administrador")
            st.dataframe(df_geral, use_container_width=True)
        else:
            st.subheader(f"Meus Resultados")
            # Filtra apenas os dados do usuário logado
            if 'LOGIN' in df_geral.columns:
                dados_filtrados = df_geral[df_geral['LOGIN'] == u['LOGIN']]
                st.dataframe(dados_filtrados, use_container_width=True)
            else:
                st.warning("Coluna 'LOGIN' não encontrada na aba de dados para filtrar resultados.")
