import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_all_data

#Seiten-Konfiguration
st.set_page_config(page_title = "F1 Interactive Dashboard", 
                   page_icon = "🏎️", 
                   layout = "wide")

#Daten laden
df_quali, df_wins, df_dnf, all_teams = load_all_data()



# --- Sidebar ---
st.sidebar.title("⚙️ Filteroptionen")
st.sidebar.markdown("Stelle hier die Filter für das gesamte Dashboard ein.")

st.sidebar.subheader("Saison auswählen")
all_seasons = sorted(df_quali["Saison"].unique(), 
                     reverse = True)
selected_seasons = st.sidebar.multiselect("Saison(en)", 
                                          options = all_seasons, 
                                          default = [max(all_seasons)] if all_seasons else [])
if not selected_seasons: selected_seasons = all_seasons

df_quali_s = df_quali[df_quali["Saison"].isin(selected_seasons)]
df_wins_s = df_wins[df_wins["Saison"].isin(selected_seasons)]
df_dnf_s = df_dnf[df_dnf["Saison"].isin(selected_seasons)]



st.sidebar.subheader("Teams auswählen")
teams_in_selected_seasons = sorted(df_quali_s["Team"].unique())
selected_teams = st.sidebar.multiselect("Team(s)", 
                                        options = teams_in_selected_seasons, 
                                        default = teams_in_selected_seasons)
if not selected_teams: selected_teams = teams_in_selected_seasons

df_quali_t = df_quali_s[df_quali_s["Team"].isin(selected_teams)]
df_wins_t = df_wins_s[df_wins_s["Team"].isin(selected_teams)]
df_dnf_t = df_dnf_s[df_dnf_s["Team"].isin(selected_teams)]



st.sidebar.subheader("Fahrer auswählen")
drivers_in_selected_teams = sorted(df_quali_t["Fahrer"].unique())
selected_drivers = st.sidebar.multiselect("Fahrer", 
                                          options = drivers_in_selected_teams,
                                          default = drivers_in_selected_teams)
if not selected_drivers: selected_drivers = drivers_in_selected_teams

final_df_quali = df_quali_t[df_quali_t["Fahrer"].isin(selected_drivers)]
final_df_wins = df_wins_t[df_wins_t["Fahrer"].isin(selected_drivers)]
final_df_dnf = df_dnf_t[df_dnf_t["Fahrer"].isin(selected_drivers)]





# --- Dashboard ---
st.title("🏎️ Interaktives Formel 1 Dashboard")
st.markdown(f"Analyse für die Saison(en) **{", ".join(map(str, selected_seasons))}**.")
st.info(f"Fokus auf **{len(selected_teams)} Team(s)** und **{len(selected_drivers)} Fahrer**.")
st.divider()



# --- Kennzahlen ---
st.header("📈 Kennzahlen")
if final_df_quali.empty and final_df_wins.empty and final_df_dnf.empty:
    st.warning("Keine Daten für die aktuelle Filterauswahl verfügbar.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamtsiege", final_df_wins.shape[0])
    col2.metric("Motorausfälle", final_df_dnf.shape[0])

    # KORREKTUR 1: Greife direkt auf die Spalte "Q3" zu, anstatt nach "Run" zu filtern.
    q3_data = final_df_quali # Wir brauchen keine extra Filterzeile
    avg_q3_time = q3_data["Q3"].mean() if not q3_data.empty else 0
    col3.metric("Avg. Q3 Zeit", f"{avg_q3_time/1000:.3f}s" if pd.notna(avg_q3_time) and avg_q3_time > 0 else "N/A")

st.divider()



# --- Analysebereiche ---
st.header("📊 Detailanalysen")

