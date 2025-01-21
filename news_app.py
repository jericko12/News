from newsapi import NewsApiClient
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta, timezone
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from ttkthemes import ThemedStyle
import os
from pathlib import Path
import json
import tempfile
try:
    from config import API_KEY
except ImportError:
    API_KEY = ''  # or prompt user to enter key

class NewsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News App")
        self.root.geometry("1200x800")
        
        # Initialize variables first
        self.font_size_var = tk.StringVar(value="11")
        self.current_font_size = 11
        
        # Configure style
        self.configure_styles()
        
        # Initialize News API
        if not API_KEY:
            self.show_api_key_dialog()
        self.newsapi = NewsApiClient(api_key=API_KEY)
        
        # Create status bar first (moved up)
        self.create_status_bar()
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="10", style='Main.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Create GUI elements
        self.create_header()
        self.create_search_frame()
        self.create_results_area()
        
        # Initialize page counter
        self.current_page = 1
        
        # Default view - show top headlines
        self.show_top_headlines()
        
        # Load settings
        self.load_settings()

    def configure_styles(self):
        style = ThemedStyle(self.root)
        style.set_theme("arc")
        
        # Initialize colors dictionary
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'primary_light': '#BBDEFB',
            'secondary': '#FF4081',
            'background': '#FAFAFA',
            'surface': '#FFFFFF',
            'error': '#F44336',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'text': '#212121',
            'text_secondary': '#757575',
            'divider': '#EEEEEE',
            'card_bg': '#ffffff',
            'card_border': '#e0e0e0',
            'hover': '#f5f5f5',
            'accent': '#FF4081',
            'link': '#1976D2'
        }
        
        # Configure styles
        style.configure('Card.TFrame',
                       background=self.colors['card_bg'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('CardHover.TFrame',
                       background=self.colors['hover'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Category.TButton',
                       font=('Helvetica', 10),
                       padding=8)
        style.map('Category.TButton',
                 background=[('active', self.colors['primary_light'])],
                 foreground=[('active', self.colors['primary_dark'])])
        
        style.configure('Link.TLabel',
                       foreground=self.colors['link'],
                       font=('Helvetica', 10, 'underline'))
        
        # Enhanced header style
        style.configure('Header.TLabel', 
                       font=('Helvetica', 28, 'bold'), 
                       padding=15, 
                       foreground=self.colors['primary'])
        
        # Enhanced button styles
        style.configure('Action.TButton', 
                       font=('Helvetica', 10, 'bold'),
                       padding=8)
        style.map('Action.TButton',
                 background=[('active', self.colors['primary_light']),
                            ('pressed', self.colors['primary_dark'])],
                 foreground=[('active', 'white'),
                            ('pressed', 'white')])

        # Enhanced treeview style
        style.configure('Article.Treeview',
                       font=('Helvetica', 11),
                       rowheight=50,
                       background=self.colors['surface'],
                       fieldbackground=self.colors['surface'],
                       borderwidth=0)
        style.map('Article.Treeview',
                 background=[('selected', self.colors['primary_light'])],
                 foreground=[('selected', self.colors['text'])])

    def bind_shortcuts(self):
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        self.root.bind('<Control-r>', lambda e: self.show_top_headlines())
        self.root.bind('<Control-Left>', lambda e: self.previous_page())
        self.root.bind('<Control-Right>', lambda e: self.next_page())
        self.root.bind('<Control-l>', lambda e: self.clear_search())

    def focus_search(self):
        search_entry = self.root.focus_get()
        if isinstance(search_entry, ttk.Entry):
            search_entry.selection_range(0, tk.END)
            search_entry.focus_set()

    def create_header(self):
        header_frame = ttk.Frame(self.main_container, style='Surface.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo and title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        logo_label = ttk.Label(title_frame, text="📰", font=('Helvetica', 32))
        logo_label.pack(side=tk.LEFT, padx=(10, 5))
        
        title_label = ttk.Label(title_frame, text="News Explorer", style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Stats frame
        self.stats_frame = ttk.Frame(header_frame)
        self.stats_frame.pack(side=tk.RIGHT, padx=10)
        
        self.update_stats()

    def update_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if hasattr(self, 'total_results'):
            ttk.Label(self.stats_frame, 
                     text=f"Total Articles: {self.total_results:,}",
                     font=('Helvetica', 10, 'bold'),
                     foreground=self.colors['primary']).pack(side=tk.RIGHT, padx=5)

    def create_search_frame(self):
        search_frame = ttk.Frame(self.main_container, style='Surface.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        # Search entry with placeholder
        search_container = ttk.Frame(search_frame)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        search_icon = ttk.Label(search_container, text="🔍")
        search_icon.pack(side=tk.LEFT, padx=(5, 0))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_container, 
                               textvariable=self.search_var,
                               font=('Helvetica', 11),
                               width=50)
        search_entry.insert(0, "Search news...")
        search_entry.bind('<FocusIn>', lambda e: self.on_entry_click(search_entry))
        search_entry.bind('<FocusOut>', lambda e: self.on_focus_out(search_entry))
        search_entry.bind('<Return>', lambda e: self.search_news())
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Add search suggestions
        self.suggestion_frame = ttk.Frame(search_container)
        self.suggestion_frame.pack(fill=tk.X, expand=True)
        self.suggestion_frame.pack_forget()  # Hide initially
        
        search_entry.bind('<KeyRelease>', self.show_search_suggestions)

        # Button frame with improved layout
        button_frame = ttk.Frame(search_frame, style='Surface.TFrame')
        button_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        self.create_action_button(button_frame, "🔍 Search", self.search_news)
        self.create_action_button(button_frame, "📰 Headlines", self.show_top_headlines)
        self.create_action_button(button_frame, "⌫ Clear", self.clear_search)
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        self.create_action_button(button_frame, "◀", self.previous_page)
        self.create_action_button(button_frame, "▶", self.next_page)

    def create_action_button(self, parent, text, command):
        btn = ttk.Button(parent, text=text, command=command, style='Action.TButton')
        btn.pack(side=tk.LEFT, padx=2)
        return btn

    def create_results_area(self):
        # Create paned window with improved styling
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=5)

        # List frame with better organization
        list_frame = ttk.Frame(self.paned_window, style='Surface.TFrame')
        self.paned_window.add(list_frame, weight=1)

        # Add category filter
        filter_frame = ttk.Frame(list_frame, style='Surface.TFrame')
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT)
        sort_options = ["Newest", "Relevance", "Popular"]
        self.sort_var = tk.StringVar(value=sort_options[0])
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var, 
                                 values=sort_options, state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_news())

        # Enhanced article list
        self.article_list = ttk.Treeview(list_frame, 
                                        columns=("title", "source", "published"),
                                        show="headings",
                                        selectmode="browse",
                                        style='Article.Treeview')
        
        self.article_list.heading("title", text="Title", anchor=tk.W)
        self.article_list.heading("source", text="Source", anchor=tk.W)
        self.article_list.heading("published", text="Published", anchor=tk.W)
        
        self.article_list.column("title", width=400, anchor=tk.W)
        self.article_list.column("source", width=100, anchor=tk.W)
        self.article_list.column("published", width=150, anchor=tk.W)
        
        self.article_list.pack(fill=tk.BOTH, expand=True, padx=5)
        self.article_list.bind('<<TreeviewSelect>>', self.on_article_select)

        # Add scrollbar to article list
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                     command=self.article_list.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.article_list.configure(yscrollcommand=list_scrollbar.set)

        # Create detail frame with improved styling
        detail_frame = ttk.Frame(self.paned_window, style='Surface.TFrame')
        self.paned_window.add(detail_frame, weight=1)

        # Create detail view with better styling
        self.create_detail_view(detail_frame)

    def create_detail_view(self, detail_frame):
        # Create notebook for multiple views
        self.detail_notebook = ttk.Notebook(detail_frame)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Article view tab
        article_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(article_frame, text="📄 Article")
        
        # Create toolbar for article view
        toolbar = ttk.Frame(article_frame, style='Surface.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls
        controls_frame = ttk.Frame(toolbar)
        controls_frame.pack(side=tk.LEFT)
        
        # Font size controls with labels
        ttk.Label(controls_frame, text="Text Size:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(controls_frame, text="A-", 
                   command=lambda: self.change_text_size(-1),
                   style='Action.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Label(controls_frame, textvariable=self.font_size_var).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="A+", 
                   command=lambda: self.change_text_size(1),
                   style='Action.TButton').pack(side=tk.LEFT, padx=2)
        
        # Action buttons with icons
        actions_frame = ttk.Frame(toolbar)
        actions_frame.pack(side=tk.RIGHT)
        
        self.create_action_button(actions_frame, "🔗 Share", self.share_article)
        self.create_action_button(actions_frame, "🌐 Browser", self.open_in_browser)
        self.create_action_button(actions_frame, "📋 Copy", self.copy_article_text)
        self.create_action_button(actions_frame, "⭐ Save", self.save_article)
        
        # Create detail text widget with read-only state
        self.detail_text = scrolledtext.ScrolledText(
            article_frame, 
            wrap=tk.WORD,
            font=('Helvetica', 11),
            padx=15,
            pady=15,
            background=self.colors['surface'],
            foreground=self.colors['text'],
            state='disabled'  # Make text widget read-only
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Related articles tab
        related_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(related_frame, text="Related")
        
        self.related_list = ttk.Treeview(related_frame,
                                        columns=("title", "source"),
                                        show="headings",
                                        style='Article.Treeview')
        self.related_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add saved articles tab
        self.create_saved_articles_frame()
        
        # Set default font size
        self.current_font_size = 11

    def change_text_size(self, delta):
        self.current_font_size = max(8, min(20, self.current_font_size + delta))
        self.font_size_var.set(str(self.current_font_size))
        self.detail_text.configure(font=('Helvetica', self.current_font_size))
        self.save_settings()

    def share_article(self):
        selection = self.article_list.selection()
        if not selection:
            return

        article_index = int(selection[0])
        article = self.current_articles[article_index]
        url = article.get('url', '')
        
        if url:
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            
            # Show success message
            self.show_success("Article URL copied to clipboard!")

    def show_success(self, message):
        self.loading_var.set(f"✅ {message}")
        self.loading_label.configure(foreground=self.colors['success'])
        self.root.after(3000, self.clear_status)

    def clear_status(self):
        self.loading_var.set("")
        self.loading_label.configure(foreground=self.colors['text'])

    def create_status_bar(self):
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        self.loading_var = tk.StringVar(value="")
        self.loading_label = ttk.Label(self.status_frame, textvariable=self.loading_var)
        self.loading_label.pack(side=tk.LEFT, padx=5)

    def on_entry_click(self, entry):
        if entry.get() == "Search news...":
            entry.delete(0, tk.END)
            entry.config(foreground='black')

    def on_focus_out(self, entry):
        if entry.get() == "":
            entry.insert(0, "Search news...")
            entry.config(foreground='grey')

    def search_news(self):
        query = self.search_var.get().strip()
        if not query:
            self.show_error("Please enter a search term")
            return

        self.show_loading("Searching news...")
        
        try:
            params = {
                'q': query,
                'language': 'en',
                'page': self.current_page,
                'page_size': 20  # Fixed page size
            }

            articles = self.newsapi.get_everything(**params)
            self.total_results = articles.get('totalResults', 0)
            self.display_articles(articles['articles'])

        except Exception as e:
            self.show_error(f"Error searching news: {str(e)}")
        finally:
            self.hide_loading()

    def show_top_headlines(self):
        self.show_loading("Fetching headlines...")
        try:
            params = {
                'country': 'us',
                'language': 'en',
                'page': self.current_page,
                'page_size': 20
            }
            
            # Add category if selected
            if hasattr(self, 'current_category') and self.current_category:
                params['category'] = self.current_category
            
            headlines = self.newsapi.get_top_headlines(**params)
            self.total_results = headlines.get('totalResults', 0)
            self.display_articles(headlines['articles'])
            
            # Update category label
            category = self.current_category.title() if hasattr(self, 'current_category') and self.current_category else "All"
            self.loading_var.set(f"📰 {category} News - Showing {len(headlines['articles'])} articles")
            
        except Exception as e:
            self.show_error(f"Error fetching headlines: {str(e)}")
        finally:
            self.hide_loading()

    def display_articles(self, articles):
        # Clear existing items
        for item in self.article_list.get_children():
            self.article_list.delete(item)
        
        if not articles:
            self.show_error("No articles found.")
            return

        # Update status bar with pagination info
        if hasattr(self, 'total_results'):
            page_size = 20
            start = (self.current_page - 1) * page_size + 1
            end = min(start + page_size - 1, self.total_results)
            self.loading_var.set(f"Showing {start}-{end} of {self.total_results} articles")

        # Store articles for detail view
        self.current_articles = articles

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Enhanced article display with categories and formatting
        for i, article in enumerate(articles):
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown source')
            published = article.get('publishedAt', '')
            dt = None
            
            # Format date
            if published:
                try:
                    # Parse the ISO format date and make it timezone-aware
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    published = dt.strftime('%b %d, %Y %H:%M')
                except:
                    pass
                
            # Add visual indicators for article age
            if dt and (now - dt).total_seconds() < 86400:  # 24 hours in seconds
                title = "🆕 " + title
                
            self.article_list.insert('', 'end', values=(title, source, published), iid=i)
            
            # Alternate row colors
            if i % 2:
                self.article_list.tag_configure(i, background='#f5f5f5')

    def on_article_select(self, event):
        selection = self.article_list.selection()
        if not selection:
            return

        article_index = int(selection[0])
        article = self.current_articles[article_index]

        # Display article details
        self.display_article_details(article)
        
        # Find and display related articles
        self.find_related_articles(article)

    def display_article_details(self, article):
        # Enable widget temporarily to update content
        self.detail_text.configure(state='normal')
        self.detail_text.delete(1.0, tk.END)
        
        title = article.get('title', 'No title')
        source = article.get('source', {}).get('name', 'Unknown source')
        author = article.get('author', 'Unknown author')
        description = article.get('description', 'No description available')
        content = article.get('content', 'No content available')
        url = article.get('url', '')
        published = article.get('publishedAt', '')
        
        # Format date nicely
        if published:
            try:
                dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                published = dt.strftime('%B %d, %Y at %H:%M')
            except:
                pass

        detail_text = f"""
{title}
{'='*len(title)}

📰 {source}
✍️ {author}
🕒 {published}

📝 Description:
{description}

📄 Content:
{content}

🔗 Read more: {url}
"""
        self.detail_text.insert(tk.END, detail_text)
        
        # Style the text
        self.detail_text.tag_add("title", "2.0", "3.0")
        self.detail_text.tag_add("url", "end-2c linestart", "end-1c")
        
        self.detail_text.tag_config("title", font=('Helvetica', 12, 'bold'))
        self.detail_text.tag_config("url", foreground="blue", underline=True)
        self.detail_text.tag_bind("url", "<Button-1>", lambda e: webbrowser.open(url))
        
        # Disable widget again to make it read-only
        self.detail_text.configure(state='disabled')

    def clear_search(self):
        self.search_var.set("")
        self.detail_text.delete(1.0, tk.END)
        for item in self.article_list.get_children():
            self.article_list.delete(item)

    def show_loading(self, message):
        self.loading_var.set(f"Loading: {message}")
        self.root.config(cursor="watch")
        self.root.update()

    def hide_loading(self):
        self.loading_var.set("")
        self.root.config(cursor="")

    def show_error(self, message):
        self.loading_var.set(f"❌ {message}")
        self.loading_label.configure(foreground=self.colors['error'])
        self.root.after(3000, self.clear_error)

    def clear_error(self):
        self.loading_var.set("")
        self.loading_label.configure(foreground=self.colors['text'])

    def next_page(self):
        if hasattr(self, 'total_results'):
            page_size = 20  # Fixed page size
            max_pages = (self.total_results + page_size - 1) // page_size
            if self.current_page < max_pages:
                self.current_page += 1
                if self.search_var.get().strip():
                    self.search_news()
                else:
                    self.show_top_headlines()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            if self.search_var.get().strip():
                self.search_news()
            else:
                self.show_top_headlines()

    def refresh_news(self):
        if self.search_var.get().strip():
            self.search_news()
        else:
            self.show_top_headlines()

    def open_in_browser(self):
        selection = self.article_list.selection()
        if selection:
            article = self.current_articles[int(selection[0])]
            url = article.get('url', '')
            if url:
                webbrowser.open(url)
                self.show_success("Article opened in browser")

    def copy_article_text(self):
        text = self.detail_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.show_success("Article text copied to clipboard")

    def show_article_preview(self, article):
        preview = tk.Toplevel(self.root)
        preview.title("Article Preview")
        preview.geometry("800x600")
        
        # Make preview window modal
        preview.transient(self.root)
        preview.grab_set()
        
        # Style preview window
        content = ttk.Frame(preview, padding=20, style='Surface.TFrame')
        content.pack(fill=tk.BOTH, expand=True)
        
        # Add close button
        close_btn = ttk.Button(content, 
                              text="✕",
                              command=preview.destroy,
                              style='Action.TButton')
        close_btn.pack(side=tk.TOP, anchor=tk.E)
        
        # Title with better styling
        title = ttk.Label(content, 
                          text=article.get('title', ''),
                          font=('Helvetica', 16, 'bold'),
                          wraplength=750)
        title.pack(fill=tk.X, pady=(0, 15))
        
        # Image with loading indicator
        if article.get('urlToImage'):
            try:
                # Show loading spinner
                loading_label = ttk.Label(content, text="Loading image...")
                loading_label.pack()
                
                # Load image in background
                def load_image():
                    response = requests.get(article.get('urlToImage'))
                    img_data = Image.open(BytesIO(response.content))
                    img_data.thumbnail((750, 400))
                    photo = ImageTk.PhotoImage(img_data)
                    
                    # Update UI in main thread
                    loading_label.destroy()
                    img_label = ttk.Label(content, image=photo)
                    img_label.image = photo
                    img_label.pack(pady=10)
                
                threading.Thread(target=load_image, daemon=True).start()
            except:
                pass
        
        # Article metadata
        meta_frame = ttk.Frame(content)
        meta_frame.pack(fill=tk.X, pady=10)
        
        source = article.get('source', {}).get('name', 'Unknown')
        author = article.get('author', 'Unknown author')
        published = article.get('publishedAt', '')
        
        if published:
            try:
                dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                published = dt.strftime('%B %d, %Y at %H:%M')
            except:
                pass
        
        ttk.Label(meta_frame, text=f"📰 {source}").pack(side=tk.LEFT, padx=5)
        ttk.Label(meta_frame, text=f"✍️ {author}").pack(side=tk.LEFT, padx=5)
        ttk.Label(meta_frame, text=f"🕒 {published}").pack(side=tk.LEFT, padx=5)
        
        # Description and content
        if article.get('description'):
            desc_frame = ttk.LabelFrame(content, text="Description", padding=10)
            desc_frame.pack(fill=tk.X, pady=10)
            ttk.Label(desc_frame, 
                     text=article.get('description'),
                     wraplength=750).pack()
        
        # Action buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_frame,
                   text="🌐 Read Full Article",
                   command=lambda: webbrowser.open(article.get('url', '')),
                   style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame,
                   text="📋 Copy Link",
                   command=lambda: self.share_specific_article(article),
                   style='Action.TButton').pack(side=tk.LEFT, padx=5)

    def show_search_suggestions(self, event):
        query = self.search_var.get().strip()
        if len(query) < 2:
            self.suggestion_frame.pack_forget()
            return
        
        # Clear previous suggestions
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        
        # Show suggestions frame
        self.suggestion_frame.pack(fill=tk.X)
        
        # Add some suggested searches
        suggestions = [
            f"{query} news",
            f"latest {query}",
            f"{query} today",
            f"{query} analysis"
        ]
        
        for suggestion in suggestions:
            suggestion_btn = ttk.Label(
                self.suggestion_frame,
                text=suggestion,
                style='Link.TLabel',
                cursor='hand2'
            )
            suggestion_btn.pack(anchor=tk.W, padx=5, pady=2)
            suggestion_btn.bind('<Button-1>', 
                              lambda e, s=suggestion: self.use_suggestion(s))

    def use_suggestion(self, suggestion):
        self.search_var.set(suggestion)
        self.suggestion_frame.pack_forget()
        self.search_news()

    def show_card_view(self):
        # Hide treeview
        self.article_list.pack_forget()
        
        # Create or show card frame
        if not hasattr(self, 'card_frame'):
            self.card_frame = ttk.Frame(self.paned_window)
            self.paned_window.add(self.card_frame, weight=1)
        else:
            self.card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clear existing cards
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        
        # Create canvas for scrolling
        canvas = tk.Canvas(self.card_frame, bg=self.colors['background'])
        scrollbar = ttk.Scrollbar(self.card_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create cards for articles
        for i, article in enumerate(self.current_articles):
            self.create_article_card(scrollable_frame, article, i)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_article_card(self, parent, article, index):
        # Card frame with hover effect
        card = ttk.Frame(parent, style='Card.TFrame', cursor='hand2')
        card.pack(fill=tk.X, padx=10, pady=5)
        
        # Bind hover effects
        card.bind('<Enter>', lambda e: self.on_card_hover(card, True))
        card.bind('<Leave>', lambda e: self.on_card_hover(card, False))
        card.bind('<Button-1>', lambda e: self.on_card_click(article))
        
        # Image
        if article.get('urlToImage'):
            try:
                response = requests.get(article.get('urlToImage'))
                img_data = Image.open(BytesIO(response.content))
                img_data.thumbnail((200, 120))
                photo = ImageTk.PhotoImage(img_data)
                img_label = ttk.Label(card, image=photo)
                img_label.image = photo
                img_label.pack(pady=5)
            except:
                pass

        # Title
        title = ttk.Label(card, 
                          text=article.get('title', ''),
                          font=('Helvetica', 11, 'bold'),
                          wraplength=300)
        title.pack(fill=tk.X, padx=10, pady=5)
        
        # Source and date
        info_frame = ttk.Frame(card)
        info_frame.pack(fill=tk.X, padx=10)
        
        source = article.get('source', {}).get('name', 'Unknown')
        ttk.Label(info_frame, 
                 text=f"📰 {source}",
                 font=('Helvetica', 9)).pack(side=tk.LEFT)
        
        ttk.Label(info_frame,
                 text=f"🕒 {article.get('publishedAt', '')}",
                 font=('Helvetica', 9)).pack(side=tk.RIGHT)
        
        # Description
        if article.get('description'):
            desc = ttk.Label(card,
                            text=article.get('description'),
                            wraplength=300,
                            font=('Helvetica', 9))
            desc.pack(fill=tk.X, padx=10, pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame,
                   text="Read More",
                   command=lambda: webbrowser.open(article.get('url', '')),
                   style='Card.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame,
                   text="Share",
                   command=lambda: self.share_specific_article(article),
                   style='Card.TButton').pack(side=tk.LEFT, padx=2)

    def show_list_view(self):
        if hasattr(self, 'card_frame'):
            self.card_frame.pack_forget()
        self.article_list.pack(fill=tk.BOTH, expand=True, padx=5)

    def share_specific_article(self, article):
        url = article.get('url', '')
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.show_success("Article URL copied to clipboard!")

    def on_card_hover(self, card, entering):
        if entering:
            card.configure(style='CardHover.TFrame')
        else:
            card.configure(style='Card.TFrame')

    def on_card_click(self, article):
        self.show_article_preview(article)

    def save_article(self):
        selection = self.article_list.selection()
        if not selection:
            return
        
        article = self.current_articles[int(selection[0])]
        
        # Create saves directory in user's Documents folder
        documents_path = str(Path.home() / "Documents")
        save_folder = os.path.join(documents_path, "NewsApp_Saved_Articles")
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        # Clean and format the title for filename
        title = article.get('title', 'Untitled')
        # Remove special characters and replace spaces with underscores
        clean_title = "".join(c if c.isalnum() or c.isspace() else '_' for c in title)
        clean_title = clean_title.replace(' ', '_')
        # Limit length and remove multiple underscores
        clean_title = '_'.join(filter(None, clean_title.split('_')))[:50]
        
        # Add date to filename
        date = datetime.now().strftime("%Y%m%d")
        filename = f"{date}_{clean_title}.txt"
        full_path = os.path.join(save_folder, filename)
        
        # Ensure filename is unique
        counter = 1
        while os.path.exists(full_path):
            filename = f"{date}_{clean_title}_{counter}.txt"
            full_path = os.path.join(save_folder, filename)
            counter += 1
        
        # Save to file with better formatting
        try:
            with open(full_path, "w", encoding='utf-8') as f:
                f.write(f"{'='*50}\n")
                f.write(f"Title: {article.get('title', '')}\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"📰 Source: {article.get('source', {}).get('name', '')}\n")
                f.write(f"✍️ Author: {article.get('author', 'Unknown')}\n")
                f.write(f"🕒 Date: {article.get('publishedAt', '')}\n")
                f.write(f"🌐 URL: {article.get('url', '')}\n\n")
                f.write(f"Description:\n{'-'*20}\n")
                f.write(f"{article.get('description', '')}\n\n")
                f.write(f"Content:\n{'-'*20}\n")
                f.write(f"{article.get('content', '')}\n")
            
            # Show success message with option to open folder
            self.show_save_success(save_folder, full_path)
        except Exception as e:
            self.show_error(f"Error saving article: {str(e)}")

    def show_save_success(self, folder_path, file_path):
        # Create success dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Article Saved")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure dialog
        dialog.configure(bg=self.colors['surface'])
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Success message
        ttk.Label(frame, 
                 text="✅ Article saved successfully!",
                 font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(frame, 
                 text=f"Location: {folder_path}",
                 wraplength=350).pack(pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame,
                   text="Open File",
                   command=lambda: os.startfile(file_path),
                   style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame,
                   text="Open Folder",
                   command=lambda: os.startfile(folder_path),
                   style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame,
                   text="Close",
                   command=dialog.destroy,
                   style='Action.TButton').pack(side=tk.RIGHT, padx=5)

    def find_related_articles(self, article):
        # Clear existing items
        self.related_list.delete(*self.related_list.get_children())
        
        # Configure columns
        self.related_list.heading("title", text="Title", anchor=tk.W)
        self.related_list.heading("source", text="Source", anchor=tk.W)
        
        self.related_list.column("title", width=300, anchor=tk.W)
        self.related_list.column("source", width=100, anchor=tk.W)
        
        # Get keywords from title and description
        keywords = []
        title = article.get('title', '').lower()
        desc = article.get('description', '').lower()
        
        # Extract meaningful words (longer than 3 chars)
        words = set((title + " " + desc).split())
        keywords = [w for w in words if len(w) > 3 and w not in {'this', 'that', 'with', 'from'}]
        
        if keywords:
            try:
                # Search for related articles
                query = ' OR '.join(keywords[:5])  # Use top 5 keywords
                params = {
                    'q': query,
                    'language': 'en',
                    'page': 1,
                    'page_size': 10
                }
                
                related = self.newsapi.get_everything(**params)
                
                # Display related articles
                for rel_article in related.get('articles', []):
                    if rel_article.get('url') != article.get('url'):  # Skip current article
                        title = rel_article.get('title', '')
                        source = rel_article.get('source', {}).get('name', '')
                        self.related_list.insert('', 'end', values=(title, source))
            
                # Add click handler for related articles
                self.related_list.bind('<Double-1>', self.on_related_article_click)
                                                  
            except Exception as e:
                print(f"Error finding related articles: {e}")

    def on_related_article_click(self, event):
        selection = self.related_list.selection()
        if selection:
            item = selection[0]
            title = self.related_list.item(item)['values'][0]
            # Find the article with matching title
            for article in self.current_articles:
                if article.get('title') == title:
                    self.display_article_details(article)
                    break

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_container, style='Surface.TFrame')
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Category buttons with icons and tooltips
        categories = [
            ("All", "📰", None, "Show all news"),
            ("Business", "💼", "business", "Business news and markets"),
            ("Technology", "💻", "technology", "Tech news and innovations"),
            ("Sports", "⚽", "sports", "Sports coverage"),
            ("Health", "🏥", "health", "Health and medical news"),
            ("Science", "🔬", "science", "Scientific discoveries"),
            ("Entertainment", "🎬", "entertainment", "Entertainment and media")
        ]
        
        # Create category buttons frame with scrolling
        cat_canvas = tk.Canvas(toolbar, height=40, bg=self.colors['surface'])
        cat_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        cat_frame = ttk.Frame(cat_canvas)
        cat_canvas.create_window((0, 0), window=cat_frame, anchor='nw')
        
        for name, icon, cat, tooltip in categories:
            btn = ttk.Button(cat_frame, 
                            text=f"{icon} {name}", 
                            command=lambda c=cat: self.filter_category(c),
                            style='Category.TButton')
            btn.pack(side=tk.LEFT, padx=2)
            
            # Create tooltip
            self.create_tooltip(btn, tooltip)

        # View toggle
        view_frame = ttk.Frame(toolbar)
        view_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(view_frame, text="View:").pack(side=tk.LEFT, padx=5)
        self.view_var = tk.StringVar(value="list")
        ttk.Radiobutton(view_frame, text="List", value="list", 
                        variable=self.view_var, 
                        command=self.toggle_view).pack(side=tk.LEFT)
        ttk.Radiobutton(view_frame, text="Cards", value="cards", 
                        variable=self.view_var,
                        command=self.toggle_view).pack(side=tk.LEFT)

    def create_tooltip(self, widget, text):
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, 
                             background=self.colors['primary_dark'],
                             foreground='white',
                             padding=5)
            label.pack()
            
            widget.tooltip = tooltip

        def leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def filter_category(self, category):
        self.current_category = category
        self.current_page = 1
        self.show_top_headlines()

    def toggle_view(self):
        if self.view_var.get() == "cards":
            self.show_card_view()
        else:
            self.show_list_view()

    def create_saved_articles_frame(self):
        # Create a new tab in the notebook for saved articles
        saved_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(saved_frame, text="📂 Saved")
        
        # Toolbar for saved articles
        toolbar = ttk.Frame(saved_frame, style='Surface.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side controls
        left_controls = ttk.Frame(toolbar)
        left_controls.pack(side=tk.LEFT)
        
        # Refresh button
        self.create_action_button(left_controls, "🔄 Refresh", self.refresh_saved_articles)
        
        # Open saved folder button
        self.create_action_button(left_controls, "📁 Open Folder", 
                                lambda: os.startfile(self.get_save_folder()))
        
        # Search saved articles
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.saved_search_var = tk.StringVar()
        self.saved_search_var.trace('w', self.filter_saved_articles)
        search_entry = ttk.Entry(search_frame, textvariable=self.saved_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Create treeview for saved articles
        self.saved_list = ttk.Treeview(saved_frame,
                                      columns=("title", "date", "source"),
                                      show="headings",
                                      style='Article.Treeview')
        
        self.saved_list.heading("title", text="Title", anchor=tk.W)
        self.saved_list.heading("date", text="Saved Date", anchor=tk.W)
        self.saved_list.heading("source", text="Source", anchor=tk.W)
        
        self.saved_list.column("title", width=400, anchor=tk.W)
        self.saved_list.column("date", width=150, anchor=tk.W)
        self.saved_list.column("source", width=150, anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(saved_frame, orient=tk.VERTICAL, 
                                 command=self.saved_list.yview)
        self.saved_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.saved_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu for saved articles
        self.saved_context_menu = tk.Menu(self.root, tearoff=0)
        self.saved_context_menu.add_command(label="Open", command=self.open_selected_saved)
        self.saved_context_menu.add_command(label="Delete", command=self.delete_saved_article)
        self.saved_context_menu.add_separator()
        self.saved_context_menu.add_command(label="Open Containing Folder", 
                                          command=lambda: os.startfile(os.path.dirname(self.get_selected_saved_path())))
        
        # Bind right-click to show context menu
        self.saved_list.bind('<Button-3>', self.show_saved_context_menu)
        # Bind double-click to open file
        self.saved_list.bind('<Double-1>', lambda e: self.open_selected_saved())
        
        # Initial load of saved articles
        self.refresh_saved_articles()

    def get_save_folder(self):
        documents_path = str(Path.home() / "Documents")
        save_folder = os.path.join(documents_path, "NewsApp_Saved_Articles")
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        return save_folder

    def refresh_saved_articles(self):
        # Clear existing items
        for item in self.saved_list.get_children():
            self.saved_list.delete(item)
        
        save_folder = self.get_save_folder()
        
        try:
            # Get all text files in the save folder
            files = [f for f in os.listdir(save_folder) if f.endswith('.txt')]
            
            for file in sorted(files, reverse=True):
                # Get file creation/modification time
                file_path = os.path.join(save_folder, file)
                timestamp = os.path.getmtime(file_path)
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                
                # Get title from filename (remove date prefix and .txt)
                title = file[9:-4].replace('_', ' ')  # Remove YYYYMMDD_ prefix
                
                # Get source from file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for the line starting with "📰 Source:"
                        for line in content.split('\n'):
                            if '📰 Source:' in line:
                                source = line.split('📰 Source:')[1].strip()
                                break
                        else:
                            source = "Unknown"
                except:
                    source = "Unknown"
                
                self.saved_list.insert('', 'end', values=(title, date_str, source), tags=(file_path,))
            
            # Update status
            self.loading_var.set(f"📂 Found {len(files)} saved articles")
            
        except Exception as e:
            self.show_error(f"Error loading saved articles: {str(e)}")

    def open_selected_saved(self):
        file_path = self.get_selected_saved_path()
        if file_path:
            try:
                os.startfile(file_path)
            except Exception as e:
                self.show_error(f"Error opening file: {str(e)}")

    def delete_saved_article(self):
        file_path = self.get_selected_saved_path()
        if file_path:
            if messagebox.askyesno("Delete Article", "Are you sure you want to delete this saved article?"):
                try:
                    os.remove(file_path)
                    self.refresh_saved_articles()
                    self.show_success("Article deleted successfully")
                except Exception as e:
                    self.show_error(f"Error deleting file: {str(e)}")

    def filter_saved_articles(self, *args):
        search_term = self.saved_search_var.get().lower()
        
        # Clear and reload list
        for item in self.saved_list.get_children():
            self.saved_list.delete(item)
        
        save_folder = self.get_save_folder()
        files = [f for f in os.listdir(save_folder) if f.endswith('.txt')]
        
        for file in sorted(files, reverse=True):
            title = file[9:-4].replace('_', ' ')  # Remove date prefix and .txt
            
            # Only add if search term is in title
            if search_term in title.lower():
                file_path = os.path.join(save_folder, file)
                timestamp = os.path.getmtime(file_path)
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                
                # Get source from file content - improved parsing
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for the line starting with "📰 Source:"
                        for line in content.split('\n'):
                            if '📰 Source:' in line:
                                source = line.split('📰 Source:')[1].strip()
                                break
                        else:
                            source = "Unknown"
                except:
                    source = "Unknown"
                
                self.saved_list.insert('', 'end', values=(title, date_str, source), tags=(file_path,))

    def show_saved_context_menu(self, event):
        try:
            self.saved_list.selection_set(self.saved_list.identify_row(event.y))
            self.saved_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.saved_context_menu.grab_release()

    def get_selected_saved_path(self):
        selection = self.saved_list.selection()
        if selection:
            return self.saved_list.item(selection[0])['tags'][0]
        return None

    def load_settings(self):
        try:
            settings_path = os.path.join(self.get_save_folder(), "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    self.font_size_var.set(settings.get('font_size', '11'))
                    self.current_font_size = int(self.font_size_var.get())
        except:
            pass

    def save_settings(self):
        try:
            settings = {
                'font_size': self.font_size_var.get()
            }
            settings_path = os.path.join(self.get_save_folder(), "settings.json")
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def show_api_key_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("API Key Required")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, 
                 text="Please enter your News API key:",
                 font=('Helvetica', 10)).pack(pady=(0, 10))
        
        key_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=key_var, width=40)
        entry.pack(pady=(0, 10))
        
        def save_key():
            global API_KEY
            API_KEY = key_var.get()
            dialog.destroy()
        
        ttk.Button(frame, text="Save", command=save_key).pack()

def main():
    root = tk.Tk()
    app = NewsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 