"""
This code taken from GitHub/CodeSearchNet/src/dataextraction/python/parse_python_data.py
"""

import re
# import os
# from multiprocessing import Pool
from typing import List, NamedTuple
#
# import pandas as pd
import parso
# from docopt import docopt
# from dpu_utils.utils import RichPath, run_and_debug
# from tqdm import tqdm
#
# from dataextraction.utils import tokenize_docstring_from_string
# from utils.pkldf2jsonl import chunked_save_df_to_jsonl

from typing import List

DOCSTRING_REGEX_TOKENIZER = re.compile(r"[^\s,'\"`.():\[\]=*;>{\}+-/\\]+|\\+|\.+|\(\)|{\}|\[\]|\(+|\)+|:+|\[+|\]+|{+|\}+|=+|\*+|;+|>+|\++|-+|/+")

def tokenize_docstring_from_string(docstr: str) -> List[str]:
    return [t for t in DOCSTRING_REGEX_TOKENIZER.findall(docstr) if t is not None and len(t) > 0]

IS_WHITESPACE_REGEX = re.compile(r'\s+')

class ParsedCode(NamedTuple):
    code_tokens: List[str]
    comment_tokens: List[str]

def tokpystr(code: str,
             func_only: bool=True,
             report_errors: bool=False,
             only_ids: bool=False,
             add_keywords: bool=True) -> ParsedCode:
    """
    Tokenize Python code given a string.
    Args:
        code: The input code
        func_only: if you want to only parse functions in code.
        report_errors: Flag that turns on verbose error reporting
        only_ids: Return only the identifiers within the code
        add_keywords: Return keywords (used only when only_ids=True)
    Returns:
        Pair of lists. First list is sequence of code tokens; second list is sequence of tokens in comments.
    """
    try:
        try:
            parsed_ast = parso.parse(code, error_recovery=False, version="2.7")
        except parso.parser.ParserSyntaxError:
            parsed_ast = parso.parse(code, error_recovery=False, version="3.7")
        code_tokens, comment_tokens = [], []

        func_nodes = list(parsed_ast.iter_funcdefs())

        # parse arbitrary snippets of code that are not functions if func_only = False
        if not func_only:
            func_nodes = [parsed_ast]

        for func_node in func_nodes:  # There should only be one, but we can process more...
            doc_node = func_node.get_doc_node()
            leaf_node = func_node.get_first_leaf()
            while True:
                # Skip over the docstring:
                if leaf_node is doc_node:
                    leaf_node = leaf_node.get_next_leaf()

                # First, retrieve comment tokens:
                for prefix in leaf_node._split_prefix():
                    if prefix.type == 'comment':
                        comment_text = prefix.value[1:]  # Split off the leading "#"
                        comment_tokens.extend(tokenize_docstring_from_string(comment_text))

                # Second, stop if we've reached the end:
                if leaf_node.type == 'endmarker':
                    break

                # Third, record code tokens:
                if not(IS_WHITESPACE_REGEX.match(leaf_node.value)):
                    if only_ids:
                        if leaf_node.type == 'name':
                            code_tokens.append(leaf_node.value)
                    else:
                        if leaf_node.type == 'keyword':
                            if add_keywords:
                                code_tokens.append(leaf_node.value)
                        else:
                            code_tokens.append(leaf_node.value)
                leaf_node = leaf_node.get_next_leaf()
        return ParsedCode(code_tokens=code_tokens, comment_tokens=comment_tokens)
    except Exception as e:
        if report_errors:
            print('Error tokenizing: %s' % (e,))
            input(code)
        return ParsedCode(code_tokens=[], comment_tokens=[])
