#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     See AUTHORS file.
#

import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from sounds.models import Sound, SoundAnalysis

console_logger = logging.getLogger("console")


class Command(BaseCommand):

    help = """Checks if there are sounds that have not been analyzed by the analyzers defined in the Analysis 
    Configuration File (or that are analyzed with older versions) and send jobs to the analysis workers if needed"""

    def add_arguments(self, parser):
        parser.add_argument(
            '--analysis_config_file',
            action='store',
            required=True,
            help="Absolute path to the analysis configuration file")
        parser.add_argument(
            '--dry_run',
            action="store_true",
            help="Flag to only print the main status of the analysis. It prevents any analysis from being triggered.")
        parser.add_argument(
            '--include_skipped',
            dest='include_skipped',
            action="store_true",
            help="Flag to analyze sounds that haven't been analyzed.")
        parser.add_argument(
            '--include_failed',
            dest='include_failed',
            action="store_true",
            help="Flag to analyze sounds that have failed their analysis.")
        parser.add_argument(
            '--include_ok',
            dest='include_ok',
            action="store_true",
            help="Flag to repeat the analysis of sounds that have been succesfully analyzed.")
        parser.add_argument(
            '--include_missing',
            dest='include_missing',
            action="store_true",
            help="Flag to repeat the analysis of sounds that have been succesfully analyzed.")
        parser.add_argument(
            '--max_per_analyzer',
            action="store",
            help="It allows to set a maximum number of analysis jobs to create per analyzer.")

    def handle(self, *args, **options):
        # Read config json
        with open(options['analysis_config_file']) as json_file:
            config_file = json.load(json_file)

        # Print information about the already analyzed sounds
        ok_total = SoundAnalysis.objects.filter(analysis_status="OK").count()
        sk_total = SoundAnalysis.objects.filter(analysis_status="SK").count()
        fa_total = SoundAnalysis.objects.filter(analysis_status="FA").count()
        n_sounds = Sound.objects.all().count()
        n_analyzers = len(config_file['analyzers'])
        missing_total = (n_sounds * n_analyzers)-(ok_total+sk_total+fa_total)
        # print headers of columns
        console_logger.info("{: >44} {: >11} {: >11} {: >11} {: >11}".format(
            *['analyzer name |', '# ok |', '# failed |', '# skipped |', '# missing']))
        # print row with total numbers
        console_logger.info("{: >44} {: >11} {: >11} {: >11} {: >11}".format(
            *['total |', '{0} |'.format(ok_total), '{0} |'.format(sk_total), '{0} |'.format(fa_total), missing_total]))

        # Count number of analysis done with each analyzer
        for a in config_file['analyzers']:
            analyzer, version = a.split("_")
            ok = SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="OK").count()
            sk = SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="SK").count()
            fa = SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="FA").count()
            missing = n_sounds-(ok+sk+fa)
            # print one row per analyzer
            console_logger.info("{: >44} {: >11} {: >11} {: >11} {: >11}".format(
                *[a+' |', '{0} |'.format(ok), '{0} |'.format(sk), '{0} |'.format(fa), missing]))

        # Only trigger analysis if dry_run flag is not included in the command
        if not options['dry_run']:
            console_logger.info("Analysis configuration file: {0}".format(config_file))
            for analyzer_complete_name in config_file['analyzers']:
                analyzer, version = analyzer_complete_name.split("_")

                if options['include_missing']:
                    for s in Sound.objects.all():
                        # if the combination sound-analyzer-version does not exist, trigger analysis
                        if not SoundAnalysis.objects.filter(sound=s, analyzer=analyzer, analyzer_version=version).exists():
                            console_logger.info(
                                "Triggering analysis of sound {0} with analyzer {1}.".format(s.id, analyzer))
                            s.analyze_new(method=analyzer_complete_name)
                if options['include_skipped']:
                    for a in SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="SK"):
                        console_logger.info(
                                "Triggering analysis of sound {0} with analyzer {1}.".format(s.id, analyzer))
                        a.sound.analyze_new(method=analyzer_complete_name)
                if options['include_failed']:
                    for a in SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="FA"):
                        console_logger.info(
                                "Triggering analysis of sound {0} with analyzer {1}.".format(s.id, analyzer))
                        a.sound.analyze_new(method=analyzer_complete_name)
                if options['include_ok']:
                    for a in SoundAnalysis.objects.filter(analyzer=analyzer, analyzer_version=version, analysis_status="OK"):
                        console_logger.info(
                                "Triggering analysis of sound {0} with analyzer {1}.".format(s.id, analyzer))
                        a.sound.analyze_new(method=analyzer_complete_name)
