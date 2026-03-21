import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

# =====================
# Leitura do CSV
# =====================
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "train.csv")

df = pd.read_csv(
    csv_path,
    sep=",",
    encoding="ISO-8859-1",
    quoting=3,
    on_bad_lines="skip"
)

# =====================
# Tratamento de datas
# =====================
df["Data-do-Pedido"] = pd.to_datetime(
    df["Data-do-Pedido"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(subset=["Data-do-Pedido"])
df = df.sort_values("Data-do-Pedido")

df["FaturaDia"] = df["Data-do-Pedido"].dt.date
df["Year"] = df["Data-do-Pedido"].dt.year
df["Month"] = df["Data-do-Pedido"].dt.month

# =====================
# Sidebar - filtros
# =====================
year = st.sidebar.selectbox(
    "Ano",
    sorted(df["Year"].unique())
)

month = st.sidebar.selectbox(
    "Mês",
    [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"),
        (4, "Abril"), (5, "Maio"), (6, "Junho"),
        (7, "Julho"), (8, "Agosto"), (9, "Setembro"),
        (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ],
    format_func=lambda x: x[1]
)

# =====================
# Aplicar filtro
# =====================
df_filtered = df[
    (df["Year"] == year) &
    (df["Month"] == month[0])
]

# =====================
# Tabela
# =====================
st.subheader("Dados filtrados")
st.dataframe(df_filtered, use_container_width=True)

# =====================
# Se não houver dados → para aqui
# =====================
if df_filtered.empty:
    st.warning("Sem dados para o período selecionado")
    st.stop()

# =====================
# Agrupar vendas por dia e cidade
# =====================
df_grouped = (
    df_filtered
    .groupby(["FaturaDia", "Cidade"])["Vendas"]
    .sum()
    .reset_index()
)

top_5_cities = (
    df_grouped
    .groupby("Cidade")["Vendas"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

df_top5 = df_grouped[df_grouped["Cidade"].isin(top_5_cities)]

# =====================
# Produtos mais vendidos
# =====================
df_products = (
    df_filtered
    .dropna(subset=["Nome-do-Produto"])
    .groupby("Nome-do-Produto")["Vendas"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# =====================
# Layout
# =====================
col1, col2 = st.columns(2)

# Gráfico 1
fig_date = px.bar(
    df_top5,
    x="FaturaDia",
    y="Vendas",
    color="Cidade",
    title="Vendas por Dia"
)

col1.plotly_chart(fig_date, width="stretch")

# Gráfico 2
if df_products.empty:
    col2.warning("Não há dados de produtos para o período selecionado.")
else:
    fig_products = px.bar(
        df_products,
        x="Vendas",
        y="Nome-do-Produto",
        orientation="h",
        title="Produtos Mais Vendidos"
    )

    col2.plotly_chart(fig_products, width="stretch")