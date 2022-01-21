from typing import List, Optional, Set

import configparser
from pathlib import Path

import requests


class Checker:
    def __init__(self, configfile: Optional[Path] = None):
        self.config = configparser.ConfigParser()
        if configfile:
            self.config.read(files=[configfile])
        self.urls: Set[str] = set()

    def add_urls(self, urls: List[str]):
        self.urls.update(set(urls))

    def _check_single(self, url):
        try:
            with requests.get(url, stream=True) as response:
                try:
                    response.raise_for_status()
                    return True
                except requests.exceptions.HTTPError:
                    return False
        except requests.exceptions.ConnectionError:
            return False

    def check(self, print_results=True):
        results = [self._check_single(u) for u in self.urls]
        if not print_results:
            return all(results)

        from rich.console import Console
        from rich.table import Table

        table = Table("URL", "Ok?", title="Checked URLs")
        for url, reachable in zip(self.urls, results):
            marker = "[green]✓[/green]" if reachable else "[red]x[/red]"
            table.add_row(url, marker)
        console = Console()
        console.print(table)
