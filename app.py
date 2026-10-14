from datetime import date

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


# =========================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Radar de Pesca Ceará - SaaS Pro",
    page_icon="🎣",
    layout="wide",
)


# =========================================================
# 2. ESTILO VISUAL
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #10283a 100%);
        color: #f2f7fc;
    }

    h1, h2, h3, p, label {
        color: #f2f7fc !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        padding: 18px;
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
    }

    section[data-testid="stSidebar"] {
        background: #091827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. PONTOS COSTEIROS DO CEARÁ
#
# lat_mapa/lon_mapa: posição aproximada do marcador no mar.
# lat_api/lon_api: posição de referência para consultar
# as condições meteorológicas.
#
# IMPORTANTE:
# As coordenadas são aproximadas, não pontos náuticos
# oficialmente verificados.
# =========================================================

LOCAIS_PESCA = [
    {
        "nome": "Praia Redonda - Icapuí",
        "lat_mapa": -4.652,
        "lon_mapa": -37.448,
        "lat_api": -4.655,
        "lon_api": -37.450,
        "estrutura": "Falésias e recifes",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Ponta Grossa - Icapuí",
        "lat_mapa": -4.681,
        "lon_mapa": -37.355,
        "lat_api": -4.685,
        "lon_api": -37.357,
        "estrutura": "Falésias e pedras",
        "desembocadura": False,
        "fator_base": 9,
    },
    {
        "nome": "Canoa Quebrada - Aracati",
        "lat_mapa": -4.518,
        "lon_mapa": -37.704,
        "lat_api": -4.525,
        "lon_api": -37.704,
        "estrutura": "Falésias e recifes",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Majorlândia - Aracati",
        "lat_mapa": -4.525,
        "lon_mapa": -37.642,
        "lat_api": -4.532,
        "lon_api": -37.642,
        "estrutura": "Pedras e recifes",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Morro Branco - Beberibe",
        "lat_mapa": -4.143,
        "lon_mapa": -38.091,
        "lat_api": -4.150,
        "lon_api": -38.091,
        "estrutura": "Falésias e recifes",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Praia das Fontes - Beberibe",
        "lat_mapa": -4.168,
        "lon_mapa": -38.087,
        "lat_api": -4.175,
        "lon_api": -38.087,
        "estrutura": "Falésias e pedras",
        "desembocadura": False,
        "fator_base": 7,
    },
    {
        "nome": "Iguape - Aquiraz",
        "lat_mapa": -3.930,
        "lon_mapa": -38.225,
        "lat_api": -3.937,
        "lon_api": -38.225,
        "estrutura": "Recifes e pedras",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Prainha - Aquiraz",
        "lat_mapa": -3.895,
        "lon_mapa": -38.368,
        "lat_api": -3.902,
        "lon_api": -38.368,
        "estrutura": "Faixa de areia e recifes",
        "desembocadura": False,
        "fator_base": 7,
    },
    {
        "nome": "Porto das Dunas - Aquiraz",
        "lat_mapa": -3.850,
        "lon_mapa": -38.390,
        "lat_api": -3.857,
        "lon_api": -38.390,
        "estrutura": "Praia arenosa",
        "desembocadura": False,
        "fator_base": 6,
    },
    {
        "nome": "Praia do Futuro - Fortaleza",
        "lat_mapa": -3.715,
        "lon_mapa": -38.448,
        "lat_api": -3.722,
        "lon_api": -38.448,
        "estrutura": "Praia arenosa e recifes",
        "desembocadura": False,
        "fator_base": 7,
    },
    {
        "nome": "Sabiaguaba - Fortaleza",
        "lat_mapa": -3.770,
        "lon_mapa": -38.438,
        "lat_api": -3.777,
        "lon_api": -38.438,
        "estrutura": "Dunas e desembocadura",
        "desembocadura": True,
        "fator_base": 8,
    },
    {
        "nome": "Cumbuco - Caucaia",
        "lat_mapa": -3.615,
        "lon_mapa": -38.725,
        "lat_api": -3.622,
        "lon_api": -38.725,
        "estrutura": "Praia arenosa",
        "desembocadura": False,
        "fator_base": 7,
    },
    {
        "nome": "Pecém - São Gonçalo do Amarante",
        "lat_mapa": -3.535,
        "lon_mapa": -38.825,
        "lat_api": -3.542,
        "lon_api": -38.825,
        "estrutura": "Pedras e estruturas costeiras",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Paracuru",
        "lat_mapa": -3.395,
        "lon_mapa": -39.010,
        "lat_api": -3.402,
        "lon_api": -39.010,
        "estrutura": "Recifes e pedras",
        "desembocadura": False,
        "fator_base": 9,
    },
    {
        "nome": "Lagoinha - Paraipaba",
        "lat_mapa": -3.365,
        "lon_mapa": -39.140,
        "lat_api": -3.372,
        "lon_api": -39.140,
        "estrutura": "Falésias e recifes",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Flecheiras - Trairi",
        "lat_mapa": -3.225,
        "lon_mapa": -39.270,
        "lat_api": -3.232,
        "lon_api": -39.270,
        "estrutura": "Recifes e pedras",
        "desembocadura": False,
        "fator_base": 9,
    },
    {
        "nome": "Mundaú - Trairi",
        "lat_mapa": -3.175,
        "lon_mapa": -39.355,
        "lat_api": -3.182,
        "lon_api": -39.355,
        "estrutura": "Estuário e recifes",
        "desembocadura": True,
        "fator_base": 8,
    },
    {
        "nome": "Icaraizinho - Amontada",
        "lat_mapa": -3.015,
        "lon_mapa": -39.655,
        "lat_api": -3.022,
        "lon_api": -39.655,
        "estrutura": "Recifes e pedras",
        "desembocadura": False,
        "fator_base": 9,
    },
    {
        "nome": "Jericoacoara - Jijoca",
        "lat_mapa": -2.785,
        "lon_mapa": -40.510,
        "lat_api": -2.792,
        "lon_api": -40.510,
        "estrutura": "Recifes e costões",
        "desembocadura": False,
        "fator_base": 8,
    },
    {
        "nome": "Praia de Camocim",
        "lat_mapa": -2.895,
        "lon_mapa": -40.840,
        "lat_api": -2.902,
        "lon_api": -40.840,
        "estrutura": "Praia e estuário",
        "desembocadura": True,
        "fator_base": 8,
    },
]


# =========================================================
# 4. CONSULTA DE PREVISÃO DO TEMPO E DO MAR
# =========================================================

@st.cache_data(ttl=1800, show_spinner=False)
def buscar_dados_por_data(lat, lon, data_desejada):
    """
    Consulta vento na API de previsão do tempo e ondas
    na API marinha do Open-Meteo.

    Se a API não retornar dados, os valores ficam ausentes.
    Não são criados valores meteorológicos fictícios.
    """

    resultado = {
        "vento": None,
        "ondas": None,
        "periodo": None,
        "corrente": None,
        "dados_reais": False,
        "erro": None,
    }

    data_texto = data_desejada.isoformat()

    try:
        # VENTO
        url_tempo = "https://api.open-meteo.com/v1/forecast"

        parametros_tempo = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wind_speed_10m",
            "start_date": data_texto,
            "end_date": data_texto,
            "timezone": "America/Fortaleza",
        }

        resposta_tempo = requests.get(
            url_tempo,
            params=parametros_tempo,
            timeout=15,
        )
        resposta_tempo.raise_for_status()
        dados_tempo = resposta_tempo.json()

        vento_valores = (
            dados_tempo.get("hourly", {}).get("wind_speed_10m", [])
        )

        vento_validos = [
            valor for valor in vento_valores
            if valor is not None
        ]

        if vento_validos:
            resultado["vento"] = sum(vento_validos) / len(vento_validos)

        # ONDAS E CORRENTE MARINHA
        url_mar = "https://marine-api.open-meteo.com/v1/marine"

        parametros_mar = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wave_height,wave_period,ocean_current_velocity",
            "start_date": data_texto,
            "end_date": data_texto,
            "timezone": "America/Fortaleza",
        }

        resposta_mar = requests.get(
            url_mar,
            params=parametros_mar,
            timeout=15,
        )
        resposta_mar.raise_for_status()
        dados_mar = resposta_mar.json()

        horario_mar = dados_mar.get("hourly", {})

        def media_valida(valores):
            validos = [
                valor for valor in valores
                if valor is not None
            ]

            if not validos:
                return None

            return sum(validos) / len(validos)

        resultado["ondas"] = media_valida(
            horario_mar.get("wave_height", [])
        )

        resultado["periodo"] = media_valida(
            horario_mar.get("wave_period", [])
        )

        resultado["corrente"] = media_valida(
            horario_mar.get("ocean_current_velocity", [])
        )

        # Só considera que existem dados se pelo menos uma
        # variável meteorológica ou marinha foi encontrada.
        resultado["dados_reais"] = any(
            resultado[chave] is not None
            for chave in ("vento", "ondas", "periodo", "corrente")
        )

        if not resultado["dados_reais"]:
            resultado["erro"] = (
                "A API não retornou dados para essa data e posição."
            )

    except requests.RequestException as erro:
        resultado["erro"] = f"Falha de conexão com a API: {erro}"

    except (ValueError, TypeError, KeyError) as erro:
        resultado["erro"] = f"Não foi possível interpretar os dados: {erro}"

    return resultado


