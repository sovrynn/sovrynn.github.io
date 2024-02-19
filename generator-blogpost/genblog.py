import os
import datetime
from bs4 import BeautifulSoup

# Read values from input.txt
with open("input-values.txt", "r") as input_file:
    values = input_file.read().splitlines()

# Check if the output folder already exists in the parent directory's "blog" directory
parent_directory = os.path.dirname(os.getcwd())  # Get the parent directory
output_folder = values[2]
output_path = os.path.join(parent_directory, "blog", output_folder)

# if os.path.exists(output_path):
#     raise Exception(f"Error: Output folder '{output_folder}' already exists in the 'blog' directory.")

# Create the output folder within the "blog" directory
os.mkdir(output_path)

# Read the HTML template
with open("template.html", "r") as template_file:
    template = template_file.read()

# Replace placeholders in the template
template = template.replace("TITLE", values[0])
template = template.replace("DATE", datetime.datetime.now().strftime("%B %d, %Y"))
template = template.replace("SECTION", values[1])

# Read HTML content from content.html
with open("content.html", "r") as content_file:
    content = content_file.read()

# Replace the CONTENT placeholder in the template with the content
template = template.replace("CONTENT", content)

# Create a BeautifulSoup object to prettify the output
soup = BeautifulSoup(template, 'html.parser')
pretty_html = soup.prettify()

# Write the beautified HTML to the index.html file in the output folder
with open(os.path.join(output_path, "index.html"), "w") as output_file:
    output_file.write(pretty_html)

print("HTML file generated and beautified successfully in the 'blog' directory.")
