# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.



import cherrypy
import os.path
import datetime

from sickbeard import helpers
from sickbeard import logger
from sickbeard import naming

import sickbeard

naming_ep_type = ("%(seasonnumber)dx%(episodenumber)02d",
                  "s%(seasonnumber)02de%(episodenumber)02d",
                   "S%(seasonnumber)02dE%(episodenumber)02d",
                   "%(seasonnumber)02dx%(episodenumber)02d")
naming_ep_type_text = ("1x02", "s01e02", "S01E02", "01x02")

naming_multi_ep_type = {0: ["-%(episodenumber)02d"]*len(naming_ep_type),
                        1: [" - " + x for x in naming_ep_type],
                        2: [x + "%(episodenumber)02d" for x in ("x", "e", "E", "x")]}
naming_multi_ep_type_text = ("extend", "duplicate", "repeat")

naming_sep_type = (" - ", " ")
naming_sep_type_text = (" - ", "space")

def change_HTTPS_CERT(https_cert):

    if https_cert == '':
        sickbeard.HTTPS_CERT = ''
        return True

    if os.path.normpath(sickbeard.HTTPS_CERT) != os.path.normpath(https_cert):
        if helpers.makeDir(os.path.dirname(os.path.abspath(https_cert))):
            sickbeard.HTTPS_CERT = os.path.normpath(https_cert)
            logger.log(u"Changed https cert path to " + https_cert)
        else:
            return False

    return True

def change_HTTPS_KEY(https_key):

    if https_key == '':
        sickbeard.HTTPS_KEY = ''
        return True

    if os.path.normpath(sickbeard.HTTPS_KEY) != os.path.normpath(https_key):
        if helpers.makeDir(os.path.dirname(os.path.abspath(https_key))):
            sickbeard.HTTPS_KEY = os.path.normpath(https_key)
            logger.log(u"Changed https key path to " + https_key)
        else:
            return False

    return True

def change_LOG_DIR(log_dir):

    if os.path.normpath(sickbeard.LOG_DIR) != os.path.normpath(log_dir):
        if helpers.makeDir(log_dir):
            sickbeard.LOG_DIR = os.path.normpath(log_dir)
            logger.sb_log_instance.initLogging()
            logger.log(u"Initialized new log file in " + log_dir)

            cherry_log = os.path.join(sickbeard.LOG_DIR, "cherrypy.log")
            cherrypy.config.update({'log.access_file': cherry_log})

            logger.log(u"Changed cherry log file to " + cherry_log)

        else:
            return False

    return True

def change_NZB_DIR(nzb_dir):

    if nzb_dir == '':
        sickbeard.NZB_DIR = ''
        return True

    if os.path.normpath(sickbeard.NZB_DIR) != os.path.normpath(nzb_dir):
        if helpers.makeDir(nzb_dir):
            sickbeard.NZB_DIR = os.path.normpath(nzb_dir)
            logger.log(u"Changed NZB folder to " + nzb_dir)
        else:
            return False

    return True


def change_TORRENT_DIR(torrent_dir):

    if torrent_dir == '':
        sickbeard.TORRENT_DIR = ''
        return True

    if os.path.normpath(sickbeard.TORRENT_DIR) != os.path.normpath(torrent_dir):
        if helpers.makeDir(torrent_dir):
            sickbeard.TORRENT_DIR = os.path.normpath(torrent_dir)
            logger.log(u"Changed torrent folder to " + torrent_dir)
        else:
            return False

    return True


def change_TV_DOWNLOAD_DIR(tv_download_dir):

    if tv_download_dir == '':
        sickbeard.TV_DOWNLOAD_DIR = ''
        return True

    if os.path.normpath(sickbeard.TV_DOWNLOAD_DIR) != os.path.normpath(tv_download_dir):
        if helpers.makeDir(tv_download_dir):
            sickbeard.TV_DOWNLOAD_DIR = os.path.normpath(tv_download_dir)
            logger.log(u"Changed TV download folder to " + tv_download_dir)
        else:
            return False

    return True


def change_SEARCH_FREQUENCY(freq):

    if freq == None:
        freq = sickbeard.DEFAULT_SEARCH_FREQUENCY
    else:
        freq = int(freq)

    if freq < sickbeard.MIN_SEARCH_FREQUENCY:
        freq = sickbeard.MIN_SEARCH_FREQUENCY

    sickbeard.SEARCH_FREQUENCY = freq

    sickbeard.currentSearchScheduler.cycleTime = datetime.timedelta(minutes=sickbeard.SEARCH_FREQUENCY)
    sickbeard.backlogSearchScheduler.cycleTime = datetime.timedelta(minutes=sickbeard.get_backlog_cycle_time())

