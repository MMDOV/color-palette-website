from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import os
import numpy as np
from PIL import Image
from collections import Counter

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBfdvA6OsdvsdfaeBXox7C0sKR6b'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class PicForm(FlaskForm):
    file = FileField("File to Upload:", validators=[DataRequired()])
    number = StringField("Number of colors:", validators=[DataRequired()])
    submit = SubmitField("Run")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = PicForm()
    if form.validate_on_submit():
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img = Image.open(f'static/images/{filename}')
            img = img.resize((150, 150))
            arr = np.asarray(img)
            cnt = Counter()
            for x in range(arr.shape[0]):
                for y in range(arr.shape[1]):
                    cnt[str(arr[x, y, :])] += 1
            top = cnt.most_common(int(form.number.data) * 200)
            i = 0
            color_list = []
            for _ in top:
                reformatted_color = np.fromstring(top[i][0].strip(']').strip('['), dtype=int, sep=' ')
                if i % 10 == 0 and len(color_list) <= int(form.number.data):
                    color_list.append(reformatted_color)
                i += 1
            return render_template('main.html', form=form, colors=color_list, filename=filename)
    return render_template('main.html', form=form, filename="Untitled.jpg")


if __name__ == '__main__':
    app.run(debug=True)
