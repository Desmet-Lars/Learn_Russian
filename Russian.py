import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import json
import os
import random
import time  # For tracking response time

class DuolingoLitePlus:
    def __init__(self, root):
        self.root = root
        self.root.title("Duolingo Lite Plus")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.user_profile = self.load_profile()
        self.skills = {
            "Russian Alphabet": {
                "questions": [
                    {"type": "multiple_choice", "question": "What is the Russian letter for 'A'?", "options": ["А", "Б", "В", "Г"], "answer": "А"},
                    {"type": "multiple_choice", "question": "What is the Russian letter for 'B'?", "options": ["А", "Б", "В", "Г"], "answer": "Б"},
                    {"type": "multiple_choice", "question": "What is the Russian letter for 'V'?", "options": ["А", "Б", "В", "Г"], "answer": "В"},
                    {"type": "multiple_choice", "question": "What is the Russian letter for 'G'?", "options": ["А", "Б", "В", "Г"], "answer": "Г"},
                    {"type": "typing", "question": "Type the letter 'Д'", "answer": "Д"}
                ],
                "completed": self.user_profile.get("completed_lessons", {}).get("Russian Alphabet", False),
            },
            "Basics 1": {
                "questions": [
                    {"type": "multiple_choice", "question": "What is 'cat' in Russian?", "options": ["Кошка", "Собака", "Машина", "Стол"], "answer": "Кошка"},
                    {"type": "translation", "question": "Translate to Russian: 'dog'", "answer": "Собака"},
                    {"type": "multiple_choice", "question": "What is 'house' in Russian?", "options": ["Дом", "Книга", "Стол", "Ручка"], "answer": "Дом"},
                    {"type": "typing", "question": "Type 'book' in Russian", "answer": "Книга"},
                    {"type": "multiple_choice", "question": "What is 'friend' in Russian?", "options": ["Друг", "Враг", "Собака", "Кошка"], "answer": "Друг"}
                ],
                "completed": self.user_profile.get("completed_lessons", {}).get("Basics 1", False),
            },
            "Basics 2": {
                "questions": [
                    {"type": "multiple_choice", "question": "What is 'water' in Russian?", "options": ["Вода", "Хлеб", "Молоко", "Чай"], "answer": "Вода"},
                    {"type": "translation", "question": "Translate to Russian: 'apple'", "answer": "Яблоко"},
                    {"type": "typing", "question": "Type 'school' in Russian", "answer": "Школа"},
                    {"type": "multiple_choice", "question": "What is 'table' in Russian?", "options": ["Стол", "Стул", "Окно", "Дверь"], "answer": "Стол"},
                    {"type": "typing", "question": "Type 'teacher' in Russian", "answer": "Учитель"}
                ],
                "completed": self.user_profile.get("completed_lessons", {}).get("Basics 2", False),
            }
        }

        self.current_skill = None
        self.current_question_index = 0
        self.xp = self.user_profile.get("xp", 0)
        self.streak = self.user_profile.get("streak", 0)
        self.incorrect_answers = []
        self.current_phase = "multiple_choice"  # Phase can be "multiple_choice" or "typing"
        self.last_answer_time = None  # To track the time taken to answer
        self.correct_answer_streak = 0  # To track consecutive correct answers

        self.create_main_menu()

    def load_profile(self):
        if os.path.exists("user_profile.json"):
            with open("user_profile.json", "r") as file:
                profile = json.load(file)
                if "completed_lessons" not in profile:
                    profile["completed_lessons"] = {}
                return profile
        else:
            return {"xp": 0, "streak": 0, "completed_lessons": {}, "correct_answer_streak": 0}

    def save_profile(self):
        self.user_profile["correct_answer_streak"] = self.correct_answer_streak
        with open("user_profile.json", "w") as file:
            json.dump(self.user_profile, file, indent=4)

    def create_main_menu(self):
        self.clear_window()

        title_label = ctk.CTkLabel(self.root, text="Duolingo Lite Plus", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        skill_tree_label = ctk.CTkLabel(self.root, text="Skill Tree", font=ctk.CTkFont(size=18, weight="bold"))
        skill_tree_label.pack(pady=10)

        for skill in self.skills:
            state = "normal" if self.is_skill_unlocked(skill) else "disabled"
            btn = ctk.CTkButton(self.root, text=skill, font=ctk.CTkFont(size=16), state=state, command=lambda s=skill: self.start_skill(s))
            btn.pack(pady=5)

        exit_btn = ctk.CTkButton(self.root, text="Exit", font=ctk.CTkFont(size=14), command=self.root.quit)
        exit_btn.pack(pady=20)

        stats_label = ctk.CTkLabel(self.root, text=f"XP: {self.xp} | Streak: {self.streak} days | Correct Answer Streak: {self.correct_answer_streak}", font=ctk.CTkFont(size=14))
        stats_label.pack(pady=10)

    def is_skill_unlocked(self, skill):
        if skill == "Russian Alphabet":
            return True
        previous_skill = list(self.skills.keys())[list(self.skills.keys()).index(skill) - 1]
        return self.skills[previous_skill]["completed"]

    def start_skill(self, skill):
        self.current_skill = skill
        self.current_question_index = 0
        self.incorrect_answers = []
        self.current_phase = "multiple_choice"
        self.show_vocabulary_review()

    def show_vocabulary_review(self):
        self.clear_window()
        questions = self.skills[self.current_skill]["questions"]

        if not self.skills[self.current_skill]["completed"]:
            if self.current_phase == "multiple_choice":
                self.show_vocabulary_question()
            elif self.current_phase == "typing":
                self.show_typing_questions()
        else:
            messagebox.showinfo("Lesson Complete", f"You've already completed the {self.current_skill} lesson.")
            self.create_main_menu()

    def show_vocabulary_question(self):
        self.clear_window()

        if self.current_question_index < len(self.skills[self.current_skill]["questions"]):
            question = self.skills[self.current_skill]["questions"][self.current_question_index]
            question_type = question["type"]

            # Record the time when the question is shown
            self.last_answer_time = time.time()

            if question_type == "multiple_choice":
                self.show_multiple_choice_question(question)
            elif question_type == "translation":
                self.show_translation_question(question)
            elif question_type == "typing":
                self.show_typing_question(question)
        else:
            self.current_phase = "typing"
            self.current_question_index = 0
            self.show_vocabulary_review()  # Switch to typing phase

    def show_multiple_choice_question(self, question):
        question_label = ctk.CTkLabel(self.root, text=question["question"], font=ctk.CTkFont(size=18))
        question_label.pack(pady=20)

        options = question["options"]
        random.shuffle(options)
        for option in options:
            btn = ctk.CTkButton(self.root, text=option, font=ctk.CTkFont(size=14),
                                command=lambda opt=option: self.check_vocabulary_answer(opt, question["answer"]))
            btn.pack(pady=5)

    def show_translation_question(self, question):
        question_label = ctk.CTkLabel(self.root, text=question["question"], font=ctk.CTkFont(size=18))
        question_label.pack(pady=20)

        answer_entry = ctk.CTkEntry(self.root, font=ctk.CTkFont(size=14))
        answer_entry.pack(pady=10)

        submit_btn = ctk.CTkButton(self.root, text="Submit", font=ctk.CTkFont(size=14),
                                  command=lambda: self.check_translation_answer(answer_entry.get(), question["answer"]))
        submit_btn.pack(pady=10)

    def show_typing_questions(self):
        self.clear_window()

        if self.current_question_index < len(self.skills[self.current_skill]["questions"]):
            question = self.skills[self.current_skill]["questions"][self.current_question_index]
            question_type = question["type"]

            if question_type == "typing":
                self.show_typing_question(question)
        else:
            self.complete_vocabulary_lesson()

    def show_typing_question(self, question):
        question_label = ctk.CTkLabel(self.root, text=question["question"], font=ctk.CTkFont(size=18))
        question_label.pack(pady=20)

        answer_entry = ctk.CTkEntry(self.root, font=ctk.CTkFont(size=14))
        answer_entry.pack(pady=10)

        self.show_russian_keyboard(answer_entry)  # Show the on-screen keyboard

        submit_btn = ctk.CTkButton(self.root, text="Submit", font=ctk.CTkFont(size=14),
                                  command=lambda: self.check_typing_answer(answer_entry.get(), question["answer"]))
        submit_btn.pack(pady=10)

    def show_russian_keyboard(self, entry):
        keyboard_frame = ctk.CTkFrame(self.root)
        keyboard_frame.pack(pady=10)

        # Russian Keyboard Layout
        keys = [
            "Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З", "Х", "Ъ",
            "Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д", "Ж", "Э",
            "Я", "Ч", "С", "М", "И", "Т", "Ь", "Б", "Ю"
        ]

        def on_key_press(key):
            entry.insert(tk.END, key)

        for key in keys:
            btn = ctk.CTkButton(keyboard_frame, text=key, width=40, height=40,
                                command=lambda k=key: on_key_press(k))
            btn.grid(row=keys.index(key) // 10, column=keys.index(key) % 10, padx=2, pady=2)

    def check_vocabulary_answer(self, selected, correct):
        if selected.strip() == correct.strip():
            self.xp += 10
            self.correct_answer_streak += 1
            time_taken = time.time() - self.last_answer_time
            messagebox.showinfo("Correct!", f"Great job! +10 XP\nTime Taken: {int(time_taken)} seconds")
        else:
            self.correct_answer_streak = 0
            messagebox.showerror("Incorrect", f"The correct answer was: {correct}")

        self.current_question_index += 1
        if self.current_question_index < len(self.skills[self.current_skill]["questions"]):
            self.show_vocabulary_question()
        else:
            self.current_phase = "typing"
            self.current_question_index = 0
            self.show_vocabulary_review()  # Switch to typing phase

    def check_translation_answer(self, entered, correct):
        if entered.strip() == correct.strip():
            self.xp += 10
            self.correct_answer_streak += 1
            time_taken = time.time() - self.last_answer_time
            messagebox.showinfo("Correct!", f"Great job! +10 XP\nTime Taken: {int(time_taken)} seconds")
        else:
            self.correct_answer_streak = 0
            messagebox.showerror("Incorrect", f"The correct answer was: {correct}")

        self.current_question_index += 1
        if self.current_question_index < len(self.skills[self.current_skill]["questions"]):
            self.show_vocabulary_review()
        else:
            self.complete_vocabulary_lesson()

    def check_typing_answer(self, entered, correct):
        if entered.strip() == correct.strip():
            self.xp += 10
            self.correct_answer_streak += 1
            time_taken = time.time() - self.last_answer_time
            messagebox.showinfo("Correct!", f"Great job! +10 XP\nTime Taken: {int(time_taken)} seconds")
        else:
            self.correct_answer_streak = 0
            messagebox.showerror("Incorrect", f"The correct answer was: {correct}")

        self.current_question_index += 1
        if self.current_question_index < len(self.skills[self.current_skill]["questions"]):
            self.show_typing_questions()
        else:
            self.complete_vocabulary_lesson()

    def complete_vocabulary_lesson(self):
        self.skills[self.current_skill]["completed"] = True
        if "completed_lessons" not in self.user_profile:
            self.user_profile["completed_lessons"] = {}

        self.user_profile["completed_lessons"][self.current_skill] = True
        self.user_profile["xp"] = self.xp
        self.user_profile["streak"] = self.streak
        self.user_profile["correct_answer_streak"] = self.correct_answer_streak
        self.save_profile()

        messagebox.showinfo("Skill Complete", f"Congratulations! You completed the {self.current_skill} lesson.")
        self.create_main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = DuolingoLitePlus(root)
    root.mainloop()
