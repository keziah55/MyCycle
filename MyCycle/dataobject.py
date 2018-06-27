"""
Data object for MyCycle
"""

import os.path

class Data:
    # separate class to handle all the data
    
    def __init__(self, fname):
        """ Object that controls the csv data. """
        
        self.modified = False
            
        try:
            self.csv_exists(fname)
            self.csvfile = fname
        except:
            raise Exception('mycycle.csv does not exist and could not make it.')
        
        self.col_names, self.df = self.read()
        
        self.aliases = [item.lower() for item in self.col_names]
        
        
    @staticmethod
    def csv_exists(fname):
        
        if not os.path.exists(fname):
            header = 'Date,Time,Distance (km),Calories,Odometer (km)\n'
            with open(fname, 'w') as fileobj:
                fileobj.write(header)
                
        return True
        
        
    def read(self):
        """ Read csv file and return list of headers and list of rows. """
        
        # read csv file
        with open(self.csvfile) as fileobj:
            csv_str = fileobj.read()
            
        # get list of rows (where each row is a string)
        df = csv_str.split('\n')
        df = list(filter(None, df))
        
        # split column names from data
        header, *df = df
        # make list of headers
        header = header.split(',')
        
        if df:
            # make each row into a list
            df = [df[n].split(',') for n in range(len(df))]
            # get type for each item in a row
            self.types = self._get_types(df[0])
            
            # cast every item in the frame as its appropriate type
            for idx, row in enumerate(df):
                for n in range(len(df[0])):
                    row[n] = self.types[n](row[n])
                
        else:
            # there is no data yet
            # and self.types hasn't been initialised
            self.types = None
            
        return header, df
        
        
    def save(self):
        """ If csv data has been modifed, save the file. """
        if self.modified:
            csv_str = self.__str__()
            with open(self.csvfile, 'w') as fileobj:
                fileobj.write(csv_str)
        
        
    def __str__(self):
        
        header = ','.join(self.col_names)
        
        # make list of strings
        rows = []
        for idx in range(self.__len__()):
            row = self.getRow(idx)
            row = list(map(str, row))
            rows.append(','.join(row))
            
        # remove empty strings
        rows = list(filter(None, rows))
        rows = '\n'.join(rows)
        
        frame = header + '\n' + rows
        
        # return string
        return frame
    
    
    def __repr__(self):
        return self.__str__()
            
    @property
    def columns(self):
        return self.col_names
        
    def __len__(self):
        return len(self.df)
    
    @property
    def shape(self):
        return self.__len__(), len(self.columns)
    
    def getRow(self, idx):
        return self.df[idx]
    
    def __setitem__(self, key, value):
        
        if not isinstance(key, tuple):
            raise ValueError('Indices should be tuple')
        else:
            idx0, idx1 = key
            self.df[idx0][idx1] = value
            self.modified = True

    
    def __getitem__(self, key):
        
        if isinstance(key, tuple):
            return self._getItemTuple(key)
        else:
            return self.getRow(key)
        

    def _getItemTuple(self, tup):
        
        row = self.getRow(tup[0])
        idx = self._getColumnIndex(tup[1])
            
        return row[idx]
    
    
    def getColumn(self, key):
        
        idx = self._getColumnIndex(key)
        col = [self.df[n][idx] for n in range(self.shape[0])]
            
        return col
    
    
    def _getColumnIndex(self, key):
        if isinstance(key, str):
            try:
                idx = self.col_names.index(key)
            except ValueError:
                try:
                    idx = self.aliases.index(key)
                except ValueError:
                    raise ValueError("Index '{}' not recognised".format(key))
        else:
            idx = key
        return idx
    
                
    def addRow(self, row):
        """ Add new row to Data. """
        
        if len(row) != self.shape[1]:
            raise ValueError('New row should have {} elements'
                             .format(self.shape[1]))
        else:
            # if we started with an empty csv file, get the types now
            if self.types is None:
                self.types = self._get_types(row)
            # type cast new row
            row = [self.types[n](row[n]) for n in range(self.shape[1])]
            self.df.append(row)
            self.modified = True
        
        
    def removeRow(self, idx):
        """ Remove row from Data. """
        try:
            del self.df[idx]
            self.modified = True
        except IndexError:
            raise IndexError
        
    
    def _get_types(self, row):
        
        # get type of each item in row
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
                
        return tuple(types)
    
    
    def setAlias(self, column, alias):
        
        if isinstance(column, int):
            idx = column
        elif isinstance(column, str):
            idx = self.columns.index(column)
        else:
            raise ValueError
            
        self.aliases[idx] = alias
    
    
    def where(self, column, condition, mode):
        """ Analyse Data object and return where a condition is met
        
            Parameters
            ----------
            column : str or index
                column to be analysed
            condition : str
                condition to be met (should evalute to True/False)
                Please use 'data' to refer to the selected column
            mode : {'idx', 'row'}
                retun either the indices of rows where the condition is met
                or the full row
        """
        
        pass
    
    
    def getMax(self, column, mode='row'):
        """ Find max in given column
        
            Parameters
            ----------
            column : str or index
                column to be analysed
            mode : {'row', 'idx'}
                return either the row containing the maximum or its index.
                Default is 'row'.
        """
        
        return self._getMinMax(data.getColumn(column), max, mode)
        
    
    def getMin(self, column, mode='row'):
        """ Find min in given column
        
            Parameters
            ----------
            column : str or index
                column to be analysed
            mode : {'idx', 'row'}
                return either the row containing the minimum or its index.
                Default is 'row'.
        """
        
        return self._getMinMax(data.getColumn(column), min, mode)
        
    @staticmethod
    def _getMinMax(col, which, mode):
        
        result = which(col)
        
        idx = col.index(result)
        
        if mode == 'idx':
            return idx
        else:
            return data[idx]
        
        
if __name__ == '__main__':
    
    home = os.path.expanduser('~')
    data = Data(os.path.join(home, '.mycycle', 'mycycle.csv'))
