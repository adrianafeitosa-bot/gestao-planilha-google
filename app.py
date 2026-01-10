import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página para layout expandido
st.set_page_config(page_title="Painel de Controle - Brisanet", layout="wide")

# 1. ESTABELECER CONEXÃO
# A conexão utiliza as credenciais configuradas no Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. INICIALIZAÇÃO DO ESTADO DE SESSÃO
# Mantém o usuário logado enquanto a aba do navegador estiver aberta
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_data = None

# 3. FUNÇÃO PARA CARREGAR DADOS COM SEGURANÇA
def carregar_dados(nome_aba):
    try:
        # worksheet deve ser o nome exato da aba na sua planilha
        # ttl=0 garante que os dados de pausas/indicadores sejam lidos em tempo real
        return conn.read(worksheet=nome_aba, ttl=0)
    except Exception as e:
        st.error(f"Erro ao acessar a aba '{nome_aba}': Verifique se o e-mail da Conta de Serviço é Editor da planilha.")
        return None

# --- FLUXO DE INTERFACE ---

if not st.session_state.logado:
    # --- TELA DE LOGIN ---
    st.title("🔐 Login do Sistema")
    
    # Carrega a base de usuários da aba LOGIN
    df_usuarios = carregar_dados("LOGIN")
    
    if df_usuarios is not None:
        with st.form("painel_login"):
            email_input = st.text_input("E-mail de Login")
            senha_input = st.text_input("Senha", type="password")
            botao_acessar = st.form_submit_button("Acessar Painel")
            
            if botao_acessar:
                # Validação de Login: Compara e-mail e converte senha para string para evitar erros
                usuario_validado = df_usuarios[
                    (df_usuarios['LOGIN'] == email_input) & 
                    (df_usuarios['SENHA'].astype(str) == str(senha_input))
                ]
                
                if not usuario_validado.empty:
                    # Armazena os dados do usuário na sessão
                    st.session_state.logado = True
                    st.session_state.user_data = usuario_validado.iloc[0].to_dict()
                    st.success(f"Bem-vindo(a), {st.session_state.user_data['NOME']}!")
                    st.rerun()
                else:
                    st.error("Credenciais incorretas. Verifique seu e-mail e senha.")

else:
    # --- ÁREA LOGADA (DASHBOARD) ---
    u = st.session_state.user_data
    
    # Barra lateral com informações e botão de logout
    with st.sidebar:
        st.subheader(f"👤 {u['NOME']}")
        st.write(f"Perfil: **{u['ACESSO']}**")
        if st.button("Sair do Sistema"):
            st.session_state.logado = False
            st.rerun()
            
    st.title("📊 Painel de Indicadores")

    # 4. CARREGAMENTO E FILTRAGEM DOS DADOS GERAIS
    # Substitua "Dashboard_Geral" pelo nome da aba onde ficam as metas/indicadores
    df_geral = carregar_dados("Dashboard_Geral")

    if df_geral is not None:
        if u['
