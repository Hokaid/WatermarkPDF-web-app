import os

from flask import Flask, render_template, request, send_file, url_for, redirect
from flask_dropzone import Dropzone
import PyPDF2
from flask import flash
from os import listdir
from os.path import isfile, join
import shutil

basedir = os.path.abspath(os.path.dirname(__file__))

def put_watermark(input_pdf, output_pdf, watermark): 
    template = PyPDF2.PdfFileReader(open(input_pdf, 'rb'))
    watermark = PyPDF2.PdfFileReader(open(watermark, 'rb'))
    output = PyPDF2.PdfFileWriter()
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
        eliminar_archivos('output/')
        eliminar_archivos('uploads/')
        eliminar_archivos('watermark/')
        if os.path.exists("resultado.zip"): os.remove("resultado.zip")
    return render_template('index.html')

@app.route('/download')
def download_file():
    p = "resultado.zip"
    return send_file(p, as_attachment=True, cache_timeout=0)

@app.route("/send", methods=['GET', 'POST'])
def send():
    if request.method == "POST":
        uploadedfiles = [f for f in listdir('uploads/') if isfile(join('uploads/', f))]
        if comprobar_envio(request.files["file"].filename,uploadedfiles):
            watermfile = request.files["file"]
            watermfile.save(os.path.join("watermark/", watermfile.filename))
            for file in uploadedfiles:
                put_watermark('uploads/'+file,'output/watermark_' + file + '','watermark/'+watermfile.filename)
            shutil.make_archive('resultado', 'zip', 'output/')
            return render_template('result.html')
    flash("Debe seleccionar una marca de agua y subir todos sus archivos en PDF")
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)