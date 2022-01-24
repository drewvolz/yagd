from typing import TypedDict, List, Union, Optional

import sys
import subprocess
import argparse
import shutil
import json
from rich.table import Table
from rich.console import Console
from rich import inspect


class Author(TypedDict):
	login: str


class Request(TypedDict):
	number: int
	title: str
	headRefName: str
	author: Author
	url: str


console = Console()


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


def build_table(path: str, include_reviewed: bool, include_mine: bool,
                show_urls: bool, authors: List[str],
                show_drafts: bool) -> None:

	table = Table(show_header=True, header_style='bold magenta')
	table.box = None
	table.show_footer = True
	table.add_column('No.', style='green')
	table.add_column('Title', justify="left")
	table.add_column('Branch', style='cyan', justify="left")
	table.add_column('Author')

	urls_query: Union[List[str], str] = ''
	state = ['state:open']
	filtered_authors = build_filter_authors(authors)

	if show_urls:
		table.add_column('Url', style='blue')
		urls_query = ['--json', 'url'] if show_urls else ''

	if include_reviewed:
		state.append('-reviewed-by:@me')

	if include_mine:
		state.append('-author:@me')

	run = [
	    'gh', 'pr', 'list', '--search', ''.join(state), '--json', 'number',
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

		console.print(f'Found {len(table.rows)} results for {path}')
		console.print(table)
	else:
		console.print(f'Found 0 results for {path}\n')


def fetch_pull_requests(repos: List[str], include_reviewed: bool,
                        include_mine: bool, show_urls: bool,
                        authors: List[str], show_drafts: bool) -> None:
	try:
		with console.status(f'[bold green]Fetching pull requests…') as status:

			while repos:
				build_table(repos.pop(0), include_reviewed, include_mine,
				            show_urls, authors, show_drafts)
	except Exception as e:
		console.print(e, style='bold red')


def main(sys_args: Optional[List[str]] = None) -> int:
	if not sys_args:
		sys_args = sys.argv[1:]

	parser = argparse.ArgumentParser(
	    prog='yagd',
	    description='Visualize pull requests from multiple users.')

	parser.add_argument(
	    '-r',
	    '--repos',
	    default=[],
	    nargs='+',
	    help='<Required> paths of the repos cloned on your machine',
	    required=True)

	parser.add_argument('-reviewed',
	                    default=False,
	                    action='store_true',
	                    help='include pull requests you already reviewed')

	parser.add_argument('-mine',
	                    default=False,
	                    action='store_true',
	                    help='include pull requests created by you')

	parser.add_argument('-urls',
	                    default=False,
	                    action='store_true',
	                    help='show the pull request url')

	parser.add_argument('-authors',
	                    default=[],
	                    nargs='+',
	                    help='show pull requests by a list of users')

	parser.add_argument('-drafts',
	                    default=False,
	                    action='store_true',
	                    help='only show draft pull requests')

	parser.add_argument('-debug',
	                    default=False,
	                    action='store_true',
	                    help='enables debug logging')

	args = parser.parse_args(sys_args)

	if not args.repos:
		parser.print_help()
		sys.exit(1)

	if shutil.which('gh') is None:
		console.print(
		    'Error: Package `gh` is not installed. Run `brew install gh` or visit https://cli.github.com',
		    style='bold red')
		sys.exit(1)

	if args.debug:
		inspect(args, methods=True)

	fetch_pull_requests(repos=args.repos,
	                    include_reviewed=args.reviewed,
	                    include_mine=args.mine,
	                    show_urls=args.urls,
	                    authors=args.authors,
	                    show_drafts=args.drafts)

	return 0


if __name__ == '__main__':
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
