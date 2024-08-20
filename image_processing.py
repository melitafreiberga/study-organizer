import cv2
import time
import numpy as np
from fpdf import FPDF
import os
from textblob import TextBlob
import pytesseract
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/Cellar/tesseract/5.4.1/bin/tesseract'


# TAKE AN IMAGE USING WEBCAM
def webcam_frame():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    # Adjust the brightness (values range between 0 and 1, though some systems might allow higher values)
    # cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.8)

    # Adjust contrast (if available)
    # cap.set(cv2.CAP_PROP_CONTRAST, 0.5)

    # Adjust exposure (negative values may work better)
    # cap.set(cv2.CAP_PROP_EXPOSURE, -1)

    # Warm up the webcam to avoid dark frames
    time.sleep(2)
    # Capture a single frame from the webcam
    ret, frame = cap.read()
    # ret is a boolean value: True if the frame is captured successfully, False otherwise
    # frame is the captured image represented as a NumPy array

    # Display the captured frame
    if ret:
        cv2.imshow("Captured Frame", frame)
        cv2.waitKey(0)  # the image window stays open until a key is pressed
    else:
        print("Error: Failed to capture image from the webcam.")
        exit()

    # Release the webcam and close any open windows
    cap.release()
    cv2.destroyAllWindows()
    return frame


