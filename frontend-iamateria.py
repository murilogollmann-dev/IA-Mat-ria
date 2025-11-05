import streamlit as st
import pandas as pd
import numpy as np

# 🧱 Configuração da página
st.set_page_config(page_title="IA Matéria", page_icon="🤖", layout="centered")
st.title("Descubra seu Material!")

# 📂 Carrega o Excel numérico
df = pd.read_excel("materiais_numerico.xlsx")

# === Inicializa session_state ===
if "chats" not in st.session_state:
    st.session_state["chats"] = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = "Chat 1"

# === FUNÇÕES AUXILIARES ===
def criar_chat():
    novo_nome = f"Chat {len(st.session_state['chats']) + 1}"
    st.session_state["chats"][novo_nome] = []
    st.session_state["current_chat"] = novo_nome

def remover_chat(nome):
    if len(st.session_state["chats"]) > 1:
        del st.session_state["chats"][nome]
        # muda para o primeiro chat existente
        st.session_state["current_chat"] = list(st.session_state["chats"].keys())[0]
    else:
        st.warning("❗ É necessário ter pelo menos um chat ativo.")

# === SIDEBAR ===
with st.sidebar:
    st.title("💬 Seus Chats")

    # Botão novo chat
    if st.button("➕ Novo Chat"):
        criar_chat()

    st.markdown("---")

    # Lista todos os chats
    for nome_chat in list(st.session_state["chats"].keys()):
        col1, col2 = st.columns([6, 1])  # apenas duas colunas
        with col1:
            if st.button(f"💭 {nome_chat}", key=f"btn_{nome_chat}"):
                st.session_state["current_chat"] = nome_chat
        with col2:
            if st.button("❌", key=f"del_{nome_chat}"):
                remover_chat(nome_chat)
                st.rerun()

    st.markdown("---")
    st.subheader("👨‍💻 Desenvolvido por:")
    st.markdown("""
    - *Cauã*
    - *Lázaro*
    - *Mateus*
    - *Murilo*
    """)
# === ÁREA PRINCIPAL ===
st.title(f"🤖 IA Matéria — {st.session_state['current_chat']}")

# Recupera histórico do chat atual
chat_atual = st.session_state["chats"][st.session_state["current_chat"]]

# Mostra mensagens anteriores
for msg in chat_atual:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Mostra legenda das propriedades
st.info("""
Digite as propriedades numéricas do material.  
Exemplo:  
`tipo=2, peso=1, resistencia=3, condutividade=4, reciclavel=1, biodegradavel=0, toxicidade=1, temperatura_max=200`
""")

# Mostra colunas disponíveis para ajudar o usuário
st.write("📊 **Propriedades disponíveis:**")
st.write(", ".join(df.columns))

# Entrada do usuário
if prompt := st.chat_input("Descreva o material:"):
    chat_atual.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Extrai propriedades digitadas
        entrada = {}
        for par in prompt.split(","):
            if "=" in par:
                chave, valor = par.split("=")
                entrada[chave.strip()] = float(valor.strip())

        entrada_df = pd.DataFrame([entrada])
        entrada_df = entrada_df.reindex(columns=df.columns, fill_value=0)
        entrada_df = entrada_df.drop(columns=["nome_material"], errors="ignore")

        # Garante que o DataFrame base está preparado (somente colunas numéricas)
        df_num = df.select_dtypes(include=[np.number])

        # Calcula distância euclidiana
        distancias = np.sqrt(((df_num - entrada_df.iloc[0]) ** 2).sum(axis=1))

        # Normaliza similaridade (0 a 100%)
        similaridades = 1 - (distancias / distancias.max())
        similaridades = (similaridades * 100).clip(lower=0)

        # Junta com o nome dos materiais
        resultados = pd.DataFrame({
            "Material": df["nome_material"],
            "Similaridade (%)": similaridades.round(2)
        }).sort_values(by="Similaridade (%)", ascending=False).head(3)

        # Cria resposta formatada
        resposta = "🔎 **Materiais mais compatíveis:**\n\n"
        for i, row in resultados.iterrows():
            resposta += f"**{row['Material']}** — Similaridade: {row['Similaridade (%)']}%\n"

    except Exception as e:
        resposta = f"⚠️ Não consegui interpretar sua entrada.\n\n**Erro técnico:** {e}"

    # Mostra resposta
    chat_atual.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)



