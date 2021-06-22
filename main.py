from utils import read_image, get_srcCenter, get_trgCenter, get_curve
from mvc import MVC_Cloner


if __name__ == "__main__":
    src_fname = "images/airplane_src.jpg"
    dst_fname = "images/sky.jpeg"
    src_image = read_image(src_fname)
    dst_image = read_image(dst_fname)

    # get user inputs
    src_center = get_srcCenter(src_image)
    dst_center = get_trgCenter(dst_image)
    curve = get_curve(src_image)

    # Run MVC algorithm
    cloner = MVC_Cloner()
    output = cloner.process(src_image, dst_image, src_center, dst_center, curve)
