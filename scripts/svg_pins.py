import lxml.etree as ET
import cairosvg

def create_svg_pin(save_folder, fill_color, alpha):
    png_path = f"{save_folder}/pin_r{fill_color[0]}_g{fill_color[1]}_b{fill_color[2]}_a{str(alpha).replace('.','')}.png"

    svg_filename = png_path.replace('.png', '.svg')
    
    # Convert the fill_color tuple to a hex color string
    fill_color_hex = f"#{fill_color[0]:02x}{fill_color[1]:02x}{fill_color[2]:02x}"
    
    # Create the SVG document
    root = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", viewBox="0 0 24 24", width="24", height="24")
    path_data = "M12 0C7.03 0 3 4.03 3 9c0 5.25 9 15 9 15s9-9.75 9-15c0-4.97-4.03-9-9-9z"
    
    # Create a path element with the specified fill color and fill-opacity
    path = ET.SubElement(root, 'path', d=path_data, fill=fill_color_hex, fill_opacity=str(alpha))
    
    # Write the SVG file
    tree = ET.ElementTree(root)
    tree.write(svg_filename, pretty_print=True, xml_declaration=True, encoding='utf-8')
    
    # Convert the SVG to a PNG
    cairosvg.svg2png(url=svg_filename, write_to=png_path)
    return png_path

if __name__ == "__main__":
    # Example usage
    res = create_svg_pin("album/15 cameras Stargazer Farm", (50, 50, 200), 0.99)
    print(res)
