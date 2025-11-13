import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from uploader import upload
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadtest', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is part of the request
        if 'file' not in request.files:
            return redirect(request.url) # No file part in the request
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        
        # print(type(file.read()))
        # Save the file if it's allowed
        try:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                id=upload(filename,file.read())
                # print(file,dir(file))
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return 'File uploaded successfully!'
        except:
            return "File Upload Failed"
    
    return render_template('upload.html')

if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=80)
    app.run(debug=True)