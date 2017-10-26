
class CreateGrid:

    def __init__(self,col_label,cursor,unique_key):
        col_list=col_label
        self.unique_key=unique_key
        self.pre_data_dict=self.CreateColName(col_list)
        self.data_dict=self.GetDataByColname(col_list,self.Collect_data(col_list,cursor,self.pre_data_dict),unique_key)
        self.ReturnDictionary()

    def CreateColName(self,col_list):
        '''
        using for creating column name
        '''
        self.col_dict={}
        for col in col_list:
            self.col_dict[col]= []
        return self.col_dict


    def Collect_data(self,col_list,cursor,data_dict):
        '''
        extract data from cursor into data dictionary
        '''
        pre_data_dict=data_dict
        for row in cursor.fetchall():
            i = 0
            for col in col_list:
                pre_data_dict[col].append(row[i])
                i+=1

        return pre_data_dict


    def GetDataByColname(self,col_list,pre_data_dict,unique_key):
        '''
        put data which was stored in the preparing data dictionary to grid data dictionary and return grid data dictionary
        '''
        grid_data_dict={}
        for row in range(len(pre_data_dict[unique_key])):
            i=0
            for col in col_list:
                grid_data_dict[(row, i)] = pre_data_dict[col][row]
                i+=1
        return grid_data_dict

    def ReturnDictionary(self):
        return self.data_dict,len(self.pre_data_dict[self.unique_key])

