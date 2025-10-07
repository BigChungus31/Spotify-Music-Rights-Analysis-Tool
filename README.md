# Spotify Music Rights Analysis Tool

A powerful Python-based analytics tool that cross-references Spotify artist catalogs with unclaimed musical work rights datasets to identify potential unclaimed royalties. Features an interactive Spotify-styled dashboard for comprehensive data visualization.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Spotify%20API](https://img.shields.io/badge/Spotify%20API-v1-1DB954)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange)
![OpenPyXL](https://img.shields.io/badge/OpenPyXL-Excel%20Reports-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Overview

This tool performs comprehensive analysis by:
- Fetching complete artist discographies from Spotify API (albums, singles, compilations)
- Extracting ISRC (International Standard Recording Code) for each track
- Cross-referencing against a 60M+ row dataset of unclaimed musical work rights
- Generating detailed Excel reports and an interactive web dashboard

**Use Case**: Music rights administrators, artists, and industry professionals can identify tracks that may have unclaimed royalties or publishing rights issues.

## Features

- **Complete Catalog Analysis**: Retrieves full discography including albums, singles, and compilations
- **ISRC-Based Matching**: Uses industry-standard ISRC codes for accurate track identification
- **Memory-Efficient Processing**: Handles large datasets (60M+ rows) using chunked processing
- **Dual Output Formats**:
  - Excel report with multiple sheets (catalog, matches, summary)
  - Interactive HTML dashboard with Spotify-inspired design
- **Real-time Progress Tracking**: Detailed console output during processing
- **Artist Metadata**: Includes follower counts, popularity scores, and genre information

## Quick Start

### Prerequisites

- Python 3.8+
- Spotify Developer Account (for API credentials)
- - Unclaimed musical works dataset (TSV format) - [Download here](https://drive.google.com/file/d/1ZAAgkfhmMaq5r6dfKq4D3qgfBewM0D2x/view?usp=sharing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tritone-analytics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

   **Get Spotify API Credentials**:
   - Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy Client ID and Client Secret

4. **Add the dataset**
   
   Download the dataset from [this link](https://drive.google.com/file/d/1ZAAgkfhmMaq5r6dfKq4D3qgfBewM0D2x/view?usp=sharing) and place it in the project root:

### Running the Analysis

```bash
python main.py
```

The script will:
1. Load and index the unclaimed works dataset (~60M rows)
2. Fetch the artist's complete Spotify catalog
3. Cross-reference ISRC codes
4. Generate output files

**Expected Runtime**: 5-10 minutes (depending on dataset size and artist catalog)

## Output Files

### 1. Excel Report (`music_rights_analysis.xlsx`)

Three-sheet workbook containing:

- **Artist Catalog**: Complete discography with ISRC codes
  - Track names, albums, release dates
  - Album types (album/single/compilation)
  - ISRC codes, track numbers, duration
  
- **Unclaimed Matches**: Tracks found in unclaimed works dataset
  - Matched tracks with all metadata
  - Unclaimed work identifiers
  
- **Summary & Notes**: Analysis overview
  - Total tracks analyzed
  - Match statistics and rates
  - Artist information and metadata

### 2. Interactive Dashboard (`dashboard.html`)

Modern web interface featuring:

- **Artist Overview**: Followers, popularity, genres
- **Key Metrics**: Total tracks, ISRC coverage, match rate
- **Interactive Tables**: 
  - Full catalog with filtering and search
  - Unclaimed matches with highlighting
- **Real-time Filtering**: Search by track/album name, filter by type

**To view**: Open `dashboard.html` in any modern web browser

### 3. JSON Data (`results.json`)

Machine-readable format containing all analysis data for further processing or integration.

## Dashboard Preview

The dashboard features a Spotify-inspired design with:
- Black and green color scheme
- Minimalist, modern interface
- Responsive layout
- Smooth interactions and hover effects
- Tab-based navigation

## Project Structure

```
tritone-analytics/
├── main.py                                    # Core analysis script
├── dashboard.html                             # Interactive web dashboard
├── requirements.txt                           # Python dependencies
├── .env                                       # API credentials (create this)
├── .gitignore                                # Git ignore rules
├── README.md                                  # Documentation
├── unclaimedmusicalworkrightshares.tsv       # Dataset (add this)
├── music_rights_analysis.xlsx                # Generated Excel report
└── results.json                               # Generated JSON data
```

## Configuration

### Customize Analysis Parameters

Edit `main.py` to modify:

```python
# Line 12: Change target artist
ARTIST_NAME = 'Linkin Park'  # Change to any artist

# Line 13: Dataset file path
TSV_FILE = 'unclaimedmusicalworkrightshares.tsv'

# Line 14-16: Output file names
OUTPUT_EXCEL = 'music_rights_analysis.xlsx'
OUTPUT_JSON = 'results.json'

# Line 17: Chunk size for dataset processing
CHUNK_SIZE = 100000  # Adjust based on available memory
```

## Example Results

**Sample Output for Linkin Park**:
```
✓ Dataset processing complete!
  Total rows processed: 59,989,691
  Unique ISRCs indexed: 10,487,354
  Valid ISRC codes: 10,487,354

Artist: Linkin Park
Followers: 31,505,811
Popularity: 89/100

Found 71 albums/singles/compilations
Total tracks: 665
Tracks with ISRC: 665
Unclaimed matches: 69
Match rate: 10.38%
```

## Technical Details

### Technologies Used

- **Python 3.8+**: Core programming language
- **Spotify Web API**: Artist and track data retrieval
- **Pandas**: Data manipulation and Excel generation
- **python-dotenv**: Environment variable management
- **Requests**: HTTP API calls
- **OpenPyXL**: Excel file generation

### Key Features

- **Chunked Processing**: Processes large datasets in 100K row chunks to minimize memory usage
- **ISRC Indexing**: Creates in-memory dictionary for O(1) lookup performance
- **Rate Limiting**: Built-in delays to respect Spotify API rate limits
- **Error Handling**: Graceful handling of missing data and API errors
- **Deduplication**: Automatically removes duplicate ISRCs from dataset

## Security Notes

- **Never commit `.env` file** to version control
- Keep API credentials secure and private
- Rotate credentials periodically
- Use environment variables for all sensitive data

## Requirements

```
requests==2.31.0
pandas==2.1.4
openpyxl==3.1.2
python-dotenv==1.0.0
```

## Troubleshooting

### Common Issues

**Issue**: `Dataset file not found`
- **Solution**: Ensure `unclaimedmusicalworkrightshares.tsv` is in the project root

**Issue**: `Authentication failed`
- **Solution**: Verify Spotify credentials in `.env` file are correct

**Issue**: `Memory error during dataset processing`
- **Solution**: Reduce `CHUNK_SIZE` in `main.py` (line 17)

**Issue**: `No matches found`
- **Solution**: This may be normal - not all artists have tracks in the unclaimed dataset

## Use Cases

1. **Music Rights Administration**: Identify potentially unclaimed royalties
2. **Artist Management**: Track catalog completeness and rights status
3. **Publishing Companies**: Audit catalogs for missing rights information
4. **Legal Teams**: Evidence gathering for rights disputes
5. **Research**: Music industry analytics and trends

## License

MIT License - Free to use and modify
---

**Note**: This tool is designed for informational and analytical purposes. Always consult legal professionals for official music rights determinations.