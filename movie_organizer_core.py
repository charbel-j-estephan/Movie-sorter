# movie_organizer_core.py
import os
import guessit
import shutil
import aiohttp
import asyncio
import json
import aiofiles
import hashlib
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path


@dataclass
class MovieInfo:
    title: str
    quality: str
    path: Path
    genres: List[str] = None
    year: str = None
    raw_data: Dict = None


class MovieOrganizer:
    def __init__(self, api_key: str, progress_callback: Callable = None):
        self.api_key = api_key
        self.progress_callback = progress_callback or (lambda x, y: None)
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.GENRES = set(GENRES)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters"""
        return "".join(
            char for char in filename if char.isalnum() or char in " ._-"
        ).strip()

    async def rename_folder(self, path: Path) -> Path:
        """Rename a folder based on movie information"""
        if (
            path.name in self.GENRES
            or path.name == "Manual Checking"
            or path.name == "movies info"
        ):
            return path

        movie_info = guessit.guessit(path.name.replace("-", " "))
        if "title" in movie_info:
            title = movie_info["title"]
            quality = str(movie_info.get("screen_size", ""))
            new_name = f"{title} ({quality})" if quality else title
            new_name = self._sanitize_filename(new_name)
            new_path = path.parent / new_name

            if path != new_path:
                try:
                    await self._safe_move(path, new_path)
                    self.logger.info(f"Renamed: {path} to {new_path}")
                    return new_path
                except Exception as e:
                    self.logger.error(f"Error renaming {path}: {str(e)}")
                    return path
        return path

    async def fetch_movie_details(self, title: str, retries: int = 3) -> Optional[Dict]:
        """Fetch movie details from OMDB API"""
        url = f"http://www.omdbapi.com/?t={title}&apikey={self.api_key}"

        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("Response") == "True":
                            return data
                    await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error fetching details for {title}: {str(e)}")
                await asyncio.sleep(2**attempt)  # Exponential backoff
        return None

    async def download_poster(
        self, poster_url: str, movie_name: str, movies_info_dir: Path
    ) -> Optional[Path]:
        """Download movie poster and save it locally"""
        if not poster_url or poster_url == "N/A":
            return None

        try:
            # Create posters directory if it doesn't exist
            posters_dir = movies_info_dir / "posters"
            posters_dir.mkdir(exist_ok=True)

            # Generate a unique filename using hash of movie name
            poster_hash = hashlib.md5(movie_name.encode()).hexdigest()
            file_extension = poster_url.split(".")[-1].split("?")[
                0
            ]  # Get extension without query params
            if file_extension not in ["jpg", "jpeg", "png"]:
                file_extension = "jpg"  # Default to jpg

            poster_path = posters_dir / f"{poster_hash}.{file_extension}"

            # If poster already exists, return the path
            if poster_path.exists():
                return poster_path

            # Download the poster
            async with self.session.get(poster_url) as response:
                if response.status == 200:
                    async with aiofiles.open(poster_path, "wb") as f:
                        await f.write(await response.read())
                    return poster_path

        except Exception as e:
            self.logger.error(f"Error downloading poster for {movie_name}: {str(e)}")
        return None

    def scan_directory(self, directory: Path) -> List[MovieInfo]:
        """Scan directory and return movie information"""
        movie_infos = []
        paths = [p for p in directory.iterdir() if p.is_dir()]

        for i, path in enumerate(paths):
            if (
                path.name in self.GENRES
                or path.name == "Manual Checking"
                or path.name == "movies info"
            ):
                continue

            movie_data = guessit.guessit(path.name)
            if "title" in movie_data:
                movie_infos.append(
                    MovieInfo(
                        title=movie_data["title"],
                        quality=str(movie_data.get("screen_size", "")),
                        path=path,
                    )
                )

            self.progress_callback("scanning", i / len(paths) * 100)

        return movie_infos

    async def process_movies(self, directory: Path):
        """Main processing function"""
        try:
            # First ensure "movies info" folder is created in root directory
            movies_info_dir = directory / "movies info"
            movies_info_dir.mkdir(exist_ok=True)

            # Create genre folders
            for genre in self.GENRES:
                (directory / genre).mkdir(exist_ok=True)

            # Create Manual Checking folder
            manual_checking = directory / "Manual Checking"
            manual_checking.mkdir(exist_ok=True)

            # Remove any duplicate "movies info" folder from Manual Checking
            duplicate_info = manual_checking / "movies info"
            if duplicate_info.exists():
                try:
                    if duplicate_info.is_dir():
                        # Move any JSON files to the root movies info directory first
                        for json_file in duplicate_info.glob("*.json"):
                            target_path = movies_info_dir / json_file.name
                            if (
                                not target_path.exists()
                            ):  # Only move if doesn't exist in root
                                json_file.rename(target_path)

                        # Now remove the duplicate directory
                        shutil.rmtree(str(duplicate_info))
                    print(f"Removed duplicate movies info folder from Manual Checking")
                except Exception as e:
                    print(
                        f"Warning: Could not fully cleanup duplicate movies info folder: {e}"
                    )

            # First rename all movie folders
            paths = [p for p in directory.iterdir() if p.is_dir()]
            total_paths = len(paths)

            for i, path in enumerate(paths):
                if (
                    path.name not in self.GENRES
                    and path.name != "Manual Checking"
                    and path.name != "movies info"
                ):
                    await self.rename_folder(path)
                    self.progress_callback("renaming", (i + 1) / total_paths * 100)

            # Scan directory after renaming
            movies = self.scan_directory(directory)

            # Process movies with poster downloads
            async def process_movie(movie: MovieInfo):
                details = await self.fetch_movie_details(movie.title)
                if details:
                    try:
                        # Download poster if available
                        poster_path = None
                        if details.get("Poster"):
                            poster_path = await self.download_poster(
                                details["Poster"], movie.path.name, movies_info_dir
                            )
                            if poster_path:
                                # Update the poster path in the details
                                details["LocalPoster"] = str(poster_path)

                        # Save movie info to JSON
                        info_path = movies_info_dir / f"{movie.path.name}_about.json"
                        with open(info_path, "w", encoding="utf-8") as f:
                            json.dump(details, f, indent=4, ensure_ascii=False)
                    except Exception as e:
                        print(f"Error saving movie info for {movie.title}: {e}")

                    movie.genres = details.get("Genre", "").split(", ")
                    movie.year = details.get("Year")
                    movie.raw_data = details
                return movie

            # Process in batches to avoid overwhelming the API
            batch_size = 5
            processed_movies = []
            total_batches = (len(movies) + batch_size - 1) // batch_size

            for i in range(0, len(movies), batch_size):
                batch = movies[i : i + batch_size]
                batch_results = await asyncio.gather(
                    *[process_movie(movie) for movie in batch]
                )
                processed_movies.extend(batch_results)
                self.progress_callback("fetching", (i + len(batch)) / len(movies) * 100)

            # Organize movies
            await self._organize_movies(directory, processed_movies)

            # Clean up empty folders at the end
            await self._cleanup_empty_folders(directory)

            # Write summary
            self._write_summary(directory, processed_movies)

        except Exception as e:
            print(f"Error in process_movies: {e}")
            raise

    async def _organize_movies(self, directory: Path, movies: List[MovieInfo]):
        """Organize movies into genre folders"""
        for i, movie in enumerate(movies):
            if not movie.genres:
                await self._move_to_manual_checking(directory, movie)
                continue

            main_genre = movie.genres[0]
            if main_genre in self.GENRES:
                genre_path = directory / main_genre
                new_path = genre_path / movie.path.name
                await self._safe_move(movie.path, new_path)
            else:
                await self._move_to_manual_checking(directory, movie)

            self.progress_callback("organizing", (i + 1) / len(movies) * 100)

    @staticmethod
    async def _safe_move(src: Path, dst: Path):
        """Safely move files using asyncio"""
        if src == dst:
            return

        def _move():
            if dst.exists():
                shutil.rmtree(str(dst))
            shutil.move(str(src), str(dst))

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, _move)

    async def _move_to_manual_checking(self, directory: Path, movie: MovieInfo):
        """Move a movie to the manual checking folder"""
        manual_checking = directory / "Manual Checking"
        new_path = manual_checking / movie.path.name
        await self._safe_move(movie.path, new_path)

    async def _cleanup_empty_folders(self, directory: Path):
        """Remove empty genre folders"""
        total_genres = len(self.GENRES)
        removed_count = 0

        # Clean up genre folders
        for i, genre in enumerate(self.GENRES):
            genre_folder = directory / genre
            if genre_folder.exists():
                try:
                    if not any(genre_folder.iterdir()):
                        genre_folder.rmdir()
                        removed_count += 1
                except Exception as e:
                    print(f"Error removing folder {genre}: {str(e)}")
            self.progress_callback("cleaning", (i + 1) / total_genres * 100)

        self.progress_callback("cleaning", 100)
        print(f"Cleanup complete. Removed {removed_count} empty folders")

    def _write_summary(self, directory: Path, movies: List[MovieInfo]):
        """Write processing summary"""
        manual_checking = len([m for m in movies if not m.genres])
        total_movies = len(movies)

        try:
            with open(directory / "process_summary.txt", "w", encoding="utf-8") as f:
                f.write(
                    f"{manual_checking} / {total_movies} movies are in 'Manual Checking'"
                )
        except Exception as e:
            print(f"Error writing summary: {e}")


# List of supported genres
GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "Game-Show",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western",
    # Combined genres
    "Action-Comedy",
    "Action-Horror",
    "Action-Adventure",
    "Adventure-Comedy",
    "Adventure-Fantasy",
    "Animation-Action",
    "Animation-Comedy",
    "Animation-Drama",
    "Animation-Family",
    "Biography-Drama",
    "Biography-History",
    "Comedy-Drama",
    "Comedy-Romance",
    "Crime-Drama",
    "Crime-Thriller",
    "Documentary-Biography",
    "Documentary-Drama",
    "Documentary-Music",
    "Drama-Family",
    "Drama-Mystery",
    "Drama-Romance",
    "Fantasy-Adventure",
    "Fantasy-Action",
    "Fantasy-Drama",
    "Fantasy-Romance",
    "Film-Noir-Crime",
    "Film-Noir-Drama",
    "Game-Show-Music",
    "History-Drama",
    "History-Romance",
    "Horror-Comedy",
    "Horror-Mystery",
    "Horror-Thriller",
    "Music-Drama",
    "Music-Romance",
    "Musical-Comedy",
    "Musical-Drama",
    "Mystery-Drama",
    "Mystery-Romance",
    "News-Talk-Show",
    "Reality-TV-Game-Show",
    "Romance-Comedy",
    "Romance-Drama",
    "Sci-Fi-Action",
    "Sci-Fi-Adventure",
    "Sci-Fi-Drama",
    "Sci-Fi-Thriller",
    "Sport-Drama",
    "Sport-Documentary",
    "Talk-Show-Comedy",
    "Talk-Show-Drama",
    "Thriller-Action",
    "Thriller-Crime",
    "Thriller-Drama",
    "War-Drama",
    "War-History",
    "Western-Action",
    "Western-Drama",
    "Western-Romance",
    # Additional genres
    "Anime",
    "Biopic",
    "Docudrama",
    "Experimental",
    "Historical",
    "Neo-Noir",
    "Superhero",
    "Survival",
    "Urban",
    "Zombie",
]
