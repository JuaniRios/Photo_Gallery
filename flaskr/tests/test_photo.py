import pytest
from flaskr.objects.photo import Photo
folder = "C:/Users/juani/Desktop/Semester 2/Programming II/PROJECT II/Testing_Pics/"


@pytest.mark.parametrize('inp, out', [
    (folder + 'juan1.jpg', ('29/11/2020 22:29', ('48.4094', '15.6180'))),
    (folder + 'juan-kathi7.jpg', ('27/03/2021 14:11', ('48.1989', '16.3708'))),
    (folder + 'juan2.jpg', ('02/02/2021 16:56', ('48.0524', '16.2927'))),
    (folder + 'rocio1.jpg', (None, None)),
    (folder + 'object1.jpg', ('14/09/2019 13:38', ('49.6677', '6.12388')))
])
def test_photo(inp, out):
    p = Photo(inp)
    date = p.datetime.strftime("%d/%m/%Y %H:%M") if hasattr(p, 'datetime') else None
    print(date)
    coor = (str(p.location_coor[0])[:7], str(p.location_coor[1])[:7]) if hasattr(p, 'location_coor') else None
    assert date == out[0]
    assert coor == out[1]
