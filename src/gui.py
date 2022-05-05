from translator import *
import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Logic Translator")

CANVAS_WIDTH  = 400
CANVAS_HEIGHT = 400

canvas = tk.Canvas(window, width = CANVAS_WIDTH, height = CANVAS_HEIGHT,  relief = 'raised')
canvas.pack()

label_INTRO_MSG = tk.Label(window, text='Translate a logical formula to plain English!')
label_INTRO_MSG.config(font=('Noto Sans Display', 14))
canvas.create_window(CANVAS_WIDTH/2, 25, window=label_INTRO_MSG)

label_HELP_MSG = tk.Label(window, text='Type "help" to see example inputs')
label_HELP_MSG.config(font=('Noto Sans Display', 10, 'italic'))
canvas.create_window(CANVAS_WIDTH/2, 50, window=label_HELP_MSG)

label_INPUT_PROMPT = tk.Label(window, text='Enter a propositional formula')
label_INPUT_PROMPT.config(font=('helvetica', 12, 'bold'))
canvas.create_window(CANVAS_WIDTH/2, 100, window=label_INPUT_PROMPT)

entry1 = tk.Entry (window, justify='center', width=int(CANVAS_WIDTH*0.7)) 
canvas.create_window(CANVAS_WIDTH/2, 140, window=entry1)




def get_translation():
    
    formula = entry1.get()
    bad_input = False
    
    if formula == "help":
        print("HELP MENU")
    
    try: 
        translation = translate(formula)
    except Exception as e:
        if formula == 'help':
            tk.messagebox.showinfo("my message",
                                   """
                                   \n• Parentheses establish precedence
                                   \n• Quantifiers must surround operand with parentheses
                                   \nValid Formulas:
                                   \nP ∧ Q
                                   \nR ∨ S
                                   \nP ⇒ Q
                                   \n(P ∧ Q) ⇒ (P ∧ Q)
                                   """)
        
        else:
            tk.messagebox.showerror("error", f"Malformed Input")

        return
    
    label_offset = 30
    label3 = tk.Label(window, text= formula, font=('MathJax_Main', 15))
    canvas.create_window(CANVAS_WIDTH/2, 230, window=label3)    
    
    label4 = tk.Label(window, text= 'translates to',font=('helvetica', 12, 'bold'))
    canvas.create_window(CANVAS_WIDTH/2, 230+label_offset, window=label4)
    
    label5 = tk.Label(window, text= translation,font=('DejaVu Math TeX Gyre', 12), fg='#137029')
    canvas.create_window(CANVAS_WIDTH/2, 230+(2*label_offset), window=label5)

    
button1 = tk.Button(text='TRANSLATE!', command=get_translation, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas.create_window(CANVAS_WIDTH/2, 180, window=button1)

window.mainloop()
