import requests


def post_photo_to_telegraph(photo):
    response = requests.post("https://telegra.ph/upload",
                             files={"file": photo})
    if response.status_code == 200:
        photo_path = response.json()[0]['src']
        photo_post_link = f"https://telegra.ph{photo_path}"
    else:
        photo_post_link = None

    return photo_post_link
