CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326)
);


CREATE TABLE rainfall (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    rainfall_mm DOUBLE PRECISION,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE drainage_nodes (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    node_type VARCHAR(50),
    elevation DOUBLE PRECISION,
    capacity DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326)
);

CREATE TABLE drainage_edges (
    id SERIAL PRIMARY KEY,
    from_node INTEGER REFERENCES drainage_nodes(id),
    to_node INTEGER REFERENCES drainage_nodes(id),
    length_m DOUBLE PRECISION,
    capacity DOUBLE PRECISION,
    geom GEOMETRY(LineString, 4326)
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    predicted_depth_m DOUBLE PRECISION,
    risk_level VARCHAR(30),
    prediction_time TIMESTAMP,
    forecast_for TIMESTAMP
);

CREATE TABLE blockages (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES drainage_nodes(id),
    severity VARCHAR(30),
    blockage_percentage DOUBLE PRECISION,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30)
);


