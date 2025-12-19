#!/usr/bin/env python3
import sqlite3
import argparse
import json
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

# Initialize rich console
console = Console()

# Configuration
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
        table = Table(
            title=f"🎤 Top Artists - Last {period}",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="green",
            title_style="bold green",
            show_header=True,
            title_justify="left"
        )

        table.add_column("Rank", style="green", justify="right", width=6)
        table.add_column("Artist", style="cyan", min_width=20)
        table.add_column("Plays", style="yellow", justify="right", width=8)

        for i, (artist, plays) in enumerate(results):
            table.add_row(str(i+1), artist, str(plays))

        console.print(table)
    else:
        console.print(f"[yellow]No listening data for the last {period}[/yellow]")

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
        table = Table(
            title=f"🎵 Top Tracks - Last {period}",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="green",
            title_style="bold green",
            show_header=True
        )

        table.add_column("Rank", style="green", justify="right", width=6)
        table.add_column("Artist", style="cyan", min_width=15)
        table.add_column("Track", style="blue", min_width=25)
        table.add_column("Plays", style="yellow", justify="right", width=8)

        for i, (artist, title, plays) in enumerate(results):
            table.add_row(str(i+1), artist, title, str(plays))

        console.print(table)
    else:
        console.print(f"[yellow]No listening data for the last {period}[/yellow]")

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
        table = Table(
            title="⏰ Recently Played",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="green",
            title_style="bold green",
            show_header=True
        )

        table.add_column("Time", style="dim", width=16)
        table.add_column("Artist", style="cyan", min_width=15)
        table.add_column("Track", style="blue", min_width=20)
        table.add_column("Album", style="magenta", min_width=20)

        for timestamp, artist, title, album in results:
            time_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
            table.add_row(time_str, artist, title, album)

        console.print(table)
    else:
        console.print("[yellow]No listening history yet[/yellow]")

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

    if results:
        # Get total plays and exact artist name
        cursor.execute('''
            SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
            FROM listening_history
            WHERE LOWER(artist) LIKE LOWER(?)
        ''', (f'%{artist_name}%',))
        total_plays, first_play, last_play = cursor.fetchone()

        cursor.execute('''
            SELECT DISTINCT artist
            FROM listening_history
            WHERE LOWER(artist) LIKE LOWER(?)
            LIMIT 1
        ''', (f'%{artist_name}%',))
        exact_artist = cursor.fetchone()
        artist_display = exact_artist[0] if exact_artist else artist_name

        db.close()

        # Create artist info panel
        first_date = datetime.strptime(first_play, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y') if first_play else "Never"
        last_date = datetime.strptime(last_play, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y') if last_play else "Never"

        info_text = Text()
        info_text.append(f"Total plays: ", style="bold")
        info_text.append(f"{total_plays}\n", style="yellow")
        info_text.append(f"First play: ", style="bold")
        info_text.append(f"{first_date}\n", style="dim")
        info_text.append(f"Last play: ", style="bold")
        info_text.append(f"{last_date}", style="dim")

        console.print(Panel(info_text,
                          title=f"🎤 {artist_display}",
                          border_style="cyan",
                          width=50))

        # Create tracks table
        table = Table(
            title=f"Top {len(results)} Tracks",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="green",
            title_style="bold green",
            show_header=True
        )

        table.add_column("Rank", style="green", justify="right", width=6)
        table.add_column("Track", style="blue", min_width=30)
        table.add_column("Plays", style="yellow", justify="right", width=8)
        table.add_column("First Play", style="dim", width=12)
        table.add_column("Last Play", style="dim", width=12)

        for i, (title, plays, first, last) in enumerate(results):
            first_str = datetime.strptime(first, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') if first else ""
            last_str = datetime.strptime(last, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') if last else ""
            table.add_row(str(i+1), title, str(plays), first_str, last_str)

        console.print(table)
    else:
        console.print(f"[red]No tracks found for artist: {artist_name}[/red]")

        # Show similar artists
        cursor.execute('''
            SELECT DISTINCT artist
            FROM listening_history
            WHERE artist LIKE ?
            LIMIT 5
        ''', (f'%{artist_name}%',))

        similar = cursor.fetchall()
        if similar:
            console.print("\n[yellow]Did you mean one of these?[/yellow]")
            for artist, in similar:
                console.print(f"  • [cyan]{artist}[/cyan]")

        db.close()

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

    # Create stats table
    table = Table(
        title="📊 Listening Statistics",
        box=box.ROUNDED,
        header_style="bold cyan",
        border_style="green",
        title_style="bold green",
        show_header=False,
        show_edge=False
    )

    table.add_column("Metric", style="bold cyan", width=20)
    table.add_column("Value", style="yellow")

    table.add_row("Total Plays", str(total_plays))
    table.add_row("Unique Artists", str(unique_artists))
    table.add_row("Unique Tracks", str(unique_tracks))
    table.add_row("Top Artist", f"{top_artist} ({top_artist_plays} plays)")

    if first_last and first_last[0]:
        first_date = datetime.strptime(first_last[0], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        last_date = datetime.strptime(first_last[1], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        table.add_row("First Track", first_date)
        table.add_row("Last Track", last_date)

    console.print(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MPD Listening Statistics")
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments')

    args = parser.parse_args()

    # Handle artist-specific command
    if args.command and args.command not in ['ta', 'tt', 'rec', 'stats']:
        if len(args.args) >= 1 and args.args[0].lower() == 'tracks':
            artist_name = args.command
            try:
                limit = int(args.args[1]) if len(args.args) > 1 else 10
                artist_top_tracks(artist_name, limit)
            except ValueError:
                console.print("[red]Error: Please provide a valid number for track count[/red]")
        else:
            console.print(f"[red]Unknown command: {args.command}[/red]")
            console.print("Available commands: [cyan]top-artists[/cyan], [cyan]top-tracks[/cyan], [cyan]recent[/cyan], [cyan]stats[/cyan]")
            console.print("Or use: [cyan]<artist_name> tracks <number>[/cyan]")
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
        console.print("[cyan]Usage:[/cyan] mpd_stats.py {top-artists|top-tracks|recent|stats}")
        console.print("Or: mpd_stats.py <artist_name> tracks <number>")
        console.print("\n[bold]Examples:[/bold]")
        console.print("  mpd_stats.py 'Taylor Swift' tracks 10")
        console.print("  mpd_stats.py top-artists week")
        console.print("  mpd_stats.py top-tracks month 20")
