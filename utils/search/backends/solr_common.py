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
#     Bram de Jong
#
import json
import urllib.request, urllib.parse, urllib.error

from utils.search import SearchEngineException


class SolrQuery:
    """A wrapper around a lot of Solr query funcionality.
    """

    def __init__(self, query_type=None, writer_type="json", indent=None, debug_query=None):
        """Creates a SolrQuery object
        query_type: Which handler to use when replying, default: default, dismax
        writer_type: Available types are: SolJSON, SolPHP, SolPython, SolRuby, XMLResponseFormat, XsltResponseWriter
        indent: format output with indentation or not
        debug_query: if 1 output debug infomation
        """
        # some default parameters
        self.params = {
            'qt': query_type,
            'wt': writer_type,
            'indent': indent,
            'debugQuery': debug_query
        }

    def set_query(self, query):
        self.params['q'] = query

    def set_dismax_query(self, query, query_fields=None, minimum_match=None, phrase_fields=None, phrase_slop=None,
                         query_phrase_slop=None, tie_breaker=None, boost_query=None, boost_functions=None):
        """Created a dismax query: http://wiki.apache.org/solr/DisMaxRequestHandler
        The DisMaxRequestHandler is designed to process simple user entered phrases (without heavy syntax) and search for the individual words
        across several fields using different weighting (boosts) based on the significance of each field. Additional options let you influence
        the score based on rules specific to each use case (independent of user input)

        query_fields: List of fields and the "boosts" to associate with each of them when building DisjunctionMaxQueries from the user's query.
                        should be a list of fields: ["tag", "description", "username"]
                        with optional boosts:  with boosts [("tag", 2), "description", ("username", 3)]
        minimum_match: see docs...
        phrase_fields: after the query, find (in these fields) fields that have all terms close together and boost them
        phrase_slop: amount of slop on phrase queries built for "pf" fields (affects boosting).
        query_phrase_slop: Amount of slop on phrase queries explicitly included in the user's query string (in qf fields; affects matching).
        tie_breaker: see docs...
        boost_query: see docs...
        boost_functions: see docs...
        """
        self.params['qt'] = "dismax"
        self.params['q'] = query
        if query_fields:
            qf = []
            for f in query_fields:
                if isinstance(f, tuple):
                    qf.append("^".join(map(str, f)))
                else:
                    qf.append(f)

            self.params['qf'] = " ".join(qf)
        else:
            self.params['qf'] = None
        self.params['mm'] = minimum_match
        self.params['pf'] = " ".join(phrase_fields) if phrase_fields else phrase_fields
        self.params['ps'] = phrase_slop
        self.params['qs'] = query_phrase_slop
        self.params['tie'] = tie_breaker
        self.params['bq'] = boost_query
        self.params['bf'] = boost_functions

    def set_query_options(self, start=None, rows=None, sort=None, filter_query=None, field_list=None):
        """Set the options for the query.
        start: row where to start
        rows: row where to end
        sort: ['field1 desc', 'field2', 'field3 desc']
        filter_query: filter the returned results by this query
        field_list: ['field1', 'field2', ...] or ['*'] these fields will be returned, default: *
        """
        self.params['sort'] = ",".join(sort) if sort else sort
        self.params['start'] = start
        self.params['rows'] = rows
        self.params['fq'] = filter_query
        self.params['fl'] = ",".join(field_list) if field_list else field_list

    def add_facet_fields(self, *args):
        """Adds facet fields
        """
        self.params['facet'] = True
        try:
            self.params['facet.field'].extend(args)
        except KeyError:
            self.params['facet.field'] = list(args)

    def set_facet_query(self, query):
        """Set additional query for faceting
        """
        self.params['facet.query'] = query

    # set global faceting options for regular fields
    def set_facet_options_default(self, limit=None, offset=None, prefix=None, sort=None, mincount=None,
                                  count_missing=None, enum_cache_mindf=None):
        """Set default facet options: these will be applied to all facets, but overridden by particular options (see set_facet_options())
        prefix: retun only facets with this prefix
        sort: sort facets, True or False
        limit: nr of facets to return
        offset: start from this row
        mincount: minimum hits a facet needs to be listed
        count_missing: count items that don't have this facet, True or False
        enum_cache_mindf: when faceting on a field with a very large number of terms, and you wish to decrease memory usage, try a low value of 25 to 50 first
        """
        self.params['facet.limit'] = limit
        self.params['facet.offset'] = offset
        self.params['facet.prefix'] = prefix
        self.params['facet.sort'] = sort
        self.params['facet.mincount'] = mincount
        self.params['facet.missing'] = count_missing
        self.params['facet.enum.cache.minDf'] = enum_cache_mindf

    # set faceting options for one particular field
    def set_facet_options(self, field, prefix=None, sort=None, limit=None, offset=None, mincount=None,
                          count_missing=None):
        """Set facet options for one particular field... see set_facet_options_default() for parameter explanation
        """
        try:
            if field not in self.params['facet.field']:
                raise SearchEngineException("setting facet options for field that doesn't exist")
        except KeyError:
            raise SearchEngineException("you haven't defined any facet fields yet")

        self.params['f.%s.facet.limit' % field] = limit
        self.params['f.%s.facet.offset' % field] = offset
        self.params['f.%s.facet.prefix' % field] = prefix
        self.params['f.%s.facet.sort' % field] = sort
        self.params['f.%s.facet.mincount' % field] = mincount
        self.params['f.%s.facet.missing' % field] = count_missing

    def add_date_facet_fields(self, *args):
        """Add date facet fields
        """
        self.params['facet'] = True
        try:
            self.params['facet.date'].extend(args)
        except KeyError:
            self.params['facet.date'] = list(args)

    def set_date_facet_options_default(self, start=None, end=None, gap=None, hardened=None, count_other=None):
        """Set default date facet options: these will be applied to all date facets, but overridden by particular options (see set_date_facet_options())
            start: date start in DateMathParser syntax
            end: date end in DateMathParser syntax
            gap: size of slices of date range
            hardend: True: if gap doesn't devide range make last slice smaller. False: go out of bounds with last slice
            count_other: A tuple of other dates to count: before, after, between, none, all
        """
        self.params['facet.date.start'] = start
        self.params['facet.date.end'] = start
        self.params['facet.date.gap'] = gap
        self.params['facet.date.hardend'] = hardened
        self.params['facet.date.other'] = count_other

    def set_date_facet_options(self, field, start=None, end=None, gap=None, hardened=None, count_other=None):
        """Set date facet options for one particular field... see set_date_facet_options_default() for parameter explanation
        """
        try:
            if field not in self.params['facet.date']:
                raise SearchEngineException("setting date facet options for field that doesn't exist")
        except KeyError:
            raise SearchEngineException("you haven't defined any date facet fields yet")

        self.params['f.%s.date.start' % field] = start
        self.params['f.%s.date.end' % field] = start
        self.params['f.%s.date.gap' % field] = gap
        self.params['f.%s.date.hardend' % field] = hardened
        self.params['f.%s.date.other' % field] = count_other

    def set_highlighting_options_default(self, field_list=None, snippets=None, fragment_size=None,
                                         merge_contiguous=None, require_field_match=None, max_analyzed_chars=None,
                                         alternate_field=None, max_alternate_field_length=None, pre=None, post=None,
                                         fragmenter=None, use_phrase_highlighter=None, regex_slop=None,
                                         regex_pattern=None, regex_max_analyzed_chars=None):
        """Set default highlighting options: these will be applied to all highlighting, but overridden by particular options (see set_highlighting_options())
        field_list: list of fields to highlight space separated
        snippets: number of snippets to generate
        fragment_size: snippet size, default: 1
        merge_contiguous: merge continuous snippets into one, True or False
        require_field_match: If True, then a field will only be highlighted if the query matched in this particular field
        max_analyzed_chars: How many characters into a document to look for suitable snippets
        alternate_field: if no match is found, use this field as summary
        max_alternate_field_length: size to clip the alternate field to
        pre: what to put before the snippet (like <strong>)
        post: what to put after the snippet (like </strong>)
        fragmenter: specify a text snippet generator for highlighted text.
        use_phrase_highlighter: use SpanScorer to highlight phrase terms only when they appear within the query phrase in the document.
        regex_slop: factor by which the regex fragmenter can stray from the ideal fragment size (given by hl.fragsize) to accomodate the regular expression
        regex_pattern: the regular expression for fragmenting.
        regex_max_analyzed_chars: only analyze this many characters from a field when using the regex fragmenter
        """
        self.params['hl'] = True
        self.params['hl.fl'] = ",".join(field_list) if field_list else field_list
        self.params['hl.fl.snippets'] = snippets
        self.params['hl.fragsize'] = fragment_size
        self.params['hl.mergeContiguous'] = merge_contiguous
        self.params['hl.requireFieldMatch'] = require_field_match
        self.params['hl.maxAnalyzedChars'] = max_analyzed_chars
        self.params['hl.alternateField'] = alternate_field
        self.params['hl.maxAlternateFieldLength'] = max_alternate_field_length
        # self.params['hl.formatter'] = # only valid one is "simple" right now
        self.params['hl.simple.pre'] = pre
        self.params['hl.simple.post'] = post
        self.params['hl.fragmenter'] = fragmenter
        self.params['hl.usePhraseHighlighter'] = use_phrase_highlighter
        self.params['hl.regex.slop'] = regex_slop
        self.params['hl.regex.pattern'] = regex_pattern
        self.params['hl.regex.maxAnalyzedChars'] = regex_max_analyzed_chars

    def set_highlighting_options(self, field, snippets=None, fragment_size=None, merge_contiguous=None,
                                 alternate_field=None, pre=None, post=None):
        """Set highlighting options for one particular field... see set_highlighting_options_default() for parameter explanation
        """
        try:
            if field not in self.params['hl.fl']:
                raise SearchEngineException("setting highlighting options for field that doesn't exist")
        except KeyError:
            raise SearchEngineException("you haven't defined any highlighting fields yet")

        self.params['f.%s.hl.fl.snippets' % field] = snippets
        self.params['f.%s.hl.fragsize' % field] = fragment_size
        self.params['f.%s.hl.mergeContiguous' % field] = merge_contiguous
        self.params['f.%s.hl.alternateField' % field] = alternate_field
        self.params['f.%s.hl.simple.pre' % field] = pre
        self.params['f.%s.hl.simple.post' % field] = post

    def __str__(self):
        return urllib.parse.urlencode(self.params, doseq=True)

    def set_group_field(self, group_field=None):
        self.params['group.field'] = group_field

    def set_group_options(self, group_func=None, group_query=None, group_rows=10, group_start=0, group_limit=1,
                          group_offset=0, group_sort=None, group_sort_ingroup=None, group_format='grouped',
                          group_main=False, group_num_groups=True, group_cache_percent=0, group_truncate=False):
        self.params['group'] = True
        self.params['group.func'] = group_func
        self.params['group.query'] = group_query
        self.params['group.rows'] = group_rows
        self.params['group.start'] = group_start
        self.params['group.limit'] = group_limit
        self.params['group.offset'] = group_offset
        self.params['group.sort'] = group_sort
        self.params['group.sort.ingroup'] = group_sort_ingroup
        self.params['group.format'] = group_format
        self.params['group.main'] = group_main
        self.params['group.ngroups'] = group_num_groups
        self.params['group.truncate'] = group_truncate
        self.params['group.cache.percent'] = group_cache_percent

    def as_kwargs(self):
        """Return params in a way that can be passed to pysolr commands as kwargs"""
        params = {k: v for k, v in self.params.items() if v is not None}
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = json.dumps(v)
        return params


