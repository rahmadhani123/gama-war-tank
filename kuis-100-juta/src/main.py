import pygame
import sys
import json
import random
import time
import os

# --- Inisialisasi ---
pygame.init()
pygame.mixer.init()

# --- Pengaturan Proyek ---
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))

# --- Pengaturan Layar ---
# Mengatur mode layar penuh
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Kuis 100 Juta")

# --- Warna ---
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
orange = (255, 165, 0)

# --- Font ---
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 40)
question_font = pygame.font.Font(None, 50)
feedback_font = pygame.font.Font(None, 60)

# --- Suara dan Musik ---
try:
    pygame.mixer.music.load(os.path.join(project_root, 'assets', 'sounds', 'background_music.mp3'))
    correct_sound = pygame.mixer.Sound(os.path.join(project_root, 'assets', 'sounds', 'correct_answer.wav'))
    wrong_sound = pygame.mixer.Sound(os.path.join(project_root, 'assets', 'sounds', 'wrong_answer.wav'))
    click_sound = pygame.mixer.Sound(os.path.join(project_root, 'assets', 'sounds', 'button_click.wav'))
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Peringatan: Tidak dapat memuat berkas suara. Game akan berjalan tanpa audio. Error: {e}")
    correct_sound, wrong_sound, click_sound = [pygame.mixer.Sound(buffer=b'') for _ in range(3)]

# --- Fungsi Utilitas ---
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def load_questions(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Layar Game ---
def main_menu():
    while True:
        screen.fill(black)
        draw_text('Kuis 100 Juta', font, white, screen, screen_width / 2, screen_height / 4)
        mx, my = pygame.mouse.get_pos()

        button_start = pygame.Rect(screen_width / 2 - 100, screen_height / 2 - 50, 200, 50)
        button_quit = pygame.Rect(screen_width / 2 - 100, screen_height / 2 + 50, 200, 50)

        pygame.draw.rect(screen, gray, button_start)
        pygame.draw.rect(screen, gray, button_quit)
        draw_text('Mulai', button_font, black, screen, button_start.centerx, button_start.centery)
        draw_text('Keluar', button_font, black, screen, button_quit.centerx, button_quit.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Izinkan keluar dengan tombol Esc
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_start.collidepoint(mx, my):
                    click_sound.play()
                    game()
                if button_quit.collidepoint(mx, my):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

def show_feedback(message, color, duration=2):
    screen.fill(black)
    draw_text(message, feedback_font, color, screen, screen_width / 2, screen_height / 2)
    pygame.display.update()
    time.sleep(duration)

def draw_game_screen(question_data, score, prize_levels, displayed_answers, help_5050_used):
    screen.fill(black)

    # Membungkus teks pertanyaan jika terlalu panjang
    question_lines = []
    words = question_data["question"].split(' ')
    current_line = ""
    for word in words:
        if question_font.size(current_line + " " + word)[0] < screen_width - 100:
            current_line += " " + word
        else:
            question_lines.append(current_line.strip())
            current_line = word
    question_lines.append(current_line.strip())

    line_y = screen_height / 4
    for line in question_lines:
        draw_text(line, question_font, white, screen, screen_width / 2, line_y)
        line_y += question_font.get_linesize()


    draw_text(f"Hadiah: Rp {prize_levels[score]:,}", button_font, white, screen, screen_width / 2, 50)

    button_5050 = pygame.Rect(screen_width - 160, 40, 120, 40)
    if not help_5050_used:
        pygame.draw.rect(screen, orange, button_5050)
        draw_text('50:50', button_font, black, screen, button_5050.centerx, button_5050.centery)

    answer_buttons = []
    button_y = screen_height / 2
    for i, answer in enumerate(displayed_answers):
        if answer:
            button = pygame.Rect(screen_width / 2 - 250, button_y + i * 60, 500, 50)
            answer_buttons.append((button, answer))
            pygame.draw.rect(screen, blue, button)
            draw_text(answer, button_font, white, screen, button.centerx, button.centery)

    pygame.display.update()
    return answer_buttons, button_5050


def game():
    questions = load_questions(os.path.join(project_root, 'questions.json'))
    random.shuffle(questions)
    question_index = 0
    score = 0
    help_5050_used = False

    prize_levels = [0, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 1000000, 5000000, 10000000, 100000000]

    running = True
    while running and question_index < len(questions):
        current_question = questions[question_index]
        correct_answer = current_question["answer"]
        displayed_answers = list(current_question["options"])

        answer_buttons, button_5050 = draw_game_screen(current_question, score, prize_levels, displayed_answers, help_5050_used)

        answered = False
        while not answered:
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    main_menu() # Kembali ke menu utama
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not help_5050_used and button_5050.collidepoint(mx, my):
                        click_sound.play()
                        help_5050_used = True
                        incorrect_answers = [a for a in current_question["options"] if a != correct_answer]
                        random.shuffle(incorrect_answers)
                        for i, answer in enumerate(current_question["options"]):
                            if answer in incorrect_answers[:2]:
                                displayed_answers[i] = None
                        answer_buttons, button_5050 = draw_game_screen(current_question, score, prize_levels, displayed_answers, help_5050_used)

                    for button, answer in answer_buttons:
                        if button.collidepoint(mx, my):
                            click_sound.play()
                            if answer == correct_answer:
                                correct_sound.play()
                                score += 1
                                if score == len(prize_levels) - 1:
                                    show_feedback(f"SELAMAT! ANDA MENANG Rp {prize_levels[score]:,}!", green)
                                    running = False
                                else:
                                    show_feedback("BENAR!", green, duration=1)
                                    question_index += 1
                            else:
                                wrong_sound.play()
                                show_feedback(f"SALAH! Jawaban: {correct_answer}", red)
                                running = False
                            answered = True
                            break

    final_prize = prize_levels[score]
    show_feedback(f"Permainan Selesai! Hadiah Anda: Rp {final_prize:,}", white)

def main():
    main_menu()

if __name__ == "__main__":
    main()
