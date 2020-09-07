#!/usr/bin/env python
# Use pyenv to ensure Python 3: https://opensource.com/article/19/5/python-3-default-mac

import argparse
import jsonpickle
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputDir', required=True)
    parser.add_argument('--outputTocPath', required=True)
    parser.add_argument('--outputPagesPath', required=True)
    args = parser.parse_args()

    print('Using input directory: %s' % args.inputDir)
    print('Using output table of contents path: %s' % args.outputTocPath)
    print('Using output pages path: %s' % args.outputPagesPath)

    gtr = GitToRoam(args.inputDir)
    (toc_json, pages_json) = gtr.run_traversal()
    out_toc = open(args.outputTocPath, 'w')
    out_toc.write(toc_json)
    out_pages = open(args.outputPagesPath, 'w')
    out_pages.write(pages_json)


class GitToRoam:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.toc_pages = []  # The final pages JSON needs to be an array
        self.pages = []

    def run_traversal(self):
        # Begin with a Table of Contents page for the repository
        directory = os.path.realpath(self.dir_path)
        directory_name = os.path.basename(directory)
        print('Creating top-level page with name: %s' % directory_name)
        toc_page = RoamPage(directory_name)
        self.toc_pages.append(toc_page)

        # Run recursive runTraversal
        self.__run_traversal(directory, toc_page)

        toc_json = jsonpickle.encode(self.toc_pages, unpicklable=False)
        pages_json = jsonpickle.encode(self.pages, unpicklable=False)
        return toc_json, pages_json

    def __run_traversal(self, dir_path, cur_toc):
        # Create pages for each of the files in this directory
        files = [f for f in os.scandir(dir_path) if not f.is_dir()]
        for file in files:
            # Add a sub-bullet to the table of contents
            # print("Appending TOC child with str: %s" % str(file.path))
            toc_child = RoamChild("[[%s]]" % str(file.name))
            cur_toc.add_child(toc_child)

            # Create page for leaf file
            print('Creating page for file: %s' % file.name)
            page = RoamPage(file.name)

            try:
                contents = open(file.path, 'r').read()
            except Exception:
                print('Unable to open file.')
                continue

            # print('Appending child with contents: %s' % contents)
            code_child = RoamChild("```%s```" % contents)
            page.add_child(code_child)

            self.pages.append(page)

        # Recursively traverse the subdirectories
        directories = [f for f in os.scandir(dir_path) if f.is_dir() and not f.name.startswith('.')]
        for directory in directories:
            print('Opening directory: %s' % directory.name)

            # Add a sub-bullet to the table of contents
            toc_child = RoamChild(directory.name)
            cur_toc.add_child(toc_child)

            self.__run_traversal(directory.path, toc_child)


class RoamPage:
    def __init__(self, title):
        self.title = title
        self.children = []

        # Exported attributes not needed for import
        # self.editEmail
        # self.editTime

    def add_child(self, child):
        self.children.append(child)


class RoamChild:
    def __init__(self, string):
        self.children = []
        self.string = string

        # Exported attributes not needed for import
        # self.createEmail
        # self.createTime
        # self.uid
        # self.editTime
        # self.editEmail

    def add_child(self, child):
        self.children.append(child)


if __name__ == '__main__':
    main()
