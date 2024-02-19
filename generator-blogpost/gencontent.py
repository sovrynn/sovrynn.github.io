from enum import Enum
import sys

"""
This is a script that converts text with some very basic (knockoff) Markdown
syntax, with limitations on nesting, into HTML code specific for my website.

Self-explanatory syntax:
  # [text] -> <h1>
  ## [text] -> <h2>
  [text] -> <p>
  `quote` -> <quote> (adds quotation marks)
  |code| -> <code>

Lists:
  Syntax: - [text] -> <ul>
  Caveats:
    - No nesting supported (nest them yourself)
    - Only unordered lists supported (number lists yourself!)

Links:
  Syntax: [link URL] [text] -> <a href>
  Caveats:
    - The URL comes first! Makes it easier to code (matches order in HTML)
    - Space between the bracketed link URL and the text
    - Spaces within the link text is OK

Images:
  Syntax: <text> -> <img section>
  Caveats:
    - Images must be at path "img/[text].png"
    - Images must be on their own line
"""

class InterLineState(Enum):
    NONE = 1
    LIST = 2

class LineAction(Enum):
    EMPTY_LINE = 1
    TEXT = 2
    H1 = 3
    H2 = 4
    LIST_ELEMENT = 5
    IMG = 6

class InterWordState(Enum):
    NONE = 1
    LINK = 2
    CODE = 3
    QUOTE = 4

class WordAction(Enum):
    ERROR = 0
    TEXT = 1
    LINK_SECTION = 2
    START_LINK_SECTION = 3
    END_LINK_SECTION = 4
    CODE_SECTION = 5
    START_CODE = 6
    END_CODE = 7
    QUOTE_SECTION = 8
    START_QUOTE = 9
    END_QUOTE = 10

TAG_P_OPEN = "<p>"
TAG_P_CLOSE = "</p>"
TAG_H1_OPEN = "<h1>"
TAG_H1_CLOSE = "</h1>"
TAG_H2_OPEN = "<h2>"
TAG_H2_CLOSE = "</h2>"
TAG_UL_OPEN = "<ul>"
TAG_UL_CLOSE = "</ul>"
TAG_LI_OPEN = "<li>"
TAG_LI_CLOSE = "</li>"
TAG_IMG_OPEN = "<section>"
TAG_IMG_CLOSE = "</section>"
TAG_CODE_OPEN = "<code>"
TAG_CODE_CLOSE = "</code>"
TAG_LINK_START = "<a href=\""
TAG_LINK_MID = "\">"
TAG_LINK_END = "</a>"
TAG_QUOTE_OPEN = "<i>"
TAG_QUOTE_CLOSE = "</i>"

LINK_START_SYM = "["
LINK_END_SYM = "]"
QUOTE_SYM = "`"
CODE_SYM = "|"

MARKDOWN_H1 = "# "
MARKDOWN_H2 = "## "
MARKDOWN_LIST = "- "
MARKDOWN_IMG = "<"
MARKDOWN_IMG_DIVIDER = "|"

NEWLINE = "\n"

INPUT_FILENAME = "input-content.txt"
OUTPUT_FILENAME = "content.html"
LINE_LENGTH_LIMIT = 72
INDENT = 2

state_interline = InterLineState.NONE
state_interword = InterWordState.NONE
state_num_indents = 0

def main():
    input_file = open(INPUT_FILENAME, "r")
    input_lines = input_file.readlines()
    input_file.close()
    
    output = process_input(input_lines)

    output_file = open(OUTPUT_FILENAME, "w")
    output_file.write(output)
    output_file.close()

def process_input(lines):
    # always leave the output on a fresh line
    output = ""
    for line in lines:
        output = process_line(line, output)

    # close trailing lists
    global state_interline
    if state_interline == InterLineState.LIST:
        global state_num_indents
        state_num_indents -= 1
        output = indent(output) + TAG_UL_CLOSE

    return output