# =========================================================
# 5. CÁLCULO DO ÍNDICE INDICATIVO
# =========================================================

def calcular_pontuacao(local, dados):
    """
    Gera um índice indicativo para comparar locais.

    Não é uma garantia de captura nem substitui a avaliação
    das condições de segurança no mar.
    """

    if not dados["dados_reais"]:
        return None

    pontos = local["fator_base"]

    vento = dados["vento"]
    ondas = dados["ondas"]

    if vento is not None:
        if vento <= 10:
            pontos += 3
        elif vento <= 18:
            pontos += 1
        elif vento > 28:
            pontos -= 4
        elif vento > 20:
            pontos -= 2

    if ondas is not None:
        if ondas <= 0.8:
            pontos += 3
        elif ondas <= 1.4:
            pontos += 1
        elif ondas > 2.5:
            pontos -= 4
        elif ondas > 1.8:
            pontos -= 2

    if local["desembocadura"]:
        pontos += 1

    if "pedras" in local["estrutura"].lower():
        pontos += 1

    return max(0, min(100, pontos * 3))


# =========================================================
# 6. CABEÇALHO
# =========================================================

st.title("🎣 Radar de Pesca Ceará")
st.caption(
    "Mapa costeiro com condições meteorológicas e marinhas "
    "para apoiar a escolha de locais de pesca."
)

