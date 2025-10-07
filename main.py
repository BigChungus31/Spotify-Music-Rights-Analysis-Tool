import requests
import pandas as pd
from datetime import datetime
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API Credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Validate credentials
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing Spotify credentials. Please check your .env file.")

# Configuration
ARTIST_NAME = 'Linkin Park'
TSV_FILE = 'unclaimedmusicalworkrightshares.tsv'
OUTPUT_EXCEL = 'music_rights_analysis.xlsx'
OUTPUT_JSON = 'results.json'
CHUNK_SIZE = 100000  # Process 100k rows at a time

class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expires = 0
        
    def get_token(self):
        """Get access token from Spotify API"""
        if self.token and time.time() < self.token_expires:
            return self.token
            
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        
        if auth_response.status_code != 200:
            raise Exception(f"Authentication failed: {auth_response.text}")
            
        auth_data = auth_response.json()
        self.token = auth_data['access_token']
        self.token_expires = time.time() + auth_data['expires_in'] - 60
        return self.token
    
    def search_artist(self, artist_name):
        """Search for artist and return artist ID"""
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        search_url = 'https://api.spotify.com/v1/search'
        params = {
            'q': artist_name,
            'type': 'artist',
            'limit': 1
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        data = response.json()
        
        if not data['artists']['items']:
            return None
            
        artist = data['artists']['items'][0]
        return {
            'id': artist['id'],
            'name': artist['name'],
            'followers': artist['followers']['total'],
            'genres': artist['genres'],
            'popularity': artist['popularity']
        }
    
    def get_artist_albums(self, artist_id):
        """Get all albums for an artist"""
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        albums = []
        url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
        params = {
            'include_groups': 'album,single,compilation',
            'limit': 50,
            'market': 'US'
        }
        
        while url:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            albums.extend(data['items'])
            url = data.get('next')
            params = None  # Only use params on first request
            time.sleep(0.1)  # Rate limiting
            
        return albums
    
    def get_album_tracks(self, album_id):
        """Get all tracks from an album"""
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        tracks = []
        url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        params = {'limit': 50, 'market': 'US'}
        
        while url:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            tracks.extend(data['items'])
            url = data.get('next')
            params = None
            time.sleep(0.1)
            
        return tracks
    
    def get_track_details(self, track_ids):
        """Get detailed track information including ISRC"""
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Spotify allows up to 50 tracks per request
        all_tracks = []
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            url = 'https://api.spotify.com/v1/tracks'
            params = {'ids': ','.join(batch), 'market': 'US'}
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            all_tracks.extend(data['tracks'])
            time.sleep(0.1)
            
        return all_tracks

def load_unclaimed_dataset(tsv_file):
    """Load and index the unclaimed works dataset by ISRC - Memory efficient chunked processing"""
    print(f"Loading dataset from {tsv_file}...")
    print(f"Processing in chunks of {CHUNK_SIZE:,} rows to handle large file...")
    
    try:
        isrc_index = {}
        total_rows = 0
        valid_isrcs = 0
        chunk_count = 0
        
        # Process file in chunks with minimal memory usage
        for chunk in pd.read_csv(
            tsv_file, 
            sep='\t', 
            encoding='utf-8', 
            header=None, 
            chunksize=CHUNK_SIZE,
            usecols=[0, 1, 2, 3],  # Only load first 4 columns
            dtype=str,  # Load everything as string to avoid type inference issues
            on_bad_lines='skip',
            low_memory=True,  # Use low_memory mode
            engine='python'  # Python engine is more forgiving with large files
        ):
            chunk_count += 1
            chunk_len = len(chunk)
            total_rows += chunk_len
            
            # Assign column names
            chunk.columns = ['row_id', 'track_id', 'code1', 'isrc']
            
            # Process each row directly to minimize memory
            for idx in range(chunk_len):
                try:
                    row = chunk.iloc[idx]
                    isrc = str(row['isrc']).strip().upper()
                    
                    # Skip invalid ISRCs
                    if isrc in ['NAN', 'NA', 'NONE', '']:
                        continue
                    
                    # Basic ISRC format validation (optional, speeds up processing)
                    if len(isrc) == 12:  # Standard ISRC length
                        # Only store if not already in index (avoid duplicates)
                        if isrc not in isrc_index:
                            isrc_index[isrc] = {
                                'row_id': str(row['row_id']),
                                'track_id': str(row['track_id']),
                                'code1': str(row['code1']),
                                'isrc': str(row['isrc'])
                            }
                            valid_isrcs += 1
                except Exception as e:
                    # Skip problematic rows
                    continue
            
            # Progress update every million rows
            if total_rows % 1000000 == 0:
                print(f"  Processed {total_rows:,} rows... ({len(isrc_index):,} unique ISRCs indexed)")
            
            # Clear chunk from memory
            del chunk
        
        print(f"\n✓ Dataset processing complete!")
        print(f"  Total rows processed: {total_rows:,}")
        print(f"  Unique ISRCs indexed: {len(isrc_index):,}")
        print(f"  Valid ISRC codes: {valid_isrcs:,}")
        
        return None, isrc_index  # Return None for df to maintain compatibility
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return None, {}

def fetch_artist_catalog(spotify, artist_name):
    """Fetch complete artist catalog with ISRCs"""
    print(f"\nSearching for artist: {artist_name}")
    
    artist_info = spotify.search_artist(artist_name)
    if not artist_info:
        print(f"Artist '{artist_name}' not found")
        return None, []
    
    print(f"Found: {artist_info['name']}")
    print(f"Followers: {artist_info['followers']:,}")
    print(f"Popularity: {artist_info['popularity']}/100")
    
    print("\nFetching albums...")
    albums = spotify.get_artist_albums(artist_info['id'])
    print(f"Found {len(albums)} albums/singles/compilations")
    
    catalog = []
    track_ids = []
    
    print("\nFetching tracks from albums...")
    for idx, album in enumerate(albums, 1):
        print(f"Processing {idx}/{len(albums)}: {album['name']}")
        tracks = spotify.get_album_tracks(album['id'])
        
        for track in tracks:
            track_ids.append(track['id'])
            catalog.append({
                'track_id': track['id'],
                'track_name': track['name'],
                'album_name': album['name'],
                'album_type': album['album_type'],
                'release_date': album['release_date'],
                'track_number': track['track_number'],
                'duration_ms': track['duration_ms']
            })
    
    print(f"\nFetching ISRC codes for {len(track_ids)} tracks...")
    detailed_tracks = spotify.get_track_details(track_ids)
    
    # Add ISRC codes
    for i, track in enumerate(catalog):
        if i < len(detailed_tracks) and detailed_tracks[i]:
            track['isrc'] = detailed_tracks[i].get('external_ids', {}).get('isrc', 'N/A')
            track['explicit'] = detailed_tracks[i].get('explicit', False)
            track['popularity'] = detailed_tracks[i].get('popularity', 0)
        else:
            track['isrc'] = 'N/A'
    
    return artist_info, catalog

def cross_reference_catalog(catalog, isrc_index):
    """Cross-reference catalog with unclaimed works dataset"""
    print("\nCross-referencing with unclaimed works dataset...")
    
    matches = []
    for track in catalog:
        isrc = track.get('isrc', 'N/A')
        if isrc != 'N/A' and isrc in isrc_index:
            match = {**track, **isrc_index[isrc]}
            matches.append(match)
    
    print(f"Found {len(matches)} matches in unclaimed works dataset")
    return matches

def create_excel_report(artist_info, catalog, matches, output_file):
    """Create Excel file with three sheets"""
    print(f"\nCreating Excel report: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Full Artist Catalog
        df_catalog = pd.DataFrame(catalog)
        df_catalog = df_catalog.sort_values(['release_date', 'album_name', 'track_number'], 
                                           ascending=[False, True, True])
        df_catalog.to_excel(writer, sheet_name='Artist Catalog', index=False)
        
        # Sheet 2: Matches (Unclaimed Works)
        if matches:
            df_matches = pd.DataFrame(matches)
            df_matches.to_excel(writer, sheet_name='Unclaimed Matches', index=False)
        else:
            # Create empty sheet with message
            df_empty = pd.DataFrame({'Message': ['No matches found in unclaimed works dataset']})
            df_empty.to_excel(writer, sheet_name='Unclaimed Matches', index=False)
        
        # Sheet 3: Summary & Notes
        summary_data = {
            'Metric': [
                'Artist Name',
                'Spotify Followers',
                'Popularity Score',
                'Total Tracks in Catalog',
                'Tracks with ISRC',
                'Matches in Unclaimed Dataset',
                'Match Rate (%)',
                '',
                'Analysis Date',
                'Dataset File',
                '',
                'Notes',
                '- This analysis cross-references Spotify catalog with unclaimed musical work rights',
                '- Matches indicate songs that may have unclaimed royalties',
                '- ISRC (International Standard Recording Code) is used for matching',
                '- Not all tracks have ISRC codes available via Spotify API'
            ],
            'Value': [
                artist_info['name'],
                f"{artist_info['followers']:,}",
                f"{artist_info['popularity']}/100",
                len(catalog),
                len([t for t in catalog if t.get('isrc', 'N/A') != 'N/A']),
                len(matches),
                f"{(len(matches) / len(catalog) * 100):.2f}%" if catalog else '0%',
                '',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                TSV_FILE,
                '',
                '',
                '',
                '',
                '',
                ''
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary & Notes', index=False)
    
    print(f"Excel report created successfully!")

def save_json_for_dashboard(artist_info, catalog, matches):
    """Save data as JSON for HTML dashboard"""
    data = {
        'artist': artist_info,
        'catalog': catalog,
        'matches': matches,
        'stats': {
            'total_tracks': len(catalog),
            'tracks_with_isrc': len([t for t in catalog if t.get('isrc', 'N/A') != 'N/A']),
            'unclaimed_matches': len(matches),
            'match_rate': (len(matches) / len(catalog) * 100) if catalog else 0
        },
        'generated_at': datetime.now().isoformat()
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON data saved to {OUTPUT_JSON}")

def main():
    print("=" * 60)
    print("SPOTIFY MUSIC RIGHTS ANALYZER")
    print("=" * 60)
    
    # Check if TSV file exists
    if not os.path.exists(TSV_FILE):
        print(f"\nERROR: Dataset file '{TSV_FILE}' not found!")
        print("Please download the file and place it in the same directory as this script.")
        return
    
    # Initialize Spotify API
    spotify = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
    
    # Load unclaimed works dataset (chunked processing)
    dataset, isrc_index = load_unclaimed_dataset(TSV_FILE)
    
    if not isrc_index:
        print("Failed to load dataset. Exiting.")
        return
    
    # Fetch artist catalog
    artist_info, catalog = fetch_artist_catalog(spotify, ARTIST_NAME)
    
    if not artist_info or not catalog:
        print("\nTrying alternative artist: Radiohead")
        artist_info, catalog = fetch_artist_catalog(spotify, 'Radiohead')
        
        if not artist_info or not catalog:
            print("Failed to fetch artist data. Exiting.")
            return
    
    # Cross-reference with unclaimed works
    matches = cross_reference_catalog(catalog, isrc_index)
    
    # Create Excel report
    create_excel_report(artist_info, catalog, matches, OUTPUT_EXCEL)
    
    # Save JSON for dashboard
    save_json_for_dashboard(artist_info, catalog, matches)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  - {OUTPUT_EXCEL} (Excel report with 3 sheets)")
    print(f"  - {OUTPUT_JSON} (JSON data for dashboard)")
    print(f"\nNext step: Open 'dashboard.html' in your browser to view results")
    print("=" * 60)

if __name__ == "__main__":
    main()