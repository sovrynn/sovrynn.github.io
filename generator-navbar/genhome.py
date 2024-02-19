import os
from bs4 import BeautifulSoup

# Read words from the input file
with open("in.txt", "r") as file:
    words = file.read().splitlines()

# Specify the directory where HTML pages will be located
html_directory = "pages"

# Generate HTML links
html_links = ""
for word in words:
    # Convert the word to lowercase and replace spaces with underscores
    word_lower = word.lower()
    word_link = f"{html_directory}/{word_lower}.html"

    # Create the HTML link
    html_links += f'<a class="navbutton" href="{word_link}">{word}</a>\n'

# Add the hardcoded "Home" link to the start of the generated HTML
home_link = '<a class="navbutton selected-navbar-link" href="index.html">Home</a>\n' + html_links

# Find the path to "index.html" one directory higher
html_file_path = os.path.abspath("../index.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r") as file:
        # Parse the HTML using Beautiful Soup
        soup = BeautifulSoup(file, 'html.parser')

        # Find the nav block and replace its content
        nav_block = soup.find('nav')
        if nav_block:
            nav_block.clear()  # Clear the existing content
            nav_block.append('\n')  # Add a newline character
            nav_block.append(BeautifulSoup(home_link, 'html.parser'))  # Add the generated HTML links

        # Save the modified HTML back to the file
        with open(html_file_path, "w") as file:
            file.write(soup.prettify())
