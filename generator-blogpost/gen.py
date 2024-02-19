import subprocess

# TEMPLATE for input-values.txt
# 1. Title
# 2. Name of the topic/navbar page in lowercase (ex: bitcoin, macro)
# 3. 4-digit blog post number (ex: 0091)

# Run the "gencontent.py" script
subprocess.run(["python3", "gencontent.py"])

# Run the "genblog.py" script
subprocess.run(["python3", "genblog.py"])

# Run the "genblogentry.py" script
subprocess.run(["python3", "genblogentry.py"])
