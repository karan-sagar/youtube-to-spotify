import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pytube import Playlist as pl
from pytube import YouTube
import re
import json

def get_tracks_from_youtube_playlist(playlist: str):
    
    '''Gets all tracks from the given YouTube playlist.'''
    
    tracks = [] # list to the title of the tracks 
    
    artists = [] # list of artists corresponding to the tracks
    
    playlist = pl(playlist) # initialize the playlist object
    
    urls_of_tracks = playlist.video_urls # get the url of all the tracks in the playlist 

    for item in urls_of_tracks:
        track_title = YouTube(str(item)) # get the title of all the tracks
        tracks.append(re.sub(r'\s*\([^)]*\)', '', track_title.title)) # append the titles to the song list. The regex expression get rid of brackets and anything within it. 
                                                                    # e.g. if the song is Kill Bill (Audio), only Kill Bill will be appended to the tracks list. 
        artists.append(track_title.author) # appends to artist name to the artists list 
        
    return tracks, artists


def authorize_spotify(client_id: str, client_secret: str, redirect_uri: str, scope: str):
    
    '''Authorize the Spotify Client.'''
    
    sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope) # initialize the SpotifyOAuth Object
    
    auth_url = sp_oauth.get_authorize_url() # authentication url 
    
    token_info = sp_oauth.get_access_token() # retrieve access token 
    
    sp = spotipy.Spotify(auth=token_info['access_token']) # use access token to create spotify client 
    
    print("Account Authorized ")
    
    return sp
    
    
def create_playlist(new_playlist_name:str, spotify_client):
    
    '''Creates a new playlist in the users spotify account.'''
    
    user_id = spotify_client.current_user()['id'] # get the current user Id
    
    #user_id = spotify_client.user() # get the current user Id
    
    playlist_name = new_playlist_name
    
    spotify_client.user_playlist_create(user_id, playlist_name)  # create the new playlist 
    
    print("Playlist Created")
    
    

def get_track_uri(spotify_client, artists:list, tracks:list):
    
    '''add the tracks to the spotify playlist'''
    
    track_uri_list = [] # list to add all track uri
    
    track_uri_not_found = [] # this list will contain any uri which are not found due to issues with the track title
    
    for i in range(0,len(tracks)):
        
        try: 
        
            name = spotify_client.search(q=f'track:{str(tracks[i])} artist:{str(artists[i])}', type='track', limit=1) # find the track given the song name and artist name

            #print(name)

            track_uri = name['tracks']['items'][0]['uri'] # get the uri of the track 
            
            track_uri_list.append(track_uri) # append the track uri to the track_uri_list
            
        except IndexError:
            
            track_uri_not_found.append(tracks[i]) # any tracks which were not found will get added to the track_uri_not_found list
            
    return track_uri_list

def add_tracks_to_spotify_playlist(sp,tracks_uri,playlist_name):  
    
    user_id = sp.current_user()['id'] # get the current user Id
    
    #user_id = spotify_client.user() # get the current user Id
    
    playlists = sp.user_playlists(user_id) # get all users playlists
    
    for i in range(0,len(playlists)): # for loop to iterate over all the users playlists and find the id of the playlist where we will be adding the tracks 
        if playlists["items"][i]["name"] == playlist_name:
            playlist_id = playlists["items"][i]["uri"]
    
    sp.user_playlist_add_tracks(user_id, playlist_id, tracks_uri, position= None ) # add the tracks to a playlist determined by the playlist id 
    
    
    
    
    
    

if __name__ == "__main__":
    
    sp = authorize_spotify(client_id="enter_your_client_id",
                        client_secret="enter_your_client_secret",
                        redirect_uri = "enter_your_redirect_uri",
                        scope = 'enter_your_scope',
                        )
    
    playlist_name = "Track Test" # name of the playlist to be created 
    
    create_playlist(playlist_name, sp) # creating the playlist 
    
    tracks, artists = get_tracks_from_youtube_playlist(playlist = "https://www.youtube.com/watch?v=H5v3kku4y6Q&list=PLUemwAVGSh5Y2pukyAltSukqLoY2ZZVvY") # get a list of aongs and artists from youtube. 
    
    tracks_uri = get_track_uri(sp, artists, tracks)  # the tracks uri 
    
    add_tracks_to_spotify_playlist(sp, tracks_uri, playlist_name) # add the tracks 
    
    print("Tracks Added!!!")
