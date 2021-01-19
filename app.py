import os

from flask import Flask, render_template, request, send_file, url_for, redirect
from flask_dropzone import Dropzone
import PyPDF4
from flask import flash
from os import listdir
from os.path import isfile, join
import shutil

basedir = os.path.abspath(os.path.dirname(__file__))

def put_watermark(input_pdf, output_pdf, watermark):
    template = PyPDF4.PdfFileReader(input_pdf)
    watermark = PyPDF4.PdfFileReader(watermark)
    output = PyPDF4.PdfFileWriter()
    for i in range(template.getNumPages()):
        page = template.getPage(i)
        page.mergePage(watermark.getPage(0))
        output.addPage(page)
    with open(output_pdf, 'wb') as file:
        output.write(file)

def eliminar_archivos(path):
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

def comprobar_envio(watermark, upfiles):
    if (watermark != "" and len(upfiles) > 0):
        if (os.path.splitext(watermark)[1] == ".pdf"):
            for file in upfiles:
                if (os.path.splitext(file)[1] != ".pdf"):
                    return False
            return True
    return False

app = Flask(__name__)
app.secret_key = "secret"
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_TIMEOUT = 5*60*1000)

dropzone = Dropzone(app)
@app.route('/',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'],f.filename))
    else:
        eliminar_archivos(os.path.join(basedir,'output/'))
        eliminar_archivos(os.path.join(basedir,'uploads/'))
        eliminar_archivos(os.path.join(basedir,'watermark/'))
        if os.path.exists(os.path.join(basedir,"resultado.zip")): os.remove(os.path.join(basedir,"resultado.zip"))
    return render_template('index.html')

@app.route('/download')
def download_file():
    p = "resultado.zip"
    return send_file(p, as_attachment=True, cache_timeout=0)

@app.route("/send", methods=['GET', 'POST'])
def send():
    if request.method == "POST":
        uploadedfiles = [f for f in listdir(os.path.join(basedir,'uploads/')) if isfile(join(os.path.join(basedir,'uploads/'), f))]
        if comprobar_envio(request.files["file"].filename,uploadedfiles):
            watermfile = request.files["file"]
            watermfile.save(os.path.join(os.path.join(basedir,"watermark/"), watermfile.filename))
            for file in uploadedfiles:
                put_watermark(os.path.join(basedir,'uploads/'+file),os.path.join(basedir,'output/watermark_' + file),os.path.join(basedir,'watermark/'+watermfile.filename))
            shutil.make_archive(os.path.join(basedir,"resultado"), 'zip', os.path.join(basedir,'output/'))
            return render_template('result.html')
    flash("Debe seleccionar una marca de agua y subir todos sus archivos en PDF")
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