class SolrResponseInterpreter:
    def __init__(self, response, next_page_query=None):
        if "grouped" in response:
            if "thread_title_grouped" in list(response["grouped"].keys()):
                grouping_field = "thread_title_grouped"
            elif "grouping_pack" in list(response["grouped"].keys()):
                grouping_field = "grouping_pack"

            self.docs = [{
                'id': group['doclist']['docs'][0]['id'],
                'score': group['doclist']['docs'][0]['score'],
                'n_more_in_group': group['doclist']['numFound'] - 1,
                'group_docs': group['doclist']['docs'],
                'group_name': group['groupValue']
            } for group in response["grouped"][grouping_field]["groups"] if group['groupValue'] is not None]
            self.start = int(response["responseHeader"]["params"]["start"])
            self.num_rows = len(self.docs)
            self.num_found = response["grouped"][grouping_field]["ngroups"]
            self.non_grouped_number_of_results = response["grouped"][grouping_field]["matches"]
        else:
            self.docs = response["response"]["docs"]
            self.start = int(response["response"]["start"])
            self.num_rows = len(self.docs)
            self.num_found = response["response"]["numFound"]
            self.non_grouped_number_of_results = -1

        self.q_time = response["responseHeader"]["QTime"]
        try:
            self.facets = response["facet_counts"]["facet_fields"]
        except KeyError:
            self.facets = {}

        """Facets are given in a list: [facet, number, facet, number, None, number] where the last one
        is the missing field count. Converting all of them to a dict for easier usage:
        {facet:number, facet:number, ..., None:number}
        """
        for facet, fields in list(self.facets.items()):
            self.facets[facet] = [(fields[index], fields[index + 1]) for index in range(0, len(fields), 2)]

        try:
            self.highlighting = response["highlighting"]
        except KeyError:
            self.highlighting = {}
