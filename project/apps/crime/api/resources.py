import csv
import json
import io

from django.urls import re_path
from django.core.serializers.json import DjangoJSONEncoder

from tastypie.resources import ModelResource, csrf_exempt
from tastypie.authentication import ApiKeyAuthentication
from tastypie.serializers import Serializer

from project.apps.crime.models import Release, Agency, City, County


class CSVPrettyJSONSerializer(Serializer):
    json_indent = 2

    formats = ['json', 'jsonp', 'xml', 'yaml', 'csv']

    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'xml': 'application/xml',
        'yaml': 'text/yaml',
        'csv': 'text/csv',
    }

    def flatten(self, data, odict = {}):
        if isinstance(data, list):
            for value in data:
                self.flatten(value, odict)
        elif isinstance(data, dict):
            for (key, value) in data.items():
                if not isinstance(value, (dict, list)):
                    odict[key] = value
                else:
                    self.flatten(value, odict)

    def to_csv(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)

        raw_data = io.StringIO()
        first = True

        if "meta" in data.keys():#if multiple objects are returned
            objects = data.get("objects")

            for value in objects:
                test = {}
                self.flatten(value, test)
                if first:
                    writer = csv.DictWriter(raw_data, test.keys(), quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                    writer.writeheader()
                    writer.writerow(test)
                    first=False
                else:
                    writer.writerow(test)
        else:
            test = {}
            self.flatten(data, test)
            if first:
                writer = csv.DictWriter(raw_data, test.keys(), quotechar="'", quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                writer.writerow(test)
                first=False
            else:
                writer.writerow(test)
        CSVContent=raw_data.getvalue()
        return CSVContent


    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return json.dumps(data, cls=DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)



class ReleaseResource(ModelResource):
    class Meta:
        queryset = Release.objects.all().order_by('-id')
        allowed_methods = ['get']
        excludes = ['id',]
        include_resource_uri = False
        serializer = CSVPrettyJSONSerializer()
        resource_name='releases'

    def prepend_urls(self):
        """
        Returns a URL scheme based on the default scheme to specify
        the response format as a file extension, e.g. /api/v1/release.json
        """
        return [
            re_path(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            re_path(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            re_path(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            re_path(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def determine_format(self, request):
        """
        Used to determine the desired format from the request.format
        attribute.
        """
        if (hasattr(request, 'format') and
                request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)
        return super(ReleaseResource, self).determine_format(request)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(ReleaseResource, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)
        return wrapper

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['documentation'] = "string" #TODO
        return data

    def build_schema(self):
        base_schema = super(ReleaseResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': f.choices,
                })
        return base_schema

    def dehydrate_file_type(self, bundle):
        for f in self._meta.object_class._meta.fields:
            if f.name == "file_type":
                choices = dict(f.choices)
        for file_type in bundle.obj.file_type:
            file_type = choices[file_type]
        return file_type

    def dehydrate_frequency_type(self, bundle):
        for f in self._meta.object_class._meta.fields:
            if f.name == "frequency_type":
                choices = dict(f.choices)
        for frequency_type in bundle.obj.frequency_type:
            frequency_type = choices[frequency_type]
        return frequency_type


#TODO add this cloudfront url
    def dehydrate_hj_url(self, bundle):
        hj_url = bundle.obj.hj_url
        if "http" not in hj_url:
            hj_url = "{0}{1}".format('string', hj_url)
        else:
            pass
        return hj_url

    def dehydrate(self, bundle):
        bundle.data['data_source'] = bundle.obj.data_source
        return bundle


class AgencyResource(ModelResource):
    class Meta:
        queryset = Agency.objects.all().order_by('id')
        allowed_methods = ['get']
        excludes = ['id',]
        include_resource_uri = False
        serializer = CSVPrettyJSONSerializer()
        resource_name='agencies'

    def prepend_urls(self):
        """
        Returns a URL scheme based on the default scheme to specify
        the response format as a file extension, e.g. /api/v1/release.json
        """
        return [
            re_path(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            re_path(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            re_path(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            re_path(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def determine_format(self, request):
        """
        Used to determine the desired format from the request.format
        attribute.
        """
        if (hasattr(request, 'format') and
                request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)
        return super(AgencyResource, self).determine_format(request)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(AgencyResource, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)
        return wrapper

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['documentation'] = "string" #TODO
        return data

    def dehydrate_agency_type(self, bundle):
        for f in self._meta.object_class._meta.fields:
            if f.name == "agency_type":
                choices = dict(f.choices)
        for agency_type in bundle.obj.agency_type:
            agency_type = choices[agency_type]
        return agency_type

    def dehydrate(self, bundle):
        counties_qs = County.objects.filter(counties_covered=bundle.obj)
        counties_list = []
        for county in counties_qs:
            counties_list.append(county.__str__())
        bundle.data['counties_covered'] = counties_list
        cities_qs = City.objects.filter(cities_covered=bundle.obj)
        cities_list = []
        for city in cities_qs:
            cities_list.append(city.__str__())
        bundle.data['cities_covered'] = cities_list
        return bundle

class CityResource(ModelResource):
    class Meta:
        queryset = City.objects.all().order_by('nj_muncode')
        allowed_methods = ['get']
        excludes = ['id',]
        include_resource_uri = False
        serializer = CSVPrettyJSONSerializer()
        resource_name='cities'

    def prepend_urls(self):
        """
        Returns a URL scheme based on the default scheme to specify
        the response format as a file extension, e.g. /api/v1/release.json
        """
        return [
            re_path(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            re_path(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            re_path(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            re_path(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def determine_format(self, request):
        """
        Used to determine the desired format from the request.format
        attribute.
        """
        if (hasattr(request, 'format') and
                request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)
        return super(CityResource, self).determine_format(request)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(CityResource, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)
        return wrapper

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['documentation'] = "string" #TODO
        return data

    def dehydrate(self, bundle):
        bundle.data['county'] = bundle.obj.county
        return bundle

class CountyResource(ModelResource):
    class Meta:
        queryset = County.objects.filter(fips__startswith="34").order_by('fips')
        allowed_methods = ['get']
        excludes = ['id',]
        include_resource_uri = False
        serializer = CSVPrettyJSONSerializer()
        resource_name='counties'

    def prepend_urls(self):
        """
        Returns a URL scheme based on the default scheme to specify
        the response format as a file extension, e.g. /api/v1/release.json
        """
        return [
            re_path(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            re_path(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            re_path(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            re_path(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def determine_format(self, request):
        """
        Used to determine the desired format from the request.format
        attribute.
        """
        if (hasattr(request, 'format') and
                request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)
        return super(CountyResource, self).determine_format(request)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(CountyResource, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)
        return wrapper

    def alter_list_data_to_serialize(self, request, data):
        data['meta']['documentation'] = "string" #TODO
        return data

    def dehydrate(self, bundle):
        bundle.data['state'] = bundle.obj.state
        return bundle