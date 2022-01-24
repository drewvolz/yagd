from typing import List, Optional

import sys
import argparse
import shutil
from rich import inspect
from rich.console import Console

from yagd.api import fetch_pull_requests

console = Console()


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

	parser.add_argument('-headers',
	                    default=False,
	                    action='store_true',
	                    help='show column headers')

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

	fetch_pull_requests(
	    console=console,
	    repos=args.repos,
	    include_reviewed=args.reviewed,
	    include_mine=args.mine,
	    show_urls=args.urls,
	    authors=args.authors,
	    show_drafts=args.drafts,
	    show_headers=args.headers,
	)

	return 0


if __name__ == '__main__':
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
