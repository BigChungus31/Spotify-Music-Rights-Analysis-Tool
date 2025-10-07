# Dataset Structure Reference

## File: unclaimedmusicalworkrightshares.tsv

### Column Structure (No Headers)

The TSV file does not have column headers. Based on analysis, the columns are:

| Index | Column Name (Assigned) | Description | Example |
|-------|------------------------|-------------|---------|
| 0 | `row_id` | Sequential ID | 9999999, 9999998, etc. |
| 1 | `track_id` | Internal track identifier | 15_7kjdK7aeWv8, 15_A64118892... |
| 2 | `code1` | Some code/classification | B5145D, CA3N3Q, JCC6ST, etc. |
| 3 | **`isrc`** | **ISRC Code (PRIMARY KEY)** | DEBE72200740, GBK9H1300010, USA2P2314675 |
| 4 | `url_description` | YouTube URL or description | youtube::7kjdK7aeWv8 BODY LANGUAGE |
| 5+ | `additional_columns` | Artist, title, and other metadata | M.A.N.D.Y., CROSSES, JESSE JAMES, etc. |

### ISRC Code Format

ISRC (International Standard Recording Code) format: `CCXXXNNNNNNN`

Where:
- `CC` = 2-letter country code (US, GB, DE, IN, etc.)
- `XXX` = 3 alphanumeric registrant code
- `NNNNNNN` = 7-digit year + designation code

**Examples from dataset:**
- `DEBE72200740` - Germany (DE)
- `GBK9H1300010` - Great Britain (GB)
- `USA2P2314675` - United States (US)
- `INVI19301733` - India (IN)
- `USHU20915906` - United States (US)
- `GBCKG2100256` - Great Britain (GB)

### How the Script Uses This

1. **Loading**: The script reads the TSV file without expecting headers
2. **Column Assignment**: Automatically assigns logical names to columns 0-3
3. **ISRC Indexing**: Creates a hash map using column 3 (ISRC) as the key
4. **Matching**: Compares Spotify ISRCs against this index for O(1) lookup time
5. **Normalization**: Cleans ISRCs (strips whitespace, converts to uppercase)

### Sample Rows

```
9999999  15_7kjdK7aeWv8      B5145D  DEBE72200740  youtube::7kjdK7aeWv8 BODY LANGUAGE  M.A.N.D.Y.         375  5.0
9999998  15_A64118892840...  CA3N3Q  GBK9H1300010  youtube::A64118892840425           CROSSES            243  50.0
9999997  15_jkPMJxmsQHU      JCC6ST  USA2P2314675  youtube::jkPMJxmsQHU JESSE JAMES    DON'T LOOK AWAY    133  50.0
```

### Data Quality Notes

- Total rows: ~10 million (estimated)
- ISRC coverage: Most rows have valid ISRC codes
- Format consistency: ISRCs follow standard format
- Encoding: UTF-8
- Delimiter: Tab (`\t`)

### Why ISRC Matching?

ISRCs are unique identifiers for sound recordings:
- International standard (ISO 3901)
- Unique per recording
- Available in both Spotify API and this dataset
- Reliable for matching across platforms
- No ambiguity with track names, artist names, or spellings

This makes ISRC the perfect key for cross-referencing between Spotify's catalog and the unclaimed works database.