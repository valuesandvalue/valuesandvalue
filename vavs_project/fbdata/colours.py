# fbdata.colours

# COLORSYS
import colorsys

def random_color():
    return "%06x" % random.randint(0,0xFFFFFF)
       
def random_hls(intensity=0.5, saturation=0.5):
    hue = random.random()*360.0
    rgb = colorsys.hls_to_rgb(hue, 0.5, 0.5)
    return rgb # to hex
