from typing import Callable, Dict, List, Optional, Set, Tuple, Union

import typer
from omegaconf import OmegaConf
from rich import print
from rich.console import Console
from rich.progress import track

from chessli.ankify import ankify_games
from chessli.enums import PerfType, SinceEnum
from chessli.games import GamesFetcher, GamesReader
from chessli.utils import (
    convert_since_enum_to_millis,
    create_config_from_options,
    extract_context_info,
)

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context,):
    """Fetch, store, show and ankify games and mistakes"""
    ctx.params = ctx.parent.params
    print(f":fire: [blue][bold]Chessli Games[/bold][/blue] :fire:", end="\n\n")


@app.command()
def ls(
    ctx: typer.Context,
    perf_type: Optional[List[PerfType]] = typer.Option(
        None, help="Filter games to the selected `perf_types`"
    ),
):
    """List your games"""
    chessli_paths, cli_config = extract_context_info(ctx)

    games_reader = GamesReader(chessli_paths, cli_config)
    games_reader.ls()


@app.command()
def fetch(
    ctx: typer.Context,
    verbose: int = typer.Option(
        1, "--verbose", "-v", count=True, help="Select the verbosity level"
    ),
    perf_type: Optional[List[PerfType]] = typer.Option(
        None, help="Filter fetching of games to the selected `perf_types`"
    ),
    since_enum: SinceEnum = typer.Option(
        SinceEnum.last_time,
        "--since",
        help="Filter fetching of games to those played since `since`",
    ),
    max: Optional[int] = typer.Option(30, help="Limit fetching of games to `max`",),
    store: bool = typer.Option(False, help="Select if fetched games should be stored"),
):
    """Fetch games from lichess and optionally store them"""
    chessli_paths, cli_config = extract_context_info(ctx)

    cli_config["since_millis"] = convert_since_enum_to_millis(
        since_enum, chessli_paths.user_config.last_fetch_time
    )

    games_fetcher = GamesFetcher(chessli_paths, cli_config)
    new_games = games_fetcher.fetch_games()


@app.command()
def ankify(
    ctx: typer.Context,
    new_games_only: bool = typer.Option(
        True, help="Fetch new games and only ankify those"
    ),
    since_enum: SinceEnum = typer.Option(
        SinceEnum.last_time,
        "--since",
        help="Filter fetching of games to those played since `since`",
    ),
    max: Optional[int] = typer.Option(30, help="Limit fetching of games to `max`",),
    perf_type: Optional[List[PerfType]] = typer.Option(
        None, help="Filter fetching of games to the selected `perf_types`"
    ),
    export_only: bool = typer.Option(
        True,
        "--export-only/--directly",
        help="Select to only export the created anki cards",
    ),
):
    """Parse your games to find mistakes and create Anki cards"""

    chessli_paths, cli_config = extract_context_info(ctx)
    cli_config["since_millis"] = convert_since_enum_to_millis(
        since_enum, chessli_paths.user_config.last_fetch_time
    )

    if new_games_only:
        games = GamesFetcher(chessli_paths, cli_config).fetch_games()
    else:
        games = GamesReader(chessli_paths, cli_config).games

    ankify_games(games=games, export_only=export_only, chessli_paths=chessli_paths)


if __name__ == "__main__":
    app()
