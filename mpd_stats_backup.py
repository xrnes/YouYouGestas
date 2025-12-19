#!/usr/bin/env python3
import sqlite3
import argparse
import json
import os
from datetime import datetime, timedelta
from tabulate import tabulate

DB_PATH = os.path.expanduser("~/.config/Seas/listening_history.db")

def get_db():
    return sqlite3.connect(DB_PATH)

def top_artists(period='all', limit=10):
    """Get top artists for a given period"""
    db = get_db()
    cursor = db.cursor()

    period_sql = {
        'day': 'datetime("now", "-1 day")',
        'week': 'datetime("now", "-7 days")',
        'month': 'datetime("now", "-30 days")',
        'year': 'datetime("now", "-365 days")',
        'all': "'1970-01-01'"
    }.get(period, "'1970-01-01'")

    cursor.execute(f'''
        SELECT artist, COUNT(*) as play_count
        FROM listening_history
        WHERE timestamp > {period_sql}
        GROUP BY artist
        ORDER BY play_count DESC
        LIMIT ?
    ''', (limit,))

    results = cursor.fetchall()
    db.close()

    if results:
        headers = ["Rank", "Artist", "Plays"]
        table = [[i+1, artist, plays] for i, (artist, plays) in enumerate(results)]
        print(f"\nTop Artists - Last {period}:")
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print(f"No listening data for the last {period}")

def top_tracks(period='all', limit=10):
    """Get top tracks for a given period"""
    db = get_db()
    cursor = db.cursor()

    period_sql = {
        'day': 'datetime("now", "-1 day")',
        'week': 'datetime("now", "-7 days")',
        'month': 'datetime("now", "-30 days")',
        'year': 'datetime("now", "-365 days")',
        'all': "'1970-01-01'"
    }.get(period, "'1970-01-01'")

    cursor.execute(f'''
        SELECT artist, title, COUNT(*) as play_count
        FROM listening_history
        WHERE timestamp > {period_sql}
        GROUP BY artist, title
        ORDER BY play_count DESC
        LIMIT ?
    ''', (limit,))

    results = cursor.fetchall()
    db.close()

    if results:
        headers = ["Rank", "Artist", "Track", "Plays"]
        table = [[i+1, artist, title, plays] for i, (artist, title, plays) in enumerate(results)]
        print(f"\nTop Tracks - Last {period}:")
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print(f"No listening data for the last {period}")

def recent_tracks(limit=20):
    """Get recently played tracks"""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT timestamp, artist, title, album
        FROM listening_history
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))

    results = cursor.fetchall()
    db.close()

    if results:
        headers = ["Time", "Artist", "Track", "Album"]
        table = []
        for timestamp, artist, title, album in results:
            time_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
            table.append([time_str, artist, title, album])

        print("\nRecently Played:")
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("No listening history yet")

def artist_top_tracks(artist_name, limit=10):
    """Get top tracks for a specific artist"""
    db = get_db()
    cursor = db.cursor()

    # Search for artist (case-insensitive, partial match)
    cursor.execute('''
        SELECT title, COUNT(*) as play_count,
               MIN(timestamp) as first_play,
               MAX(timestamp) as last_play
        FROM listening_history
        WHERE LOWER(artist) LIKE LOWER(?)
        GROUP BY title
        ORDER BY play_count DESC
        LIMIT ?
    ''', (f'%{artist_name}%', limit))

    results = cursor.fetchall()
    db.close()

    if results:
        headers = ["Rank", "Track", "Plays", "First Play", "Last Play"]
        table = []
        for i, (title, plays, first_play, last_play) in enumerate(results):
            # Format timestamps nicely
            first_str = datetime.strptime(first_play, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') if first_play else "Never"
            last_str = datetime.strptime(last_play, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') if last_play else "Never"
            table.append([i+1, title, plays, first_str, last_str])

        # Get total plays for this artist
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT COUNT(*)
            FROM listening_history
            WHERE LOWER(artist) LIKE LOWER(?)
        ''', (f'%{artist_name}%',))
        total_plays = cursor.fetchone()[0]
        db.close()

        # Get exact artist name from first result
        if results:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT DISTINCT artist
                FROM listening_history
                WHERE LOWER(artist) LIKE LOWER(?)
                LIMIT 1
            ''', (f'%{artist_name}%',))
            exact_artist = cursor.fetchone()
            artist_display = exact_artist[0] if exact_artist else artist_name
            db.close()
        else:
            artist_display = artist_name

        print(f"\n🎵 Top tracks by {artist_display}:")
        print(f"Total plays: {total_plays}")
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print(f"No tracks found for artist: {artist_name}")

def stats_summary():
    """Show overall statistics"""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) FROM listening_history')
    total_plays = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT artist) FROM listening_history')
    unique_artists = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT title) FROM listening_history')
    unique_tracks = cursor.fetchone()[0]

    cursor.execute('''
        SELECT artist, COUNT(*) as plays
        FROM listening_history
        GROUP BY artist
        ORDER BY plays DESC
        LIMIT 1
    ''')
    top_artist_result = cursor.fetchone()
    top_artist = top_artist_result[0] if top_artist_result else "None"
    top_artist_plays = top_artist_result[1] if top_artist_result else 0

    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM listening_history')
    first_last = cursor.fetchone()

    db.close()

    print("\n📊 Listening Statistics:")
    print(f"Total Plays: {total_plays}")
    print(f"Unique Artists: {unique_artists}")
    print(f"Unique Tracks: {unique_tracks}")
    print(f"Top Artist: {top_artist} ({top_artist_plays} plays)")
    if first_last and first_last[0]:
        print(f"First Track: {first_last[0]}")
        print(f"Last Track: {first_last[1]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MPD Listening Statistics")
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments')

    args = parser.parse_args()

    # Handle artist-specific command
    if args.command and args.command not in ['ta', 'tt', 'rec', 'stats']:
        # This might be an artist name followed by "tracks N"
        if len(args.args) >= 1 and args.args[0].lower() == 'tracks':
            artist_name = args.command
            try:
                limit = int(args.args[1]) if len(args.args) > 1 else 10
                artist_top_tracks(artist_name, limit)
            except ValueError:
                print("Error: Please provide a valid number for track count")
        else:
            print(f"Unknown command: {args.command}")
            print("Available commands: ta, tt, rec, stats")
            print("Or use: <artist_name> tracks <number>")
    elif args.command == 'ta':
        period = 'all'
        limit = 10
        if args.args:
            period = args.args[0] if args.args[0] in ['day', 'week', 'month', 'year', 'all'] else 'all'
            if len(args.args) > 1:
                try:
                    limit = int(args.args[1])
                except ValueError:
                    pass
        top_artists(period, limit)
    elif args.command == 'tt':
        period = 'all'
        limit = 10
        if args.args:
            period = args.args[0] if args.args[0] in ['day', 'week', 'month', 'year', 'all'] else 'all'
            if len(args.args) > 1:
                try:
                    limit = int(args.args[1])
                except ValueError:
                    pass
        top_tracks(period, limit)
    elif args.command == 'rec':
        limit = 20
        if args.args:
            try:
                limit = int(args.args[0])
            except ValueError:
                pass
        recent_tracks(limit)
    elif args.command == 'stats':
        stats_summary()
    else:
        print("Usage: mpd_stats.py {ta|tt|rec|stats}")
        print("Or: mpd_stats.py <artist_name> tracks <number>")
        print("Examples:")
        print("  mpd_stats.py 'Taylor Swift' tracks 10")
        print("  mpd_stats.py ta week")
        print("  mpd_stats.py tt month 20")
