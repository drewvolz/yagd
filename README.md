# yagd - yet another github dashboard

Designed for visualizing open pull requests across multiple repositories and usernames.

Backed by the [gh cli] for searching and filtering, and [rich] for displaying results.

<div style="text-align:center">
  <img src='./images/screenshot.png'/>
</div>

---

Requires Python 3.6+.

```shell script
$ python3 -m venv ./venv
$ source ./venv/bin/activate # or activate.csh or activate.fish
$ pip install -r requirements-dev.txt
$ pip install -r requirements.txt
$ python3 -m yagd
```

Other commands:

## CLI

```shell script
$ python3 -m yagd --help
```

```shell script
usage: yagd [-h] -r REPOS [REPOS ...] [-reviewed] [-mine] [-urls] [-authors AUTHORS [AUTHORS ...]] [-drafts] [-debug]

Visualize pull requests from multiple users.

optional arguments:
  -h, --help            show this help message and exit
  -r REPOS [REPOS ...], --repos REPOS [REPOS ...]
                        <Required> paths of the repos cloned on your machine
  -reviewed             include pull requests you already reviewed
  -mine                 include pull requests created by you
  -urls                 show the pull request url
  -authors AUTHORS [AUTHORS ...]
                        show pull requests by a list of users
  -drafts               only show draft pull requests
  -debug                enables debug logging
```

The main CLI entry point; see `--help`.

Basic usage is as follows:

```shell script
# query multiple repositories
$ python3 -m yagd --repos <path1> <path2>

# query a single repo, filtered by a set of authors
$ python3 -m yagd --repos <path> -authors <user1> <user2>

# unfilter requests you have previously reviewed
$ python3 -m yagd -repos <path> -reviewed

# unfilter requests that you have authored
# note: -mine is overriden by -authors
$ python3 -m yagd --repos <path> -mine

# limit the scope to only draft requests
$ python3 -m yagd --repos <path> -drafts

# add the pull request url to the results
$ python3 -m yagd --repos <path> -urls

# complex usage
$ python3 -m yagd -r <repo1> <repo2> -reviewed -mine -authors <user1> <user2> -drafts -urls
```

## Misc. Scripts

```shell script
$ make
```

An overall wrapper for the below two commands
* Type checking and linting invoked with `mypy` via rules that live inside `.mypy.ini`.
* Formatting invoked via `yapf` via rules that live inside `script/format`.

```shell script
$ make format
```

Keeping things tidy.

```shell script
$ make lint
```

Keeping things type-checked and linted.

---

You may notice that there are multiple `requirements*.txt` files. They are split apart so that the dependencies install easily.

| filename                  | why                                          |
| ------------------------- | -------------------------------------------- |
| `requirements.txt`        | Common runtime dependencies                  |
| `requirements-dev.txt`    | Development dependencies – mypy, yapf, etc   |

[gh cli]: https://cli.github.com
[rich]: https://github.com/Textualize/rich
![screenshot]: ./mages/screenshot.pngØ∏