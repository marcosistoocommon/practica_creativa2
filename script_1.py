#!/usr/bin/env python

import subprocess, os

subprocess.run("git clone https://github.com/CDPS-ETSIT/practica_creativa2.git", shell=True)
subprocess.run("sudo apt update", shell=True)
subprocess.run("sudo apt install software-properties-common", shell=True)
subprocess.run("sudo add-apt-repository -y ppa:deadsnakes/ppa", shell=True)
subprocess.run("sudo apt install -y python3.9 python3.9-venv python3.9-distutils", shell=True)
os.chdir("practica_creativa2/bookinfo/src/productpage/")

subprocess.run("python3.9 -m venv venv", shell=True)
subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True)

# Edit productpage_monolith.py to add team_id environment variable
with open('productpage_monolith.py', 'r') as f:
    content = f.read()

# Add the team_id variable definition after imports
if 'team_id = os.environ.get' not in content:
    # Find a good place to insert - after the app initialization
    insert_marker = 'app = Flask(__name__)'
    content = content.replace(insert_marker, insert_marker + '\nteam_id = os.environ.get("TEAM_ID", "17")')

# Replace the render_template call to include team_id if not already there
if 'team_id=team_id' not in content:
    old_render = """    return render_template(
        'productpage.html',
        detailsStatus=detailsStatus,
        reviewsStatus=200,
        product=product,
        details=details,
        reviews={"R1":"OK"},
        user=user)"""

    new_render = """    return render_template(
        'productpage.html',
        detailsStatus=detailsStatus,
        reviewsStatus=200,
        product=product,
        details=details,
        reviews={"R1":"OK"},
        user=user,
        team_id=team_id)"""

    content = content.replace(old_render, new_render)

with open('productpage_monolith.py', 'w') as f:
    f.write(content)

# Edit productpage.html to add team_id to the title
with open('templates/productpage.html', 'r') as f:
    html_content = f.read()

# Replace the title block to include team_id
old_title = "{% block title %}Simple Bookstore App{% endblock %}"
new_title = "{% block title %} Grupo {{ team_id }}{% endblock %}"

html_content = html_content.replace(old_title, new_title)

with open('templates/productpage.html', 'w') as f:
    f.write(html_content)

os.environ['TEAM_ID'] = '17'
subprocess.run("export TEAM_ID=17 && ./venv/bin/python3.9 productpage_monolith.py 6050", shell=True)