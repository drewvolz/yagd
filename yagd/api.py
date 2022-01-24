from typing import TypedDict, List, Union

import subprocess
import json
from rich.table import Table
from rich.console import Console


class Author(TypedDict):
	login: str


class Request(TypedDict):
	number: int
	title: str
	headRefName: str
	author: Author
	url: str


def build_row(table: Table, item: str, showUrls: bool) -> None:
	data: Request = json.loads(item)
	row = [
	    f'#{data["number"]}', data['title'], data['headRefName'],
	    data['author']['login']
	]

	row.append(data['url']) if showUrls else row
	table.add_row(*row)


def build_filter_authors(authors: List[str]) -> Union[List[str], str]:
	if len(authors):
		contains = [f'contains("{username}")' for username in authors]
		joined = ' or '.join(contains)
		return f' | select(.author.login | {joined})'
	else:
		return ''


def build_table(console: Console, path: str, include_reviewed: bool,
                include_mine: bool, show_urls: bool, authors: List[str],
                show_drafts: bool, show_headers: bool) -> None:

	table = Table(show_header=show_headers, header_style='bold magenta')
	table.box = None
	table.show_footer = True
	table.add_column('No.', style='green')
	table.add_column('Title')
	table.add_column('Branch', style='cyan')
	table.add_column('Author')

	urls_query: Union[List[str], str] = ''
	state = ['state:open']
	filtered_authors = build_filter_authors(authors)

	if show_urls:
		table.add_column('Url', style='blue')
		urls_query = ['--json', 'url'] if show_urls else ''

	if not include_reviewed:
		state.append('-reviewed-by:@me')

	if not include_mine:
		state.append('-author:@me')

	run = [
	    'gh', 'pr', 'list', '--search', ' '.join(state), '--json', 'number',
	    '--json', 'title', *urls_query, '--json', 'author', '--json',
	    'headRefName', '--jq', f'(.[] {filtered_authors})'
	]

	if show_drafts:
		run.append('--draft')

	process = subprocess.Popen(run,
	                           cwd=path,
	                           stdout=subprocess.PIPE,
	                           stderr=subprocess.PIPE)

	output, errors = process.communicate()

	if len(output):
		cleaned = [
		    v for v in json.loads(json.dumps(output.decode())).split('\n') if v
		]

		for item in cleaned:
			build_row(table, item, show_urls)

		num_rows = len(table.rows)
		inflection = 'result' if num_rows == 1 else 'results'

		console.print(f'Found {num_rows} {inflection} for {path}')
		console.print(table)
	else:
		console.print(f'Found 0 results for {path}\n')


def fetch_pull_requests(console: Console, repos: List[str],
                        include_reviewed: bool, include_mine: bool,
                        show_urls: bool, authors: List[str], show_drafts: bool,
                        show_headers: bool) -> None:
	try:
		with console.status(f'[bold green]Fetching pull requests…') as status:

			while repos:
				build_table(console, repos.pop(0), include_reviewed,
				            include_mine, show_urls, authors, show_drafts,
				            show_headers)
	except Exception as e:
		console.print(e, style='bold red')