def process_line(line, output):
    global state_num_indents
    global state_interline
    global state_interword

    line_action = get_line_action(line)

    # Lists are the only multi-line state. May need to close it
    if state_interline == InterLineState.LIST and line_action != LineAction.LIST_ELEMENT:
        output = close_tag(output, TAG_UL_CLOSE)
        state_interline = InterLineState.NONE
    
    if line_action == LineAction.TEXT:
        line = line.strip()
        output = tag_and_process_words(output, line, TAG_P_OPEN, TAG_P_CLOSE)
    elif line_action == LineAction.H1:
        line = line[2:].strip()
        output = tag_and_process_words(output, line, TAG_H1_OPEN, TAG_H1_CLOSE)
    elif line_action == LineAction.H2:
        line = line[3:].strip()
        output = tag_and_process_words(output, line, TAG_H2_OPEN, TAG_H2_CLOSE)
    elif line_action == LineAction.LIST_ELEMENT:
        line = line[2:].strip()
        if (state_interline != InterLineState.LIST):
            state_interline = InterLineState.LIST
            output = open_tag(output, TAG_UL_OPEN)
        output = tag_and_process_words(output, line, TAG_LI_OPEN, TAG_LI_CLOSE)
    elif line_action == LineAction.IMG:
        line = line.strip()
        output = open_tag(output, TAG_IMG_OPEN)
        (filename, description) = line[1:-1].split(MARKDOWN_IMG_DIVIDER)
        output = indent(output) + "<img src=\"img/" + filename + "\" alt=\"" + description + "\">" + NEWLINE
        output = open_tag(output, TAG_P_OPEN)
        output = indent(output) + description + NEWLINE
        output = close_tag(output, TAG_P_CLOSE)
        output = close_tag(output, TAG_IMG_CLOSE)
    
    if state_interword != InterWordState.NONE:
        error(
            "ERROR: You forgot to close a link or a code section.",
            "Line: " + line
        )

    return output

def error(*messages):
    for message in messages:
        print(message)
    sys.exit()

def get_line_action(line):
    if is_empty_line(line):
        return LineAction.EMPTY_LINE
    elif line[0:2] == MARKDOWN_H1:
        return LineAction.H1
    elif line[0:3] == MARKDOWN_H2:
        return LineAction.H2
    elif line[0:2] == MARKDOWN_LIST:
        return LineAction.LIST_ELEMENT
    elif line[0] == MARKDOWN_IMG:
        return LineAction.IMG
    else:
        return LineAction.TEXT


def is_empty_line(line):
    return line == NEWLINE

def tag_and_process_words(output, line, opening_tag, closing_tag):
    output = open_tag(output, opening_tag)
    output = process_words(output, line)
    output = close_tag(output, closing_tag)
    return output

def process_words(output, line):
    words = line.split()
    # always keep this properly indented
    line_builder = indent("")
    for word in words:
        (output, line_builder) = process_word(output, line_builder, word)
    output = output + line_builder + NEWLINE
    return output

