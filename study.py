import tkinter as tk
def show_study_window(main_win, settings):

    def on_closing():
        main_win.attributes('-disabled', False)
        main_win.deiconify()
        root.destroy()

    main_win.attributes('-disabled', True)
    main_win.iconify()
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title("HardStudy")
    root.iconbitmap('icon.ico')
    window_width = 600
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    tk.Label(root, text="Переведите:").grid(row=1, column=1, padx=3, pady=3)
    phrase = tk.Label(root, text="hello")
    phrase.grid(row=1, column=2, padx=3, pady=3)

    def on_entry_change(event):
        # Получаем текущий текст из строки ввода
        text = meaning.get()
        text_len = len(text)
        #for c in text:
        print(text[text_len-1])

    #     # Устанавливаем отфильтрованный текст обратно в строку ввода
    #     entry.delete(0, tk.END)
    #     entry.insert(0, filtered_text)

    tk.Label(root, text="Значение:").grid(row=2, column=1, padx=3, pady=3)
    meaning = tk.Entry(root, width=30)
    meaning.grid(row=2, column=2, padx=3, pady=3)
    meaning.bind("<KeyRelease>", on_entry_change)

    root.mainloop()