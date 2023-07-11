# Importing Libraries
from bs4 import BeautifulSoup
import pytesseract
import PIL.Image
import requests
import streamlit as st

# Set Up the Configurations' Options
CONFIG = r"--psm 6 --oem 3"

# Dizy Site
SITE = "https://www.dizy.com"

# Query URL
QUERY = "https://www.dizy.com/it/cruciverba/?q="

# Transform and analyze the image to extract text


def img_to_text(image: bytes) -> str:

    return pytesseract.image_to_string(PIL.Image.open(image), config=CONFIG)

# Function for cleaning data and splitting the clues


def clean_and_split_clues(text: str) -> list:

    # Clean the data
    text = text.replace(
        "ORIZZONTALI",
        "").replace(
        "VERTICALI",
        "").replace(
            ":",
            "").replace(
                "-",
                "").replace(
                    "_",
                    "").replace(
                        ".",
        "")
    not_filtered_list = text.split()

    # Split the clues
    cleared_clues = []
    current_clue = ""
    for word in not_filtered_list:
        if word.isdigit() and len(word) not in [3, 4]:
            if current_clue:
                cleared_clues.append(current_clue.strip())
                current_clue = ""
        else:
            current_clue += f"{word} "
    if current_clue:
        cleared_clues.append(current_clue.strip())

    return cleared_clues

# Solve the clues scraping on the clues site, pairing the answers


def solve_clues(clues: list, bar=None) -> dict:
    answers = {}

    if bar is not None:
        increment = 0
        add = 100 // len(clues)

    for i, phrase in enumerate(clues):
        if bar is not None:
            increment += add
            bar.progress(increment, "Resolving Clues...")

        url = QUERY + phrase
        source = requests.get(url).text
        soup = BeautifulSoup(source, "html.parser")

        ul = soup.find("ul")
        if ul is not None:
            href = ul.find("a")
            if href is not None:
                link = SITE + href["href"]
                source = requests.get(link).text
                soup = BeautifulSoup(source, "html.parser")

                table = soup.find("table")
                if table is not None:
                    answer = table.find("b")
                    if answer is not None:
                        answers[clues[i]] = answer.text

    if bar is not None:
        bar.progress(100, "Finished!")

    return answers


# Main program
if __name__ == "__main__":

    # Modifiyng App name and icon
    st.set_page_config(
        page_title='Crossword Solver',
        page_icon="favicon.ico",
        layout="centered")

    # Title of the Program
    st.title("Crossword Solver")

    # Creating a Camera input to take photos
    image = st.camera_input(".", label_visibility="hidden")

    # Check if an image is being inserted
    if image is not None:

        with st.spinner("Extracting text..."):
            # Extract text from the image
            text = img_to_text(image)

            # Find the clues
            clues = clean_and_split_clues(text)

        # Creating a progress bar
        bar = st.progress(0, "Resolving Clues...")

        # Finding the clue's answers
        answers = solve_clues(clues, bar)

        # Looping through the result and displaying the answers
        for clue, answer in answers.items():
            st.markdown(f"{clue} -> **{answer}**")