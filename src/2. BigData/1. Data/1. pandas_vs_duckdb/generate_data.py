"""
Generate a synthetic temperature dataset for the pandas vs DuckDB benchmark.

Each row is `station_name;measurement` (no header), in the style of the
"One Billion Row Challenge". Measurements are drawn from a normal distribution
(sd = 10 degrees) around each station's mean temperature from stations.csv,
rounded to one decimal place.

Values are derived from a hash of the row number, so the same row count always
produces the same data, regardless of how many threads DuckDB uses.

Usage:
    uv run python generate_data.py --rows 100000000 --output medium_dataset.csv
    uv run python generate_data.py --rows 1000000000 --output large_dataset.csv
"""

import argparse
import time
from pathlib import Path

import duckdb

STATIONS_FILE = Path(__file__).parent / "stations.csv"
STD_DEV = 10.0


def generate(rows: int, output: Path, stations_file: Path = STATIONS_FILE) -> None:
    if rows <= 0:
        raise ValueError(f"--rows must be positive, got {rows}")
    if not stations_file.exists():
        raise FileNotFoundError(f"Station list not found: {stations_file}")

    print(f"Generating {rows:,} rows -> {output} ...")
    start_time = time.time()

    with duckdb.connect() as conn:
        conn.execute(
            """
            CREATE TABLE stations AS
            SELECT row_number() OVER () - 1 AS idx, station_name, mean_temperature
            FROM read_csv(?, delim=';', header=true,
                          columns={'station_name': 'varchar', 'mean_temperature': 'double'})
            """,
            [str(stations_file)],
        )
        n_stations = conn.execute("SELECT count(*) FROM stations").fetchone()[0]

        # Box-Muller transform on two hash-derived uniforms -> normal noise
        conn.execute(
            f"""
            COPY (
                SELECT
                    s.station_name,
                    CAST(greatest(-99.9, least(99.9,
                        s.mean_temperature + {STD_DEV} * sqrt(-2 * ln(r.u1)) * cos(2 * pi() * r.u2)
                    )) AS DECIMAL(4, 1)) AS measurement
                FROM (
                    SELECT
                        hash(i, 'station') % {n_stations} AS idx,
                        (hash(i, 'u1') % 1000000 + 1) / 1000001.0 AS u1,
                        (hash(i, 'u2') % 1000000) / 1000000.0 AS u2
                    FROM range({rows}) t(i)
                ) r
                JOIN stations s USING (idx)
            ) TO '{output}' (HEADER false, DELIMITER ';')
            """
        )

    size_gb = output.stat().st_size / 1e9
    print(f"✓ {output.name}: {rows:,} rows, {size_gb:.2f} GB in {time.time() - start_time:.1f} s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", type=int, required=True, help="Number of rows to generate")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")
    args = parser.parse_args()
    generate(args.rows, args.output)
