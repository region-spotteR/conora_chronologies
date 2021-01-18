from test_prepare import data
from test_plot import plots

country='de'
# variation A
# data=data(country)
# data.load(data.attr.url,country)

data=data(country)
data.load(country)

plots_obj=plots(data.attr)
plots_obj.plot_smoothened(data.smooth,country)
plots_obj.plot_threshold(data.simulated,country)
print('done')