st.warning(
    "As posições dos marcadores são aproximadas. "
    "Confira cada ponto no mapa antes de utilizá-lo. "
    "O índice é apenas indicativo e não representa uma "
    "previsão garantida de captura ou de segurança."
)


# =========================================================
# 7. FILTROS
# =========================================================

col_data, col_local = st.columns([1, 2])

with col_data:
    data_escolhida = st.date_input(
        "Data da consulta",
        value=date.today(),
        help="Selecione a data para consultar os dados disponíveis.",
    )

with col_local:
    nomes_locais = ["Todos os locais"] + [
        local["nome"] for local in LOCAIS_PESCA
    ]

    local_selecionado = st.selectbox(
        "Filtrar local",
        nomes_locais,
    )


if local_selecionado == "Todos os locais":
    locais_exibidos = LOCAIS_PESCA
else:
    locais_exibidos = [
        local for local in LOCAIS_PESCA
        if local["nome"] == local_selecionado
    ]


# =========================================================
# 8. CONSULTA DOS DADOS
# =========================================================

resultados = []

with st.spinner("Consultando as condições do tempo e do mar..."):
    for local in locais_exibidos:
        dados = buscar_dados_por_data(
            local["lat_api"],
            local["lon_api"],
            data_escolhida,
        )

        pontuacao = calcular_pontuacao(local, dados)

        resultados.append({
            "Local": local["nome"],
            "Índice indicativo": (
                round(pontuacao, 1)
                if pontuacao is not None
                else None
            ),
            "Vento (km/h)": (
                round(dados["vento"], 1)
                if dados["vento"] is not None
                else None
            ),
            "Ondas (m)": (
                round(dados["ondas"], 2)
                if dados["ondas"] is not None
                else None
            ),
            "Período das ondas (s)": (
                round(dados["periodo"], 1)
                if dados["periodo"] is not None
                else None
            ),
            "Corrente (m/s)": (
                round(dados["corrente"], 2)
                if dados["corrente"] is not None
                else None
            ),
            "Estrutura costeira": local["estrutura"],
            "Desembocadura próxima": (
                "Sim" if local["desembocadura"] else "Não"
            ),
            "Dados disponíveis": (
                "Sim" if dados["dados_reais"] else "Não"
            ),
            "Erro da consulta": dados["erro"],
            "lat_mapa": local["lat_mapa"],
            "lon_mapa": local["lon_mapa"],
        })


tabela = pd.DataFrame(resultados)

if not tabela.empty:
    tabela = tabela.sort_values(
        by="Índice indicativo",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)