# --- Qualifying-Analyse ---
with st.expander("🏆 Qualifying Analyse", expanded = True):
    if final_df_quali.empty:
        st.warning("Keine Qualifying-Daten für diese Auswahl.")
    else:
        tab1, tab2 = st.tabs(["Zeiten pro Fahrer & Run", "Zeit vs. Startposition"])
        with tab1:
            df_q_melt = final_df_quali.melt(
                id_vars = ["Fahrer", "Team"], 
                value_vars = ["Q1", "Q2", "Q3"], 
                var_name = "Run", 
                value_name = "Zeit"
            )
            df_q_melt.dropna(subset = ["Zeit"], inplace = True)
            
            avg_times = df_q_melt.groupby(["Fahrer", "Run"])["Zeit"].mean().reset_index()
            fig = px.bar(avg_times,
                         x = "Fahrer", 
                         y = "Zeit", 
                         color = "Run", 
                         barmode = "group", 
                         template = "plotly_dark",
                         title = "Durchschnittliche Qualifying-Zeiten pro Fahrer", 
                         category_orders = {"Run": ["Q1", "Q2", "Q3"]},
                         labels = {"Zeit": "Zeit in Millisekunden"})
            st.plotly_chart(fig, use_container_width = True)
            
        with tab2:
            df_q3_scatter = final_df_quali.dropna(subset=["Q3"])
            fig = px.scatter(df_q3_scatter, 
                             x= "Startplatz", 
                             y =  "Q3", 
                             color = "Fahrer",
                             title = "Q3-Zeit vs. Erzielte Startposition",
                             labels = {"Q3": "Zeit in Q3 (ms)", "Startplatz": "Startposition"})
            st.plotly_chart(fig, use_container_width = True)

# --- Sieges-Analyse ---
with st.expander("🥇 Rennsiege Analyse", expanded = True):
    if final_df_wins.empty:
        st.warning("Keine Sieges-Daten für diese Auswahl.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Nach Fahrer", "Nach Nationalität", "Nach Team", "Nach Alter"])
        with tab1:
            wins_by_driver = final_df_wins["Fahrer"].value_counts().reset_index()
            fig = px.bar(wins_by_driver, 
                         y = "Fahrer", 
                         x = "count", 
                         orientation = "h", 
                         template = "plotly_dark", 
                         title = "Gesamtsiege pro Fahrer")
            st.plotly_chart(fig.update_layout(yaxis = {"categoryorder":"total ascending"}), use_container_width = True)
        with tab2:
            wins_by_nation = final_df_wins["Nationalität"].value_counts().reset_index()
            fig = px.pie(wins_by_nation, 
                         names = "Nationalität", 
                         values = "count", 
                         template = "plotly_dark", 
                         title = "Siegesverteilung nach Nationalität", 
                         hole = 0.4)
            st.plotly_chart(fig, use_container_width = True)
        with tab3:
            wins_by_team = final_df_wins["Team"].value_counts().reset_index()
            fig = px.bar(wins_by_team, 
                         y = "Team", 
                         x = "count", 
                         orientation = "h", 
                         template = "plotly_dark", 
                         title = "Gesamtsiege pro Team")
            st.plotly_chart(fig.update_layout(yaxis = {"categoryorder":"total ascending"}), use_container_width = True)
        with tab4:
            fig = px.histogram(final_df_wins, 
                               x = "Alter", 
                               nbins = 15, 
                               title = "Altersverteilung bei Rennsiegen", 
                               template = "plotly_dark")
            st.plotly_chart(fig, use_container_width = True)

# --- DNF-Analyse ---
with st.expander("🔧 Analyse der Technischen Ausfälle", expanded = True):
    if final_df_dnf.empty:
        st.warning("Keine Ausfall-Daten für diese Auswahl.")
    else:
        tab1, tab2 = st.tabs(["Nach Team & Saison", "Nach Fahrer"])
        with tab1:
            dnf_counts = final_df_dnf.groupby(["Saison", "Team"]).size().reset_index(name = "Anzahl")
            fig = px.bar(dnf_counts, 
                         x = "Saison", 
                         y = "Anzahl", 
                         color = "Team", 
                         template = "plotly_dark", 
                         title = "Motorausfälle pro Saison & Team")
            st.plotly_chart(fig, use_container_width = True)
        with tab2:
            dnf_by_driver = final_df_dnf["Fahrer"].value_counts().reset_index()
            fig = px.bar(dnf_by_driver, 
                         y = "Fahrer", 
                         x = "count", 
                         orientation = "h", 
                         template = "plotly_dark", 
                         title = "Motorausfälle pro Fahrer")
            st.plotly_chart(fig.update_layout(yaxis = {"categoryorder":"total ascending"}), use_container_width = True)