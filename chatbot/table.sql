CREATE TABLE IF NOT EXISTS oven (
	unique_id INT PRIMARY KEY,
	brand VARCHAR(100) NOT NULL,
	model_name VARCHAR(100) NOT NULL,
	technology_type VARCHAR(100) NOT NULL,
	cassification VARCHAR(100) NOT NULL,
	fuel_type VARCHAR(100) NOT NULL,
	input_rate REAL, -- kW
	convection_idle_energy_rate REAL, -- kW
	max_baking_tray INTEGER,
	steam_idle_energy_rate REAL, -- kW
	convection_cooking_energy_efficiency REAL,
	steam_cooking_energy_efficiency REAL,
	steam_water_consumption REAL -- gal/pan
);