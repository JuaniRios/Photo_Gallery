from datetime import date as ddate, datetime
import base64
from flaskr.models import PicturesModel, db, FacesModel
from PIL import Image
import numpy as np


def get_user_pictures(user_id, category):
    """
    Get all the pictures from a given user, and return them ordered by the given category
    """
    picture_dict = {}
    faces_dict = {}
    country_dict = {}
    town_dict = {}
    date_dict = {}

    pictures = PicturesModel.query.filter_by(user_id=user_id).all()

    unknown_date = False
    for picture in pictures:
        picture_dict[picture.id] = picture.data

        if picture.town is not None:
            town = town_dict.setdefault(picture.town, [])
            town.append(picture.id)
        else:
            town = town_dict.setdefault('Unknown', [])
            town.append(picture.id)

        if picture.country is not None:
            country = country_dict.setdefault(picture.country, [])
            country.append(picture.id)
        else:
            country = country_dict.setdefault('Unknown', [])
            country.append(picture.id)

        if picture.date is not None:
            temp = datetime.strptime(picture.date, "%Y-%m-%d %H:%M:%S")
            date = date_dict.setdefault(temp.date(), [])
            date.append(picture.id)

        else:
            unknown_date = True
            date = date_dict.setdefault(ddate(1, 1, 1), [])
            date.append(picture.id)

    sorted_countries = sorted([country for country in country_dict.keys()])
    if 'Unknown' in sorted_countries:  # move category to end of list
        i = sorted_countries.index('Unknown')
        elem = sorted_countries.pop(i)
        sorted_countries.append(elem)

    sorted_towns = sorted([town for town in town_dict.keys()])
    if 'Unknown' in sorted_countries:  # move category to end of list
        i = sorted_towns.index('Unknown')
        elem = sorted_towns.pop(i)
        sorted_towns.append(elem)

    date_pretty = {key.strftime("%A, %B %d, %Y"): val for key, val in date_dict.items()}
    sorted_dates = list(date_dict.keys())
    sorted_dates.sort(reverse=True)
    temp = [date.strftime("%A, %B %d, %Y") for date in sorted_dates]
    sorted_dates = temp
    if unknown_date:  # move unknown date category to end of list
        sorted_dates[-1] = 'Unknown'

    # Get faces and update faces_dict
    stored_people = db.session.query(FacesModel.person_id.distinct()).filter_by(user_id=int(user_id)).all()
    if len(stored_people) > 0:
        for person_id in stored_people:
            person_face_list = FacesModel.query.filter_by(user_id=int(user_id), person_id=person_id[0])
            person_pictures_id = [person.picture_id for person in person_face_list]
            for id in person_pictures_id:
                face = faces_dict.setdefault(person_id[0], [])
                face.append(id)
        sorted_faces = sorted([name for name in faces_dict.keys()])
    else:
        sorted_faces = []

    if category == 'faces':
        output_dicts = [faces_dict, sorted_faces]
    if category == 'country':
        output_dicts = [country_dict, sorted_countries]
    if category == 'town':
        output_dicts = [town_dict, sorted_towns]
    if category == 'date':
        output_dicts = [date_pretty, sorted_dates]

    return picture_dict, output_dicts[0], output_dicts[1]
