from datetime import datetime
import time
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# Configuração inicial da página (Layout Largo estilo SaaS)
st.set_page_config(
    page_title="Radar de Pesca Ceará - SaaS Pro", page_icon="🎣", layout="wide"
)

# ==========================================
# 1. ESTILIZAÇÃO CSS CUSTOMIZADA (SaaS Theme)
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)),
                          url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #FFFFFF !important;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .saas-card {
        background-color: rgba(15, 23, 42, 0.75);
        border-left: 4px solid #00E5FF;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎣 Radar de Pesca - Ceará SaaS Intelligence")
st.markdown(
    "Plataforma avançada de decisão oceanográfica para pesca de praia"
    " (*Surfcasting*)."
)

# ==========================================
# 2. BASE DE DADOS GEOGRÁFICA
# lat/lon: coordenadas usadas para consultas meteorológicas/marinhas.
# map_lat/map_lon serão obtidas por geocodificação para posicionar o ponto
# em terra, usando o nome do local. A geocodificação precisa ser conferida.
# ==========================================
MUNICIPIOS_CEARA = [
    {"nome": "Icapuí", "lat": -4.2650, "lon": -37.8420, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 9.0},
    {"nome": "Aracati (Canoa Quebrada)", "lat": -4.4330, "lon": -37.7690, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.5},
    {"nome": "Fortim", "lat": -4.4120, "lon": -37.7950, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.5},
    {"nome": "Beberibe (Morro Branco)", "lat": -4.1350, "lon": -38.1180, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 8.5},
    {"nome": "Cascavel (Iguape)", "lat": -3.9780, "lon": -38.2750, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "Aquiraz (Prainha)", "lat": -3.8750, "lon": -38.3450, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "Fortaleza (Praia do Futuro)", "lat": -3.7310, "lon": -38.4410, "tem_estrutura_pedra": False, "proximo_foz_rio": False, "fator_base": 7.0},
    {"nome": "Caucaia (Cumbuco)", "lat": -3.6150, "lon": -38.7280, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "São Gonçalo do Amarante (Pecém)", "lat": -3.5410, "lon": -38.8050, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 7.5},
    {"nome": "Paracuru", "lat": -3.4090, "lon": -39.2300, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 8.5},
    {"nome": "Paraipaba (Lagoinha)", "lat": -3.1850, "lon": -39.0550, "tem_estrutura_pedra": False, "proximo_foz_rio": False, "fator_base": 7.5},
    {"nome": "Trairi (Flecheiras)", "lat": -3.2210, "lon": -39.2750, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 8.0},
    {"nome": "Amontada (Icaraizinho)", "lat": -2.7120, "lon": -39.7900, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 8.0},
    {"nome": "Itarema (Almofala)", "lat": -2.9150, "lon": -39.9100, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "Acaraú", "lat": -2.8750, "lon": -40.1150, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "Jijoca de Jericoacoara", "lat": -2.7950, "lon": -40.5050, "tem_estrutura_pedra": True, "proximo_foz_rio": False, "fator_base": 8.5},
    {"nome": "Camocim", "lat": -2.9180, "lon": -40.8350, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.5},
    {"nome": "Barroquinha", "lat": -2.9980, "lon": -41.1100, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 8.0},
    {"nome": "Chaval", "lat": -3.0250, "lon": -40.9700, "tem_estrutura_pedra": False, "proximo_foz_rio": True, "fator_base": 7.5},
    {"nome": "Cruz (Preá)", "lat": -2.8180, "lon": -40.4150, "tem_estrutura_pedra": False, "proximo_foz_rio": False, "fator_base": 7.5},
]

# ==========================================
# 2.1. GEOCODIFICAÇÃO DAS POSIÇÕES DO MAPA
# Busca as localidades no Nominatim/OSM e mantém as coordenadas originais
# como fallback se o serviço não responder. Os resultados devem ser validados
# antes de serem tratados como pontos exatos de praia/pesca.
# ==========================================
@st.cache_data(ttl=30 * 24 * 60 * 60, show_spinner=False)
def geocodificar_local(nome):
    consulta = f"{nome}, Ceará, Brasil"
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "RadarPescaCearaSaaS/1.0 (aplicativo de pesquisa costeira)"}
    try:
        resposta = requests.get(
            url,
            params={"q": consulta, "format": "jsonv2", "limit": 1, "countrycodes": "br"},
            headers=headers,
            timeout=8,
        )
        resposta.raise_for_status()
        dados = resposta.json()
        if dados:
            return float(dados[0]["lat"]), float(dados[0]["lon"]), str(dados[0].get("display_name", ""))
    except (requests.RequestException, ValueError, KeyError, TypeError):
        pass
    return None

