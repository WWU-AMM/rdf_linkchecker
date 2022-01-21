from typing import List, Optional, Set

import configparser
from pathlib import Path

import requests


class Checker:
    """`requests` based link checker"""

    CONFIG_DEFAULTS = {
        "connection": {"retries": 1, "timeout": 10},
        "skip": {"domains": "https://mardi4nfdi.de/,https://mardi4nfdi.de/"},
    }

    def __init__(self, configfile: Optional[Path] = None):
        self.config = configparser.ConfigParser()
        self.config.read_dict(self.CONFIG_DEFAULTS)
        if configfile:
            self.config.read(files=[configfile])
        self.urls: Set[str] = set()

    def _accept_url(self, url):
        skip_domains = self.config["skip"]["domains"].split(",")
        for skip in skip_domains:
            if skip in url:
                return False
        return True

    def add_urls(self, urls: List[str]) -> None:
        upd = {u for u in urls if self._accept_url(u)}
        self.urls.update(upd)

    def _check_single(self, url) -> bool:
        """Return True if resource request succeeded, else False

        Uses the streaming version to cut down on dl size/time
        """
        con = self.config["connection"]

        def _check():
            try:
                with requests.get(
                    url, timeout=int(con["timeout"]), stream=True
                ) as response:
                    try:
                        response.raise_for_status()
                        return True
                    except requests.exceptions.HTTPError:
                        return False
            except requests.exceptions.ConnectionError:
                return False

        for try_no in range(int(con["retries"]) + 1):
            if not _check():
                continue
            return True
        return False

    def check(self, print_results=True) -> bool:
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
