import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogVideoList
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogTVShowInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmcgui.WindowXMLDialog.__init__(self)
        tmdb_id = kwargs.get('id')
        dbid = kwargs.get('dbid')
        imdb_id = kwargs.get('imdbid')
        if tmdb_id:
            self.tmdb_id = tmdb_id
        elif dbid and (int(dbid) > -1):
            self.tmdb_id = GetImdbIDFromDatabase("tvshow", dbid)
            log("IMDBId from local DB:" + str(self.tmdb_id))
        elif imdb_id:
            self.tmdb_id = GetMovieDBID(imdb_id)
        elif self.name:
            self.tmdb_id = search_movie(kwargs.get('name'))
        else:
            self.tmdb_id = ""
        if self.tmdb_id:
            self.tvshow, actors, crew, similar_shows, genres, production_companies, keywords = GetExtendedTVSHowInfo(self.tmdb_id)
            if not self.tvshow:
                self.close()
            xbmc.executebuiltin("RunScript(script.toolbox,info=blur,id=%s,radius=20,prefix=movie)" % self.tvshow["Thumb"])
            self.youtube_vids = GetYoutubeSearchVideosV3(self.tvshow["Title"], "", "relevance", 15)
            self.set_listitems = []
            self.youtube_listitems = CreateListItems(self.youtube_vids, 0)
            passHomeDataToSkin(self.tvshow, "tvshow.", True, True)
        else:
            Notify("No ID found")
            self.close()
        self.actor_listitems = CreateListItems(actors, 0)
        self.crew_listitems = CreateListItems(crew, 0)
        self.similar_shows_listitems = CreateListItems(similar_shows, 0)
        # self.list_listitems = CreateListItems(lists, 0)
        self.studio_listitems = CreateListItems(production_companies, 0)
        # self.releases_listitems = CreateListItems(releases, 0)
        self.genre_listitems = CreateListItems(genres, 0)
        self.keyword_listitems = CreateListItems(keywords, 0)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        self.getControl(50).addItems(self.actor_listitems)
        self.getControl(150).addItems(self.similar_shows_listitems)
        # self.getControl(250).addItems(self.set_listitems)
        self.getControl(350).addItems(self.youtube_listitems)
        # self.getControl(450).addItems(self.list_listitems)
        self.getControl(550).addItems(self.studio_listitems)
        # self.getControl(650).addItems(self.releases_listitems)
        self.getControl(750).addItems(self.crew_listitems)
        self.getControl(850).addItems(self.genre_listitems)
        self.getControl(950).addItems(self.keyword_listitems)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlID):
        homewindow.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [50, 750]:
            actorid = self.getControl(controlID).getSelectedItem().getProperty("id")
            AddToWindowStack("tvshow", self.tmdb_id)
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % __addonname__, __cwd__, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [150]:
            tmdb_id = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            AddToWindowStack("tvshow", self.tmdb_id)
            dialog = DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=tmdb_id)
            dialog.doModal()
        elif controlID == 350:
            listitem = self.getControl(350).getSelectedItem()
            self.close()
            PlayTrailer(listitem.getProperty("youtube_id"))
        elif controlID == 550:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            studioitems = GetCompanyInfo(self.getControl(controlID).getSelectedItem().getProperty("id"))
            AddToWindowStack("video", self.tmdb_id)
            self.close()
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=studioitems)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 950:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            keywordid = self.getControl(controlID).getSelectedItem().getProperty("id")
            keyworditems = GetMoviesWithKeyword(keywordid)
            AddToWindowStack("video", self.tmdb_id)
            self.close()
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=keyworditems)
            dialog.doModal()
        elif controlID == 850:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            genreid = self.getControl(controlID).getSelectedItem().getProperty("id")
            genreitems = GetMoviesWithGenre(genreid)
            AddToWindowStack("video", self.tmdb_id)
            self.close()
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=genreitems)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        # elif controlID == 650:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     country = self.getControl(controlID).getSelectedItem().getProperty("iso_3166_1")
        #     certification = self.getControl(controlID).getSelectedItem().getProperty("certification")
        #     cert_items = GetMoviesWithCertification(country, certification)
        #     AddToWindowStack("video", self.tmdb_id)
        #     self.close()
        #     dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=cert_items)
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     dialog.doModal()
        # elif controlID == 450:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     list_items = GetMoviesFromList(self.getControl(controlID).getSelectedItem().getProperty("id"))
        #     self.close()
        #     AddToWindowStack("video", self.tmdb_id)
        #     dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=list_items)
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     dialog.doModal()

    def onFocus(self, controlID):
        pass