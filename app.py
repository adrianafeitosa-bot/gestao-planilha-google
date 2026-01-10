import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão Interna", layout="wide")

# Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTADO DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_data = None

def carregar_dados(aba):
    try:
        # ttl=0 garante que os dados de pausas/metas sejam lidos em tempo real
        return conn.read(worksheet=aba, ttl=0)
    except Exception as e:
        st.error(f"Erro ao acessar a aba '{aba}': Verifique as permissões.")
        return None

# --- LÓGICA DE INTERFACE ---
if not st.session_state.logado:
    st.title("🔐 Login do Sistema")
    df_usuarios = carregar_dados("LOGIN")
    
    if df_usuarios is not None:
        with st.form("painel_login"):
            email = st.text_input("Login (E-mail)")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Acessar")
            
            if entrar:
                # Validação robusta de tipos
                filtro = df_usuarios[
                    (df_usuarios['LOGIN'] == email) & 
                    (df_usuarios['SENHA'].astype(str) == str(senha))
                ]
                
                if not filtro.empty:
                    st.session_state.logado = True
                    st.session_state.user_data = filtro.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
else:
    # --- ÁREA LOGADA ---
    u = st.session_state.user_data
    
    # Navegação Lateral
    st.sidebar.title(f"Olá, {u['NOME']}")
    st.sidebar.write(f"Perfil: **{u['ACESSO']}**")
    
    # Seletor de Abas da Planilha
    pagina = st.sidebar.radio("Selecione o Indicador:", ["Geral", "META", "CSAT", "IR"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title(f"📊 Indicadores - {pagina}")

    # Mapeamento de abas
    aba_destino = "Dashboard_Geral" if pagina == "Geral" else pagina
    df_dados = carregar_dados(aba_destino)

    if df_dados is not None:
        # Lógica de Visualização por Perfil
        if u['ACESSO'] == "Administrador":
            st.subheader(f"Visão Completa: {pagina}")
            # Filtro de busca para o Admin
            busca = st.text_input("Pesquisar por nome ou e-mail:")
            if busca:
                df_dados = df_dados[df_dados.astype(str).apply(lambda x: busca.lower() in x.str.lower().values, axis=1)]
            st.dataframe(df_dados, use_container_width=True)
        else:
            st.subheader(f"Meus Resultados: {pagina}")
            if 'LOGIN' in df_dados.columns:
                dados_filtrados = df_dados[df_dados['LOGIN'] == u['LOGIN']]
                st.dataframe(dados_filtrados, use_container_width=True)
            else:
                st.warning(f"A aba {pagina} não possui coluna 'LOGIN' para filtrar seu acesso.")
