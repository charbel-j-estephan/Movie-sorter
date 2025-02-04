# Entertainment Media Organizer

A Python-based desktop application that helps you organize and manage your movies and TV series collection with a professional streaming service-like interface. The application automatically fetches media information, downloads posters, organizes content by genre, and tracks your watching progress.

## Features

### Content Organization
- **Smart Media Separation**: Automatically distinguishes between movies and TV series
- **Genre-Based Organization**: Organizes content into detailed genre categories
- **Multiple Organization Options**: Sort by genres, sub-genres, release year, and more
- **TV Series Management**: Dedicated TV series section with episode tracking
- **Smart Folder Naming**: Intelligently renames media folders with proper formatting

### Media Information
- **Comprehensive Info Fetching**: Retrieves detailed information from OMDB API
- **Poster Downloads**: Automatically downloads and caches media posters
- **Rich Details View**: Detailed interface showing plot, cast, ratings, and more
- **Watch Progress Tracking**: Keeps track of watched content and timestamps
- **Last Watched**: Shows recently watched content and progress

### User Interface
- **Streaming Service Design**: Professional UI inspired by popular streaming platforms
- **Advanced Search**: Search bar for quick content discovery
- **Smart Filtering**: Filter content by available genres and multiple criteria
- **Progress Indicators**: Visual indicators for watch progress and timestamps
- **Responsive Layout**: Adaptive grid layout for different screen sizes

### Playback Features
- **Video Playback**: Direct media playback with system default video player
- **Progress Resume**: Remembers last watched position for all content
- **Trailer Access**: Quick access to trailers via YouTube
- **Watch History**: Tracks and displays viewing history

### System Features
- **Settings Management**: Dedicated settings page for configuration
- **Directory Management**: Ability to change media directories
- **API Configuration**: Easy API key management
- **Loading Screen**: Professional loading screen with progress tracking
- **Manual Processing**: Special folder for content needing manual attention

## Prerequisites

- Python 3.8+
- PySide6
- OMDB API Key (free tier available at http://www.omdbapi.com/apikey.aspx)

## Required Packages

```
PySide6
aiohttp
aiofiles
guessit
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/charbel-j-estephan/Movie-sorter.git
cd movie-organizer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python movie_organizer_app.py
```

## First Time Setup

1. On first launch, you'll be prompted to enter your OMDB API key
2. If you don't have an API key, click "How to get an API Key?" for instructions
3. After entering the API key, select your movies directory
4. The application will begin organizing your movies

## Usage

1. **Main Interface**:
   - Professional streaming service-like grid layout
   - Quick search bar for content discovery
   - Filter content by available genres
   - View recently watched items
   - Track watch progress for all content

2. **Media Details**:
   - Rich details view for movies and TV series
   - Play content directly with timestamp resume
   - Track watching progress automatically
   - View comprehensive information including plot, cast, and ratings
   - Quick access to trailers and related content

3. **Content Management**:
   - Separate sections for movies and TV series
   - Detailed genre-based organization
   - Smart filtering by available genres
   - Progress tracking and timestamp storage
   - Last watched section with resume capability

4. **Settings**:
   - Change media directories at any time
   - Update OMDB API key
   - Customize organization preferences
   - Manage watch history and progress data
   - Configure interface preferences

## Project Structure

- `movie_organizer_app.py`: Main application file
- `movie_organizer_core.py`: Core organization logic
- `movie_browser.py`: Movie browsing interface
- `movie_tile.py`: Individual movie tile component
- `movie_details_dialog.py`: Detailed movie information dialog
- `loading_screen.py`: Loading screen with progress tracking
- `setup_dialog.py`: First-time setup dialog

## Features in Detail

### Content Organization
- Separate organization for movies and TV series
- Detailed genre and sub-genre categorization
- Handles multiple quality versions of the same content
- Supports various video formats
- Maintains original file structure within folders
- Tracks watch progress and timestamps

### Media Information and Progress Tracking
- Fetches comprehensive details from OMDB for all media
- Caches information locally for quick access
- Downloads and stores posters locally
- Tracks watching progress and timestamps
- Maintains viewing history
- Handles API rate limiting and retries

### User Interface
- Professional streaming service-like design
- Modern, responsive layout
- Advanced search functionality
- Genre-based filtering system
- Watch progress indicators
- Last watched section
- Settings page for customization
- Smooth loading with progress indication
- Detailed media information view
- Quick access to playback and trailers

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- OMDB API for movie information
- PySide6 for the GUI framework
- guessit for movie name parsing