# =========================================================
# 9. INDICADORES
# =========================================================

total_locais = len(tabela)

locais_com_dados = (
    int((tabela["Dados disponíveis"] == "Sim").sum())
    if total_locais
    else 0
)

tabela_com_pontuacao = tabela.dropna(
    subset=["Índice indicativo"]
)

if not tabela_com_pontuacao.empty:
    melhor_local = tabela_com_pontuacao.iloc[0]
    nome_melhor = melhor_local["Local"]
    pontuacao_melhor = melhor_local["Índice indicativo"]
else:
    nome_melhor = "Sem dados disponíveis"
    pontuacao_melhor = "—"


metrica1, metrica2, metrica3 = st.columns(3)

with metrica1:
    st.metric("Locais no mapa", total_locais)

with metrica2:
    st.metric("Locais com dados", locais_com_dados)

with metrica3:
    st.metric("Maior índice indicativo", pontuacao_melhor)

st.caption(f"Local com maior índice: {nome_melhor}")


# =========================================================
# 10. MAPA
# =========================================================

if locais_exibidos:
    centro_lat = sum(
        local["lat_mapa"] for local in locais_exibidos
    ) / len(locais_exibidos)

    centro_lon = sum(
        local["lon_mapa"] for local in locais_exibidos
    ) / len(locais_exibidos)

    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=8 if len(locais_exibidos) > 1 else 12,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for _, linha in tabela.iterrows():
        pontuacao = linha["Índice indicativo"]

        if pd.isna(pontuacao):
            cor = "gray"
            texto_indice = "Sem dados suficientes"
        elif pontuacao >= 30:
            cor = "green"
            texto_indice = f"Índice: {pontuacao:.1f}"
        elif pontuacao >= 20:
            cor = "orange"
            texto_indice = f"Índice: {pontuacao:.1f}"
        else:
            cor = "red"
            texto_indice = f"Índice: {pontuacao:.1f}"

        popup_html = f"""
        <div style="width:230px">
            <b>{linha['Local']}</b><br>
            {texto_indice}<br>
            Vento: {linha['Vento (km/h)']} km/h<br>
            Ondas: {linha['Ondas (m)']} m<br>
            Período: {linha['Período das ondas (s)']} s<br>
            Corrente: {linha['Corrente (m/s)']} m/s<br>
            Dados disponíveis: {linha['Dados disponíveis']}
        </div>
        """

        folium.Marker(
            location=[
                linha["lat_mapa"],
                linha["lon_mapa"],
            ],
            tooltip=linha["Local"],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(
                color=cor,
                icon="info-sign",
            ),
        ).add_to(mapa)

    st.subheader("📍 Mapa dos pontos costeiros")
    st_folium(
        mapa,
        use_container_width=True,
        height=600,
        returned_objects=[],
    )


# =========================================================
# 11. TABELA DE CONDIÇÕES
# =========================================================

st.subheader("📊 Condições por local")

colunas_visiveis = [
    "Local",
    "Índice indicativo",
    "Vento (km/h)",
    "Ondas (m)",
    "Período das ondas (s)",
    "Corrente (m/s)",
    "Estrutura costeira",
    "Desembocadura próxima",
    "Dados disponíveis",
]

st.dataframe(
    tabela[colunas_visiveis],
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# 12. DIAGNÓSTICO DOS DADOS
# =========================================================

with st.expander("🔎 Ver detalhes e problemas nas consultas"):
    st.write(
        "Esta seção mostra os dados recebidos das APIs. "
        "Campos vazios indicam que a variável não foi retornada."
    )

    for _, linha in tabela.iterrows():
        with st.container():
            st.markdown(f"**{linha['Local']}**")

            if linha["Erro da consulta"]:
                st.warning(linha["Erro da consulta"])
            elif linha["Dados disponíveis"] == "Não":
                st.info("Não há dados suficientes para calcular o índice.")
            else:
                st.success("Consulta retornou dados.")

            st.caption(
                f"Marcador: "
                f"{linha['lat_mapa']:.5f}, "
                f"{linha['lon_mapa']:.5f}"
            )


# =========================================================
# 13. AVISO FINAL
# =========================================================

st.divider()

st.caption(
    "Fonte meteorológica: Open-Meteo. "
    "A disponibilidade depende da data, da região e das APIs. "
    "Confirme as condições locais, a previsão oficial e a "
    "segurança da navegação antes de sair para pescar."
)