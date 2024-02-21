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


from django import template
from django.conf import settings
from urllib.parse import quote_plus

from sounds.models import License
from utils.tags import annotate_tags

register = template.Library()


@register.inclusion_tag('search/facet2.html', takes_context=True)
def display_facet2(context, facet_name):
    sqp = context['sqp']
    facets = context['facets']
    facet_type = {'tag': 'cloud', 'username': 'cloud'}.get(facet_name, 'list')
    facet_title = {
        'tag': 'Related tags',
        'username': 'Related users',
        'grouping_pack': 'Packs',
        'license': 'Licenses'
    }.get(facet_name, facet_name.capitalize())
    facet = annotate_tags([dict(value=f[0], count=f[1]) for f in facets[facet_name] if f[0] != "0"],
                          sort="value", small_size=0.7, large_size=2.0)
    
    # If the filter is grouping_pack and there are elements which do not contain the character "_" means that
    # these sounds do not belong to any pack (as grouping pack values should by "packId_packName" if there is a pack
    # or "soundId" if there is no pack assigned. We did this to be able to filter properly in the facets, as pack names
    # are not unique!. What we do then is filter out the facet elements where, only for the case of grouping_pack,
    # the element name is a single number that does not contain the character "_"

    # We add the extra Free Cultural Works license facet
    if facet_name == 'license':
        fcw_count = 0
        only_fcw_in_facet = True
        for element in facet:
            if element['value'].lower() == 'attribution' or element['value'].lower() == 'creative commons 0':
                fcw_count += element['count']
            else:
                only_fcw_in_facet = False
        if fcw_count and not only_fcw_in_facet:
            facet.append({
                    'value': settings.FCW_FILTER_VALUE,
                    'count': fcw_count,
                    'size': 1.0,
                })

    filtered_facet = []
    for element in facet:
        if facet_name == "grouping_pack":
            if element['value'].count("_") > 0:
                # We also modify the display name to remove the id
                element['display_value'] = element['value'][element['value'].find("_")+1:]
            else:
                # If facet element belongs to "grouping pack" filter but does not have the "_" character in it, it
                # means this corresponds to the "no pack" grouping which we don't want to show as a facet element.
                continue
        elif element['value'] == settings.FCW_FILTER_VALUE:
            element['display_value'] = "Approved for Free Cultural Works"
        elif facet_name == 'license':
            # License field in solr is case insensitive and will return facet names in lowercase. 
            # We need to properly capitalize them to use official CC license names.
            element['display_value'] = element['value'].title().replace('Noncommercial', 'NonCommercial')
        else:
            # In all other cases, use the value as is for display purposes
            element['display_value'] = element['value']
        
        #if element['name'] == settings.FCW_FILTER_VALUE:
        #    # If adding the FCW filter (which has more complex logic) don't wrap the filter in " as it breaks the syntax parsing    
        #    element['params'] = f"{filter_query} {facet_name}:{quote_plus(element['name'])}"
        #else:
        #    element['params'] = f"{filter_query} {facet_name}:\"{quote_plus(element['name'])}\""

        
        
        if element["value"] == settings.FCW_FILTER_VALUE:
            filter_str = f'{facet_name}:{element["value"]}'
        elif ' ' in element["value"]:
            filter_str = f'{facet_name}:"{element["value"]}"'
        else:
            filter_str = f'{facet_name}:{element["value"]}'
        element['add_filter_url'] = sqp.get_url(add_filters=[filter_str])
        
        filtered_facet.append(element)

    # We sort the facets by count. Also, we apply an opacity filter on "could" type facets
    if filtered_facet:
        filtered_facet = sorted(filtered_facet, key=lambda x: x['count'], reverse=True)
        max_count = max([element['count'] for element in filtered_facet])
        for element in filtered_facet:
            element['weight'] = element['count'] / max_count

    # We also add icons to license facets
    if facet_name == 'license':
        for element in filtered_facet:
            if element['value'] != settings.FCW_FILTER_VALUE:
                element['icon'] = License.bw_cc_icon_name_from_license_name(element['display_value'])
            else:
                element['icon'] = 'fcw'

    return {'type': facet_type, 'title': facet_title, 'facet': filtered_facet}