@st.cache_data(ttl=30 * 24 * 60 * 60, show_spinner=False)
def obter_coordenadas_mapa():
    """Resolve localidades uma vez e devolve coordenadas para os marcadores."""
    pontos = {}
    for i, mun in enumerate(MUNICIPIOS_CEARA):
        # O Nominatim limita a frequência de consultas; aguarda entre pedidos.
        if i > 0:
            time.sleep(1.1)
        resultado = geocodificar_local(mun["nome"])
        if resultado:
            lat_mapa, lon_mapa, nome_encontrado = resultado
            pontos[mun["nome"]] = {
                "map_lat": lat_mapa,
                "map_lon": lon_mapa,
                "geocodificado": True,
                "local_encontrado": nome_encontrado,
            }
        else:
            pontos[mun["nome"]] = {
                "map_lat": mun["lat"],
                "map_lon": mun["lon"],
                "geocodificado": False,
                "local_encontrado": "Coordenadas originais (fallback)",
            }
    return pontos

with st.spinner("Localizando os municípios e localidades para posicionar os marcadores..."):
    COORDENADAS_MAPA = obter_coordenadas_mapa()

# ==========================================
# 3. MOTOR DE DADOS E INTELIGÊNCIA
# ==========================================
@st.cache_data(ttl=3600)
def buscar_dados_por_data(lat, lon, data_desejada):
    headers = {"User-Agent": "RadarPescaCearaSaaS/1.0"}
    try:
        url_w = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=wind_speed_10m"
        )
        resp_w = requests.get(url_w, headers=headers, timeout=8)
        resp_w.raise_for_status()
        dados_w = resp_w.json()

        url_m = (
            "https://marine-api.open-meteo.com/v1/marine?"
            f"latitude={lat}&longitude={lon}"
            "&hourly=wave_height,wave_period,ocean_current_velocity"
        )
        resp_m = requests.get(url_m, headers=headers, timeout=8)
        resp_m.raise_for_status()
        dados_m = resp_m.json()

        tempos_w = dados_w.get("hourly", {}).get("time", [])
        ventos = dados_w.get("hourly", {}).get("wind_speed_10m", [])
        tempos_m = dados_m.get("hourly", {}).get("time", [])
        ondas_alt = dados_m.get("hourly", {}).get("wave_height", [])
        ondas_per = dados_m.get("hourly", {}).get("wave_period", [])
        correntes = dados_m.get("hourly", {}).get("ocean_current_velocity", [])

        v_dia = [v for t, v in zip(tempos_w, ventos) if t.startswith(data_desejada) and v is not None]
        a_dia = [a for t, a in zip(tempos_m, ondas_alt) if t.startswith(data_desejada) and a is not None]
        p_dia = [p for t, p in zip(tempos_m, ondas_per) if t.startswith(data_desejada) and p is not None]
        c_dia = [c for t, c in zip(tempos_m, correntes) if t.startswith(data_desejada) and c is not None]

        if v_dia and a_dia:
            return {
                "vento_vel": sum(v_dia) / len(v_dia),
                "onda_alt": sum(a_dia) / len(a_dia),
                "onda_per": sum(p_dia) / len(p_dia) if p_dia else 6.0,
                "corrente": sum(c_dia) / len(c_dia) if c_dia else 0.3,
                "dados_reais": True,
            }
    except (requests.RequestException, ValueError, TypeError, KeyError):
        pass
    return {
        "vento_vel": 15.0,
        "onda_alt": 1.0,
        "onda_per": 6.0,
        "corrente": 0.3,
        "dados_reais": False,
    }


