from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user

from flaskr.objects.get_user_pictures import get_user_pictures
from flaskr.objects.insert_picture_data import insert_picture_data
from flaskr.objects.photo import Photo
from flaskr.objects.merge_faces import merge_faces
from models import db, UserModel, login, PicturesModel, NamesModel, FacesModel

# Flask Configurations
app = Flask(__name__)
app.secret_key = 'xyz'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'C:/Users/juani/Desktop/Semester 2/PhotoGallery/flaskr/temp_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    else:
        return redirect(url_for('login'))


@app.route('/gallery/<category>', methods=['GET', 'POST'])
@app.route('/gallery', defaults={'category': 'date'}, methods=['GET', 'POST'])
@login_required
def gallery(category):
    if request.method == 'GET':
        # See if user has any pictures in the database. If not, communicate this to the template to display a msg.
        present = PicturesModel.query.filter_by(user_id=current_user.get_id()).first()
        if present:
            # Get the dicts to be used in the html
            picture_dict, cat_dict, sorted_keys = get_user_pictures(current_user.get_id(), category)
            # If requesting faces, also create a naming dictionary for each face based on the NamesModel
            if category == 'faces':
                names_dict = {}
                for key in sorted_keys:
                    row = NamesModel.query.filter_by(person_id=key).first()
                    names_dict[key] = (row.name, row.picture)
            else:
                names_dict = None

            # Function that splits list into n parts.
            def split(a, n):
                k, m = divmod(len(a), n)
                return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

            # divide pictures in each category in 4 groups, so it can be displayed properly on the website
            for key, val_list in cat_dict.items():
                val_list = [column for column in split(val_list, 4)]
                cat_dict[key] = val_list

            return render_template("gallery.html", cat_dict=cat_dict, pictures=picture_dict,
                                   sorted_keys=sorted_keys, names_dict=names_dict, present=True)
        else:
            return render_template('gallery.html', present=False)

    # Uploaded pictures to the website go through a post request at the gallery.
    elif request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(url_for('gallery'))

        files = request.files.getlist('files[]')
        # Create list of Photo objects based on the given jpgs
        photos = [Photo(file) for file in files if allowed_file(file.filename)]
        # Add them to the database
        insert_picture_data(photos, current_user.get_id())

        flash('File(s) successfully uploaded')

        return redirect(url_for('gallery'))


# Endpoint to change the name of a face
@app.route('/change_name', methods=['POST'])
@login_required
def rename_person():
    id = request.form['id']
    name = request.form['name']
    existing = NamesModel.query.filter_by(name=name).first()
    # If the name is not on the db, create an entry
    if existing is None:
        person = NamesModel.query.filter_by(person_id=id).first()
        person.name = name
        db.session.commit()
    # Else, merge the new face into the already named face
    else:
        merge_faces(current_user.get_id(), existing.person_id, id)
    resp = jsonify(success=True)
    return resp

# Endpoint to delete a picture from the db.
@app.route('/delete_picture', methods=['POST'])
@login_required
def delete_picture():
    id = request.form['id']
    PicturesModel.query.filter_by(id=id).delete()
    FacesModel.query.filter_by(picture_id=id).delete()
    db.session.commit()
    resp = jsonify(success=True)
    return resp

# Endpoint to delete a face from the db. Pictures remain intact
@app.route('/delete_face/<person_id>', methods=['GET'])
@login_required
def delete_face(person_id):
    NamesModel.query.filter_by(person_id=person_id).delete()
    FacesModel.query.filter_by(person_id=person_id).delete()
    db.session.commit()
    return redirect('/gallery/faces')

# Endpoint to sign up with an email, username, and password
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect('/gallery')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')

        else:
            user = UserModel(email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = False
    if current_user.is_authenticated:
        flash(f'Welcome {current_user}!')
        return redirect('/gallery')

    if request.method == 'POST':
        username = request.form['username']
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/gallery')
        else:
            return render_template('login.html', error=True)
    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')