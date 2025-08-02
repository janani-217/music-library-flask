from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

class MusicLibraryMongoDB:
    def __init__(self, db_name='music_library', collection_name='songs'):
        try:
            self.client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except pymongo.errors.ConnectionFailure as e:
            print(f"Error: Failed to connect to MongoDB server: {e}")
            self.client = None
    def add_song(self, song):
            self.collection.insert_one({
                "title": song['title'],
                "artist": song['artist'],
                "album": song['album'],
                "duration": song['duration']
            })

    def display_all_songs(self):
            return list(self.collection.find())
        
    def search_song_by_id(self, song_id):
            return self.collection.find_one({"_id": ObjectId(song_id)})
        
    def delete_song_by_id(self, song_id):
            result = self.collection.delete_one({"_id": ObjectId(song_id)})
            return result.deleted_count > 0
    
library = MusicLibraryMongoDB()

@app.route('/add_song', methods=['POST'])
def insert_song():
            song = {
                "title"   : request.form['title'],
                "artist"  : request.form['artist'],
                "album"   : request.form['album'],
                "duration": request.form['duration']
            }
            library.add_song(song)
            return redirect(url_for('index'))

@app.route('/search_by_id',methods=['GET'])
def search_by_id():
    song_id = request.args.get('song_id')
    song = library.search_song_by_id(song_id)
    return render_template('search.html',song=song)

@app.route('/delete_by_id',methods=['POST'])
def delete_by_id():
    song_id = request.form.get('song_id')
    song = library.delete_song_by_id(song_id)
    return render_template('delete.html',song=song)

@app.route('/update_song', methods=['POST'])
def update_song():
    artist = request.form['artist']
    new_title = request.form['title']
    new_album = request.form['album']
    new_duration = request.form['duration']
    
    # Update the song information in the database
    result = library.collection.update_one(
        {"artist": artist},
        {"$set": {
            "title": new_title,
            "album": new_album,
            "duration": new_duration
        }}
    )
    
    if result.modified_count > 0:
        return "Song information updated successfully."
    else:
        return "No song found with that artist."
            
@app.route('/')
def index():
    songs = library.display_all_songs()
    return render_template('index.html',songs=songs)

if __name__ == "__main__":
    app.run(debug=True)
