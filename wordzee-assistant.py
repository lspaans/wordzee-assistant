#!/usr/bin/env python3

"""A tool for assisting."""

import argparse
import logging
import os
import sys
from collections.abc import Iterable
from itertools import permutations

SCRIPT_NAME = os.path.basename(sys.argv[0])

DEBUG = False
LOG_FORMAT = "%(message)s"

MIN_NUMBER_OF_LETTERS = 1

WORDS_FILE = "/usr/share/dict/words"


def get_arguments():
    parser = argparse.ArgumentParser(prog=SCRIPT_NAME, description=__doc__)

    parser.add_argument(
        "--debug",
        default=DEBUG,
        help=f"write debug info to STDERR (default: {DEBUG})",
        action="store_true",
    )

    parser.add_argument(
        "-f",
        "--words-file",
        default=WORDS_FILE,
        help=f"alternative dictionary file (default: {WORDS_FILE})",
        metavar="FILE",
        type=argparse.FileType("r"),
    )

    parser.add_argument(
        "letters",
        help='letters (e.g."asdf")',
        metavar="LETTERS",
    )

    arguments = parser.parse_args()

    assert len(arguments.letters) >= MIN_NUMBER_OF_LETTERS

    return arguments


def get_logger(
    debug=False,
    initialize=False,
    log_format=LOG_FORMAT,
    name=__name__,
):
    logger = logging.getLogger(name)

    if not initialize:
        return logger

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(log_format))

    logger.setLevel(logging.DEBUG if debug is True else logging.INFO)

    logger.addHandler(handler)

    return logger


def get_intersection(these_words, those_words):
    assert isinstance(these_words, Iterable)
    assert isinstance(those_words, Iterable)
    return list(set(these_words) & set(those_words))


def get_unique_permutations(letters):
    assert isinstance(letters, Iterable)
    return list(
        set([
            "".join(permutation).lower()
            for permutation in permutations(letters)
        ])
    )


def get_words_from_file(file_):
    return [word.lower().rstrip() for word in file_.readlines()]


def main():
    arguments = get_arguments()
    logger = get_logger(initialize=True, debug=arguments.debug)

    code = 0

    try:
        for match in get_intersection(
            get_words_from_file(arguments.words_file),
            get_unique_permutations([char for char in arguments.letters]),
        ):
            logger.info(match)

    except KeyboardInterrupt:
        logger.info("script interrupted")
    except Exception as exc:
        logger.exception(exc)
        code = 255
    finally:
        logging.shutdown()

    return code


if __name__ == "__main__":
    sys.exit(main())
