from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import base64
import pickle



class ScrumdoExtra:
    """ Interface that 'Extras' for the scrumdo site must implement.  Extras usually
        implement a connection to a third party service. """

    def getName(self):
        "Returns a user-friendly version of the name of this extra.  Generally should be just a couple words long."
        raise NotImplementedError("ScrumdoExtra subclasses must implement getName()")

    def availableFor(self, project):
        return True

    def getLogo(self):
        "Returns a URL to a logo that can be used on the config page."
        raise NotImplementedError("ScrumdoExtra subclasses must implement getLogo()")

    def getSlug(self):
        """ Returns a version of the name consisting of only letters, numbers, or dashes
            Max length, 25 chars    """
        raise NotImplementedError("ScrumdoExtra subclasses must implement getSlug()")


    def getDescription(self):
        " Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user. "
        raise NotImplementedError("ScrumdoExtra subclasses must implement getDescription()")



    def isPremium(self):
        return False




class ScrumdoProjectExtra( ScrumdoExtra ):
    "Base class for extras that should be associated with a project.  "
    requiresAdmin = True


    def associate( self, project):
        "called when an extra is first associated with a project."
        pass


    def newsItemPosted(self, project, newsItem):
        "Called when a news item is posted to a project"
        pass
        
    def unassociate( self, project):
        "called when an extra is removed from a project."
        pass

    def getShortStatus( self,  project ):
        """ Should return a string representing the current status that this extra has for a given project.
            Examples: 'Successfully synchronize on 1/1/2010' or 'Syncronization last failed' or 'Everything OK' """
        raise NotImplementedError("ScrumdoProjectExtra subclasses must implement getShortStatus()")

    def getExtraActions( self, project, **kwargs):
        """ Should return a list of tupples with a label, url, and silk icon that represent actions that a user can manually
            invoke for this extra. Example: ('Syncronize','/blah/blah/syncronize','') """
        return []
    
    def getExtraStoryActions(self, project, story):
        """ Should return a list of tupples with a label, url, silk icon, that represent actions that a user can manually
            invoke for this extra on a story. Example: ('Syncronize','/blah/blah/syncronize','') """
        return []

    def doProjectdoProjectConfiguration( self, request, project, stage=""):
        """ Should return a django style response that handles any configuration that this extra may need. 
            Stage is an optional parameter that you can use for multi step configuration sequences.  It's
            taken from the last bit of the URL /extras/extra-slug/project-slug/configure/STAGE """
        raise NotImplementedError("ScrumdoProjectExtra subclasses must implement doProjectConfiguration()")

    def initialSync( self, project):
        """ Does whatever needs doing for an initial sync of the project.
            An extra's configuration should add this event to the queue when
            it's ready.  """
        pass

    def pullProject( self, project ):
        """ Should cause a full pull syncronization of this extra from whatever external source
            there is.  This will be called on a scheduled basis for all active projects.  The project
            parameter be an apps.projects.models.Project object.    """
        pass

    # Not yet implemented...
    # def externalHook( self, request ):
    #   "Every extra gets a URL that external services can POST to.  This should handle those requests."
    #   pass


    def storyUpdated( self, project, story ):
        "Called when a story is updated in a project that this extra is associated with."
        pass

    def storyDeleted( self, project, external_id):
        """Called when a story is deleted in a project that this extra is associated with.
           Note: the ScrumDo story has already been deleted by the time this method is called. """
        pass

    def storyCreated( self, project, story):
        "Called when a story is created in a project that this extra is associated with."
        pass

    def storyStatusChange( self, project, story):
        "Called when a story's status has changed in a project that this extra is associated with."
        pass

    def getExtraHookURL( self, project ):
        """ Returns where an external site can post to, to give this extra information.
            You probably don't want to change this in subclasses. """

        current_site = Site.objects.get_current()
        return "http://" + current_site.domain + "/extras/" + self.getSlug() + "/project/" +  project.slug + "/hook"

    def storyImported(self, project, story):
        "Occurs when a user imports a story from the story queue"
        pass

    def taskUpdated(self, project, task):
        pass

    def taskDeleted(self, project, external_id):
        pass

    def taskCreated(self, project, task):
        pass

    def taskStatusChange(self, project, task):
        pass
    

