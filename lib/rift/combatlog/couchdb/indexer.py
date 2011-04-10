import json
import os


def pretty_print(var):
    print json.dumps(var, sort_keys = False, indent = 4)


def read_view_js(design_dir, design_file):
    index = ""
    documents = {}
    for line in file(os.path.join(os.path.dirname(__file__), "views", design_dir, design_file)):
        if line.startswith("function map"):
            index = "map"
            documents[index] = ""
            line = line.replace(" map", "", 1)
        if line.startswith("function reduce"):
            index = "reduce"
            documents[index] = ""
            line = line.replace(" reduce", "", 1)
        if index:
            documents[index] += line
    return documents

def read_view_py(design_dir, design_file):
    index = ""
    documents = {}
    for line in file(os.path.join(os.path.dirname(__file__), "views", design_dir, design_file)):
        if line.startswith("def map"):
            index = "map"
            documents[index] = ""
            line = line.replace(" map", " fun", 1)
        if line.startswith("def reduce"):
            index = "reduce"
            documents[index] = ""
            line = line.replace(" reduce", " fun", 1)
        if index:
            documents[index] += line
    return documents

def read_view_erl(design_dir, design_file):
    index = ""
    documents = {}
    for line in file(os.path.join(os.path.dirname(__file__), "views", design_dir, design_file)):
        if line.startswith("map("):
            index = "map"
            documents[index] = ""
            line = line.replace("map(", "fun(", 1)
        if line.startswith("reduce("):
            index = "reduce"
            documents[index] = ""
            line = line.replace("reduce(", "fun(", 1)
        if index:
            documents[index] += line
    return documents

def create_views(db):
    designs = []
    views = []
    for design_dir in os.listdir(os.path.join(os.path.dirname(__file__), "views")):
        design = {
            "_id" : "_design/" + design_dir, 
            "views" : {},
            }
        for design_file in os.listdir(os.path.join(os.path.dirname(__file__), "views", design_dir)):
            documents = {}
            language = ""
            if os.path.splitext(design_file)[1] == ".js":
                language = "javascript"
                documents = read_view_js(design_dir, design_file)
            if os.path.splitext(design_file)[1] == ".py":
                language = "python"
                design["language"] = language
                documents = read_view_py(design_dir, design_file)
            if os.path.splitext(design_file)[1] == ".erl":
                language = "erlang"
                design["language"] = language
                documents = read_view_erl(design_dir, design_file)
            design["views"][os.path.splitext(design_file)[0]] = documents
            views.append(design_dir + "/" + os.path.splitext(design_file)[0])
        designs.append(design)
    db.update(designs)
    return views

# xxx: this is terrible
def list_views(db):
    designs = []
    views = []
    for design_dir in os.listdir(os.path.join(os.path.dirname(__file__), "views")):
        design = {
            "_id" : "_design/" + design_dir, 
            "views" : {},
            }
        for design_file in os.listdir(os.path.join(os.path.dirname(__file__), "views", design_dir)):
            documents = {}
            language = ""
            if os.path.splitext(design_file)[1] == ".js":
                language = "javascript"
                documents = read_view_js(design_dir, design_file)
            if os.path.splitext(design_file)[1] == ".py":
                language = "python"
                design["language"] = language
                documents = read_view_py(design_dir, design_file)
            if os.path.splitext(design_file)[1] == ".erl":
                language = "erlang"
                design["language"] = language
                documents = read_view_erl(design_dir, design_file)
            design["views"][os.path.splitext(design_file)[0]] = documents
            views.append(design_dir + "/" + os.path.splitext(design_file)[0])
        designs.append(design)
    return views


def create(db):
    views = create_views(db)
    for view in views:
        len(db.view(view))

def update(db):
    views = list_views(db)
    for view in views:
        len(db.view(view))
    