def process_word(output, line_builder, word):
    global state_interword
    global state_num_indents

    word_action = get_word_action(word)
    
    if word_action == WordAction.LINK_SECTION:
        # We already parsed the URL and now parsing a single-word link text
        if state_interword == InterWordState.LINK:
            to_append = word[1:-1] + TAG_LINK_END \
                        if word[-1] == "]" \
                        else word[1:-2] + TAG_LINK_END + word[-1]
            (output, line_builder) = append_to_output(output, line_builder, to_append)
            state_interword = InterWordState.NONE
            state_num_indents -= 1
        # We need to add the URL to the output. Always start a new line in the HTML
        else:
            # Don't go to a newline if the link is at the start of the source text line
            if len(line_builder) != state_num_indents * INDENT:
                output += line_builder + NEWLINE 
            output = indent(output) + TAG_LINK_START + word[1:-1] + TAG_LINK_MID + NEWLINE
            state_num_indents += 1
            line_builder = indent("")
            state_interword = InterWordState.LINK
    elif word_action == WordAction.START_LINK_SECTION:
        # We already parsed the URL and now parsing the link text
        to_append = word[1:]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
    elif word_action == WordAction.END_LINK_SECTION:
        # We finished parsing the link text
        to_append = word[:-1] + TAG_LINK_END \
                    if word[-1] == LINK_END_SYM \
                    else word[:-2] + TAG_LINK_END + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.NONE
        state_num_indents -= 1
    elif word_action == WordAction.CODE_SECTION:
        to_append = TAG_CODE_OPEN + word[1:-1] + TAG_CODE_CLOSE \
                    if word[-1] == CODE_SYM \
                    else TAG_CODE_OPEN + word[1:-2] + TAG_CODE_CLOSE + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
    elif word_action == WordAction.START_CODE:
        to_append = TAG_CODE_OPEN + word[1:]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        # I don't believe this is actually ever used
        state_interword = InterWordState.CODE
    elif word_action == WordAction.END_CODE:
        to_append = word[:-1] + TAG_CODE_CLOSE \
                    if word[-1] == CODE_SYM \
                    else word[:-2] + TAG_CODE_CLOSE + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.NONE
    elif word_action == WordAction.START_QUOTE:
        to_append = TAG_QUOTE_OPEN + '"' + word[1:]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        # I don't believe this is actually ever used
        state_interword = InterWordState.QUOTE
    elif word_action == WordAction.END_QUOTE:
        to_append = word[:-1] + '"' + TAG_QUOTE_CLOSE \
                    if word[-1] == QUOTE_SYM \
                    else word[:-2] + '"' + TAG_QUOTE_CLOSE + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.NONE
    elif word_action == WordAction.TEXT:
        (output, line_builder) = append_to_output(output, line_builder, word)
    elif word_action == WordAction.ERROR:
        error(word, "You've majorly screwed up")
    
    return (output, line_builder)

def get_word_action(word):
    global state_interword

    # No markdown can be nested inside of quotes (for now). Quite hacky but so be it
    if state_interword == InterWordState.QUOTE:
        if word[-1] == QUOTE_SYM or (len(word) > 1 and word[-2] == QUOTE_SYM):
            return WordAction.END_QUOTE
        else:
            return WordAction.TEXT

    return get_word_action_for_types(word,
        [
            [QUOTE_SYM, QUOTE_SYM, WordAction.ERROR, WordAction.START_QUOTE, WordAction.END_QUOTE],
            [LINK_START_SYM, LINK_END_SYM, WordAction.LINK_SECTION, WordAction.START_LINK_SECTION, WordAction.END_LINK_SECTION],
            [CODE_SYM, CODE_SYM, WordAction.CODE_SECTION, WordAction.START_CODE, WordAction.END_CODE]
        ]
    )

# Recursion is pretty
def get_word_action_for_types(word, sym_action_batches):
    if sym_action_batches == []:
        return WordAction.TEXT
    
    word_action_for_type = get_word_action_for_type(word, *sym_action_batches[0])
    return get_word_action_for_types(word, sym_action_batches[1:]) \
        if word_action_for_type is None \
        else word_action_for_type

def get_word_action_for_type(word, start_sym, end_sym, full_action, start_action, end_action):
    is_start_action = word[0] == start_sym
    # Second clause is in here for trailing parentheses or periods
    is_end_action = word[-1] == end_sym or (len(word) > 2 and word[-2] == end_sym)
    if is_start_action and is_end_action:
        return full_action
    elif is_start_action:
        return start_action
    elif is_end_action:
        return end_action
    else:
        return None

def open_tag(output, open_tag):
    global state_num_indents

    output = indent(output) + open_tag + NEWLINE
    state_num_indents += 1
    return output

def close_tag(output, close_tag):
    global state_num_indents

    state_num_indents -= 1
    output = indent(output) + close_tag + NEWLINE
    return output

def indent(text):
    global state_num_indents

    return text + state_num_indents * (" " * INDENT)

def append_to_output(output, line_builder, to_append):
    if exceeds_line_limit(line_builder, to_append):
        output += line_builder + NEWLINE
        line_builder = indent("") + to_append
    else:
        if line_builder[-1] == " ":
            line_builder += to_append
        else:
            line_builder += " " + to_append
    return (output, line_builder)

def exceeds_line_limit(line_builder, to_append):
    return len(line_builder) + len(to_append) > LINE_LENGTH_LIMIT - 1

main()