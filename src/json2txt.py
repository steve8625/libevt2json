# json2txt.py
# -*- coding: utf-8 -*-

import json
import os
import logging
from collections import OrderedDict

input_file_extension = ".log"
output_file_extension = ".txt"

class EVTParser:

    # file handle
    output_file = None
    current_evt_txt_file = None

    # class local variables
    result = OrderedDict()
    number_of_strings = -1
    str_count = 0
    in_event = False

    # default output folder
    folder_path = '.'

    def reset_flag(self):
        self.result = OrderedDict()
        self.number_of_strings = -1
        self.str_count = 0
        self.in_event = False

    def open_log_file(self, path):
        try:
            self.current_evt_txt_file = open(path, 'r')
            return True
        except IOError:
            logging.error('cannot open log file (%s)' % (path))

    def close_log_file(self):
        if self.current_evt_txt_file != None:
            self.current_evt_txt_file.close()
        else:
            logging.warning('evt log file already closed or not existed')

    def open_output_file(self, output_file_name):
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        
        file_full_path = os.path.join(self.folder_path,output_file_name)
        self.output_file = open(file_full_path, 'w+')

    def close_output_file(self):
        if self.output_file != None:
            self.output_file.close()
        else:
            logging.warning('output file already closed or not existed')

    def write_json_to_file(self, input_json):
        if self.output_file != None:
            input_str = ("%s\n" % input_json).encode('UTF-8')
            self.output_file.write(input_str)
        else:
            logging.warning('output file not opened')

    def close(self):
        self.close_output_file()
        self.close_log_file()

    def parse(self, root, file, output_postfix):
        log_path = os.path.join(root, file)
        self.open_log_file(log_path)
        parser.open_output_file("%s%s%s" % (file.strip(input_file_extension), output_postfix , output_file_extension))
        self.parse_log_file()

    def set_output_folder(self,folder_path):
        if folder_path:
            self.folder_path = folder_path
        
    def parse_log_file(self):
        lines = self.current_evt_txt_file.readlines()
        for line_temp in lines:    
            
            line = line_temp.decode('utf-8')
            
            # start parsing with event number 
            if "Event number" in line:
                # deal with ill-formatted input that number_of_strings does not equal to parsed lines
                self.reset_flag() 
                self.in_event = True

            if self.in_event: 
                if 'String:' in line:
                    split_str = line.split(':',2)

                    # remove white space after ":" token and special characters (\n or \t)
                    key_str = split_str[0].strip('\t')
                    num_str = split_str[1][1:].strip('\t')
                    val_str = split_str[2][1:].strip('\n')
                    self.result.update({key_str +  " #" + num_str : val_str})
                    self.str_count += 1
                else:
                    split_str = line.split(':',1)
                    
                    # get how many lines of strings to parse 
                    if 'Number of strings' in line:
                        self.number_of_strings=int(split_str[1])
                    
                    # remove white space after ":" token and special characters (\n or \t)
                    key_str = split_str[0].strip('\t')
                    val_str = split_str[1][1:].strip('\n')
                    self.result.update({key_str : val_str})

                # end condition -> when we parse number_of_strings lines of strings
                if self.str_count == self.number_of_strings:
                    json_format=json.dumps(self.result,ensure_ascii=False)
                    self.write_json_to_file(json_format)
                    self.reset_flag()

if __name__ == '__main__':

    # create parser class object
    parser = EVTParser()
    
    # set output postfix
    output_postfix="_result"
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith(input_file_extension):

                file_path = os.path.join(root,file)
                dir_path = os.path.dirname(file_path)
                
                # set output folder (e.g. save output file in the same directory)
                parser.set_output_folder(dir_path)            
                # parse input log file and 
                parser.parse(root, file, output_postfix)
                # close current file handle
                parser.close()
