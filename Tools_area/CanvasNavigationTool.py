from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc



def add_toolbar(canvas):
    """Copied verbatim from embedding_wx2.py"""
    toolbar = NavigationToolbar2Wx(canvas)
    toolbar.Realize()
    # By adding toolbar in sizer, we are able to put it at the bottom
    # of the frame - so appearance is closer to GTK version.
    # update the axes menu on the toolbar
    toolbar.update()
    return toolbar