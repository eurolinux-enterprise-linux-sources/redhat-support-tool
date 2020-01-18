# -*- coding: utf-8 -*-

#
# Copyright (c) 2012 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from optparse import Option, SUPPRESS_HELP
from redhat_support_lib.infrastructure.errors import RequestError, \
    ConnectionError
from redhat_support_tool.helpers.confighelper import EmptyValueError
from redhat_support_tool.helpers.confighelper import _
from redhat_support_tool.plugins import Plugin, ObjectDisplayOption
from redhat_support_tool.plugins.add_comment import AddComment
from redhat_support_tool.helpers import apihelper, common, confighelper
from redhat_support_tool.helpers.launchhelper import LaunchHelper
import redhat_support_lib.utils.reporthelper as reporthelper
import os
import logging


__author__ = 'Keith Robertson <kroberts@redhat.com>'
__author__ = 'Spenser Shumaker <sshumake@redhat.com>'

logger = logging.getLogger("redhat_support_tool.plugins.add_attachment")


class AddAttachment(Plugin):
    plugin_name = 'addattachment'
    comment = None
    attachment = None

    @classmethod
    def get_usage(cls):
        '''
        The usage statement that will be printed by OptionParser.

        Example:
            - %prog -c CASENUMBER [options] <comment text here>
        Important: %prog is a OptionParser built-in.  Use it!
        '''
        return _('%prog -c CASENUMBER [options] /path/to/file')

    @classmethod
    def get_desc(cls):
        '''
        The description statement that will be printed by OptionParser.

        Example:
            - 'Use the \'%s\' command to add a comment to a case.'\
             % cls.plugin_name
        '''
        return _('Use the \'%s\' command to add an attachment to a case.')\
             % cls.plugin_name

    @classmethod
    def get_epilog(cls):
        '''
        The epilog string that will be printed by OptionParser.  Usually
        used to print an example of how to use the program.

        Example:
         Examples:
          - %s -c 12345678 Lorem ipsum dolor sit amet, consectetur adipisicing
          - %s -c 12345678
        '''
        return _('Examples:\n'
                 '- %s -c 12345678 /var/log/messages\n'
                 '- %s -c 12345678 -d \'The log file containing the error\' '
                 '/var/log/messages\n'
                 '- %s -c 12345678') % \
                 (cls.plugin_name, cls.plugin_name, cls.plugin_name)

    @classmethod
    def get_options(cls):
        '''
        Subclasses that need command line options should override this method
        and return an array of optparse.Option(s) to be used by the
        OptionParser.

        Example:
         return [Option("-f", "--file", action="store",
                        dest="filename", help='Some file'),
                 Option("-c", "--case",
                        action="store", dest="casenumber",
                        help='A case')]

         Would produce the following:
         Command (? for help): help mycommand

         Usage: mycommand [options]

         Use the 'mycommand' command to find a knowledge base solution by ID
         Options:
           -h, --help  show this help message and exit
           -f, --file  Some file
           -c, --case  A case
         Example:
          - mycommand -c 12345 -f abc.txt

        '''
        return [Option("-c", "--casenumber", dest="casenumber",
                        help=_('The case number from which the comment '
                        'should be added. (required)'), default=False),
                Option("-p", "--public", dest="public",
                        help=SUPPRESS_HELP, default=None),
                Option("-d", "--description", dest="description",
                        help=_("A description for the attachment. The \
Red Hat Support Tool will generate a default description for the attachment \
if none is provided that contains the name of the file and the RPM package to \
which it belongs if available. (optional)"), default=False),
                Option("-x", "--no-split", dest="nosplit",
                        help=_('Do not attempt to split uploaded files, upload'
                               ' may fail as a result if an alternative'
                               ' destination is not available.'))]

    def _check_case_number(self):
        msg = _("ERROR: %s requires a case number.")\
                    % self.plugin_name

        if not self._options['casenumber']:
            if common.is_interactive():
                line = raw_input(_('Please provide a case number (or \'q\' '
                                       'to exit): '))
                line = str(line).strip()
                if line == 'q':
                    raise Exception()
                if str(line).strip():
                    self._options['casenumber'] = line
                else:
                    print msg
                    raise Exception(msg)
            else:
                print msg
                raise Exception(msg)

    def _check_description(self):
        if common.is_interactive():
            if not self._options['description']:
                line = raw_input(_('Please provide a description or '
                                   'enter to accept default (or \'q\' '
                                       'to exit): '))
                line = str(line).strip()
                if line == 'q':
                    raise Exception()
                if str(line).strip():
                    self._options['description'] = line

        if not self._options['description']:
            rpm = ''
            try:
                rpm = rpm.join(['from package ',
                                reporthelper.rpm_for_file(self.attachment)])
            except:
                pass

            self._options['description'] = '[RHST] File %s %s' % \
            (os.path.basename(self.attachment), rpm)

    def _check_is_public(self):
        if confighelper.get_config_helper().get(option='ponies') and \
           common.is_interactive():
            if self._options['public'] == None:
                line = raw_input(_('Is this a public attachment (Y/n)? '))
                if str(line).strip().lower() == 'n':
                    self._options['public'] = False
                else:
                    self._options['public'] = True
        else:
            self._options['public'] = True

    def _check_file(self):
        msg = _("ERROR: %s requires a path to a file.")\
                    % self.plugin_name
        self.attachment = None
        if self._args:
            self.attachment = self._args[0]
            self.attachment = os.path.expanduser(self.attachment)
            if not os.path.isfile(self.attachment):
                msg = _('ERROR: %s is not a valid file.') % self.attachment
                print msg
                raise Exception(msg)
        elif common.is_interactive():
            while True:
                line = raw_input(_('Please provide the full path to the'
                                   ' file (or \'q\' to exit): '))
                if str(line).strip() == 'q':
                    raise Exception()
                line = str(line).strip()
                self.attachment = line
                self.attachment = os.path.expanduser(self.attachment)
                if os.path.isfile(self.attachment):
                    break
                else:
                    print _('ERROR: %s is not a valid file.') \
                        % self.attachment
        else:
            print msg
            raise Exception(msg)

        # Assume Base10 units for the '900 MB' limit for now...
        max_file_size = 900 * 1000 * 1000
        file_stat = os.stat(self.attachment)
        if (file_stat.st_size > max_file_size):
            if common.is_interactive():
                line = raw_input(_('%s is too large to upload to the Red Hat'
                                   ' Customer Portal, would you like to split'
                                   ' the file before uploading (Y/n)? ') % (
                                                            self.attachment))
                if str(line).strip().lower() == 'n':
                    return
            elif not self._options['nosplit']:
                return

            split_file = common.split_file(self.attachment, max_file_size)
            if len(split_file) > 0:
                self.attachment = split_file

    def validate_args(self):
        self._check_file()
        self._check_case_number()
        self._check_description()
        self._check_is_public()

    def non_interactive_action(self):
        api = None
        try:
            api = apihelper.get_api()

            if type(self.attachment) is list:
                updatemsg = _('The following split file has been uploaded to'
                              ' the case:\n')
                for attachment in self.attachment:
                    retVal = api.attachments.add(
                                    caseNumber=self._options['casenumber'],
                                    public=self._options['public'],
                                    fileName=attachment['file'],
                                    description=self._options['description'])
                    updatemsg += '\n    %s %s' % (
                                        os.path.basename(attachment['file']),
                                        attachment['msg'])

                lh = LaunchHelper(AddComment)
                comment_displayopt = ObjectDisplayOption(None, None,
                                                         [updatemsg])
                lh.run('-c %s' % (self._options['casenumber']),
                       comment_displayopt)
            else:
                retVal = api.attachments.add(
                                    caseNumber=self._options['casenumber'],
                                    public=self._options['public'],
                                    fileName=self.attachment,
                                    description=self._options['description'])
            if retVal is None:
                print _('ERROR: There was a problem adding your attachment '
                        'to %s' % self._options['casenumber'])
                raise Exception()
        except EmptyValueError, eve:
            msg = _('ERROR: %s') % str(eve)
            print msg
            logger.log(logging.WARNING, msg)
            raise
        except RequestError, re:
            msg = _('Unable to connect to support services API. '
                    'Reason: %s') % re.reason
            print msg
            logger.log(logging.WARNING, msg)
            raise
        except ConnectionError:
            msg = _('Problem connecting to the support services '
                    'API.  Is the service accessible from this host?')
            print msg
            logger.log(logging.WARNING, msg)
            raise
        except Exception:
            msg = _("Unable to get attachment")
            print msg
            logger.log(logging.WARNING, msg)
            raise
