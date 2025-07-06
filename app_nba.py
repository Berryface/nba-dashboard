import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import io
from nba_api.stats.endpoints import ScoreboardV2, BoxScoreTraditionalV2
from datetime import datetime


st.set_page_config(page_title="NBA Dashboard 2023-24", page_icon="🏀", layout="wide")


st.sidebar.header("⚙️ Configuración")

modo = st.sidebar.radio(
    "Modo de análisis",
    ["Estadísticas de temporada completa", "Estadísticas de un partido"]
)


st.markdown(
    """
    <h1 style="color:#e74c3c; text-align:center;">
    🏀 Dashboard NBA 2023-24
    </h1>
    """,
    unsafe_allow_html=True
)

st.image("LOGO.png", width=100)


if modo == "Estadísticas de temporada completa":

    
    df = pd.read_csv("nba_players_stats_2023_24.csv")
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()


    
    df["MIN"] = df["MIN"].replace(0, 0.1)
    df["PTS_per_MIN"] = df["PTS"] / df["MIN"]
    df["AST_per_MIN"] = df["AST"] / df["MIN"]
    df["REB_per_MIN"] = df["REB"] / df["MIN"]

    df["FG3A"] = df["FG3A"].replace(0, 0.1)
    df["FGA"] = df["FGA"].replace(0, 0.1)
    df["TOV"] = df["TOV"].replace(0, 0.1)

    df["3P_percent"] = (df["FG3M"] / df["FG3A"]) * 100
    df["AST_per_TOV"] = df["AST"] / df["TOV"]
    df["PTS_per_FGA"] = df["PTS"] / df["FGA"]

    
    st.sidebar.header("Filtros")

    equipos = df["TEAM_ABBREVIATION"].unique().tolist()
    equipos.sort()
    equipos.insert(0, "Todos")

    estadisticas = [
        "PTS", "AST", "REB", "STL", "BLK", "FG3M", "MIN", "PLUS_MINUS",
        "PTS_per_MIN", "AST_per_MIN", "REB_per_MIN",
        "3P_percent", "AST_per_TOV", "PTS_per_FGA"
    ]

    equipo_seleccionado = st.sidebar.selectbox("Equipo", equipos)
    estadistica = st.sidebar.selectbox("Estadística", estadisticas)
    top_n = st.sidebar.slider("Top N jugadores", 5, 30, 10)

   
    df_filtrado = df.copy()
    if equipo_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["TEAM_ABBREVIATION"] == equipo_seleccionado]

    df_top = df_filtrado.sort_values(by=estadistica, ascending=False).head(top_n)
    df_top[estadistica] = df_top[estadistica].round(2)

    
    st.subheader(f"Top {top_n} jugadores por {estadistica}")
    st.dataframe(df_top[["PLAYER_NAME", "TEAM_ABBREVIATION", estadistica]])

    
    fig = px.bar(
        df_top,
        x=estadistica,
        y="PLAYER_NAME",
        orientation="h",
        color=estadistica,
        color_continuous_scale="reds",
        title=f"Top {top_n} jugadores por {estadistica}",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")  

    st.sidebar.download_button(
    label="⬇️ Descargar CSV",
    data=csv_data,
    file_name="nba_players_stats_2023_24.csv",
    mime="text/csv"
)

    
    st.header("🔍 Comparación cara a cara de jugadores")

    jugadores = df["PLAYER_NAME"].unique().tolist()
    jugadores.sort()

    col1, col2 = st.columns(2)
    with col1:
        jugador1 = st.selectbox("Jugador 1", jugadores, index=0)
    with col2:
        jugador2 = st.selectbox("Jugador 2", jugadores, index=1)

    stats_compare = ["PTS", "AST", "REB", "STL", "BLK", "FG3M", "MIN", "PTS_per_MIN", "AST_per_MIN", "REB_per_MIN"]

    jugador1_data = df[df["PLAYER_NAME"] == jugador1][stats_compare].iloc[0]
    jugador2_data = df[df["PLAYER_NAME"] == jugador2][stats_compare].iloc[0]

    compare_df = pd.DataFrame({
        "Estadística": stats_compare,
        jugador1: jugador1_data.values,
        jugador2: jugador2_data.values
    }).melt(id_vars="Estadística", var_name="Jugador", value_name="Valor")

    fig_compare = px.bar(
        compare_df,
        x="Estadística",
        y="Valor",
        color="Jugador",
        barmode="group",
        title=f"Comparación estadística: {jugador1} vs {jugador2}",
        template="plotly_white"
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    
    st.subheader("🌟 Comparación en radar (estilo 2K)")
    radar_stats = ["PTS", "AST", "REB", "STL", "BLK", "FG3M"]

    player1_values = jugador1_data[radar_stats].values
    player2_values = jugador2_data[radar_stats].values

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=player1_values,
        theta=radar_stats,
        fill='toself',
        name=jugador1
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=player2_values,
        theta=radar_stats,
        fill='toself',
        name=jugador2
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title=f"Radar comparativo: {jugador1} vs {jugador2}"
    )
    st.plotly_chart(fig_radar, use_container_width=True)


elif modo == "Estadísticas de un partido":
    st.sidebar.header("📅 Selección de fecha")
    fecha = st.sidebar.date_input("Elige la fecha", value=datetime.today())
    fecha_str = fecha.strftime("%Y-%m-%d")

    try:
        scoreboard = ScoreboardV2(game_date=fecha_str, league_id="00")
        games = scoreboard.get_data_frames()[0]
    except Exception as e:
        st.error(f"No se pudo recuperar la lista de partidos: {e}")
        games = pd.DataFrame()

    if games.empty:
        st.warning("No hubo partidos en esta fecha o no se pudieron obtener datos.")
    else:
        partidos = games[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ABBREVIATION", "VISITOR_TEAM_ABBREVIATION"]]
        partidos["MATCH"] = partidos["HOME_TEAM_ABBREVIATION"] + " vs " + partidos["VISITOR_TEAM_ABBREVIATION"]

        partido_elegido = st.selectbox("Selecciona el partido", partidos["MATCH"])
        game_id = partidos[partidos["MATCH"] == partido_elegido]["GAME_ID"].values[0]

        boxscore = BoxScoreTraditionalV2(game_id=game_id)
        stats_df = boxscore.get_data_frames()[0]

        st.subheader(f"📊 Boxscore: {partido_elegido}")
        st.dataframe(stats_df)

        df_points = stats_df[stats_df["MIN"] != "0:00"]
        df_points["PTS"] = pd.to_numeric(df_points["PTS"], errors="coerce")

        fig_partido = px.bar(
            df_points,
            x="PLAYER_NAME",
            y="PTS",
            color="TEAM_ABBREVIATION",
            title=f"Puntos por jugador en {partido_elegido}"
        )
        st.plotly_chart(fig_partido, use_container_width=True)


st.markdown(
    """
    <hr>
    <p style="text-align:center; color:gray; font-size:14px;">
    © 2025 Desarrollado por <strong>Juan José Vidal Parra</strong>
    </p>
    """,
    unsafe_allow_html=True
)
