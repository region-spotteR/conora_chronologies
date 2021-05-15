from prepare import data
from plot import plots
from tabulator import historical_table

country='lv'
# variation A
# data=data(country)
# data.load(data.attr.url,country)

data=data(country)
data.load(country)

#test=new_plots(data.attr)
#more_tests=new_plots()
history_dict_list=historical_table.create_dicts(data.smooth,country)
history_columns=historical_table.create_history_columns(data.smooth.headers7)
historical_table.write_tabulator(history_dict_list,history_columns,country)

plots_obj=plots(data.attr)
plots_obj.plot_timeline(data.smooth,country)
plots_obj.plot_smoothened(data.smooth,country)
plots_obj.plot_threshold(data.simulated,country)
print('done')
