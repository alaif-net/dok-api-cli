from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True, style="bold red")


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_table(headers: list[str], rows: list[list[str]], title: str = "") -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_error(message: str) -> None:
    err_console.print(f"エラー: {message}")


def exit_with_error(message: str) -> None:
    print_error(message)
    sys.exit(1)