# PRE-PROCESS THE IMAGE & DETECT THE DOCUMENT CONTOUR
def contour_detection(image_path):
    # Step 1: Read the Captured Image
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image. Check the path and file existence.")
        exit()

    # Step 2: Gamma Correction to Enhance Contrast
    invGamma = 1.0 / 0.3
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.LUT(gray, table)

    # Step 3: Simple Thresholding
    ret, thresh1 = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)

    # Step 4: Dilation and Erosion (Morphological Closing)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh1, kernel, iterations=1)
    closed = cv2.erode(dilated, kernel, iterations=1)

    # Step 5: Canny Edge Detection
    edged = cv2.Canny(closed, 50, 150)
    cv2.imshow("Canny Edges", edged)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Step 6: Find Contours and Identify the Largest Quadrilateral
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    document_contour = None
    max_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 40000:  # Filter out small contours
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # Check if the contour has four points and is the largest found
            if len(approx) == 4 and area > max_area:
                document_contour = approx  # NumPy array with the coordinates of the vertices
                max_area = area

    # Step 7: Draw the Contour or Convex Hull Around the Detected Document
    if document_contour is not None:
        hull = cv2.convexHull(document_contour)
        cv2.drawContours(image, [hull], -1, (0, 255, 0), 3)
        cv2.imshow("Document Detected", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Document contour not found")
        exit()
    return image, document_contour


# APPLY THE PERSPECTIVE TRANSFORM
def perspective_transform(image, document_contour):
    # Step 1: Ensure the contour points are in the correct order (top-left, top-right, bottom-right, bottom-left)
    def order_points(pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        # The point with the smallest sum is the top-left corner (because both x and y are smallest)
        # and the point with the largest sum is the bottom-right corner
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right
        diff = np.diff(pts, axis=1)
        # The point with the smallest difference is the top-right corner (where x is large, and y is small)
        # and the point with the largest difference is the bottom-left corner (where x is small, and y is large)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left
        return rect

    ordered_points = order_points(document_contour.reshape(4, 2))

    # Step 2: Calculate the width and height of the new image (Euclidean distance)
    (tl, tr, br, bl) = ordered_points

    # Compute the width of the new image, which will be the maximum
    # distance between bottom-right and bottom-left or the top-right and top-left points
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    # Compute the height of the new image, which will be the maximum
    # distance between the top-right and bottom-right or the top-left and bottom-left points
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Step 3: Define the destination points for perspective transform
    dst = np.array([
        [0, 0],  # top-left
        [maxWidth - 1, 0],  # top-right
        [maxWidth - 1, maxHeight - 1],  # bottom-right
        [0, maxHeight - 1]], dtype="float32")  # bottom-left

    # Step 4: Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(ordered_points, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # Step 5: Display the warped image (the "scanned" document)
    cv2.imshow("Warped Image", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return warped


# APPLY BINARIZATION (BLACK & WHITE CONVERSION)
def binarize_image(warped):
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    # Otsu's thresholding
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow("Binarized Image", binary)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return binary


# SHARPEN THE IMAGE
def sharpen_image(processed_image):
    # Sharpening
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(processed_image, -1, kernel)
    cv2.imshow("Sharpened Image", sharpened)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return sharpened


# OPTICAL CHARACTER RECOGNITION
def ocr(final_image):
    # Use pytesseract to do OCR on the image
    extracted_text = pytesseract.image_to_string(final_image, lang='eng')
    # Create a TextBlob object
    # blob = TextBlob(extracted_text)
    # Correct the spelling (issues with changing people's names)
    # corrected_text = blob.correct()
    return extracted_text
    # print("Corrected Text:", corrected_text)


# REVIEW EXTRACTED TEXT
def manual_review_gui(extracted_text):
    layout = BoxLayout(orientation='vertical')

    # TextInput widget for text editing, preloaded with extracted text
    text_input = TextInput(text=extracted_text, multiline=True)
    layout.add_widget(text_input)

    # Save function
    def save_text(instance):
        text = text_input.text
        with open("saved_text.txt", "w") as file:
            file.write(text)
        print("Text saved successfully!")

    # Button to save the text
    save_button = Button(text="Save Text")
    save_button.bind(on_press=save_text)
    layout.add_widget(save_button)

    return layout


# TURN THE FINAL IMAGE INTO A PDF
def turn_into_pdf(final_image):
    # Save the NumPy array as an image file
    image_path = "my_package/non_py_files/final_image.png"
    cv2.imwrite(image_path, final_image)
    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.image(image_path, x=10, y=10, w=190)
    pdf.output("scanned_document.pdf", "F")

    # Open the PDF with the default viewer
    pdf_path = "scanned_document.pdf"
    if os.name == 'nt':  # For Windows
        os.startfile(pdf_path)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f'open "{pdf_path}"')
    else:  # For other systems, try xdg-open
        os.system(f'xdg-open "{pdf_path}"')

    return


# HANDLING USER INTERACTION
class DocumentProcessingApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_state = 'INITIAL'
        self.image = None
        self.document_contour = None
        self.warped = None
        self.processed_image = None
        self.final_image = None
        self.pdf_generated = False

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.question_label = Label(text="Do you want to use a pre-captured image?")
        self.layout.add_widget(self.question_label)

        self.yes_button = Button(text="Yes")
        self.no_button = Button(text="No")

        self.yes_button.bind(on_press=self.on_yes)
        self.no_button.bind(on_press=self.on_no)

        self.layout.add_widget(self.yes_button)
        self.layout.add_widget(self.no_button)

        return self.layout

    def on_yes(self, instance):
        self.process_state('YES')

    def on_no(self, instance):
        self.process_state('NO')

    def process_state(self, user_choice):
        if self.current_state == 'INITIAL':
            if user_choice == 'YES':
                self.handle_image_choice(use_precaptured=True)
            elif user_choice == 'NO':
                self.handle_image_choice(use_precaptured=False)

        elif self.current_state == 'IMAGE_CAPTURED':
            if user_choice == 'YES':
                self.handle_binarization(binarize=True)
            elif user_choice == 'NO':
                self.handle_binarization(binarize=False)

        elif self.current_state == 'BINARIZED':
            if user_choice == 'YES':
                self.handle_ocr()
            elif user_choice == 'NO':
                self.current_state = 'FINAL'
                self.next_question("Do you want to turn the final image into a PDF?")

        elif self.current_state == 'OCR_COMPLETED' or self.current_state == 'FINAL':
            if user_choice == 'YES':
                self.handle_pdf_creation()
            elif user_choice == 'NO':
                self.question_label.text = "This page is for saving the final image"
                self.save_image(self.final_image)
                self.current_state = 'DONE'

    def handle_image_choice(self, use_precaptured):
        try:
            if use_precaptured:
                self.image, self.document_contour = contour_detection("my_package/non_py_files/captured_image2.jpeg")
            else:
                self.image, self.document_contour = contour_detection(webcam_frame())

            self.warped = perspective_transform(self.image, self.document_contour)
            self.current_state = 'IMAGE_CAPTURED'
            self.next_question("Do you want to convert the document to black and white?")

        except FileNotFoundError as e:
            self.question_label.text = f"File not found: {e}"
        except cv2.error as e:
            self.question_label.text = f"Image processing error: {e}"
        except Exception as e:
            self.question_label.text = f"An unexpected error occurred: {e}"

    def handle_binarization(self, binarize):
        try:
            if binarize:
                self.processed_image = binarize_image(self.warped)
            else:
                self.processed_image = self.warped

            self.final_image = sharpen_image(self.processed_image)
            self.current_state = 'BINARIZED'
            self.next_question("Do you want to perform Optical Character Recognition?")

        except cv2.error as e:
            self.question_label.text = f"Image processing error: {e}"
        except Exception as e:
            self.question_label.text = f"An unexpected error occurred: {e}"

    def handle_ocr(self):
        try:
            app = App()
            app.build = lambda: manual_review_gui(ocr(self.final_image))
            app.run()
            self.current_state = 'OCR_COMPLETED'
            self.next_question("Do you want to turn the final image into a PDF?")

        except pytesseract.TesseractNotFoundError as e:
            self.question_label.text = f"Tesseract not found: {e}"
        except pytesseract.TesseractError as e:
            self.question_label.text = f"OCR processing error: {e}"
        except Exception as e:
            self.question_label.text = f"An unexpected error occurred: {e}"

    def handle_pdf_creation(self):
        try:
            turn_into_pdf(self.final_image)
            self.pdf_generated = True
            self.current_state = 'DONE'
            self.question_label.text = "PDF generated successfully!"

        except Exception as e:
            self.question_label.text = f"Error creating PDF: {e}"

    def next_question(self, question):
        self.question_label.text = question

    def save_image(self, instance):
        # Remove yes/no buttons
        self.layout.remove_widget(self.yes_button)
        self.layout.remove_widget(self.no_button)
        # TextInput for the directory path
        self.directory_input = TextInput(hint_text="Enter directory path", multiline=False)
        self.layout.add_widget(self.directory_input)
        # TextInput for the image file name
        self.filename_input = TextInput(hint_text="Enter file name (without extension)", multiline=False)
        self.layout.add_widget(self.filename_input)
        # Button to save the image
        self.save_button = Button(text="Save Image")
        self.save_button.bind(on_press=self.perform_save)
        self.layout.add_widget(self.save_button)
        # Button to skip saving
        self.skip_save_button = Button(text="Don't Save")
        self.skip_save_button.bind(on_press=self.skip_saving)
        self.layout.add_widget(self.skip_save_button)

    def perform_save(self, instance):
        directory = self.directory_input.text.strip()
        filename = self.filename_input.text.strip()

        if not directory or not filename:
            self.question_label.text = "Please enter both directory path and file name"
            return

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                self.question_label.text = f"Directory '{directory}' created."
            except OSError as e:
                self.question_label.text = f"Error: Unable to create directory '{directory}'. {e}"
                return

        image_path = os.path.join(directory, f"{filename}.png")

        try:
            cv2.imwrite(image_path, self.final_image)
            self.question_label.text = f"Image saved successfully at {image_path}."
        except Exception as e:
            self.question_label.text = f"Failed to save the image: {e}"

    def skip_saving(self, instance):
        self.question_label.text = "Image not saved. Process completed."
        self.layout.remove_widget(self.directory_input)
        self.layout.remove_widget(self.filename_input)
        self.layout.remove_widget(self.save_button)
        self.layout.remove_widget(self.skip_save_button)
