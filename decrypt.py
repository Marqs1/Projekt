
from PIL import Image

def extract_text_from_image(image_path):
    # Otw�rz obraz
    image = Image.open(image_path)
    pixels = image.load()

    # Inicjalizacja zmiennych
    binary_text = ""
    extracted_text = ""

    width, height = image.size
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]

            for n in range(3):  # Przechodzimy przez R, G, B
                binary_text += str(pixel[n] & 1)  # Odbieramy LSB

                # Sprawdzamy, czy uzbiera�o si� 8 bit�w (1 bajt)
                if len(binary_text) == 8:
                    character = chr(int(binary_text, 2))
                    if character == "\0":  # Znak ko�ca tekstu
                        return extracted_text
                    extracted_text += character
                    binary_text = ""

    return extracted_text

# Funkcja g��wna
def main():
    image_path = input("Podaj �cie�k� do zaszyfrowanego obrazu: ")
    extracted_text = extract_text_from_image(image_path)
    print("Wyodr�bniony tekst:", extracted_text)

if __name__ == '__main__':
    main()
