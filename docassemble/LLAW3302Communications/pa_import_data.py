# Module that validates and imports the spreadsheet into
# an object that we can manipulate in Docassemble
import pandas as pd
from docassemble.base.util import DAFileList, DADict, DAList, DAObject

class PAImportData(DAObject):
   
    # Store the name of 'Specific Induction Day' column
    # as a constant here
    sid = 'Specific Induction Day' 
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.kwargs = kwargs
        self.file = kwargs.get('file')
        self.tab_name = kwargs.get('tab_name', 'not defined')
        self.columns = kwargs.get('columns', None)
        self.error_message = ""

    def say_hello(self):
        result = []
        fp = self.file.path()
        result.append(('file',self.file))
        result.append(('file path',fp))
        result.append(('tab_name',self.tab_name))
        sn = pd.ExcelFile(fp).sheet_names
        result.append(('sheet_names', sn))
        result.append(('columns', self.columns))
        try:
            df = self._read_in_data()
            result.append(('df col 0',df.columns[0]))
            result.append(('valid',self._validate_data()))
            result.append(('objects', self.process_data()))
        except Exception as e:
            result.append(('datframe error', e))
        result.append(('error messge', self.error_message))
        return result
   
    def _read_in_data(self):
        # Read in the excel file and return the data frame
        fp = self.file.path()
        xls = pd.ExcelFile(fp)
        # Choose the right sheet.  If the file has more than one sheet then look for the
        # specific sheet.  Otherwise, just read in that sheet
        sn = xls.sheet_names
        if len(sn) == 1:
            return pd.read_excel(fp)
        elif self.tab_name in xls.sheet_names:
            return pd.read_excel(fp, sheet_name=self.tab_name)
        else:
            # What do we do if we have nothing?
            return None
    
    def _validate_data(self):
        # The only validation we do is to make sure the columns in the first row match
        # the self.columns
        df_cols = self._read_in_data().columns
        # Iterate over the columns looking for a mismatch
        for i in range(0, len(self.columns)):
            # If we find one we return false (invalid)
            if self.columns[i] != df_cols[i]:
                return False
        # If we make it through the loop we're valid
        return True
            
    def process_data(self):
        df = self._read_in_data()
        if df is None:
            self.error_message = 'No data returned from spreadsheet'
            return []
    
        if not self._validate_data():
            self.error_message = 'Data validation failed'
            return []
        
        # If we're here we have valid non-empty data
        days_of_week = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        data_objects = []

        for _, row in df.iterrows():
            obj = {}
            # Iterate over the columns
            for a_column in self.columns:
                if a_column != self.sid:
                    obj[a_column] = row[a_column]
                else:
                    obj[a_column] = days_of_week.get(row[a_column],row[a_column])
            # And then add it to our list
            data_objects.append(obj)

        return data_objects