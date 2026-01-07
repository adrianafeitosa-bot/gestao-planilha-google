import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Painel de Controle - Google Sheets")

# 1. Estabelecer a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Ler os dados da planilha
# O ttl=5 garante que os dados atualizem a cada 5 segundos
data = conn.read(worksheet="Página1", ttl=5)

st.write("### Visualização da Planilha")
st.dataframe(data)

# 3. Formulário para adicionar novos dados
with st.sidebar:
    st.header("Adicionar Novo Registro")
    with st.form("meu_formulario"):
        # Adapte estes campos para as colunas da sua planilha real!
        # Exemplo: Se sua planilha tem colunas 'Nome' e 'Email'
        coluna1 = st.text_input("Nome") 
        coluna2 = st.text_input("Email")
        
        enviado = st.form_submit_button("Enviar para Planilha")

        if enviado:
            # Cria uma nova linha com os dados
            novo_dado = pd.DataFrame([{"Nome": coluna1, "Email": coluna2}])
            
            # Junta com os dados antigos
            dados_atualizados = pd.concat([data, novo_dado], ignore_index=True)
            
            # Atualiza a planilha no Google
            conn.update(worksheet="Página1", data=dados_atualizados)
            
            st.success("Dados salvos com sucesso!")
