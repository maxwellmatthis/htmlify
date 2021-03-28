#!/usr/bin/python3

import cv2
from sys import argv
import urllib.request


class ImageConverter:
    def __init__(self, path):
        self.banner()

        self.color_classes = {}
        self.joined_relevant_pixels = []

        print('img source: ' + str(path))

        if 'http' in path:
            filename = path.split('/')[len(path.split('/')) - 1]
            with urllib.request.urlopen(path) as response, open(filename, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            path = filename
        img = cv2.imread(path, 1)
        print('image shape: ' + str(img.shape))

        self.img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        print('downscaled image shape: ' + str(self.img.shape))

        r = self.img[0][0][2]
        g = self.img[0][0][1]
        b = self.img[0][0][0]
        self.background = (r, g, b)
        print('auto detected background color: ' + str(self.background))

        self.map_pixels()
        self.save_html()

    def banner(self):
        print(' _     _             _ _  __')
        print('| |__ | |_ _ __ ___ | (_)/ _|_   _')
        print('| \'_ \| __| \'_ ` _ \| | | |_| | | |')
        print('| | | | |_| | | | | | | |  _| |_| |')
        print('|_| |_|\__|_| |_| |_|_|_|_|  \__, |')
        print('                             |___/')

    def map_pixels(self):
        for row_num in range(0, self.img.shape[0]):
            row = self.img[row_num]
            for column_num in range(0, row.shape[0]):
                rgb = row[column_num]
                self.process_pixel(row_num, column_num, rgb)

    def is_background(self, rgb):
        if rgb[0] == self.background[0] and rgb[1] == self.background[1] and rgb[2] == self.background[2]:
            return True
        return False

    def process_pixel(self, row, column, rgb):
        if not self.is_background(rgb):
            cclass = 'p' + str(rgb[0]) + '-' + \
                str(rgb[1]) + '-' + str(rgb[2])
            if cclass not in self.color_classes:
                self.color_classes[cclass] = rgb

            last_pixel = None
            if len(self.joined_relevant_pixels) > 0:
                last_pixel = self.joined_relevant_pixels[len(
                    self.joined_relevant_pixels) - 1]

            if last_pixel and last_pixel['row'] == row and last_pixel['cclass'] == cclass:
                self.joined_relevant_pixels[len(
                    self.joined_relevant_pixels) - 1]['width'] = last_pixel['width'] + 1
            else:
                self.joined_relevant_pixels.append({
                    'row': row,
                    'column': column,
                    'cclass': cclass,
                    'width': 1
                })

    def save_html(self):
        html = ''
        css = ''

        for box in self.joined_relevant_pixels:
            html += '<div class="{}" style="width:{}px;top:{}px;left:{}px;"></div>'.format(
                box['cclass'], box['width'], box['row'], box['column'])

        for cclass in self.color_classes:
            rgb = self.color_classes[cclass]
            css += '.' + cclass + \
                '{background:' + \
                'rgba({},{},{})'.format(
                    str(rgb[2]), str(rgb[1]), str(rgb[0])) + '}'

        css = '<style>body{background:rgba(' + str(self.background[0]) + ',' + str(self.background[1]) + ',' + str(
            self.background[2]) + ')}div{height:1px;position:absolute;}' + css + '</style>'

        output = 'htmlified.html'
        # if not len(argv) >= 2 and not argv[2] else argv[2]
        with open(output, 'w') as f:
            f.write(html + css)

        print('total file size: ' + str(len(html) + len(css)) + ' bytes')


if __name__ == '__main__':
    if (len(argv) > 0 and argv[1]):
        ImageConverter(argv[1])
    else:
        print('Incorrect Usage!')
        print(
            'Usage: htmlify.py [/path/to/image or URL] [optional: /path/to/output]')
