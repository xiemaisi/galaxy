"""
API for searching Galaxy Datasets
"""
import logging, os, string, shutil, urllib, re, socket
from cgi import escape, FieldStorage
from galaxy import util, datatypes, jobs, web, util
from galaxy.web.base.controller import SharableItemSecurityMixin, BaseAPIController
from galaxy.util.sanitize_html import sanitize_html
from galaxy.model.search import GalaxySearchEngine

#from galaxy.model.orm import *
#from galaxy.model import *

log = logging.getLogger( __name__ )

class SearchController( BaseAPIController, SharableItemSecurityMixin ):

    @web.expose_api
    def create( self, trans, payload, **kwd ):
        """
        POST /api/search
        Do a search of the various elements of Galaxy.
        """
        query_txt = payload.get("query", None)
        out = []
        if query_txt is not None:
            se = GalaxySearchEngine()
            query = se.query(query_txt)
            if query is not None:
                current_user_roles = trans.get_current_user_roles()
                for item in query.process(trans):
                    append = False
                    if trans.user_is_admin(): 
                        append = True
                    if not append:
                        if type( item ) in ( trans.app.model.LibraryFolder, trans.app.model.LibraryDatasetDatasetAssociation, trans.app.model.LibraryDataset ):
                            if (trans.app.security_agent.can_access_library_item( trans.get_current_user_roles(), item, trans.user ) ):
                                append = True
                    if not append:
                        if hasattr(row, 'dataset'):
                            if trans.app.security_agent.can_access_dataset( current_user_roles, row.dataset ):
                                append = True
                    if append:
                        row = query.item_to_api_value(item)
                        out.append( self.encode_all_ids( trans, row) )
        return out
