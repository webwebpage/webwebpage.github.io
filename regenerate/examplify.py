# this script does beautiful and useful things, but they can only be done in ugly ways.
# the idea is to override the browser opening action in webweb examples

from collections import defaultdict
import importlib.util
import json
import os
import re
import shutil
import sys
import webbrowser

import util

def get_examples_map(input_dir):
    """generate a dictionary of examples to the code for each language and the file
    eg: {
        'simple' : {
            'python' : 'python/simple.py',
            'matlab' : 'matlab/simple.m',
        },
        ...
    }
    """
    file_map = defaultdict(dict)
    for dir_name, subdir_names, file_names in os.walk(input_dir):
        for file_name in file_names:
            name, ext = os.path.splitext(file_name)
            if ext in ['.md', '.py', '.m']:
                language = os.path.basename(dir_name)
                file_map[name][language] = os.path.join(dir_name, file_name)

    return file_map

def examplify(input_dir, data_output_dir, pages_output_dir, container, nav_order=0, parent_container=None):
    util.clean_dir(pages_output_dir)
    util.clean_dir(data_output_dir)

    examples_map = get_examples_map(input_dir)

    util.Index(
        title=container,
        writeable_title=container,
        nav_order=nav_order,
        layout='main_page',
        has_children=True,
        parent=parent_container,
    ).write(pages_output_dir)

    ordered_examples_map = sorted(examples_map.items(), key=lambda x: x[0])

    for i, (name, language_to_file_map) in enumerate(ordered_examples_map):
        Example(
            writeable_name=name,
            language_to_file_map=language_to_file_map,
            example_number=i + 1,
            container=container,
            parent_container=parent_container,
        ).write(
            page_directory=pages_output_dir,
            data_directory=data_output_dir,
        )

