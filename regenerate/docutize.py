import os
from collections import defaultdict
import util

# for each {TYPE} make:
#   - dir docs/docs/{TYPE}
#   - file docs/docs/{TYPE}/{TYPE}.md
#   - dir _data/docs/{TYPE}

# for each {ELEMENT} in {TYPE}:
#   - file docs/docs/{TYPE}/{ELEMENT}.md
#   - file docs/docs/{TYPE}/{TYPE}.md
#   - dir _data/docs/{TYPE}/{ELEMENT}
#       - file _data/docs/{TYPE}/{ELEMENT}/json.json
#       - file _data/docs/{TYPE}/{ELEMENT}/representations/python.json

def docutize(input_dir, data_dir, pages_dir):
    doc_categories = get_doc_categories(input_dir)
    
    for i, (category, info) in enumerate(doc_categories.items()):
        write_category(category, info, pages_dir, i + 1)

def get_doc_categories(input_dir):
    """generate a dictionary for each category of documentation:
    eg: {
        'display' : {
            'text' : PATH,
            'elements' : {
                'ELEMENT_NAME' : {
                    'text' : PATH,
                    'example' : PATH,
                }

            }
        },
        ...
    }
    """
    doc_categories = defaultdict(dict)

    for category in os.listdir(input_dir):
        category_path = os.path.join(input_dir, category)

        if not os.path.isdir(category_path):
            continue

        content = {
            'elements' : {},
        }

        for element in os.listdir(category_path):
            element_path = os.path.join(category_path, element)

            if os.path.isfile(element_path):
                element_name, _ = os.path.splitext(element)

                # TODO: possibly allow for embedding webweb stuff?
                # use the 'text.md' file for the description of the documentation category
                if element_name == 'text':
                    content['text'] = element_path
            elif os.path.isdir(element_path):
                element_content = {}

                for component in os.listdir(element_path):
                    component_name, _ = os.path.splitext(component)
                    component_path = os.path.join(element_path, component)

                    element_content[component_name] = component_path

                element_base_name = os.path.basename(element_path)
                content['elements'][element_base_name] = element_content

        doc_categories[category] = content

    return doc_categories

def write_category(category, info, directory, number):
    """for each category, we'll make the following:
    - directories:
        - docs/documentation/{CATEGORY}
    - files:
        - docs/documentation/{CATEGORY}/{CATEGORY}.md
        - and for each ELEMENT, a file:
            - docs/documentation/{CATEGORY}/{ELEMENT}.md
    """
    category_dir = os.path.join(directory, category)
    util.clean_dir(category_dir)

    # write index
    if info.get('text'):
        with open(info['text'], 'r') as f:
            index_content = f.read()
    else:
        index_content = None

    index = util.Page(
        title=category,
        has_children=True,
        parent='documentation',
        content=index_content,
        permalink='/documentation/{category}/'.format(category=category),
        nav_order=number,
    )

    index.write(category_dir)

    for i, (element, components) in enumerate(info['elements'].items()):
        page_kwargs = {
            'title' : element,
            'parent' : category,
            'grand_parent' : 'documentation',
            'nav_order' : i + 1,
        }

        if components.get('text'):
            with open(components['text'], 'r') as f:
                page_kwargs['content'] = f.read()

        page = util.Page(**page_kwargs)
        page.write(category_dir)
