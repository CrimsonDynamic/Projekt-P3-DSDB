# in data_loader.py

import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def load_all_data():
    """
    Lädt die vorbereiteten Daten aus den Parquet-Dateien
    und führt die notwendigen Joins und Transformationen mit Pandas durch,
    um die finalen DataFrames für das Dashboard zu erstellen.
    """
    SCRIPT_DIR = Path(__file__).parent
    DATA_FOLDER = SCRIPT_DIR / "data"

    try:
        df_fahrer = pd.read_parquet(DATA_FOLDER / 'fahrer.parquet')
        df_konstrukteure = pd.read_parquet(DATA_FOLDER / 'konstrukteure.parquet')
        df_rennen = pd.read_parquet(DATA_FOLDER / 'rennen.parquet')
        df_quali = pd.read_parquet(DATA_FOLDER / 'qualifikation.parquet')
        df_ergebnisse = pd.read_parquet(DATA_FOLDER / 'ergebnisse.parquet')
    except FileNotFoundError:
        st.error("Fehler: Die Parquet-Dateien im 'data'-Ordner wurden nicht gefunden. Bitte führe zuerst das Jupyter Notebook 'projekt.ipynb' aus.")
        st.stop()

    # --- Datenaufbereitung mit Pandas ---
    
    # -- A. df_wins (unverändert) ---
    df_wins = df_ergebnisse[df_ergebnisse['Position'] == 1].copy()
    df_wins = pd.merge(df_wins, df_rennen[['Rennen_ID', 'Datum', 'Saison']], on='Rennen_ID')
    df_wins = pd.merge(df_wins, df_fahrer[['Fahrer_ID', 'Name', 'Nationalität', 'Geburtsdatum']], on='Fahrer_ID')
    df_wins = pd.merge(df_wins, df_konstrukteure[['Konstrukteur_ID', 'Name']], on='Konstrukteur_ID', suffixes=('_Fahrer', '_Team'))
    df_wins.rename(columns={'Name_Fahrer': 'Fahrer', 'Name_Team': 'Team'}, inplace=True)
    df_wins['Alter'] = ((df_wins['Datum'] - df_wins['Geburtsdatum']).dt.days / 365.25).astype(int)

    # -- B. df_dnf ---
    # FINALE KORREKTUR: Die Liste ist jetzt exakt auf deine Daten zugeschnitten.
    technical_issues = [
        'Retired', 
        'Undertray'
    ]
    df_dnf = df_ergebnisse[df_ergebnisse['Status'].isin(technical_issues)].copy()
    df_dnf = pd.merge(df_dnf, df_rennen[['Rennen_ID', 'Saison']], on='Rennen_ID')
    df_dnf = pd.merge(df_dnf, df_konstrukteure[['Konstrukteur_ID', 'Name']], on='Konstrukteur_ID')
    df_dnf = pd.merge(df_dnf, df_fahrer[['Fahrer_ID', 'Name']], on='Fahrer_ID', suffixes=('_Team', '_Fahrer'))
    df_dnf.rename(columns={'Name_Team': 'Team', 'Name_Fahrer': 'Fahrer', 'Status': 'Ausfallgrund'}, inplace=True)

    # -- C. df_quali (unverändert) ---
    team_mapping = df_ergebnisse[['Fahrer_ID', 'Rennen_ID', 'Konstrukteur_ID']].drop_duplicates()
    df_quali = pd.merge(df_quali, df_rennen[['Saison', 'Runde', 'Rennen_ID']], on=['Saison', 'Runde'])
    df_quali = pd.merge(df_quali, team_mapping, on=['Fahrer_ID', 'Rennen_ID'], how='left')
    df_quali = pd.merge(df_quali, df_konstrukteure[['Konstrukteur_ID', 'Name']], on='Konstrukteur_ID', how='left')
    df_quali = pd.merge(df_quali, df_fahrer[['Fahrer_ID', 'Name']], on='Fahrer_ID', suffixes=('_Team', '_Fahrer'))
    df_quali.rename(columns={'Name_Team': 'Team', 'Name_Fahrer': 'Fahrer'}, inplace=True)
    df_quali.dropna(subset=['Team'], inplace=True)
    
    # -- D. all_teams (unverändert) ---
    all_teams = sorted(df_konstrukteure['Name'].unique())

    return df_quali, df_wins, df_dnf, all_teams