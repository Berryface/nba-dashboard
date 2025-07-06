from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd


player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2023-24',
    season_type_all_star='Regular Season'
)


df = player_stats.get_data_frames()[0]


df.to_csv("nba_players_stats.csv", index=False, encoding='utf-8-sig')

print("Archivo 'nba_players_stats.csv' generado con éxito.")
