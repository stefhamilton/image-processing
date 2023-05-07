import lxml.etree as ET
import cairosvg

def create_svg_pin(save_folder, fill_color, alpha):
    png_path = f"{save_folder}/pin_bearing.png"

    svg_filename = png_path.replace('.png', '.svg')
    
    # Create the SVG document
    root = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", viewBox="0 0 24 32", width="24", height="32")
    path_data = "M12 0C6.485 0 2 4.485 2 10c0 6 10 22 10 22s10-16 10-22c0-5.515-4.485-10-10-10z"
    
    # Create the fill color in the format rgba(red, green, blue, alpha)
    fill_color_rgba = f"rgba({fill_color[0]}, {fill_color[1]}, {fill_color[2]}, {alpha})"
    
    # Create a path element with the specified fill color and fill-opacity
    path = ET.SubElement(root, 'path', d=path_data, fill=fill_color_rgba)
    
    # Write the SVG file
    tree = ET.ElementTree(root)
    tree.write(svg_filename, pretty_print=True, xml_declaration=True, encoding='utf-8')
    
    # Convert the SVG to a PNG
    cairosvg.svg2png(url=svg_filename, write_to=png_path)
    return png_path

if __name__ == "__main__":
    # Example usage
    res = create_svg_pin("album/15 cameras Stargazer Farm", (50, 50, 200), 0.3)
    print(res)
