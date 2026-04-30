import json
import os
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

DATA_FILE = "favorites.json"


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        self.favorites = []
        self.load_favorites()

        self.create_widgets()
        self.update_favorites_list()

    def create_widgets(self):
        # Рамка поиска
        search_frame = ttk.LabelFrame(self.root, text="Поиск пользователей GitHub", padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Имя пользователя:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<Return>", lambda e: self.search_users())

        search_btn = ttk.Button(search_frame, text="Поиск", command=self.search_users)
        search_btn.grid(row=0, column=2, padx=5, pady=5)

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("username", "html_url")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        self.results_tree.heading("username", text="Логин")
        self.results_tree.heading("html_url", text="Профиль")

        self.results_tree.column("username", width=200)
        self.results_tree.column("html_url", width=500)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки для результатов
        results_buttons = ttk.Frame(results_frame)
        results_buttons.pack(fill="x", pady=5)

        add_fav_btn = ttk.Button(results_buttons, text="★ Добавить в избранное", command=self.add_to_favorites)
        add_fav_btn.pack(side="left", padx=5)

        view_profile_btn = ttk.Button(results_buttons, text="Открыть профиль", command=self.open_profile)
        view_profile_btn.pack(side="left", padx=5)

        # Избранное
        fav_frame = ttk.LabelFrame(self.root, text="★ Избранные пользователи", padding=10)
        fav_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns_fav = ("username", "html_url")
        self.fav_tree = ttk.Treeview(fav_frame, columns=columns_fav, show="headings", height=5)

        self.fav_tree.heading("username", text="Логин")
        self.fav_tree.heading("html_url", text="Профиль")

        self.fav_tree.column("username", width=200)
        self.fav_tree.column("html_url", width=500)

        fav_scrollbar = ttk.Scrollbar(fav_frame, orient="vertical", command=self.fav_tree.yview)
        self.fav_tree.configure(yscrollcommand=fav_scrollbar.set)

        self.fav_tree.pack(side="left", fill="both", expand=True)
        fav_scrollbar.pack(side="right", fill="y")

        # Кнопки для избранного
        fav_buttons = ttk.Frame(fav_frame)
        fav_buttons.pack(fill="x", pady=5)

        remove_fav_btn = ttk.Button(fav_buttons, text="✖ Удалить из избранного", command=self.remove_from_favorites)
        remove_fav_btn.pack(side="left", padx=5)

        open_fav_btn = ttk.Button(fav_buttons, text="Открыть профиль", command=self.open_favorite_profile)
        open_fav_btn.pack(side="left", padx=5)

    def search_users(self):
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showerror("Ошибка", "Поле поиска не может быть пустым!")
            return

        try:
            url = f"https://api.github.com/search/users?q={query}&per_page=20"
            req = urllib.request.Request(url, headers={"User-Agent": "GitHub-User-Finder"})
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                users = data.get("items", [])

            if not users:
                messagebox.showinfo("Результат", "Пользователи не найдены")
                return

            # Очищаем таблицу результатов
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # Добавляем результаты
            for user in users:
                self.results_tree.insert("", "end", values=(
                    user["login"],
                    user["html_url"]
                ))

            messagebox.showinfo("Успех", f"Найдено пользователей: {len(users)}")

        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка", f"Ошибка сети: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def add_to_favorites(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        item = self.results_tree.item(selected[0])
        username = item["values"][0]
        profile_url = item["values"][1]

        # Проверка, не добавлен ли уже
        for fav in self.favorites:
            if fav["username"] == username:
                messagebox.showwarning("Предупреждение", "Этот пользователь уже в избранном!")
                return

        self.favorites.append({
            "username": username,
            "html_url": profile_url
        })

        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")

    def remove_from_favorites(self):
        selected = self.fav_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из избранного!")
            return

        item = self.fav_tree.item(selected[0])
        username = item["values"][0]

        self.favorites = [fav for fav in self.favorites if fav["username"] != username]
        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Успех", f"Пользователь {username} удалён из избранного!")

    def open_profile(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя!")
            return

        item = self.results_tree.item(selected[0])
        url = item["values"][1]
        webbrowser.open(url)

    def open_favorite_profile(self):
        selected = self.fav_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя!")
            return

        item = self.fav_tree.item(selected[0])
        url = item["values"][1]
        webbrowser.open(url)

    def update_favorites_list(self):
        # Очищаем список
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)

        # Заполняем избранными
        for fav in self.favorites:
            self.fav_tree.insert("", "end", values=(
                fav["username"],
                fav["html_url"]
            ))

    def load_favorites(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
            except json.JSONDecodeError:
                self.favorites = []

    def save_favorites(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
