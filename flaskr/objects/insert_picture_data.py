import base64
import io
import uuid

import face_recognition
import numpy as np
from PIL import Image

from flaskr.models import PicturesModel, db, FacesModel, NamesModel
from flaskr.objects.update_faces import update_faces


def insert_picture_data(photo_list, user_id):
    """
    :param: photo_list as list of Photo objects
    :return: True
    This function takes the Photo objects and adds their attributes to the pictures table.
    """
    for photo in photo_list:
        data = photo.data
        town = None
        country = None
        date = None

        if hasattr(photo, 'location_addr'):
            address = photo.location_addr['address']
            # Catch all different namings for the same town data:
            if 'town' in address:
                typ = 'town'
            elif 'city' in address:
                typ = 'city'
            elif 'village' in address:
                typ = 'village'
            elif 'suburb' in address:
                typ = 'suburb'
            else:
                raise TypeError

            town = address[typ]
            country = address['country']

        if hasattr(photo, 'datetime'):
            date = photo.datetime
        entry = PicturesModel(user_id=user_id, country=country, town=town, date=date, data=data)
        db.session.add(entry)
        db.session.flush()
        image = face_recognition.load_image_file(io.BytesIO(base64.b64decode(data)))

        incoming_face_locations = face_recognition.face_locations(image)
        incoming_faces = []
        for face_location in incoming_face_locations:
            top, right, bottom, left = face_location
            face = image[top:bottom, left:right]
            incoming_faces.append(face)

        incoming_face_encodings = face_recognition.face_encodings(image, known_face_locations=incoming_face_locations)

        stored_people = db.session.query(FacesModel.person_id.distinct()).filter_by(user_id=int(user_id)).all()

        for i in range(len(incoming_face_encodings)):
            unknown_face_b64 = base64.b64encode(incoming_face_encodings[i])
            for person_id in stored_people:
                # get all the faces associated with a certain person_id
                person_face_list = FacesModel.query.filter_by(user_id=int(user_id), person_id=person_id[
                    0])  # stored_people returns tuple; unpack
                person_face_list_np = []
                for person in person_face_list:
                    person_face_list_np.append(np.frombuffer(base64.b64decode(person.data), dtype=np.float64))

                results = face_recognition.compare_faces(person_face_list_np, incoming_face_encodings[i])
                if True in results:
                    # If a match found in the faces associated to a person_id, add the face to db, with that same id

                    face = FacesModel(user_id=user_id, person_id=person_id[0], picture_id=entry.id,
                                      data=unknown_face_b64)
                    break

            # If break didn't happen (i.e no match found), add face data with new uuid4 (by default)
            rd_id = str(uuid.uuid4())
            face = FacesModel(user_id=user_id, person_id=rd_id, picture_id=entry.id, data=unknown_face_b64)
            db.session.add(face)

            # Convert face array into base64 jpeg
            img = Image.fromarray(incoming_faces[i])
            img_data = io.BytesIO()
            img.save(img_data, 'JPEG')
            img_data = base64.b64encode(img_data.getvalue())
            name = NamesModel(person_id=rd_id, picture=img_data)
            db.session.add(name)

        db.session.commit()

    update_faces(user_id)

# directory = 'C:/Users/juani/Desktop/Semester 2/PhotoGallery/flaskr/temp_images/'
# photo_list = []
# for filename in os.listdir(directory):
#     photo_list.append(Photo(directory+filename))
# #
# insert_picture_data(photo_list, 1)
