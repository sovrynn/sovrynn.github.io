from bs4 import BeautifulSoup
from datetime import datetime

# Read values from "input-values.txt"
with open("input-values.txt", "r") as input_values_file:
    input_values = input_values_file.read().splitlines()

if len(input_values) < 3:
    print("Not enough input values provided.")
else:
    # Read the HTML template from "template-pointer.html"
    with open("template-pointer.html", "r") as template_file:
        template_content = template_file.read()

    # Modify the HTML template based on the conditions
    template_content = template_content.replace("DATE", datetime.now().strftime("%b %d, %Y"))
    template_content = template_content.replace("TITLE", input_values[0])
    template_content = template_content.replace("BLOG-INDEX", input_values[2])

    # Read the existing content of the output HTML file
    with open(f"../pages/{input_values[1]}.html", "r") as output_file:
        output_content = output_file.read()

    # Create a BeautifulSoup object for the output content
    output_soup = BeautifulSoup(output_content, "html.parser")

    # Find the main block and insert the modified template at the start
    main_block = output_soup.find("main")
    main_block.insert(0, BeautifulSoup(template_content, "html.parser"))

    # Beautify the output HTML
    prettified_output = output_soup.prettify()

    # Write the modified output to the same file
    with open(f"../pages/{input_values[1]}.html", "w") as output_file:
        output_file.write(prettified_output)

    print("HTML file successfully updated.")