def change_VERSION_NOTIFY(version_notify):
   
    oldSetting = sickbeard.VERSION_NOTIFY

    sickbeard.VERSION_NOTIFY = version_notify

    if version_notify == False:
        sickbeard.NEWEST_VERSION_STRING = None;
        
    if oldSetting == False and version_notify == True:
        sickbeard.versionCheckScheduler.action.run() #@UndefinedVariable

def CheckSection(CFG, sec):
    """ Check if INI section exists, if not create it """
    try:
        CFG[sec]
        return True
    except:
        CFG[sec] = {}
        return False

################################################################################
# Check_setting_int                                                            #
################################################################################
def minimax(val, low, high):
    """ Return value forced within range """
    try:
        val = int(val)
    except:
        val = 0
    if val < low:
        return low
    if val > high:
        return high
    return val

################################################################################
# Check_setting_int                                                            #
################################################################################
def check_setting_int(config, cfg_name, item_name, def_val):
    try:
        my_val = int(config[cfg_name][item_name])
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val
    logger.log(item_name + " -> " + str(my_val), logger.DEBUG)
    return my_val

################################################################################
# Check_setting_float                                                          #
################################################################################
def check_setting_float(config, cfg_name, item_name, def_val):
    try:
        my_val = float(config[cfg_name][item_name])
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val

    logger.log(item_name + " -> " + str(my_val), logger.DEBUG)
    return my_val

################################################################################
# Check_setting_str                                                            #
################################################################################
def check_setting_str(config, cfg_name, item_name, def_val, log=True):
    try:
        my_val = config[cfg_name][item_name]
    except:
        my_val = def_val
        try:
            config[cfg_name][item_name] = my_val
        except:
            config[cfg_name] = {}
            config[cfg_name][item_name] = my_val

    if log:
        logger.log(item_name + " -> " + my_val, logger.DEBUG)
    else:
        logger.log(item_name + " -> ******", logger.DEBUG)
    return my_val


class ConfigMigrator():

    def __init__(self, config_obj):
        """
        Initializes a config migrator that can take the config from the version indicated in the config
        file up to the version required by SB
        """
        
        self.config_obj = config_obj

        # check the version of the config
        self.config_version = check_setting_int(config_obj, 'General', 'config_version', 0)

    def migrate_config(self):
        """
        Calls each successive migration until the config is the same version as SB expects
        """
        
        while self.config_version < sickbeard.CONFIG_VERSION:
            next_version = self.config_version + 1
            
            # do the migration, expect a method named _migrate_v<num>
            logger.log(u"Migrating config up to version "+str(next_version))
            getattr(self, '_migrate_v'+str(next_version))()
            self.config_version = next_version

    def _migrate_v1(self):
        """
        Reads in the old naming settings from your config and generates a new config template from them.
        """
        
        sickbeard.NAMING_PATTERN = self._name_to_pattern()
        
        sickbeard.NAMING_CUSTOM_ABD = bool(check_setting_int(self.config_obj, 'General', 'naming_dates', 0))
        
        if sickbeard.NAMING_CUSTOM_ABD:
            sickbeard.NAMING_ABD_PATTERN = self._name_to_pattern(True)
        else:
            sickbeard.NAMING_ABD_PATTERN = naming.name_abd_presets[0]
        
    def _name_to_pattern(self, abd=False):

        # get the old settings from the file
        use_periods = bool(check_setting_int(self.config_obj, 'General', 'naming_use_periods', 0))
        ep_type = bool(check_setting_int(self.config_obj, 'General', 'naming_ep_type', 0))
        sep_type = bool(check_setting_int(self.config_obj, 'General', 'naming_sep_type', 0))
        use_quality = bool(check_setting_int(self.config_obj, 'General', 'naming_quality', 0))

        use_show_name = bool(check_setting_int(self.config_obj, 'General', 'naming_show_name', 1))
        use_ep_name = bool(check_setting_int(self.config_obj, 'General', 'naming_ep_name', 1))

        # make the presets into templates
        naming_ep_type = ("%Sx%0E",
                          "s%0Se%0E",
                           "S%0SE%0E",
                           "%0Sx%0E")
        naming_sep_type = (" - ", " ")

        # set up our data to use
        if use_periods:
            show_name = '%S.N'
            ep_name = '%E.N'
            ep_quality = '%Q.N'
            abd = '%A.D'
        else:
            show_name = '%SN'
            ep_name = '%EN'
            ep_quality = '%QN'
            abd = '%A-D'

        if abd:
            ep_string = abd
        else:
            ep_string = naming_ep_type[ep_type]

        finalName = ""

        # start with the show name
        if use_show_name:
            finalName += show_name + naming_sep_type[sep_type]

        # add the season/ep stuff
        finalName += ep_string

        # add the episode name
        if use_ep_name:
            finalName += naming_sep_type[sep_type] + ep_name

        # add the quality
        if use_quality:
            finalName += naming_sep_type[sep_type] + ep_quality

        return finalName


