import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Gestão Interna - Brisanet", layout="wide")

# 2. Estabelecer conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Inicialização do estado de login
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user_data = None

# 4. Função para carregar dados com tratamento de erro
def carregar_dados(aba):
    try:
        # ttl=0 para garantir dados atualizados de pausas e metas
        return conn.read(worksheet=aba, ttl=0)
    except Exception as e:
        # Se você ver esta mensagem, verifique se compartilhou a planilha com o e-mail da conta de serviço
        st.error(f"Erro ao acessar a aba '{aba}': Verifique as permissões de 'Editor' na planilha.")
        return None

# --- LÓGICA DE INTERFACE ---

if not st.session_state.logado:
    st.title("🔐 Login do Sistema")
    
    # Carrega base de usuários
    df_usuarios = carregar_dados("LOGIN")
    
    if df_usuarios is not None:
        with st.form("painel_login"):
            email_input = st.text_input("E-mail de Login")
            senha_input = st.text_input("Senha", type="password")
            botao_acessar = st.form_submit_button("Acessar Painel")
            
            if botao_acessar:
                # Validação: converte senha para string para evitar erro com números
                usuario_valido = df_usuarios[
                    (df_usuarios['LOGIN'] == email_input) & 
                    (df_usuarios['SENHA'].astype(str) == str(senha_input))
                ]
                
                if not usuario_valido.empty:
                    st.session_state.logado = True
                    st.session_state.user_data = usuario_validado.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")

else:
    # --- ÁREA LOGADA ---
    u = st.session_state.user_data
    
    # Barra lateral
    with st.sidebar:
        st.subheader(f"👤 {u['NOME']}")
        st.write(f"Perfil: **{u['ACESSO']}**")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()
            
    st.title("📊 Painel de Indicadores")

    # Carrega dados principais
    df_geral = carregar_dados("Dashboard_Geral")

    if df_geral is not None:
        # Lógica para Administrador
        if u['ACESSO'] == "Administrador":
            st.subheader("Visão Geral (Administrador)")
            st.dataframe(df_geral, use_container_width=True)
        
        # Lógica para Vendedor (Operador)
        else:
            st.subheader(f"Meus Resultados - {u['NOME']}")
            if 'LOGIN' in df_geral.columns:
                meus_dados = df_geral[df_geral['LOGIN'] == u['LOGIN']]
                if not meus_dados.empty:
                    st.dataframe(meus_dados, use_container_width=True)
                else:
                    st.info("Nenhum dado encontrado para o seu login.")
            else:
                st.warning("Coluna 'LOGIN' não encontrada na aba Dashboard_Geral.")

    # Alerta fixo sobre normas da P.A.
    st.divider()
    st.warning("⚠️ **Atenção:** Evitem o uso de celular na P.A. e cumpram rigorosamente os horários de pausa para evitar medidas administrativas.")
