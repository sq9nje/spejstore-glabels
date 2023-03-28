from fastapi import FastAPI
import requests
import tempfile
import os

SPEJSTORE_URL = os.getenv('SPEJSTORE_URL', "http://marconi:8000/")
SPEJSTORE_PRINTER = os.getenv('SPEJSTORE_PRINTER',"TLP2844")
SPEJSTORE_TEMPLATE_DIR = os.getenv('SPEJSTORE_TEMPLATE_DIR',"/app/templates/")

def get_label_details(label_id):
    r = requests.get("{}api/1/labels/{}".format(SPEJSTORE_URL, label_id))
    return r.json()


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/1/preview/{label_id}.pdf")
async def preview_labe(label_id):
    label = get_label_details(label_id)
    label_template = "{}{}.glabels".format(SPEJSTORE_TEMPLATE_DIR, label['style']['description'])
    csv = tempfile.NamedTemporaryFile(prefix="spejstore_")
    try:
        csv.write("name,description,url")
        csv.write("{},{},{}{}".format(label['item']['name'], label['item']['description'], SPEJSTORE_URL, label['item']['name']))
        glabels_command = "glabels-3-batch -i {} -o {}.pdf {}".format(csv.name, csv.name, label_template)
        os.system(glabels_command)
    finally:
        csv.close()

@app.post("/api/1/print/{label_id}")
async def print_label(label_id):
    label = get_label_details(label_id)
    label_template = "{}{}.glabels".format(SPEJSTORE_TEMPLATE_DIR, label['style']['description'])
    csv = tempfile.NamedTemporaryFile(prefix="spejstore_")
    try:
        csv.write("name,description,url")
        csv.write("{},{},{}{}".format(label['item']['name'], label['item']['description'], SPEJSTORE_URL, label['item']['name']))
        glabels_command = "glabels-3-batch -i {} -o {}.pdf {}".format(csv.name, csv.name, label_template)
        lpr_command = "lpr -P {} -r {}.pdf".format(SPEJSTORE_PRINTER, csv.name)
        os.system(glabels_command)
        os.system(lpr_command)
    finally:
        csv.close()


