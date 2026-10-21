import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Triagem IA", layout="wide")
st.title("Triagem de atendimento com IA")


@st.cache_data(ttl=10)
def carregar() -> pd.DataFrame:
    con = sqlite3.connect("triagem.db")
    df = pd.read_sql_query("SELECT * FROM triagens ORDER BY id DESC", con)
    con.close()
    return df


df = carregar()

if df.empty:
    st.info("Ainda não há triagens. Envie mensagens pela API.")
    st.stop()

# Filtros
col_f1, col_f2 = st.columns(2)
cats = col_f1.multiselect("Categoria", sorted(df["categoria"].unique()))
urgs = col_f2.multiselect("Urgência", ["alta", "media", "baixa"])
if cats:
    df = df[df["categoria"].isin(cats)]
if urgs:
    df = df[df["urgencia"].isin(urgs)]

# Métricas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de triagens", len(df))
m2.metric("Urgência alta", int((df["urgencia"] == "alta").sum()))
m3.metric("Confiança média", f"{df['confianca'].mean():.0%}")
m4.metric("Para revisão humana", int(df["revisao_humana"].sum()))

# Gráficos
g1, g2 = st.columns(2)
g1.subheader("Por categoria")
g1.bar_chart(df["categoria"].value_counts())
g2.subheader("Por urgência")
g2.bar_chart(df["urgencia"].value_counts())

st.subheader("Mensagens por dia")
por_dia = df.assign(dia=pd.to_datetime(df["criado_em"]).dt.date).groupby("dia").size()
st.line_chart(por_dia)

# Tabela
st.subheader("Últimas triagens")
st.dataframe(
    df[["id", "criado_em", "categoria", "urgencia", "confianca", "resumo", "revisao_humana"]].head(50),
    use_container_width=True,
    hide_index=True,
)