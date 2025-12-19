#!/usr/bin/env python3
import sqlite3
import time
import os
import logging
from datetime import datetime  # CORRECT IMPORT
from mpd import MPDClient

# Configuration
DB_PATH = os.path.expanduser("~/.config/Seas/listening_history.db")
LOG_FILE = os.path.expanduser("~/.config/Seas/mpd_scrobbler.log")
MPD_HOST = "localhost"
MPD_PORT = 6600
MIN_PERCENTAGE = 50
MIN_DURATION = 30

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class MPDTracker:
    def __init__(self):
        self.client = MPDClient()
        self.db = sqlite3.connect(DB_PATH)
        self.current_track = None
        self.start_time = None
        self.last_update = time.time()
        
    def connect_mpd(self):
        try:
            self.client.connect(MPD_HOST, MPD_PORT)
            logging.info("Connected to MPD")
        except Exception as e:
            logging.error(f"Failed to connect to MPD: {e}")
            return False
        return True
    
    def track_meets_criteria(self, duration, elapsed):
        if duration <= 0:
            return False
        if duration < MIN_DURATION and elapsed >= MIN_DURATION:
            return True
        percentage = (elapsed / duration) * 100
        return percentage >= MIN_PERCENTAGE
    
    def log_track(self, song):
        try:
            cursor = self.db.cursor()
            # Get current time as string
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO listening_history 
                (timestamp, artist, album, title, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                time_str,
                song.get('artist', 'Unknown Artist'),
                song.get('album', 'Unknown Album'),
                song.get('title', 'Unknown Track'),
                int(float(song.get('duration', 0)))
            ))
            self.db.commit()
            
            artist = song.get('artist', 'Unknown Artist')
            title = song.get('title', 'Unknown Track')
            logging.info(f"Logged: {artist} - {title} at {time_str}")
            
        except Exception as e:
            logging.error(f"Failed to log track: {e}")
    
    def update_stats_cache(self):
        # ... keep your existing code here ...
        pass
    
    def run(self):
        if not self.connect_mpd():
            return
        
        logging.info("Starting MPD tracker...")
        
        try:
            while True:
                try:
                    status = self.client.status()
                    current_song = self.client.currentsong()
                    
                    if current_song and 'title' in current_song:
                        elapsed = float(status.get('elapsed', 0))
                        duration = float(current_song.get('duration', 0))
                        
                        track_id = f"{current_song.get('artist', '')}_{current_song.get('title', '')}"
                        if track_id != self.current_track:
                            if self.current_track is not None:
                                prev_elapsed = time.time() - self.start_time
                                if self.prev_duration and self.track_meets_criteria(self.prev_duration, prev_elapsed):
                                    self.log_track(self.prev_song)
                                    self.update_stats_cache()
                            
                            self.current_track = track_id
                            self.start_time = time.time()
                            self.prev_song = current_song.copy()
                            self.prev_duration = duration
                    
                    elif self.current_track and self.start_time:
                        elapsed = time.time() - self.start_time
                        if self.track_meets_criteria(self.prev_duration, elapsed):
                            self.log_track(self.prev_song)
                            self.update_stats_cache()
                            self.current_track = None
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Error in main loop: {e}")
                    time.sleep(5)
                    self.connect_mpd()
                    
        except KeyboardInterrupt:
            logging.info("Shutting down...")
        finally:
            self.client.close()
            self.db.close()

if __name__ == "__main__":
    tracker = MPDTracker()
    tracker.run()
