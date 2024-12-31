CREATE TABLE energy_meter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_time TEXT NOT NULL,
    total_power REAL NOT NULL,
    power_delta REAL NOT NULL,
    imp_total INTEGER NOT NULL,
    imp_minute INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    time TEXT NOT NULL,
    tariff TEXT NOT NULL
);