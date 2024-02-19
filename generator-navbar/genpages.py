import os
from bs4 import BeautifulSoup

# Read words from the input file
with open("in.txt", "r") as file:
    words = file.read().splitlines()

# Get the parent directory
parent_directory = os.path.dirname(os.getcwd())
pages_directory = os.path.join(parent_directory, "pages")  # Path to the "pages" subdirectory

# Get a list of HTML filenames in the "pages" subdirectory
html_filenames = [filename for filename in os.listdir(pages_directory) if filename.endswith(".html")]

# Iterate through HTML files in the "pages" subdirectory
for filename in html_filenames:
    file_path = os.path.join(pages_directory, filename)

    with open(file_path, "r") as file:
        # Parse the HTML using Beautiful Soup
        soup = BeautifulSoup(file, 'html.parser')

        # Find the nav block and replace its content
        nav_block = soup.find('nav')
        if nav_block:
            nav_block.clear()  # Clear the existing content

            # Add the hardcoded "Home" link
            home_link = soup.new_tag("a", href="../index.html", **{"class": "navbutton"})
            home_link.string = "Home"
            nav_block.append(home_link)
            nav_block.append('\n')  # Add a newline after the "Home" link

            for word in words:
                # Convert the word to lowercase and replace spaces with underscores
                word_lower = word.lower()
                word_link = word_lower.replace(" ", "_") + ".html"
                if word_link == filename:
                    # Add the "selected-navbar-link" property if there is a match
                    link = soup.new_tag("a", href=word_link, **{"class": "navbutton selected-navbar-link"})
                    link.string = word
                    nav_block.append(link)
                else:
                    link = soup.new_tag("a", href=word_link, **{"class": "navbutton"})
                    link.string = word
                    nav_block.append(link)
                nav_block.append('\n')  # Add a newline after each link

        # Save the modified HTML back to the file
        with open(file_path, "w") as file:
            file.write(soup.prettify())
