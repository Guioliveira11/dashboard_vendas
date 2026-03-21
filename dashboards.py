import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

# =====================
# Leitura do CSV
# =====================
# Usar caminho absoluto baseado no diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data.csv")

df = pd.read_csv(
    csv_path,
    sep=None,
    engine="python",
    encoding="ISO-8859-1"
)

# =====================
# Tratamento de datas
# =====================
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df = df.sort_values("InvoiceDate")


# 🔧 Normalizar para dia (remove hora/minuto/segundo)
df["InvoiceDay"] = df["InvoiceDate"].dt.date


# =====================
# Criar colunas auxiliares
# =====================
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month

# 🔹 Criar coluna Total (corrige o erro)
df["Total"] = df["Quantity"] * df["UnitPrice"]

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
# Tabela acima do gráfico
# =====================
st.subheader("Dados filtrados")
st.dataframe(df_filtered, use_container_width=True)

# =====================
# Agrupar vendas por dia
# =====================
df_grouped = (
    df_filtered
    .groupby(["InvoiceDay", "Country"])["Total"]
    .sum()
    .reset_index()
)

# Filtrar pelos 5 principais países
top_5_countries = (
    df_grouped
    .groupby("Country")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)


df_top5 = df_grouped[df_grouped["Country"].isin(top_5_countries)]

# =====================
# Produtos mais vendidos    
# =====================
df_products = (
    df_filtered
    .dropna(subset=["Description"])
    .groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)


# =====================
# Layout
# =====================
col1, col2 = st.columns(2)


# Gráfico1: Vendas por dia

fig_date = px.bar(
    df_top5,
    x="InvoiceDay",
    y="Total",
    color = "Country", 
    title="Vendas por Dia"
)

col1.plotly_chart(fig_date, use_container_width=True)

# Gráfico 2 - Produtos mais vendidos
if df_products.empty:
    col2.warning("Não há dados de produtos para o período selecionado.")
else:
    fig_products = px.bar(
        df_products,
        x="Quantity",
        y="Description",
        orientation="h",
        title="Produtos Mais Vendidos"
    )
    col2.plotly_chart(fig_products, use_container_width=True)

