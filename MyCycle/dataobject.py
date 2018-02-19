"""
Data object for MyCycle
"""

import re   

class Data:
    # separate class to handle all the data
    
    def __init__(self, fname):
        """ Object that controls the csv data. """
        
        self.modified = False
            
        self.csvfile = fname
        
        # csv_data is a string containing all the data
        with open(self.csvfile) as fileobj:
            self.csv_data = fileobj.read()
            
        # make csv_data into a 'DataFrame' which is indexable etc.
        self.get_df()
            
    def get_df(self):
            
        # csv_df is a list of strings and is the basis for regarding Data
        # as a 2D array/DataFrame
        self.csv_df = self.csv_data.split('\n')
        self.csv_df = list(filter(None, self.csv_df))
        
        header, *self.csv_df = self.csv_df
        self.col_names = header.split(',')
        
        self.types = self._get_types()
        
    @property
    def columns(self):
        return self.col_names
       
    def __len__(self):
        return len(self.csv_df)
    
    def __setitem__(self, key, value):
        
#        print(key, value)
        
        if not isinstance(key, tuple):
            raise ValueError('Indices should be tuple')
        else:
            row = self.getRow(key[0])
            
            old_row = list(map(str, row))
            old_row = ','.join(old_row)
            
            new_row = row
            new_row[key[1]] = value
            
            new_row = list(map(str, new_row))
            new_row = ','.join(new_row)
            
#            print('old_row:', old_row)
#            print('new_row:', new_row)
            
            self.csv_data = re.sub(old_row, new_row, self.csv_data)
            
            self.modified = True
            self.get_df()
            
#            print('Data.csv_data:\n', self.csv_data)
    
    def __getitem__(self, key):
        
        if isinstance(key, tuple):
            return self._getItemTuple(key)
        else:
            return self.getRow(key)
    
    def _getItemTuple(self, tup):
        
        row = self.getRow(tup[0])
        
        if isinstance(tup[1], str):
            idx = self.col_names.index(tup[1])
        else:
            idx = tup[1]
            
        return row[idx]
    
    def _get_types(self):
        
        row = self.csv_df[0]
        row = row.split(',')
        types = []
        
        for item in row:
            try:
                int(item)
                types.append(int)
            except ValueError:
                try:
                    float(item)
                    types.append(float)
                except ValueError:
                    types.append(str)
                
        return types
        
    def getRow(self, idx):
        row = self.csv_df[idx].split(',')
        row = [self.types[n](row[n]) for n in range(len(self.types))]
        return row
    
    def getColumn(self, key):
        
        if isinstance(key, str):
            idx = self.col_names.index(key)
        else:
            idx = key
        
        col = []
        for line in self.csv_df:
            csv = line.split(',')
            col.append(csv[idx])
            
        col = list(map(self.types[idx], col))
            
        return col
                
    def add_new(self, new_data):
        """ Add new line to csv. """
        self.csv_data += new_data
        self.modified = True
        self.get_df()
        
    def remove_line(self, idx):
        row = self.csv_df[idx]
        self.csv_data = re.sub(row, '', self.csv_data)
        self.modified = True
        self.get_df()
        
    def save(self):
        # save csv file
        if self.modified:
            with open(self.csvfile, 'w') as fileobj:
                fileobj.write(self.csv_data)
            
        return True