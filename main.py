#Here we are importing all libraries that we need for our project
import datetime
import io
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from fpdf import FPDF
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)

# Secret key for sessions encryption
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return render_template("index.html", title="Image Reader")


@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():

    #In this section we are searching the number in the names of files for counting and creating new file, or it will rewrite.
    list_file=[]
    for obj in os.listdir("C:/Users/User/Desktop/Python_MA_Project"):
        if "changed-image-processing" in obj:
            list_file.append(obj)
    list_file.sort()
    obj = list_file[len(list_file)-1][24:].replace('.jpg','')
    print(obj)

    #This section for request processing
    if request.method == 'POST':
        start_time = datetime.datetime.now()

        #we are reading file from input
        image_data = request.files['file'].read()
        
        #Saving file from input for further processing
        img=Image.open(io.BytesIO(image_data))
        img_con = img.convert('RGB')
        img_con.save('uploaded-image.jpg')

        test=Image.open('uploaded-image.jpg')
        wid, hgt = test.size
        
        #Checking the size of image
        if (wid<1000 and hgt<1000):
            
            #Resing image for better detection of words
            new_test = test.resize((1250,1550), Image.ANTIALIAS)
            new_test.save(f'changed-image-processing{int(obj)+1}.jpg', dpi = (300,300))

        else:
            test.save(f'changed-image-processing{int(obj)+1}.jpg', dpi = (300,300))

        #Reading text from image
        custom_oem_psm_config = r'--oem 3 --psm 6'
        scanned_text = pytesseract.image_to_string(f'changed-image-processing{int(obj)+1}.jpg', config=custom_oem_psm_config)

        #Saving file into .txt format file
        with open(f'file{int(obj)+1}.txt', 'w', encoding='utf-8') as f:
            f.write(scanned_text)
            f.close

        #saving file as PDF file
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Times', '', 11)
        f = open(f'file{int(obj)+1}.txt', "r", encoding="latin-1")
        for x in f:
            pdf.cell(200, 10, txt = x, ln = 1, align = 'C')
        pdf.output(f'pdf_file{int(obj)+1}.pdf')

        print("Found data:", scanned_text)

        session['data'] = {
            "text": scanned_text,
            "time": str((datetime.datetime.now() - start_time).total_seconds())
        }

        return redirect(url_for('result'))


@app.route('/result')
def result():
    if "data" in session:
        data = session['data']
        return render_template(
            "result.html",
            title="Result",
            time=data["time"],
            text=data["text"],
            words=len(data["text"].split(" "))
        )
    else:
        return "Wrong request method."


if __name__ == '__main__':
    # Setup Tesseract executable path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    app.run(debug=True)
