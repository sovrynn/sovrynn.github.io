from enum import Enum
import sys

"""
This is a script that converts text with some very basic (knockoff) Markdown
syntax, with limitations on nesting, into HTML code specific for my website.

Self-explanatory syntax:
  # [text] -> <h1>
  ## [text] -> <h2>
  [text] -> <p>
  `code` -> <code>

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

class WordAction(Enum):
    TEXT = 1
    LINK_SECTION = 2
    START_LINK_SECTION = 3
    END_LINK_SECTION = 4
    CODE_SECTION = 5
    START_CODE = 6
    END_CODE = 7

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

NEWLINE = "\n"

INPUT_FILENAME = "in.txt"
OUTPUT_FILENAME = "out.txt"
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
        img_name = line[1:-1]
        output = indent(output) + "<img src=\"img/" + img_name + ".png\" alt=\"" + img_name + "\">" + NEWLINE
        output = open_tag(output, TAG_P_OPEN)
        output = indent(output) + img_name + NEWLINE
        output = close_tag(output, TAG_P_CLOSE)
        output = close_tag(output, TAG_IMG_CLOSE)
    
    if state_interword != InterWordState.NONE:
        print("ERROR: You forgot to close a link or a code section.")
        print("Line: " + line)
        sys.exit()

    return output

def get_line_action(line):
    if is_empty_line(line):
        return LineAction.EMPTY_LINE
    elif line[0:2] == "# ":
        return LineAction.H1
    elif line[0:3] == "## ":
        return LineAction.H2
    elif line[0:2] == "- ":
        return LineAction.LIST_ELEMENT
    elif line[0] == "<":
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
    
    if word_action == WordAction.CODE_SECTION:
        to_append = TAG_CODE_OPEN + word[1:-1] + TAG_CODE_CLOSE \
                    if word[-1] == "`" \
                    else TAG_CODE_OPEN + word[1:-2] + TAG_CODE_CLOSE + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
    elif word_action == WordAction.LINK_SECTION:
        # We already parsed the URL and now parsing a single-word link text
        if state_interword == InterWordState.LINK:
            to_append = word[1:-1] + TAG_LINK_END \
                        if word[-1] == "]" \
                        else word[1:-2] + TAG_LINK_END + word[-1]
            (output, line_builder) = append_to_output(output, line_builder, to_append)
            state_interword = InterWordState.NONE
            state_num_indents -= 1
        # We need to add the URL to the output. Always start a new line
        else:
            output += line_builder + NEWLINE 
            output = indent(output) + TAG_LINK_START + word[1:-1] + TAG_LINK_MID + NEWLINE
            state_num_indents += 1
            line_builder = indent("")
            state_interword = InterWordState.LINK
    elif word_action == WordAction.START_CODE:
        to_append = TAG_CODE_OPEN + word[1:]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.CODE
    elif word_action == WordAction.END_CODE:
        to_append = word[:-1] + TAG_CODE_CLOSE \
                    if word[-1] == "`" \
                    else word[:-2] + TAG_CODE_CLOSE + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.NONE
    elif word_action == WordAction.START_LINK_SECTION:
        # We already parsed the URL and now parsing the link text
        to_append = word[1:]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
    elif word_action == WordAction.END_LINK_SECTION:
        # We finished parsing the link text
        to_append = word[:-1] + TAG_LINK_END \
                    if word[-1] == "]" \
                    else word[:-2] + TAG_LINK_END + word[-1]
        (output, line_builder) = append_to_output(output, line_builder, to_append)
        state_interword = InterWordState.NONE
        state_num_indents -= 1
    elif word_action == WordAction.TEXT:
        (output, line_builder) = append_to_output(output, line_builder, word)
    
    return (output, line_builder)

def get_word_action(word):
    start_code = word[0] == "`"
    end_code = word[-1] == "`" or (len(word) > 1 and word[-2] == "`")
    if start_code and end_code:
        return WordAction.CODE_SECTION
    elif start_code:
        return WordAction.START_CODE
    elif end_code:
        return WordAction.END_CODE

    start_link = word[0] == "["
    end_link = word[-1] == "]" or (len(word) > 1 and word[-2] == "]")
    if start_link and end_link:
        return WordAction.LINK_SECTION
    elif start_link:
        return WordAction.START_LINK_SECTION
    elif end_link:
        return WordAction.END_LINK_SECTION
    
    return WordAction.TEXT

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