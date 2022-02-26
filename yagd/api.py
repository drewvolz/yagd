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


def build_row(table: Table, item: str, show_urls: bool, show_branch: bool,
              show_author: bool) -> None:
	data: Request = json.loads(item)
	row = [f'#{data["number"]}', data['title']]

	if show_branch:
		row.append(data['headRefName'])

	if show_author:
		row.append(data['author']['login'])

	if show_urls:
		row.append(data['url'])

	table.add_row(*row)


def fetch_authors(authors_from_teams: List[dict[str, str]]) -> List[str]:
	member_names = []

	for pair in authors_from_teams:
		org = pair['org']
		team = pair['team']

		run = ['gh', 'api', f'/orgs/{org}/teams/{team}/members']

		process = subprocess.Popen(run,
		                           stdout=subprocess.PIPE,
		                           stderr=subprocess.PIPE)
		output, errors = process.communicate()

		if (errors):
			print(f'Error in trying to run `{" ".join(run)}`')
			print(errors.decode('utf-8'))

		if len(output):
			member_names = [
			    v['login'] for v in json.loads(output.decode()) if v
			]

	return member_names


def build_author_query_string(authors: List[str]) -> Union[List[str], str]:
	contains = [f'contains("{username}")' for username in authors]
	joined = ' or '.join(contains)
	return f' | select(.author.login | {joined})'


def build_filter_authors(
        authors: List[str],
        authors_from_teams: List[dict[str, str]]) -> Union[List[str], str]:

	author_names = []

	if len(authors):
		author_names = authors

	if len(authors_from_teams):
		member_names = fetch_authors(authors_from_teams)
		author_names = [name for name in member_names]

	return build_author_query_string(author_names)


def build_table(console: Console, path: str, include_reviewed: bool,
                include_mine: bool, show_urls: bool, authors: List[str],
                authors_from_teams: List[dict[str, str]], show_drafts: bool,
                show_headers: bool, show_branch: bool,
                show_author: bool) -> None:

	table = Table(show_header=show_headers, header_style='bold magenta')
	table.box = None
	table.show_footer = True
	table.add_column('No.', style='green')
	table.add_column('Title')

	if show_branch:
		table.add_column('Branch', style='cyan')

	if show_author:
		table.add_column('Author')

	urls_query: Union[List[str], str] = ''
	state = ['state:open']
	filtered_authors = build_filter_authors(authors, authors_from_teams)

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

	if (errors):
		print(f'Error in trying to run `{" ".join(run)}`')
		print(errors.decode('utf-8'))

	if len(output):
		cleaned = [
		    v for v in json.loads(json.dumps(output.decode())).split('\n') if v
		]

		for item in cleaned:
			build_row(table, item, show_urls, show_branch, show_author)

		num_rows = len(table.rows)
		inflection = 'result' if num_rows == 1 else 'results'

		console.print(f'Found {num_rows} {inflection} for {path}')
		console.print(table)


def fetch_pull_requests(console: Console, repos: List[str],
                        include_reviewed: bool, include_mine: bool,
                        show_urls: bool, authors: List[str],
                        authors_from_teams: List[dict[str, str]],
                        show_drafts: bool, show_headers: bool,
                        show_branch: bool, show_author: bool) -> None:
	try:
		with console.status(f'[bold green]Fetching pull requests…') as status:

			while repos:
				build_table(console, repos.pop(0), include_reviewed,
				            include_mine, show_urls, authors,
				            authors_from_teams, show_drafts, show_headers,
				            show_branch, show_author)
	except Exception as e:
		console.print(e, style='bold red')
