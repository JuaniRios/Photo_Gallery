import base64

import face_recognition
import numpy as np

from flaskr.models import db, FacesModel, NamesModel


# Some faces might not have been recognized at first. So before displaying, check if 2 person_ids are not the same person.
def update_faces(user_id):
    """
    For each person_id, get the list of all faces belonging to that id. Convert them from binary to np array.
    Then compare that list of faces, to other list of faces from a different user_id to see if there is any match.
    If there is a match, merge those 2 lists to a same user_id.
    :param user_id: relative to what user do the update
    :return: None
    """
    # Get all distinct person_id's
    stored_people = db.session.query(FacesModel.person_id.distinct()).filter_by(user_id=int(user_id)).all()
    # Go through each id
    for i in range(len(stored_people)):
        if i > len(stored_people)-1:
            break
        # Get all pictures associated with one id
        person1_face_list = FacesModel.query.filter_by(user_id=int(user_id), person_id=stored_people[i][0])  # stored_people returns tuple; unpack

        # Convert from base64 to np array
        person1_face_list_np = []
        for person in person1_face_list:
            person1_face_list_np.append(np.frombuffer(base64.b64decode(person.data), dtype=np.float64))

        # Everyone else is stored_people minus the person we are currently comparing
        everyone_else = stored_people[:]
        del everyone_else[i]

        # For every id in everyone_else, do the check
        for j in range(len(everyone_else)):
            # Get all pictures associated with one id
            person2_face_list = FacesModel.query.filter_by(user_id=int(user_id), person_id=everyone_else[j][0])  # stored_people returns tuple; unpack

            # Convert each pic in the list from base64 to np array
            person2_face_list_np = []
            for person in person2_face_list:
                person2_face_list_np.append(np.frombuffer(base64.b64decode(person.data), dtype=np.float64))

            # face-recognizer can only compare a list to a single pic, so loop over the pics associated with an id.
            # if a match is found, replace all user_id's from person2 with person1's and then break the loop.
            for pic in person2_face_list_np:
                results = face_recognition.compare_faces(person1_face_list_np, pic)
                if True in results:
                    # Delete person entry in name table
                    NamesModel.query.filter_by(person_id=everyone_else[j][0]).delete()
                    # Change person_id
                    for entry in person2_face_list:
                        entry.person_id = stored_people[i][0]

                    db.session.commit()
                    break