@register.inclusion_tag('search/facet.html', takes_context=True)
def display_facet(context, flt, facet, facet_type, title=""):
    facet = annotate_tags([dict(name=f[0], count=f[1]) for f in facet if f[0] != "0"],
                          sort="name", small_size=0.7, large_size=2.0)

    # If the filter is grouping_pack and there are elements which do not contain the character "_" means that
    # these sounds do not belong to any pack (as grouping pack values should by "packId_packName" if there is a pack
    # or "soundId" if there is no pack assigned. We did this to be able to filter properly in the facets, as pack names
    # are not unique!. What we do then is filter out the facet elements where, only for the case of grouping_pack,
    # the element name is a single number that does not contain the character "_"

    # We add the extra Free Cultural Works license facet
    if flt == 'license':
        fcw_count = 0
        only_fcw_in_facet = True
        for element in facet:
            if element['name'].lower() == 'attribution' or element['name'].lower() == 'creative commons 0':
                fcw_count += element['count']
            else:
                only_fcw_in_facet = False
        if fcw_count and not only_fcw_in_facet:
            facet.append({
                    'name': settings.FCW_FILTER_VALUE,
                    'count': fcw_count,
                    'size': 1.0,
                })
    
    filtered_facet = []
    filter_query = quote_plus(context['filter_query'])
    for element in facet:
        if flt == "grouping_pack":
            if element['name'].count("_") > 0:
                # We also modify the display name to remove the id
                element['display_name'] = element['name'][element['name'].find("_")+1:]
            else:
                # If facet element belongs to "grouping pack" filter but does not have the "_" character in it, it
                # means this corresponds to the "no pack" grouping which we don't want to show as a facet element.
                continue
        elif element['name'] == settings.FCW_FILTER_VALUE:
            element['display_name'] = "Approved for Free Cultural Works"
        elif flt == 'license':
            # License field in solr is case insensitive and will return facet names in lowercase. 
            # We need to properly capitalize them to use official CC license names.
            element['display_name'] = element['name'].title().replace('Noncommercial', 'NonCommercial')
        else:
            element['display_name'] = element['name']
        
        if element['name'] == settings.FCW_FILTER_VALUE:
            # If adding the FCW filter (which has more complex logic) don't wrap the filter in " as it breaks the syntax parsing    
            element['params'] = f"{filter_query} {flt}:{quote_plus(element['name'])}"
        else:
            element['params'] = f"{filter_query} {flt}:\"{quote_plus(element['name'])}\""

        element['id'] = f"{flt}--{quote_plus(element['name'])}"
        element['add_filter_url'] = '.?advanced={}&g={}&dp={}&q={}&f={}&s={}&w={}'.format(
            context['advanced'],
            context['group_by_pack_in_request'],
            context['only_sounds_with_pack'],
            context['search_query'],
            element['params'],
            context['sort'] if context['sort'] is not None else '',
            context['weights'] or ''
        )
        if context['similar_to'] is not None:
            element['add_filter_url'] += '&similar_to={}'.format(context['similar_to'])
        if context['use_map_mode'] == True:
            element['add_filter_url'] += '&mm=1'
        filtered_facet.append(element)

    # We sort the facets by count. Also, we apply an opacity filter on "could" type pacets
    if filtered_facet:
        filtered_facet = sorted(filtered_facet, key=lambda x: x['count'], reverse=True)
        max_count = max([element['count'] for element in filtered_facet])
        for element in filtered_facet:
            element['weight'] = element['count'] / max_count

    # We also add icons to license facets
    if flt == 'license':
        for element in filtered_facet:
            if element['name'] != settings.FCW_FILTER_VALUE:
                element['icon'] = License.bw_cc_icon_name_from_license_name(element['display_name'])
            else:
                element['icon'] = 'fcw'
    context.update({
        "facet": filtered_facet,
        "type": facet_type,
        "filter": flt,
        "title": title
    })
    return context
