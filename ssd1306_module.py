import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class Display:
    def __init__(self):
        # Raspberry Pi pin configuration:
        RST = None  # Not using the RST pin
        
        # Create an SSD1306 display instance
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        
        # Initialize the display
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        
        # Create an image with a black background
        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Load font with size 14
        self.font_size = 14
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', self.font_size)
        
    def new_text(self, text, x=0, y=0, font_size=None):
        # Clear the previous text
        self.clear()
        self.text(text,x,y,font_size)
        
    def text(self, text, x=0, y=0, font_size=None):
        # Use the default font size if font_size is not provided
        if font_size is not None:
            self.font_size = font_size
            self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', self.font_size)
  
        # Write the new text on the image
        self.draw.text((x, y), text, font=self.font, fill=1)
        
        # Display the updated image on the screen
        self.disp.image(self.image)
        self.disp.display()
        
    def clear(self):
        # Clear the previous text
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)
        
    def new_text_1st_half(self, text, font_size=None):
        # Clear the previous text
        self.draw.rectangle((0, 0, 128, 16), outline=0, fill=0)
        self.text(text,0,0,font_size)
        
    def new_text_2nd_half(self, text, font_size=None):
        # Clear the previous text
        self.draw.rectangle((0, 16, 128, 32), outline=0, fill=0)
        self.text(text,0,17,font_size)
