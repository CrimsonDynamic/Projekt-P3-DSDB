CREATE TABLE IF NOT EXISTS Fahrer (
    Fahrer_ID TEXT PRIMARY KEY,
    Name TEXT,
    Nationalität TEXT,
    Geburtsdatum DATE
);

CREATE TABLE IF NOT EXISTS Konstrukteur (
    Konstrukteur_ID TEXT PRIMARY KEY,
    Name TEXT
);

CREATE TABLE IF NOT EXISTS Rennen (
    Rennen_ID TEXT PRIMARY KEY,
    Saison INTEGER,
    GP_Name TEXT,
    Datum DATE,
    Runde INTEGER
);

CREATE TABLE IF NOT EXISTS Qualifikation (
    Fahrer_ID TEXT,
    Runde INTEGER,
    Q1 INTEGER,
    Q2 INTEGER,
    Q3 INTEGER,
    Startposition INTEGER,
    Saison INTEGER,
    PRIMARY KEY (Fahrer_ID, Runde)
);

CREATE TABLE IF NOT EXISTS Ergebnis (
    Rennen_ID TEXT,
    Fahrer_ID TEXT,
    Position INTEGER,
    Status TEXT,
    Konstrukteur_ID TEXT,
    PRIMARY KEY (Rennen_ID, Fahrer_ID)
);