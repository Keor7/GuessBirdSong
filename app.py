#install: nicegui, unidecode
from nicegui import ui
import random
import os
from string import digits
from unidecode import unidecode
from difflib import SequenceMatcher

picked_song = -1
last_picked_song = -1

cats = []
nb_selected_song = 0
songs = []

#utils
def get_path_from_i(i: int):
    return str(".\SONGS\\" + songs[i][0] + "\\" + songs[i][1] + ".mp3")
def get_name_from_i(i: int): #remove digits from name
    return songs[i][1].translate(str.maketrans('', '', digits))
def get_image_path_from_i(i: int): #check for image (jpg, jpeg, png, gif), return exact bird image or standard bird image or None
    path = str(".\SONGS\\" + songs[i][0] + "\\" + get_name_from_i(i))
    path_no_number = str(".\SONGS\\" + songs[i][0] + "\\" + songs[i][1])
    if os.path.isfile(path + ".jpg"):
        return path + ".jpg"
    elif os.path.isfile(path + ".jpeg"):
        return path + ".jpeg"
    elif os.path.isfile(path + ".png"):
        return path + ".png"
    elif os.path.isfile(path + ".gif"):
        return path + ".gif"
    elif os.path.isfile(path_no_number + ".jpg"):
        return path + ".jpg"
    elif os.path.isfile(path_no_number + ".jpeg"):
        return path + ".jpeg"
    elif os.path.isfile(path_no_number + ".png"):
        return path + ".png"
    elif os.path.isfile(path_no_number + ".gif"):
        return path + ".gif"
    else:
        return None

#load songs database, wich is directories and files supposed as such :
#./SONGS/
##./SONGS/categoryA/
##./SONGS/categoryA/bird.mp3
##./SONGS/categoryA/bird.gif (optionnal)
##./SONGS/categoryB/
##./SONGS/categoryB/same bird.jpeg
##./SONGS/categoryB/same bird.mp3
##./SONGS/categoryB/same bird02.mp3
#
#SONGS:
#The mp3 filename (without extension and numbers) is the correct answer for the song.
#   Support spaces, accents and dash -, etc.
#   Numbers are ignored and not displayed.
#for example : for the file 'same bird02.mp3', the title 'same bird' is the correct answer.
#
#PICTURES:
#The mp3 filename (without extension) is the used to search for picture.
#   Valid extension are : .gif .jpg .jpeg .png
#   Supports spaces, accents and dash -, etc.
#   If no picture is found, standard picture is searched ignoring numbers in the title
#for example : for the file 'same bird02.mp3', the picture 'same bird.jpeg' will be used.
def load_songs():
    global cats, songs, nb_selected_song

    #browse folders
    with os.scandir("./SONGS") as it:
        for entry in it:
            # sub-folder = category name
            if not entry.name.startswith('.') and entry.is_dir():
                #print("dir " + entry.name)
                cats.append(entry.name)
                #app.add_media_files('/' + str(entry.name), Path('SONGS/' + str(entry.name))) #FIXME not used right now, but is it needed for online server ?
            #browse sub-folders : for any .mp3
                for e in os.scandir("./SONGS/" + entry.name):
                    if not e.name.startswith('.') and e.is_file() and e.name.endswith('.mp3'):
                        #print("file " + e.name)
                        songs.append((entry.name, e.name.split(".")[0]))
                    pass
    nb_selected_song = len(songs)

@ui.refreshable
def audio_player() -> None:
    global aplayer
    aplayer = ui.audio(get_path_from_i(picked_song), autoplay=True)

@ui.refreshable
def last_bird() -> None:
    if not last_picked_song == -1:
        with ui.column():
            #bouton
            ui.button('Réécouter ' + get_name_from_i(last_picked_song), icon='history', on_click=lambda: last_player.play())
            #player
            last_player = ui.audio(get_path_from_i(last_picked_song))
            last_player.on('play', aplayer.pause)
            aplayer.on('play', last_player.pause)
            #image
            img = get_image_path_from_i(last_picked_song)
            if not img is None:
                with ui.image(img):
                    ui.label(get_name_from_i(last_picked_song)).classes('absolute-bottom text-subtitle2 text-center')

@ui.refreshable
def display_bird_image() -> None:
    global current_bird_image
    current_bird_image = ui.image(get_image_path_from_i(picked_song)).bind_visibility_from(switch, 'value')

#TODO : Optimize me
def pick_random_song():
    global picked_song, last_picked_song
    i = random.randint(0, len(songs) - 1)
    if len(cats_select.value) <= 0 :
        ui.notify("Selectionnez au moins une catégorie !")
    elif not i == picked_song and songs[i][0] in cats_select.value:
        last_picked_song = picked_song
        picked_song = i
        #ui.notify("DEBUG : Picked " + str(picked_song) + " " + songs[i][1] + " from " + songs[i][0])
        #Charger le nouveau son et update le lecteur
        audio_player.refresh()
        last_bird.refresh()
        display_bird_image.refresh()
        switch.set_value(False)
    else:
        #ui.notify("Picked " + str(i) + ". Repicking...")
        pick_random_song()

#Accept answer, answer with no accent, allows 10% error (typo?)
# is case-insensitive, ignore spaces
def check_answer():
    user_answer = user_input.value.strip().lower()
    correct_answer = get_name_from_i(picked_song)
    if user_answer == correct_answer or unidecode(user_answer) == unidecode(correct_answer):
        ui.notify("Correct!")
    elif SequenceMatcher(None, unidecode(user_answer), unidecode(songs[picked_song][1])).ratio() >= 0.9:
        ui.notify("~Correct! (" + correct_answer +')')
    else:
        ui.notify("La réponse était '" + correct_answer +'"')
    user_input.value = ''
    pick_random_song()

def cats_update():
    global nb_selected_song
    nb_selected_song = len(cats)
    nb_selected_song_label.text = str(nb_selected_song) + " chants sélectionnés"
    pick_random_song()

#Loadings...
load_songs()
#Display Categories
with ui.row():
    cats_select = ui.select(cats, multiple=True, value=cats, label='Catégories', on_change=cats_update).classes('w-64').props('use-chips')
    nb_selected_song_label = ui.label(str(nb_selected_song) + " chants sélectionnés")
ui.separator()

#Display game
with ui.row():
    with ui.column():
        #Generate audio player
        aplayer = audio_player()

        #Get user input
        user_input = ui.input(label='Qui chante?').on('keydown.enter', check_answer)
        with user_input.add_slot('append'):
            ui.button(icon='quiz', on_click=check_answer)

        #Switch for clue
        switch = ui.switch('Indice')
        current_bird_image = display_bird_image()

    #section for last bird with : button, player and picture if any
    last_bird_section = last_bird()

# pick random song and start playing
pick_random_song()

#just a fancy favicon
icon = 'data:image/png;base64,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'

ui.run(title='Bird song Guesser', favicon=icon, reload=True, show=False)