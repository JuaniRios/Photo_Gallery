from flaskr.models import FacesModel, db, NamesModel


def merge_faces(user_id, base_id, merging_id):
    """
    given 2 different person ids, merge them together into a single id (base_id)
    """
    NamesModel.query.filter_by(person_id=merging_id).delete()
    merging_faces = FacesModel.query.filter_by(user_id=int(user_id), person_id=merging_id)
    for face in merging_faces:
        face.person_id = base_id
    db.session.commit()


