import imageio as iio
images = []


FILENAMES = [f"/Users/benhoskings/Documents/Projects/pokemon-legacy/assets/battle/main_display/text_box_{idx+1}.png" for idx in range(2)]

images = []

for filename in FILENAMES:
    images.append(iio.v3.imread(filename))

iio.mimsave('test.gif', images)