class Example(object):
    def __init__(self, writeable_name, language_to_file_map, example_number, container, parent_container=None):
        self.writeable_name = writeable_name
        self.language_to_file_map = language_to_file_map
        self.container = container
        self.parent_container = parent_container
        self.example_number = example_number
        self.read_meta()

        self.json = {}
        self.read()

    def read_meta(self):
        with open(self.language_to_file_map['meta'], 'r') as f:
            content = [l.strip() for l in f.readlines()]

        if content[0] == '---':
            content.pop(0)

        self.extra = {}
        while content and content[0] != '---':
            line = content.pop(0)
            if line:
                key, value = line.split(': ', 1)

                if key == 'name':
                    self.title = value
                elif key == 'nav_order' :
                    self.nav_order = value
                else:
                    self.extra[key] = value

        if content and content[0] == '---':
            content.pop(0)
        if content and not content[0]:
            content.pop(0)

        self.text = "\n".join([line + "\n" for line in content])

    def create_output_directories(self):
        # set up the data directory
        if not os.path.exists(self.data_directory_name):
            os.mkdir(self.data_directory_name)

        # set up the representation directory
        if not os.path.exists(self.representations_directory_name):
            os.mkdir(self.representations_directory_name)

    @property
    def data_directory_name(self):
        return os.path.join(self.data_directory, self.writeable_name)

    @property
    def representations_directory_name(self):
        return os.path.join(self.data_directory_name, 'representations')

    def read(self):
        if self.language_to_file_map.get('python'):
            self.read_json()
        
        self.read_representations()

    def read_json(self):
        # override the webbrowser so we don't have to open it
        webbrowser.open_new = lambda _: None

        # load the example
        module = util.get_module(self.writeable_name, self.language_to_file_map['python'])
        self.json = json.loads(module.web.json)

    def read_representations(self):
        """this function returns a dictionary with data displayed in the code switcher"""
        self.representations = {}
        for lang_name, lang_file_path in self.language_to_file_map.items():
            with open(lang_file_path, 'r') as f:
                lang_code = f.readlines()

            # remove trailing newline
            lang_code[-1] = lang_code[-1].rstrip()

            self.representations[lang_name] = lang_code

        # add the pretty json for displaying
        if self.json:
            self.representations['json'] = json.dumps(self.json, indent=4, sort_keys=True)

    def write(self, page_directory, data_directory):
        self.page_directory = page_directory
        self.data_directory = data_directory
        self.create_output_directories()
        self.write_data()
        self.write_page()

    def write_data(self):
        # write the json
        if self.json:
            path = os.path.join(self.data_directory_name, 'json.json')
            with open(path, 'w') as f:
                json.dump(self.json, f, indent=4, sort_keys=True)

        # write each representation
        for representation_name, content in self.representations.items():
            path = os.path.join(
                self.representations_directory_name,
                self.writeable_representation(representation_name) + '.json'
            )

            with open(path, 'w') as f:
                json.dump(content, f, indent=4, sort_keys=True)

    @property
    def content(self):
        content = []

        if self.json:
            content.append(self.get_webweb_visualization())

        if self.extra:
            extra_content = self.get_extra_content()

            if extra_content:
                content.append(extra_content)

        if self.text:
            content.append(self.text)

        if self.representations and list(self.representations.keys()) != ['meta']:
            content.append(self.get_representations_select())

        if content:
            return "\n".join(content)

    def get_extra_content(self):
        key_ordering = ['type', 'synonyms', 'default']
        extra_content = []
        for key in key_ordering:
            value = self.extra.get(key, None)
            if value:
                line = "```{0}```: ".format(key)

                if util.is_int(value):
                    line += "```{0}```".format(int(value))
                elif util.is_float(value):
                    line += "```{0}```".format(float(value))
                else:
                    line += value

                extra_content.append(line + "\n")

        return "\n".join(extra_content)

    def write_page(self):
        util.Page(
            title=self.title,
            writeable_title=self.writeable_name,
            layout='home',
            content=self.content,
            parent=self.container,
            grand_parent=self.parent_container,
            nav_order=getattr(self, 'nav_order', self.example_number),
        ).write(self.page_directory)

    def get_representations_select(self):
        # display code in a consistent order
        representation_ordering = ['python', 'python (networkx)', 'matlab', 'json']

        ordered_representations = [rep for rep in representation_ordering if self.representations.get(rep)]

        if not ordered_representations:
            return

        select_include = '{{% include code_switcher.html code_options="{options}" switcher_name="example-code-switcher" %}}'.format(
            options="---".join(ordered_representations)
        )

        representation_options = []
        for representation in ordered_representations:
            representation_options.append(self.get_representation_select_option(representation))

        options = "\n".join(representation_options)

        return "\n".join([select_include, options])

    def writeable_representation(self, representation):
        return re.sub(r'\W+', '', representation.replace(' ', '_'))

    @property
    def data_path(self):
        path_parts = ['site.data']

        if self.parent_container:
            path_parts.append(self.parent_container)

        path_parts.append(self.container)
        path_parts.append(self.writeable_name)

        return ".".join(path_parts)


    def get_representation_select_option(self, representation):
        representation_content_path = "{data_path}.representations.{representation}".format(
            data_path=self.data_path,
            representation=self.writeable_representation(representation),
        )

        language = representation

        if representation == 'python (networkx)':
            language = 'python'

        content = "```{language}\n{{{{{content_path}}}}}\n```".format(
            language=language, 
            content_path=representation_content_path,
        )

        representation_display_classes = [
            "select-code-block",
            "example-code-switcher",
            "{0}-code-block".format(self.writeable_representation(representation)),
        ]

        # make python visible
        if representation == 'python':
            representation_display_classes.append("select-code-block-visible")

        div = "<div class='{0}'></div>".format(" ".join(representation_display_classes))

        return "\n".join([div, content])

    def get_webweb_visualization(self):
        return "{{% include webweb.html webweb_json={data_path}.json %}}\n".format(
            data_path=self.data_path,
            name=self.writeable_name,
        )
