import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Portal de Indicadores", layout="wide")

# 1. CONEXÃO COM O GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# URL da aba LOGIN (usando o link com GID para evitar erros de descoberta de aba)
URL_ABA_LOGIN = "https://docs.google.com/spreadsheets/d/17nviSL3em2Z4NrkQIINDUsKjthPNiYTVNH5UwSfC8Pk/edit#gid=1610446452"

# 2. FUNÇÃO PARA CARREGAR USUÁRIOS
@st.cache_data(ttl=60)
def carregar_usuarios():
    # Lê a aba de logins usando o link direto
    return conn.read(spreadsheet=URL_ABA_LOGIN)

try:
    df_usuarios = carregar_usuarios()
except Exception as e:
    st.error(f"Erro ao conectar com a base de usuários: {e}")
    st.stop()

# 3. GERENCIAMENTO DE ESTADO DA SESSÃO (LOGIN)
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.session_state.user_name = ""

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.markdown("## 🔐 Acesso ao Sistema")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.form("form_login"):
                email_input = st.text_input("E-mail (Login)")
                # A senha na sua planilha é numérica, tratamos como string para comparar
                senha_input = st.text_input("Senha", type="password")
                botao_entrar = st.form_submit_button("Entrar")

                if botao_entrar:
                    # Verifica se o usuário e senha coincidem
                    usuario_valido = df_usuarios[
                        (df_usuarios['LOGIN'] == email_input) & 
                        (df_usuarios['SENHA'].astype(str) == str(senha_input))
                    ]
                    
                    if not usuario_valido.empty:
                        st.session_state.logado = True
                        st.session_state.user_email = email_input
                        st.session_state.user_role = usuario_valido.iloc[0]['ACESSO']
                        st.session_state.user_name = usuario_valido.iloc[0]['NOME']
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")

# --- TELA DO DASHBOARD (APÓS LOGIN) ---
else:
    # Sidebar de Navegação e Logout
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user_name}**")
        st.info(f"Nível de Acesso: {st.session_state.user_role}")
        
        if st.button("Sair do Sistema"):
            st.session_state.logado = False
            st.rerun()

    st.title(f"📊 Painel de Indicadores")

    # 4. CARREGAMENTO E FILTRAGEM DOS DADOS
    # Substitua "Dashboard_Geral" pelo nome exato da aba que contém os dados/metas
    try:
        # Carrega os dados da aba de indicadores
        df_dados = conn.read(worksheet="Dashboard_Geral", ttl=10)

        if st.session_state.user_role == "Administrador":
            st.subheader("Visualização Administrativa (Todos os Dados)")
            st.dataframe(df_dados, use_container_width=True)
            
            # Exemplo de formulário para adicionar novos dados (apenas para Admin)
            with st.expander("➕ Adicionar Novo Registro"):
                with st.form("novo_registro"):
                    novo_nome = st.text_input("Nome do Vendedor")
                    novo_login = st.text_input("E-mail/Login")
                    enviar = st.form_submit_button("Salvar na Planilha")
                    
                    if enviar:
                        novo_dado = pd.DataFrame([{"NOME": novo_nome, "LOGIN": novo_login}])
                        dados_atualizados = pd.concat([df_dados, novo_dado], ignore_index=True)
                        conn.update(worksheet="Dashboard_Geral", data=dados_atualizados)
                        st.success("Dados atualizados!")

        else:
            # FILTRO PARA VENDEDOR: Mostra apenas linhas onde a coluna LOGIN é igual ao e-mail logado
            st.subheader(f"Meus Resultados")
            
            # Garanta que a aba de dados possua uma coluna chamada 'LOGIN'
            df_filtrado = df_dados[df_dados['LOGIN'] == st.session_state.user_email]
            
            if df_filtrado.empty:
                st.warning("Nenhum dado encontrado para o seu usuário nesta aba.")
            else:
                st.dataframe(df_filtrado, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar a aba de dados: {e}")
        st.info("Dica: Verifique se a aba 'Dashboard_Geral' existe na sua planilha.")
