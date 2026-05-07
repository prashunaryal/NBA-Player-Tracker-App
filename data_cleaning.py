"""
data_cleaning.py

Script for scraping and cleaning NBA per-game stats from Basketball-Reference.

This script follows cleaning steps:
1. Scrape data from local HTML files using BeautifulSoup
2. Remove repeated header rows
3. Keep only relevant columns
4. Convert string values to numeric
5. Filter to qualified players (40+ games and 20+ minutes)
6. Remove duplicate traded player rows

Input:
    nba.html (2024-25 season)
    nba_1996.html (1995-96 season)

Output:
    df_2025 (DataFrame)
    df_1996 (DataFrame)
"""

from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup

# Basketball-Reference uses the data-stat attribute on each <th>/<td>
# This dictionary maps those attributes to clean column names
STAT_TO_COL = {
    "ranker": "Rk",
    "name_display": "Player",
    "pos": "Pos",
    "age": "Age",
    "team_name_abbr": "Tm",
    "games": "G",
    "mp_per_g": "MP",
    "pts_per_g": "PTS",
    "trb_per_g": "TRB",
    "ast_per_g": "AST",
    "fg_pct": "FG%",
    "fg3_pct": "3P%",
    "stl_per_g": "STL",
    "blk_per_g": "BLK",
}


def print_step_result(step_name, passed):
    """Print a consistent pass/fix message for each step."""
    if passed:
        print(f"{step_name} passed.")
    else:
        print(f"{step_name} needs work.")


def load_season(filename):
    """Scrape and clean a Basketball-Reference per-game stats HTML file."""

    # --------------------------------------------------
    # Step 1: Scrape data from the HTML file
    # --------------------------------------------------
    """
    Open the local HTML file and parse the per_game_stats table.
    The page has multiple tables. We use soup.find() to grab the one
    with id="per_game_stats", which is the regular season stats table.
    """
    html_path = Path(__file__).resolve().parent / filename
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table", id="per_game_stats")
    if table is None:
        raise SystemExit(f"Table per_game_stats not found in {filename}")

    # Extract rows by looping through each <tr> and pulling text from cells
    # whose data-stat attribute is in our STAT_TO_COL mapping
    rows = []
    for tr in table.select("tbody tr"):
        row = {}
        for cell in tr.find_all(["th", "td"]):
            stat = cell.get("data-stat")
            if stat in STAT_TO_COL:
                row[STAT_TO_COL[stat]] = cell.get_text(strip=True)
        if not row.get("Player") or row["Player"] == "League Average":
            continue
        rows.append(row)

    df = pd.DataFrame(rows)

    # Test for Step 1
    print_step_result(f"Step 1 ({filename})", not df.empty)

    # --------------------------------------------------
    # Step 2: Remove repeated header rows
    # --------------------------------------------------
    """
    Basketball-Reference repeats the header row every ~25 rows inside the
    table itself. Remove any row where the Rk column literally says "Rk".
    """
    df = df[df["Rk"] != "Rk"]

    # Test for Step 2
    print_step_result(f"Step 2 ({filename})", "Rk" not in df["Rk"].values)

    # --------------------------------------------------
    # Step 3: Keep only relevant columns
    # --------------------------------------------------
    """
    The original table has 30+ columns. We only need the ones we'll use
    for analysis: Player, Pos, Age, Tm, G, MP, PTS, TRB, AST, FG%, 3P%, STL, BLK.
    """
    df = df[["Player", "Pos", "Age", "Tm", "G", "MP", "PTS", "TRB", "AST", "FG%", "3P%", "STL", "BLK"]]

    # Test for Step 3
    expected_columns = ["Player", "Pos", "Age", "Tm", "G", "MP", "PTS", "TRB", "AST", "FG%", "3P%", "STL", "BLK"]
    print_step_result(f"Step 3 ({filename})", list(df.columns) == expected_columns)

    # --------------------------------------------------
    # Step 4: Convert string values to numeric
    # --------------------------------------------------
    """
    Everything scraped from HTML comes in as a string. Convert the numeric
    columns (PTS, TRB, AST, G, MP, STL, BLK, 3P%) so we can do math on them.
    Using errors='coerce' so bad values become NaN instead of crashing.
    """
    for col in ["PTS", "TRB", "AST", "G", "MP", "STL", "BLK", "3P%"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Test for Step 4
    print_step_result(
        f"Step 4 ({filename})",
        all(pd.api.types.is_numeric_dtype(df[col]) for col in ["PTS", "TRB", "AST", "G", "MP", "STL", "BLK", "3P%"]),
    )

    # --------------------------------------------------
    # Step 5: Filter to qualified players
    # --------------------------------------------------
    """
    Keep only players with 40+ games played AND 20+ minutes per game.
    This removes bench players and call-ups whose tiny sample sizes
    would skew our positional averages.
    """
    df = df[(df["G"] >= 40) & (df["MP"] >= 20)]

    # Test for Step 5
    print_step_result(
        f"Step 5 ({filename})",
        (df["G"] >= 40).all() and (df["MP"] >= 20).all(),
    )

    # --------------------------------------------------
    # Step 6: Remove duplicate traded player rows
    # --------------------------------------------------
    """
    Players who were traded mid-season appear multiple times — once per
    team and once as a combined row labeled "2TM" (two teams) or "3TM"
    (three teams). Keep only the combined row.
    """
    df = df[~df.duplicated(subset="Player", keep=False) | (df["Tm"].isin(["2TM", "3TM"]))]

    # Test for Step 6
    print_step_result(
        f"Step 6 ({filename})",
        df["Player"].duplicated().sum() == 0,
    )

    return df


# Load both seasons when this module is imported
df_2025 = load_season("nba.html")
df_1996 = load_season("nba_1996.html")