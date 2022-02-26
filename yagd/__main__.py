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
	    description='Visualize pull requests across multiple repos and users.')

	parser.add_argument(
	    '-r',
	    '--repos',
	    default=[],
	    nargs='+',
	    help='<Required> paths of the repos cloned on your machine')

	parser.add_argument('-rv',
	                    '--reviewed',
	                    default=False,
	                    action='store_true',
	                    help='include pull requests you already reviewed')

	parser.add_argument('-m',
	                    '--mine',
	                    default=False,
	                    action='store_true',
	                    help='include pull requests created by you')

	parser.add_argument('-u',
	                    '--urls',
	                    default=False,
	                    action='store_true',
	                    help='show the pull request url')

	parser.add_argument('-a',
	                    '--authors',
	                    default=[],
	                    nargs='+',
	                    help='show pull requests by a list of users')

	parser.add_argument('-at',
	                    '--authors-from-teams',
	                    default=[],
	                    nargs='+',
	                    help='fetch authors from a list of github teams')

	parser.add_argument('-d',
	                    '--drafts',
	                    default=False,
	                    action='store_true',
	                    help='only show draft pull requests')

	parser.add_argument('-hd',
	                    '--headers',
	                    default=False,
	                    action='store_true',
	                    help='show column headers')

	parser.add_argument('-sb',
	                    '--show-branch',
	                    default=False,
	                    action='store_true',
	                    help='show the pull request branch')

	parser.add_argument('-sa',
	                    '--show-author',
	                    default=False,
	                    action='store_true',
	                    help='show the pull request author name')

	parser.add_argument('-db',
	                    '--debug',
	                    default=False,
	                    action='store_true',
	                    help='enables debug logging')

	parser.add_argument('-c',
	                    '--use-config',
	                    action='store_true',
	                    help='use a saved config environment')

	args = parser.parse_args(sys_args)

	if not args.repos and not args.use_config:
		parser.print_help()
		sys.exit(1)

	if shutil.which('gh') is None:
		console.print(
		    'Error: Package `gh` is not installed. Run `brew install gh` or visit https://cli.github.com',
		    style='bold red')
		sys.exit(1)

	config = {
	    'console': console,
	    'repos': args.repos,
	    'include_reviewed': args.reviewed,
	    'include_mine': args.mine,
	    'show_urls': args.urls,
	    'authors': args.authors,
	    'authors_from_teams': args.authors_from_teams,
	    'show_drafts': args.drafts,
	    'show_headers': args.headers,
	    'show_branch': args.show_branch,
	    'show_author': args.show_author,
	}

	if args.use_config:
		from config import default
		[
		    config.update({key: default.get(key)}) for key in config.keys()
		    if default.get(key)
		]

		if args.debug:
			console.print('debug config', style='bold green')
			inspect(config, methods=False)

	fetch_pull_requests(**config)

	return 0


if __name__ == '__main__':
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
