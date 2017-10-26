import matplotlib.pyplot as plt
import matplotlib.cbook as cbook


class PltReadImage:
    def __init__(self,image_path):
        self.plt=plt
        image_file = cbook.get_sample_data(image_path)
        self.image=plt.imread(image_file)


