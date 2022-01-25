from typing import List, Optional, Set

import configparser
import operator
from pathlib import Path

import requests
from user_agent import generate_user_agent

from rdf_linkchecker.checkers import CONFIG_DEFAULTS

_SESSION_HEADER = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.google.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


class Checker:
    """`requests` based link checker"""

    def __init__(self, configfile: Optional[Path] = None):
        self.config = configparser.ConfigParser()
        self.config.read_dict(CONFIG_DEFAULTS)
        if configfile:
            self.config.read(filenames=[configfile])
        self.urls: Set[str] = set()
        try:
            self.skip_domains = self.config["skip"]["domains"].split(",")
        except AttributeError:
            self.skip_domains = []
        self._session = requests.Session()
        self._session.headers.update(_SESSION_HEADER)
        self._session.headers.update({"User-Agent": generate_user_agent()})

    def _accept_url(self, url):
        for skip in self.skip_domains:
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
                with self._session.get(
                    url, timeout=int(con["timeout"]), stream=True
                ) as response:
                    try:
                        response.raise_for_status()
                        return True
                    except requests.exceptions.HTTPError:
                        return False
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
            ):
                return False

        for try_no in range(int(con["retries"]) + 1):
            if not _check():
                continue
            return True
        return False

    def check(self) -> bool:
        results = [self._check_single(u) for u in self.urls]
        if self.config["reporting"]["level"] != "none":
            self.report_results(results)
        return all(results)

    def report_results(self, results):
        rptg = self.config["reporting"]

        from rich.console import Console
        from rich.table import Table

        table = Table("URL", "Ok?", title="Checked URLs")
        for url, reachable in sorted(
            zip(self.urls, results), key=operator.itemgetter(0)
        ):
            if rptg["level"] == "all" or (
                rptg["level"] == "only-failed" and not reachable
            ):
                marker = "[green]✓[/green]" if reachable else "[red]x[/red]"
                table.add_row(url, marker)

        def _print(console):
            if table.row_count:
                console.print(table)

        if rptg["target"] != "console":
            with open(rptg["target"], "wt") as report_file:
                console = Console(file=report_file)
                _print(console)
        else:
            console = Console()
            _print(console)