def calcular_score_pesca(mun, data_desejada):
    clima = buscar_dados_por_data(mun["lat"], mun["lon"], data_desejada)
    score = mun["fator_base"]

    alt = clima["onda_alt"]
    if 0.6 <= alt <= 1.6:
        score += 1.0
    elif alt > 2.2:
        score -= 2.5
    elif alt < 0.4:
        score -= 1.0

    v_vel = clima["vento_vel"]
    if 10 <= v_vel <= 25:
        score += 0.5
    elif v_vel > 35:
        score -= 2.0

    if mun["proximo_foz_rio"]:
        score += 1.5
    if mun["tem_estrutura_pedra"]:
        score += 1.0

    score_final = round(max(0.0, min(10.0, score)), 1)
    coordenadas_mapa = COORDENADAS_MAPA.get(mun["nome"], {})

    return {
        "Município": mun["nome"],
        "latitude": mun["lat"],
        "longitude": mun["lon"],
        "map_lat": coordenadas_mapa.get("map_lat", mun["lat"]),
        "map_lon": coordenadas_mapa.get("map_lon", mun["lon"]),
        "geocodificado": coordenadas_mapa.get("geocodificado", False),
        "local_encontrado": coordenadas_mapa.get("local_encontrado", "Coordenadas originais"),
        "dados_reais": clima["dados_reais"],
        "Score": score_final,
        "Onda Média (m)": round(alt, 2),
        "Período (s)": round(clima["onda_per"], 1),
        "Vento Médio (km/h)": round(clima["vento_vel"], 1),
        "Correnteza (m/s)": round(clima["corrente"], 2),
        "Estrutura de Pedra": "Sim 🪨 (Abrigo natural)" if mun["tem_estrutura_pedra"] else "Praia limpa de areia 🏖️",
        "Foz de Rio": "Próxima (Rica em nutrientes) 🌊" if mun["proximo_foz_rio"] else "Distante ❌",
    }

# ==========================================
# 4. PAINEL DE CONTROLE LATERAL
# ==========================================
st.sidebar.header("Painel de Controle SaaS")
data_selecionada = st.sidebar.date_input("Data da Pesca", datetime.now()).strftime("%Y-%m-%d")
st.sidebar.info("ℹ️ O mapa e as previsões atualizam automaticamente ao alterar a data.")
st.sidebar.caption("As posições do mapa são obtidas por geocodificação de localidades e precisam ser conferidas para uso como pesqueiros exatos.")

resultados = [calcular_score_pesca(mun, data_selecionada) for mun in MUNICIPIOS_CEARA]
df = pd.DataFrame(resultados)
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# Aviso visível se algumas localidades não puderam ser geocodificadas.
nao_localizados = df.loc[~df["geocodificado"], "Município"].tolist()
if nao_localizados:
    st.warning(
        "Não foi possível geocodificar estas localidades; os marcadores usam as coordenadas antigas: "
        + ", ".join(nao_localizados)
    )

# ==========================================
# 5. RENDERIZAÇÃO DA PÁGINA
# ==========================================
st.subheader(f"🏆 Top 3 Melhores Destinos para {data_selecionada}")
top_3 = df.head(3)
cols = st.columns(3)
for idx, (_, row) in enumerate(top_3.iterrows()):
    with cols[idx]:
        st.metric(
            label=f"#{idx + 1} - {row['Município']}",
            value=f"Score: {row['Score']}",
            delta=f"Onda: {row['Onda Média (m)']}m",
        )

st.markdown("---")
st.subheader("🗺️ Mapa Interativo de Inteligência Costeira")
st.markdown(
    "Clique em qualquer marcador para inspecionar as condições estimadas de "
    "ondas, ventos, correnteza e características do local. Confira a posição "
    "geocodificada antes de usar o marcador como ponto exato de pesca."
)

mapa_saas = folium.Map(
    location=[-3.85, -39.50],
    zoom_start=7,
    tiles="OpenStreetMap",
    control_scale=True,
)

primeiro_lugar = df.iloc[0]["Município"] if len(df) > 0 else ""
segundo_lugar = df.iloc[1]["Município"] if len(df) > 1 else ""
terceiro_lugar = df.iloc[2]["Município"] if len(df) > 2 else ""

