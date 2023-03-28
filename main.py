from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
import requests
import tempfile
import os

SPEJSTORE_URL = os.getenv('SPEJSTORE_URL', "http://inv.home/")
SPEJSTORE_PRINTER = os.getenv('SPEJSTORE_PRINTER',"TLP2844")
SPEJSTORE_TEMPLATE_DIR = os.getenv('SPEJSTORE_TEMPLATE_DIR',"/app/templates/")

def get_label_details(label_id):
    r = requests.get("{}api/1/labels/{}".format(SPEJSTORE_URL, label_id))
    return r.json()

def get_label_csv(label):
    label_prop_keys = ','.join(f'"{w}"' for w in label['item']['props'].keys())
    header = '"name","description","url"'
    row = '"{}","{}","{}/item/{}"'.format(label['item']['name'], label['item']['description'], SPEJSTORE_URL, label['item']['uuid'])
    if len(label_prop_keys) > 0:
        header += ',' + label_prop_keys
        row += ',' + ','.join(f'"{w}"' for w in label['item']['props'].values())
    header += '\n'
    row += '\n'
    return bytes(header+row, 'utf-8')

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
        csv.write(get_label_csv(label))
        csv.seek(0)
        filename = "{}.pdf".format(csv.name)
        glabels_command = "glabels-3-batch -i {} -o {}.pdf {}".format(csv.name, filename, label_template)
        os.system(glabels_command)
    finally:
        csv.close()
    return FileResponse(path=filename)

@app.post("/api/1/print/{label_id}")
async def print_label(label_id):
    label = get_label_details(label_id)
    label_template = "{}{}.glabels".format(SPEJSTORE_TEMPLATE_DIR, label['style']['description'])
    csv = tempfile.NamedTemporaryFile(prefix="spejstore_")
    try:
        csv.write(get_label_csv(label))
        csv.seek(0)
        glabels_command = "glabels-3-batch -i {} -o {}.pdf {}".format(csv.name, csv.name, label_template)
        lpr_command = "lp -d {} -t {} {}.pdf".format(SPEJSTORE_PRINTER, label_id, csv.name)
        os.system(glabels_command)
        os.system(lpr_command)
    finally:
        csv.close()
