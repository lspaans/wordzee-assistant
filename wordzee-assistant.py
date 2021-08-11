#!/usr/bin/env python3

"""A tool for finding words for the popular Wordzee game based on a number
of letters provided as input."""

import argparse
import logging
import os
import sys
from collections.abc import Iterable
from itertools import permutations

SCRIPT_NAME = os.path.basename(sys.argv[0])

DEBUG = False
LOG_FORMAT = "%(message)s"

MIN_WORD_LENGTH = 1

WORDS_FILE = "/usr/share/dict/words"


class Error(Exception):
    pass


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
        "-m",
        "--min-word-length",
        default=MIN_WORD_LENGTH,
        help=f"minimum word length (default: {MIN_WORD_LENGTH})",
        metavar="NUM",
        type=int,
    )

    parser.add_argument(
        "letters",
        help='letters (e.g."asdf")',
        metavar="LETTERS",
    )

    arguments = parser.parse_args()

    assert len(arguments.letters) >= arguments.min_word_length

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

    intersection = set(these_words) & set(those_words)

    if len(intersection) == 0:
        raise Error("No matching words found")

    return list(intersection)


def get_unique_permutations(letters, min_word_length=MIN_WORD_LENGTH):
    assert isinstance(letters, Iterable)
    return list(
        set([
            "".join(permutation).lower()
            for length in range(min_word_length, len(letters) + 1)
            for permutation in permutations(letters, length)
        ])
    )


def get_words_from_file(file_):
    return [word.lower().rstrip() for word in file_.readlines()]


def main():
    arguments = get_arguments()
    logger = get_logger(initialize=True, debug=arguments.debug)

    code = 0

    try:
        for match in sorted(
            get_intersection(
                get_words_from_file(arguments.words_file),
                get_unique_permutations(
                    [char for char in arguments.letters],
                    arguments.min_word_length,
                ),
            ),
            key=lambda word: len(word),
            reverse=True
        ):
            logger.info(match)

    except KeyboardInterrupt:
        logger.info("script interrupted")
    except Error as exc:
        logger.error(exc)
        code = 1
    except Exception as exc:
        logger.exception(exc)
        code = 255
    finally:
        logging.shutdown()

    return code


if __name__ == "__main__":
    sys.exit(main())