for _, row in df.iterrows():
    mun_nome = row["Município"]
    score = row["Score"]

    if mun_nome == primeiro_lugar:
        cor_marcador = "#FFD700"
        posicao_txt = "🥇 1º Lugar"
    elif mun_nome == segundo_lugar:
        cor_marcador = "#C0C0C0"
        posicao_txt = "🥈 2º Lugar"
    elif mun_nome == terceiro_lugar:
        cor_marcador = "#CD7F32"
        posicao_txt = "🥉 3º Lugar"
    elif score >= 10.0:
        cor_marcador = "#28a745"
        posicao_txt = f"⭐ Nota Máxima ({score})"
    else:
        cor_marcador = "#dc3545"
        posicao_txt = f"⚠️ Score: {score}"

    estado_localizacao = "Localização obtida no OpenStreetMap" if row["geocodificado"] else "Localização antiga (não geocodificada)"
    estado_dados = "API consultada" if row["dados_reais"] else "valores de contingência (API indisponível)"
    popup_saas_html = f"""
    <div style="font-family: 'Segoe UI', sans-serif; width: 250px; padding: 5px; color: #0F172A;">
        <h4 style="color: #0F172A; margin-bottom: 5px; border-bottom: 2px solid #00E5FF; padding-bottom: 3px;">{mun_nome}</h4>
        <p style="margin: 3px 0; font-size: 13px;"><b>🏅 Posição:</b> {posicao_txt}</p>
        <p style="margin: 3px 0; font-size: 11px;"><b>📍 Geolocalização:</b> {estado_localizacao}</p>
        <p style="margin: 3px 0; font-size: 11px;"><b>🌐 Dados:</b> {estado_dados}</p>
        <hr style="margin: 4px 0; border: 0; border-top: 1px solid #CBD5E1;">
        <p style="margin: 3px 0; font-size: 13px;"><b>🌊 Altura de Onda:</b> {row['Onda Média (m)']} m</p>
        <p style="margin: 3px 0; font-size: 13px;"><b>⏱️ Período de Onda:</b> {row['Período (s)']} s</p>
        <p style="margin: 3px 0; font-size: 13px;"><b>💨 Vento Médio:</b> {row['Vento Médio (km/h)']} km/h</p>
        <p style="margin: 3px 0; font-size: 13px;"><b>🌀 Correnteza Marinha:</b> {row['Correnteza (m/s)']} m/s</p>
        <hr style="margin: 4px 0; border: 0; border-top: 1px solid #CBD5E1;">
        <p style="margin: 3px 0; font-size: 12px;"><b>🪨 Relevo:</b> {row['Estrutura de Pedra']}</p>
        <p style="margin: 3px 0; font-size: 12px;"><b>🌊 Foz/Estuário:</b> {row['Foz de Rio']}</p>
    </div>
    """

    # CORREÇÃO PRINCIPAL: usa as coordenadas de mapa, não as coordenadas
    # de consulta da previsão. A ordem do Folium é [latitude, longitude].
    folium.CircleMarker(
        location=[float(row["map_lat"]), float(row["map_lon"])],
        radius=9,
        popup=folium.Popup(popup_saas_html, max_width=280),
        tooltip=f"📍 {mun_nome} | {posicao_txt}",
        color=cor_marcador,
        fill=True,
        fill_color=cor_marcador,
        fill_opacity=0.95,
        weight=2,
    ).add_to(mapa_saas)

st_folium(mapa_saas, width=1200, height=520, returned_objects=[])

st.markdown(
    """
    <div class="saas-card">
        <h4>💡 Relatório Técnico do Litoral Cearense</h4>
        <p>O sistema combina características cadastradas dos locais com dados meteorológicos e marinhos quando disponíveis. A posição do marcador é obtida por geocodificação de localidades do OpenStreetMap; isso não garante que seja o ponto exato da praia ou do pesqueiro. Confira os locais antes de tomar decisões de pesca.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("📋 Tabela Analítica Consolidada")
colunas_ocultas = ["latitude", "longitude", "map_lat", "map_lon", "geocodificado", "local_encontrado", "dados_reais"]
df_exibicao = df.drop(columns=colunas_ocultas, errors="ignore").copy()
df_exibicao.insert(0, "Posição", range(1, len(df_exibicao) + 1))
st.dataframe(df_exibicao, width="stretch", hide_index=True)

with st.expander("🔎 Conferir coordenadas usadas no mapa"):
    st.caption("Confira se cada ponto está na praia/localidade pretendida. A geocodificação de um nome de município pode retornar o centro da localidade, não a faixa de areia.")
    conferencias = df[["Município", "map_lat", "map_lon", "geocodificado", "local_encontrado"]].copy()
    conferencias = conferencias.rename(columns={
        "map_lat": "Latitude do mapa",
        "map_lon": "Longitude do mapa",
        "geocodificado": "Encontrado no OSM",
        "local_encontrado": "Resultado da busca",
    })
    st.dataframe(conferencias, width="stretch", hide_index=True)
