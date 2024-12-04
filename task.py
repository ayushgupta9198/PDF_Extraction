import os
import openai
import json
from PyPDF2 import PdfReader

"""you can paste your openai key here """

openai.api_key = "" 


# Function: Extract text from a PDF file
def extract_pdf_text(file_path):
    try:
        reader = PdfReader(file_path)
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text.strip())
        return "\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

# Function: Query OpenAI model with content and user questions
def get_answers_from_model(pdf_text, user_question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant answering questions based on provided content. Match answers word-to-word if possible."},
                {"role": "user", "content": f"Content:\n{pdf_text}\nQuestion: {user_question}"}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        if "I am not sure" in answer or len(answer.split()) < 3:  # Check for low confidence
            return "Data Not Available"
        return answer
    except Exception as e:
        return "Data Not Available"

# Function: Check word-to-word match
def word_to_word_match(question, pdf_text):
    lines = pdf_text.splitlines()
    for line in lines:
        if question.lower() in line.lower():
            return line.strip()
    return None

# Function: Display answers line by line and generate JSON blob
def process_question(pdf_text, question):
    exact_match = word_to_word_match(question, pdf_text)
    if exact_match:
        return {"question": question, "answer": exact_match}

    answer = get_answers_from_model(pdf_text, question)
    return {"question": question, "answer": answer}

# Chatbot-like interface for user interaction
def chatbot_interface():
    print("Welcome to the PDF Q&A Assistant!")
    pdf_path = input("Please provide the path to your PDF file: ").strip()

    if not os.path.exists(pdf_path):
        print("Error: PDF file not found.")
        return

    try:
        pdf_content = extract_pdf_text(pdf_path)
    except ValueError as e:
        print(str(e))
        return

    print("\nPDF content successfully loaded. You can now ask questions!")
    print("Type 'exit' to quit the chatbot.\n")

    questions_and_answers = []
    while True:
        question = input("Ask a question: ").strip()
        if question.lower() == "exit":
            print("Exiting the chatbot. Goodbye!")
            break

        response = process_question(pdf_content, question)
        questions_and_answers.append(response)
        print(f"Q: {response['question']}")
        print(f"A: {response['answer']}\n")

    # Generate structured JSON blob
    output = {"results": questions_and_answers}
    print("\nStructured JSON Output:")
    print(json.dumps(output, indent=4))

# Entry point for the program
if __name__ == "__main__":
    chatbot_interface()
