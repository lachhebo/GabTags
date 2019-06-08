from os import walk

import musicbrainzngs as mb
from PyLyrics import *

from .moteur import Moteur
from .view import View
from .treeview import TreeView


class Data_Crawler :


    class __Data_Crawler :


        def __init__(self):
            try :
                mb.set_useragent("GabTag", version = "1.0.5", contact = "ismael.lachheb@protonmail.com")
                self.internet = True
            except :
                self.internet = False
            self.tag_finder = {}
            self.lyrics = {}
            self.view = View.getInstance()
            self.treeview = TreeView.getInstance()
            self.directory = ''


        def crawl_one_file(self,namefile, directory):
            if Moteur().check_extension(namefile) and self.internet == True :
                audio = Moteur().getFile(namefile,directory)

                tags = audio.get_tag_research()

                if tags[0] == "" and tags[1] == "" :
                    ## Either filename if no_tags
                    mzquery = self.remove_extension(namefile)
                    self.tag_finder[namefile] = self.reorder_data(mb.search_recordings(query = mzquery,limit=1))
                    self.treeview.add_crawled([namefile])
                else :
                    ## Using tags title artist and album if they are present
                    if tags[0] != "" and tags[1] != 0 :
                        try :
                            #print(" we change the value of tag finder")
                            self.tag_finder[namefile] = self.reorder_data(mb.search_recordings(recording = tags[0], artistname = tags[1],limit=1))
                            self.treeview.add_crawled([namefile])
                            #print(self.tag_finder[namefile]["title"])
                        except : ## TODO Check Internet Connection
                            pass

                    elif tags[1] == "" :
                        try :
                            self.tag_finder[namefile] = self.reorder_data(mb.search_recordings(recording = tags[0], release = tags[2],limit=1))
                            self.treeview.add_crawled([namefile])
                        except :
                            pass

                    elif tags[0] == "" :
                        try :
                            self.tag_finder[namefile] = self.reorder_data(mb.search_recordings(query = self.remove_extension(namefile), artistname = tags[1],limit=1))
                            self.treeview.add_crawled([namefile])
                        except :
                            self.treeview.add_crawled([namefile])

                    else :
                        self.treeview.add_crawled([namefile])

        def crawl_lyrics(self, namefile, directory):
            if Moteur().check_extension(namefile)  and self.internet == True :
                audio = Moteur().getFile(namefile,directory)

                tags = audio.get_tag_research()


                if tags[0]=="" or tags[1]=="" :
                    pass
                else :
                    try :
                        self.lyrics[namefile] =  PyLyrics.getLyrics(tags[1],tags[0])
                    except :
                        self.lyrics[namefile] = ""


        def update_data_crawled(self,modifications, directory):
            for namefile in modifications :
                self.treeview.remove_crawled([namefile])
                #print("we update tags :",namefile)
                if self.stop(directory):
                    break
                self.crawl_one_file(namefile,directory)
                if self.stop(directory):
                    break
                self.crawl_lyrics(namefile,directory)


        def erase_data(self):
            self.tag_finder = {}
            self.lyrics = {}

        def get_filelist(self,directory):
            self.directory = directory

            filelist = []
            for (dirpath, dirnames, filenames) in walk(directory):
                filelist.extend(filenames)
                break

            return filelist

        def get_data_from_online(self,filelist,directory):

            for namefile in filelist:
                if Moteur().check_extension(namefile) and self.internet == True  :

                    if self.stop(directory):
                        break

                    self.crawl_one_file(namefile,directory)
                    self.crawl_lyrics(namefile,directory)


                    if self.stop(directory):
                        break

        def is_finished(self,filelist):
            for namefile in filelist :
                if namefile in self.tag_finder :
                    if namefile not in self.lyrics:
                        return False
                else :
                    return False
            return True


        def stop(self, directory):
            if self.directory == directory :
                return False
            else :
                return True

        def update_directory(self,directory):
            self.directory = directory

        def get_lyrics(self,model,listiter, multiline_selected):
            if multiline_selected :
                return "No lyrics on Multiple File"
            else :
                namefile = model[listiter][0]
                if namefile in self.lyrics :
                    if self.lyrics[namefile] != "":
                        return self.lyrics[namefile]
                    else :
                        return "Lyrics not avalaible"
                else :
                    return "File not crawled yet on lyrics.wikia"

        def get_tags(self,model,listiter, multiline_selected):

            namefile = model[listiter][0]
            if namefile in self.tag_finder :
                candidat =  self.tag_finder[namefile].copy()
            else :
                return { "title":"", "artist":"", "album":"", "track":"", "year":"", "genre":"", "cover":""}


            if multiline_selected == 1 :
                 for i in range(1,len(listiter)):
                    beta = model[listiter[i]][0]
                    if beta in self.tag_finder :
                        for tagi in ["artist","album","year","genre","cover"] :
                            if candidat[tagi] != self.tag_finder[beta][tagi] :
                                candidat[tagi] = ""
                        candidat["title"] = ""
                        candidat["track"] = ""


            return candidat

        def reorder_data(self,mzdata):
            '''
            take a bunch of data from mz and make it in the form { title = , ...}
            '''

            dictionnary = {
                "title":"",
                "artist": "",
                "genre":"",
                "cover":"",
                "album":"",
                "track":"",
                "year":""}

            if len(mzdata['recording-list']) >= 1 :
                dictionnary["title"]    = mzdata['recording-list'][0]['title']
                dictionnary["artist"]   = mzdata['recording-list'][0]['artist-credit'][0]["artist"]["name"]

                if 'disambiguation' in mzdata['recording-list'][0]['artist-credit'][0]["artist"]:
                    dictionnary["genre"] = mzdata['recording-list'][0]['artist-credit'][0]["artist"]["disambiguation"]
                else :
                    dictionnary["genre"] = ""

                if 'release-list' in mzdata['recording-list'][0] :
                    for i in range(len(mzdata['recording-list'][0]["release-list"])):
                        try :
                            dictionnary["cover"] = mb.get_image(mbid = mzdata['recording-list'][0]["release-list"][i]["id"],coverid = "front", size = 250)
                            if type(dictionnary) == bytes :
                                break
                        except :
                            dictionnary["cover"] = ""

                    dictionnary["album"]    = mzdata['recording-list'][0]['release-list'][0]["release-group"]["title"] #album
                    dictionnary["track"]    = mzdata['recording-list'][0]['release-list'][0]["medium-list"][0]['track-list'][0]["number"]
                    if 'date' in mzdata['recording-list'][0]['release-list'][0] :
                        dictionnary["year"] = mzdata['recording-list'][0]['release-list'][0]["date"].split("-")[0]
                    else :
                        dictionnary["year"] = ""
                else :
                    dictionnary["album"]    = ""
                    dictionnary["track"]    = ""
                    dictionnary["year"]     = ""
                    dictionnary["cover"]    = ""

            return dictionnary




        def remove_extension(self, filename):
            '''
            return the filename without the extension
            '''
            namelist = filename.split('.')
            #print(namelist)
            return namelist[0:-1]




    __instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if Data_Crawler.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Data_Crawler.__instance = Data_Crawler.__Data_Crawler()


    @staticmethod
    def getInstance():
        """ Static access method. """
        if Data_Crawler.__instance == None:
            Data_Crawler()
        return Data_Crawler.__instance
