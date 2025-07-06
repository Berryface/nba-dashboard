# estadisticas_nba.py

from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd


try:
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2023-24',
        season_type_all_star='Regular Season'
    )

  
    df = player_stats.get_data_frames()[0]

    
    df.to_csv("nba_players_stats_2023_24.csv", index=False, encoding='utf-8-sig')

    print("✅ Archivo 'nba_players_stats_2023_24.csv' generado con éxito.")
except Exception as e:
    print("❌ Ocurrió un error al obtener los datos:", e)

input("Presiona Enter para salir...")
