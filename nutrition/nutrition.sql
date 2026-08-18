CREATE TABLE foods (
    food_slug TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    source_name TEXT,
    source_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nutrition_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_slug TEXT NOT NULL REFERENCES foods(food_slug),
    serving_size_g REAL,
    calories_kcal REAL,
    protein_g REAL,
    fat_g REAL,
    carbohydrates_g REAL,
    fiber_g REAL,
    source_name TEXT,
    source_url TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
