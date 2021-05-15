import json
from datetime import datetime
from loguru import logger

class historical_table:
    def create_dicts(history_obj):
        """
        Creates a dictionary of the historical data for tabulator.js. For each observation a dictionary is created. 
        If there is enough values the `_children` attributes contains last weeks data. Note that the column index is used to map the column with its header

        Parameters
        ----------
        history_obj : history
            A history object from transform_enrich.py
        
        Returns
        -------
        list : list
            A list of dictionaries for each entry.
        """
        try:
            dates=history_obj.data7[0]
            data=history_obj.data7 # Simplification for the time being
            cases=history_obj.data7[1]
            day_of_week=[datetime.fromisoformat(x).strftime('%A') for x in dates]

            result_list=[]
            base_dict_list=[]
            for i in reversed(range(0,len(dates))):
                base_dict=dict(day=dates[i],week_day=day_of_week[i], new_cases=cases[i])
                flexible_dict={str(j):(data[j][i] if len(data[j])>i else None) for j in range(2,len(data))}
                base_dict_new={**base_dict,**flexible_dict}
                base_dict_list.insert(0,base_dict_new)

                if len(result_list)>6:
                    new_dict={**base_dict,**flexible_dict,**{'_children':base_dict_list[1:7]}}
                else: 
                    new_dict={**base_dict,**flexible_dict}
                                  
                result_list.insert(0,new_dict)

            return result_list



        except Exception as e:
            logger.error(e)

    def create_history_columns(headers):
        """
        Creates a dictionary for each column header. Also maps these headers to fields. 

        Parameters
        ----------
        headers : list
            A list containing the column headers of the table
        
        Returns
        -------
        str : str
            A string containing a dictionary item for each header.
        """
        try:
            result_str=''
            for j in range(2,len(headers)):
                result_str+="{ title: \""+headers[j]+"\", field: \""+str(j)+"\", width: 150 },\n"

            return result_str

        except Exception as e:
            logger.error(e)

    def write_tabulator(history_dict_list,history_columns,country):
        """
        Creates a html string and writes the file

        Parameters
        ----------
        history_dict_list : list
            A list of dictionaries for each observations. Based on the create_dict-method
        history_columns : str
            A string containing a dictionary for each column of column header and mapped field
        country : str
            A two digit country code to append to the html-file-name
        """

        try:
            html_string='''

        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link
            href="https://unpkg.com/tabulator-tables@4.9.3/dist/css/tabulator.min.css"
            rel="stylesheet"
            />
            <link rel="stylesheet" href="style.css" />
            <style>
            /* .tabulator-headers {
                background-color: #9e3039;
            }
            .tabulator .tabulator-header .tabulator-col {
                background: #9e3039;
            }
            .tabulator .tabulator-header {
                color: #fff;
            }
            .tabulator
                .tabulator-header
                .tabulator-col.tabulator-sortable[aria-sort="none"]
                .tabulator-col-content
                .tabulator-col-sorter
                .tabulator-arrow {
                border-bottom: 6px solid #fff;
            }
            .tabulator .tabulator-header .tabulator-col.tabulator-sortable:hover {
                background-color: #fff;
                color: #9e3039;
            } */
            </style>
        </head>
        <body>
            <div id="table"></div>
            <script
            type="text/javascript"
            src="https://unpkg.com/tabulator-tables@4.9.3/dist/js/tabulator.min.js"
            ></script>
            <script type="text/javascript">
            //sample data
            var tableDataNested = ''' + json.dumps(history_dict_list) + '''

            var table = new Tabulator("#table", {
                data: tableDataNested,
                dataTree: true,
                dataTreeFilter:false, //disabled child row filtering
                dataTreeStartExpanded: false,
                columns: [
                {
                    title: "Weekday",
                    field: "week_day",
                    width: 150,
                    responsive: 0,
                    headerFilter: true,
                },
                { title: "Day", field: "day", width: 200, responsive: 0 }, //never hide this column
                { title: "New Cases", field: "new_cases", width: 150 },
            ''' + history_columns + '''
                ],
                initialHeaderFilter: [
                { field: "week_day", value: "Saturday" }, //set the initial value of the header filter to "Saturday"
                ],
            });
            </script>
        </body>
        </html>
        '''

            with open(f'plot_output/history_{country}.html','w') as f:
                f.write(html_string)

        except Exception as e:
            logger.error(e)


