# Serie A Fantasy Football Scraper

A Python data-engineering project for extracting, parsing, validating, and storing historical Serie A fantasy-football data.

> **Status:** Work in progress — the core scraping and persistence pipeline is implemented, while orchestration, testing, error handling, and historical coverage are still being developed.

## Overview

The goal of this project is to build a structured historical dataset that can later support APIs, statistical analysis, and machine-learning experiments.

The scraper currently extracts:

* Serie A fixtures and results
* Teams
* Player match ratings
* Bonus/malus events
* Player profiles
* Player roles
* Classic and Mantra valuations
* Classic and Mantra FVM values
* Player information such as nationality, birth date, height, and preferred foot

The extracted data is validated with **Pydantic / SQLModel** and persisted in **PostgreSQL**.

## Pipeline

```text
Matchday pages
      │
      ▼
Discover matches
      │
      ▼
Fetch match pages
      │
      ├──► Match information
      │
      └──► Player ratings
                │
                ▼
          Discover players
                │
                ▼
          Fetch player pages
                │
                ▼
          Player information
                │
                ▼
          Validate models
                │
                ▼
            PostgreSQL
```

HTTP requests are performed asynchronously so that multiple match and player pages can be fetched concurrently.

## Project structure

```text
fantasy_football/
├── src/
│   └── fantasy_football_scraper/
│       ├── config.py
│       │
│       ├── db/
│       │   ├── create_db.py
│       │   ├── db_engine.py
│       │   ├── models.py
│       │   └── save_data.py
│       │
│       ├── fetch/
│       │   ├── fetcher.py
│       │   └── urls.py
│       │
│       ├── parse/
│       │   └── html_parsing.py
│       │
│       └── services/
│           └── ratings.py
│
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

### `fetch/`

Responsible for HTTP communication and URL generation.

`fetcher.py` uses `niquests.AsyncSession` and `asyncio.gather()` to fetch multiple pages concurrently, while `urls.py` builds season, matchday, and match URLs.

### `parse/`

Contains the HTML extraction logic built with Beautiful Soup.

The parsing layer converts HTML pages into Python dictionaries without interacting directly with the database.

### `db/`

Contains the SQLModel entities, PostgreSQL connection configuration, table creation, and persistence logic.

### `services/`

Coordinates the complete extraction workflow by combining URL generation, fetching, parsing, model validation, and persistence.

## Data model

The current database contains five main entities.

### Team

```text
Team
├── id
└── team_name
```

### Match

```text
Match
├── fc_match_id
├── home_team_id
├── away_team_id
├── home_score
├── away_score
└── match_date
```

### Player

```text
Player
├── fc_player_id
├── name
├── slug
├── birthdate
├── height
├── foot
└── nationality
```

### PlayerStats

Stores season-specific information about a player.

```text
PlayerStats
├── fc_player_id
├── team_id
├── main_role
├── specific_roles
├── classic_value
├── classic_vfm
├── mantra_value
├── mantra_vfm
├── season
└── date
```

### Rating

Stores the performance of a player in a specific match.

```text
Rating
├── fc_match_id
├── fc_player_id
├── team_id
├── rating
└── bonus_malus
```

Fields such as nationalities, specific roles, and bonus/malus events are stored using PostgreSQL `JSONB`.

## Requirements

* Python 3.14+
* PostgreSQL
* [`uv`](https://docs.astral.sh/uv/)

Main Python dependencies include:

* Beautiful Soup
* niquests
* SQLModel
* SQLAlchemy
* psycopg2
* Pydantic
* python-dateutil
* python-dotenv

## Installation

Clone the repository:

```bash
git clone https://github.com/Alessandroc92/fantasy_football.git
cd fantasy_football
```

Install the dependencies:

```bash
uv sync
```

## Configuration

Database credentials and the source base URL are loaded from environment variables.

Create a `.env` file in the project root:

```env
BASE_URL=https://www.example.com/

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## Create the database tables

After creating the PostgreSQL database, generate the application tables with:

```bash
uv run python -m fantasy_football_scraper.db.create_db
```

SQLModel uses the models defined in `db/models.py` to create the required tables and relationships.

## Running the scraper

The main extraction workflow is currently implemented in:

```python
fantasy_football_scraper.services.ratings.extract_ratings
```

It can be called asynchronously:

```python
import asyncio

from fantasy_football_scraper.services.ratings import extract_ratings


asyncio.run(
    extract_ratings(
        start_season=2025,
        end_season=2026,
    )
)
```

## Current status

| Component                  | Status                         |
| -------------------------- | ------------------------------ |
| Matchday URL generation    | ✅ Implemented                  |
| Async HTTP fetching        | 🚧 Implemented / being refined |
| Match discovery            | ✅ Implemented                  |
| Match parsing              | ✅ Implemented                  |
| Player rating parsing      | ✅ Implemented                  |
| Player profile parsing     | ✅ Implemented                  |
| SQLModel models            | ✅ Implemented                  |
| PostgreSQL persistence     | ✅ Implemented                  |
| Model validation           | ✅ Implemented                  |
| Multi-season orchestration | 🚧 In progress                 |
| Error handling and retries | 🚧 In progress                 |
| Automated tests            | 📋 Planned                     |
| Logging                    | 📋 Planned                     |
| Docker environment         | 📋 Planned                     |
| API layer                  | 📋 Planned                     |
| Statistical / ML analysis  | 📋 Planned                     |

## Roadmap

* [ ] Complete multi-season historical extraction
* [ ] Remove temporary development limits
* [ ] Improve concurrency management
* [ ] Add request timeouts and retry/backoff policies
* [ ] Improve parser error handling
* [ ] Add structured logging
* [ ] Add unit tests for parsers and models
* [ ] Add integration tests for the persistence layer
* [ ] Add database migrations
* [ ] Containerize PostgreSQL and the scraper with Docker
* [ ] Add a REST API for accessing the collected data
* [ ] Build statistical and machine-learning experiments on top of the historical dataset

## Longer-term direction

The scraper is intended to become the data-ingestion layer of a larger project:

```text
    Website
        │
        ▼
   Scraper / ETL
        │
        ▼
    PostgreSQL
        │
        ├──────────► REST API
        │
        └──────────► Analytics / ML
```

This separation allows data collection, serving, and analysis to evolve as independent components.

## Data and repository scope

This repository contains the **source code of the scraper and database schema only**.

It does **not** include or redistribute the database produced via scraping, and any example or test data added to the repository should be synthetic or limited to what is necessary to demonstrate the application.

The project is intended primarily for learning, experimentation, and portfolio purposes; anyone running the scraper is responsible for verifying and respecting the terms, access policies, copyright, database rights, and applicable rules of the data source.
