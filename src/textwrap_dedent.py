# limited port of Python 3's textwrap.py module

# - textwrap.dedent() function

import re
# -- Loosely related functionality -------------------------------------
re_MULTILINE = 8 # even though multiline 

_whitespace_only_re = re.compile('^[ \t]+$', re_MULTILINE) # type: ignore
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re_MULTILINE) # type: ignore

def dedent(text):
    """Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalized to a newline character.
    """
    # Look for the longest leading string of spaces and tabs common to
    # all lines.
    margin = None
    text = _whitespace_only_re.sub('', text)
    # upy workaround
    # indents = _leading_whitespace_re.findall(text)
    lines = text.splitlines()
    indents = []
    for line in lines:
        match = _leading_whitespace_re.match(line)
        if match:
            indents.append(match.group(1))
        else:
            indents.append('')    
    # end upy workaround
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Find the largest common whitespace between current line and previous
        # winner.
        else:
            for i, (x, y) in enumerate(zip(margin, indent)):
                if x != y:
                    margin = margin[:i]
                    break

    # sanity check (testing/debugging only)
    # if 0 and margin:
    #     for line in text.split("\n"):
    #         assert not line or line.startswith(margin), \
    #                "line = %r, margin = %r" % (line, margin)

    if margin:
        l = len(margin)
        # text = re.sub(r'(?m)^' + margin, '', text)
        # upy workaround
        text = "\n".join(line[l:] for line in text.split("\n"))
        

    return text
